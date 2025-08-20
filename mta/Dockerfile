FROM debian:12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends postfix rsyslog gettext-base && rm -rf /var/lib/apt/lists/*

COPY ./config/* /etc/postfix/

COPY docker-entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 25

CMD ["/entrypoint.sh"]
