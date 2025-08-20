#!/bin/sh
set -e

: "${RELAY_DOMAIN:=nullvelope.local}"
: "${SMTP_INGEST_HOST:=relay}"
: "${SMTP_INGEST_PORT:=1025}"
: "${MYHOSTNAME:=mail.nullvelope.local}"

envsubst < /etc/postfix/main.cf.template > /etc/postfix/main.cf
envsubst < /etc/postfix/transport.template > /etc/postfix/transport
postmap /etc/postfix/transport

exec /usr/sbin/postfix start-fg
