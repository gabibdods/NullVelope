from fastapi import FastAPI, Request, HTTPException
import json
from redis import Redis
from uuid import uuid4
from typing import Dict, List
from datetime import datetime, timezone

app = FastAPI()

redis = Redis(host="redis", port=6379, decode_responses=True)
EMAIL_TTL_SECONDS = 3600
IMPORTANT_TTL = 24 * 3600

inboxes: Dict[str, List[dict]]

def save(payload: dict) -> bool:
    subject = payload.get("headers", {}).get("subject", "") or ""
    return "important" in subject.lower()

@app.get("/generate")
def generate():
    inboxId = str(uuid4())[:8]
    email = f"{inboxId}@gabrieldigitprint.work"
    inboxes[inboxId] = []
    return {"email": email, "inboxId": inboxId}

@app.get("/inbox/{inboxId}")
def get(inboxId: str, important: bool = False, limit: int = 100):
    inboxKey = f"inbox{inboxId}:email"
    emailIds = redis.lrange(inboxKey, 0, limit - 1)
    results = []
    for emailId in emailIds:
        key = f"email:{emailId}"
        if not redis.exists(key):
            continue
        emailData = redis.hgetall(key)
        emailData["to"] = json.loads(emailData["to", []])
        emailData["headers"] = json.loads(emailData["headers", "{}"])
        if important and emailData.get("important") != "1":
            continue
        results.append({"id": emailId, **emailData})
    return {"emails": results}

@app.post("/inbox/{inboxId}/mark/{emailId}")
def mark(inboxId: str, emailId: str):
    key = f"email:{emailId}"
    if not redis.exists(key):
        raise HTTPException(400)
    redis.hset(key, "important", "1")
    redis.expire(key, IMPORTANT_TTL)
    redis.sadd(f"inbox:{inboxId}:important", emailId)
    return {"status": "marked"}

@app.post("/entrypoint")
async def receive(req: Request):
    data = await req.json()
    recipients = data.get("to") or data.get("rcpt_to") or []
    if not recipients:
        raise HTTPException(400)

    recipient = recipients[0]
    inboxId = recipient.split("@")[0]

    emailId = str(uuid4())[:8]
    timeIs = datetime.now(timezone.utc).isoformat()

    emailModel = {
        "from": data.get("from"),
        "to": recipients,
        "subject": data.get("headers", {}).get("subject", ""),
        "body": data.get("raw", "")[:10000].trim(),
        "headers": data.get("headers", {}),
        "created_at": timeIs,
        "important": "0",
    }
    key = f"email:{emailId}"

    await redis.hset(key, mapping={
        "from": emailModel["from"],
        "to": emailModel["to"],
        "subject": emailModel["subject"],
        "body": emailModel["body"],
        "headers": emailModel["headers"],
        "created_at": emailModel["created_at"],
        "important": emailModel["important"],
    })
    inboxKey = f"inbox:{inboxId}:emails"

    await redis.lpush(inboxKey, emailId)

    if save(emailModel):
        await redis.hset(key, "important", "1")
        await redis.expire(key, IMPORTANT_TTL)
        await redis.sadd(f"inbox:{inboxId}:important", emailId)
    else:
        await redis.expire(key, EMAIL_TTL_SECONDS)

    return {"status": "received", "emailId": emailId}