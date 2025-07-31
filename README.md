# NullVelope

# Disposable Email Server with Real-Time Reception

### Description

- This project implements a self-hosted temporary email server that generates disposable inboxes and receives real-time emails for short-term use
- It enables users to obtain one-time email addresses to receive verification links or messages anonymously without revealing their personal accounts

---

## NOTICE

- Please read through this `README.md` to better understand the project's source code and setup instructions
- Also, make sure to review the contents of the `License/` directory
- Your attention to these details is appreciated — enjoy exploring the project!

---

## Problem Statement

- Many online platforms require email verification for access, even if users prefer not to share their real email
- Building a temporary email system from scratch involves handling SMTP delivery, DNS configuration, secure message storage, and web integration
- This project addresses these challenges with a modular, secure architecture

---

## Project Goals

### Enable Anonymous Email Reception

- Generate random disposable email addresses with the domain @tempmail123.xyz, receive messages, and present them via a web interface

### Prevent Abuse and Ensure Privacy

- Secure the system against spam, abusive use, and long-term storage by implementing auto-expiring inboxes and rate-limiting mechanisms

---

## Tools, Materials & Resources

### Haraka

- Lightweight Node.js SMTP server used to receive and filter incoming emails

### FastAPI

- Backend framework used to handle inbox creation, message routing, and secure API responses

### SQLite & Redis

- Storage backends to persist inbox metadata and email contents

---

## Design Decision

### Haraka for SMTP Handling

- Chosen for its lightweight architecture and extensible plugin support in Node.js for email filtering and delivery hooks

### UUID-Generated Inboxes

- Each inbox uses a short `UUIDv4` prefix for uniqueness and anonymity, simplifying routing and frontend references

### Polling or WebSocket Frontend

- Inbox UI supports real-time updates using either polling mechanisms or WebSocket-based refresh strategies

---

## Features

### Instant Inbox Generation

- Users can create a temporary inbox in one click without registration or authentication

### Real-Time Email Reception

- Incoming messages are available immediately in the inbox via WebSocket or polling-based refresh

### Secure Ephemeral Storage

- Inboxes and messages automatically expire within 10 to 60 minutes to ensure privacy and limit persistence

---

## Block Diagram

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

## Functional Overview

- The system consists of a mail reception layer (Haraka), an API backend (FastAPI), a storage engine (SQLite/Redis), and a frontend client
- Emails sent to a generated address are routed through Haraka, parsed, and inserted into the storage layer, from which they are served to the user interface

---

## Challenges & Solutions

### Handling SMTP Delivery in Real-Time

- Solved using Haraka plugins that intercept and stream email data into FastAPI or directly into a database queue

### Filtering Attachments and Malicious Input

- Configured MIME parsers to block `.exe`, `.bat`, and other unsafe file types before storage or frontend access

---

## Lessons Learned

### Custom Mail Infrastructure

- Gained experience setting up DNS, MX records, and custom SMTP routing with full domain control

### Backend Synchronization

- Designed asynchronous inbox creation and message flow using REST APIs and message queue concepts

---

## Project Structure

```plaintext
root/
├── License/
│   ├── LICENSE.md
│   │
│   └── NOTICE.md
│
├── .gitattributes
│
├── .gitignore
│
└── README.md

```

---

## Future Enhancements

- Add Docker Compose support for full system deployment
- Implement inbox refresh using native WebSocket streams
- Add QR code generation for inbox URLs
- Support Gmail/IMAP proxying via mailparser.io
- Auto-archive emails instead of hard-deletion
