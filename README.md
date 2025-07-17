# 📬 Temporary Email Server — Disposable Inboxes with Real-Time Reception

This project implements a server that generates **temporary email addresses** for anonymous use. It captures and stores emails sent to those addresses for a short time, allowing users to receive verification links or one-time messages without using their personal email.

---

## 🔍 Problem Statement

Many online services require email verification even when users don't wish to provide their real email addresses. Disposable or temporary email services solve this by allowing anonymous email reception — but building such systems from scratch involves handling DNS, SMTP, mail delivery, parsing, and secure message storage.

This project tackles that complexity by creating a custom, lightweight temporary mail server.

---

## 🎯 Project Goals

- ✅ Generate **random temporary email addresses** (e.g., `abc123@tempmail123.xyz`)
- ✅ Receive and store **incoming email messages**
- ✅ Provide users with a **web-based inbox** to read emails for a short duration
- ✅ Automatically **expire inboxes and messages** for privacy and storage efficiency
- ✅ Rate-limit abuse and prevent spam or malicious attachments

---

## 🛠️ Tools & Technology Stack

### 🧠 Core Components

| Layer            | Tool/Tech                  | Purpose                             |
|------------------|----------------------------|-------------------------------------|
| 📮 Mail Server   | Haraka (Node.js)           | Receives emails via SMTP            |
| 🧠 Backend API   | Python + FastAPI           | Manages inbox creation & message API|
| 🗃️ Database      | SQLite / Redis             | Stores inboxes and messages         |
| 🌐 Frontend      | React / HTML               | Displays inboxes in real-time       |
| 🧾 Domain & DNS  | Custom domain + MX records | Routes email to Haraka server       |
| 🔒 Security      | Rate limiting + Cleanup    | Prevent spam and data persistence   |

---

## 🧩 Design Decisions

- Chose **Haraka** as the SMTP server due to its lightweight, Node.js-based plugin system
- Used **FastAPI** for the backend to combine speed with easy API development
- Emails are routed from Haraka directly to the backend (via hooks or database inserts)
- Opted for **SQLite** during development for simplicity, but Redis is also supported for scaling
- Inboxes are identified via `UUIDv4` prefixes (first 8 characters) to ensure uniqueness
- Frontend supports polling or WebSocket-based inbox refreshing

---

## 🔧 Architecture Overview

```plaintext
                          +------------------------+
                          |   tempmail123.xyz      |
                          |   (DNS + MX Record)    |
                          +-----------+------------+
                                      |
                              Email sent to temp address
                                      |
                          +-----------v------------+
                          |     Haraka SMTP Server |
                          |  (accepts *@tempmail123.xyz) |
                          +-----------+------------+
                                      |
                        +-------------v--------------+
                        |      FastAPI Backend       |
                        | - /generate (create inbox) |
                        | - /inbox/<id> (list mails) |
                        +-------------+--------------+
                                      |
                          +-----------v------------+
                          |     SQLite / Redis     |
                          |  (stores metadata/msg) |
                          +-----------+------------+
                                      |
                              Inbox viewer (React)
```

---

## 🧠 Features
- ✨ One-click temp inbox creation
- ✉️ Real-time email viewing via frontend
- 🔐 Disposable email cleanup every 10–60 minutes
- 🧼 Attachment filtering (block .exe, .bat, etc.)
- 🚫 Rate-limiting to prevent abuse
- ⚙️ Compatible with Docker and cloud deployment
- ⚔️ Challenges & Solutions

---

## Challenge Solution

| Challenge                            | Solution                                                              |
| ------------------------------------ | --------------------------------------------------------------------- |
| Handling raw SMTP delivery           | Used Haraka’s plugin system to intercept and process incoming mail    |
| Fast API response for inbox messages | Optimized read queries with Redis/SQLite, decoupled storage from SMTP |
| Abusing inbox generation             | Implemented rate-limiting and temporary IP blocks                     |
| Parsing emails & attachments         | Hooked Haraka to a MIME parser and stripped unsupported file types    |
| Domain delivery configuration        | Verified MX records + DNS settings using test SMTP tools              |


---

## 📚 Lessons Learned
Learned to configure a domain’s MX records to direct traffic to a custom mail server

Built a lightweight SMTP server using Haraka’s plugin hooks

Designed asynchronous inbox systems using FastAPI and Redis

Gained experience in email protocol flows (SMTP, MIME, etc.)

Practiced frontend-backend integration using generated identifiers and polling

Balanced usability and privacy with auto-expiring data models

---

## 🧪 Bonus & Optional Features
- Use a "catch-all" forwarding system like ImprovMX to capture all mail to *@yourdomain.com
- Integrate mailparser.io to pull from Gmail or custom IMAP accounts
- Support WebSocket-based inbox refresh
- Wrap the entire setup into Docker Compose
- Extend frontend with QR inbox access and password-less login
