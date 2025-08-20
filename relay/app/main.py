import os
import base64
import datetime
from typing import List, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from email import policy
from email.parser import BytesParser
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import AsyncMessage

MONGO_URL = os.environ.get("MONGO_URL")
MONGO_DB = os.environ.get("MONGO_DB")
DOMAIN = os.environ.get("DOMAIN")
SMTP_LISTEN = os.environ.get("SMTP_LISTEN")
SMTP_PORT = int(os.environ.get("SMTP_PORT"))
API_PORT = int(os.environ.get("API_PORT"))
MESSAGE_TTL_SECONDS = int(os.environ.get("MESSAGE_TTL_SECONDS"))
ADDRESS_TTL_SECONDS = int(os.environ.get("ADDRESS_TTL_SECONDS"))
CORS_ORIGINS = os.environ.get("CORS_ORIGINS")

client = MongoClient(MONGO_URL)
db = client[MONGO_DB]
messages: Collection = db["messages"]
addresses: Collection = db["addresses"]

def _safe_disposition(part):
    if hasattr(part, "get_content_disposition"):
        return part.get_content_disposition()
    cd = part.get("Content-Disposition")
    if not cd:
        return None
    return cd.split(";", 1)[0].strip().lower()

def _safe_get_text(part):
    if hasattr(part, "get_content"):
        try:
            return part.get_content()
        except Exception:
            pass
    payload = part.get_payload(decode=True)
    if isinstance(payload, (bytes, bytearray)):
        charset = None
        try:
            charset = part.get_content_charset()
        except Exception:
            pass
        charset = charset or "utf-8"
        try:
            return payload.decode(charset, "ignore")
        except Exception:
            return payload.decode("utf-8", "ignore")
    if isinstance(payload, str):
        return payload
    return ""

def _extract_bodies(msg):
    text_body = ""
    html_body = ""
    attachments = []

    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = _safe_disposition(part)

            if disp == "attachment":
                data = part.get_payload(decode=True) or b""
                content_b64 = None
                if len(data) <= 256 * 1024:
                    content_b64 = base64.b64encode(data).decode("ascii")
                attachments.append({
                    "filename": getattr(part, "get_filename", lambda: None)(),
                    "content_type": ctype,
                    "size": len(data),
                    "content_b64": content_b64,
                })
            elif ctype == "text/plain":
                text_body += _safe_get_text(part)
            elif ctype == "text/html":
                html_body += _safe_get_text(part)
    else:
        ctype = msg.get_content_type() if hasattr(msg, "get_content_type") else msg.get("Content-Type", "").split(";",1)[0].strip().lower()
        if ctype == "text/html":
            html_body = _safe_get_text(msg)
        else:
            text_body = _safe_get_text(msg)

    return text_body, html_body, attachments

class StoreHandler(AsyncMessage):
    async def handle_message(self, message):
        try:
            has_new_api = hasattr(message, "get_body")
            if not has_new_api and hasattr(message, "as_bytes"):
                message = BytesParser(policy=policy.default).parsebytes(message.as_bytes())
        except Exception:
            pass

        subject = message.get("Subject", "")
        mail_from = message.get("From", "")
        to_hdr = message.get_all("To", []) or []
        cc_hdr = message.get_all("Cc", []) or []

        rcpt_all = []
        for hdr in to_hdr + cc_hdr:
            rcpt_all.extend([p.strip() for p in hdr.split(",") if p.strip()])

        local_parts = []
        for addr in rcpt_all:
            try:
                if "@" in addr:
                    local, dom = addr.split("@", 1)
                    if dom.lower().strip("<> ") == DOMAIN:
                        local_parts.append(local.lower().strip("<> "))
            except Exception:
                continue

        text_body, html_body, attachments = _extract_bodies(message)

        doc = {
            "subject": subject,
            "from": mail_from,
            "to": rcpt_all,
            "local_parts": list(set(local_parts)) or [],
            "received_at": datetime.datetime.now(datetime.UTC),
            "headers": {k: v for (k, v) in message.items()},
            "text": text_body,
            "html": html_body,
            "attachments": attachments,
        }
        messages.insert_one(doc)
        return "250 Message accepted for delivery"

_controller: Optional[Controller] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        messages.drop_index("received_at_1")
    except Exception:
        pass
    try:
        addresses.drop_index("created_at_1")
    except Exception:
        pass
    messages.create_index([("received_at", ASCENDING)], expireAfterSeconds=MESSAGE_TTL_SECONDS)
    addresses.create_index([("created_at", ASCENDING)], expireAfterSeconds=ADDRESS_TTL_SECONDS)

    global _controller
    _controller = Controller(StoreHandler(), hostname=SMTP_LISTEN, port=SMTP_PORT)
    _controller.start()

    try:
        yield
    finally:
        if _controller is not None:
            _controller.stop()

app = FastAPI(title="Temp Mail API", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NewAddressResponse(BaseModel):
    local_part: str
    address: str
    expires_in_seconds: int

@app.post("/api/addresses", response_model=NewAddressResponse)
def make_address():
    import secrets, string
    alphabet = string.ascii_lowercase + string.digits
    local_part = "tm_" + "".join(secrets.choice(alphabet) for _ in range(10))
    address = f"{local_part}@{DOMAIN}"
    addresses.insert_one({"local_part": local_part, "created_at": datetime.datetime.now(datetime.UTC)})
    return NewAddressResponse(local_part=local_part, address=address, expires_in_seconds=ADDRESS_TTL_SECONDS)

class MessagePreview(BaseModel):
    id: str
    subject: str
    from_: str
    received_at: str
    has_attachments: bool

@app.get("/api/addresses/{local_part}/messages", response_model=List[MessagePreview])
def list_messages(local_part: str):
    cur = messages.find({"local_parts": local_part.lower()}).sort("received_at", -1).limit(100)
    return [
        MessagePreview(
            id=str(m["_id"]),
            subject=m.get("subject",""),
            from_=m.get("from",""),
            received_at=m.get("received_at").isoformat()+"Z",
            has_attachments=bool(m.get("attachments"))
        )
        for m in cur
    ]

class Attachment(BaseModel):
    filename: Optional[str]
    content_type: Optional[str]
    size: int
    content_b64: Optional[str]

class MessageDetail(BaseModel):
    id: str
    subject: str
    from_: str
    to: List[str]
    received_at: str
    text: str
    html: str
    attachments: List[Attachment]

from bson.objectid import ObjectId

@app.get("/api/messages/{message_id}", response_model=MessageDetail)
def get_message(message_id: str):
    try:
        oid = ObjectId(message_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Invalid message id")
    m = messages.find_one({"_id": oid})
    if not m:
        raise HTTPException(status_code=404, detail="Message not found")
    return MessageDetail(
        id=str(m["_id"]),
        subject=m.get("subject",""),
        from_=m.get("from",""),
        to=m.get("to",[]),
        received_at=m.get("received_at").isoformat()+"Z",
        text=m.get("text",""),
        html=m.get("html",""),
        attachments=[Attachment(**a) for a in m.get("attachments",[])],
    )

# z-page for testing
#@app.get("/api/healthz")
#def health():
#    return {"ok": True, "domain": DOMAIN, "smtp": {"host": SMTP_LISTEN, "port": SMTP_PORT}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=API_PORT, reload=False)