const http = require('http');

exports.register = function() {
    this.loginfo("fastapi-webhook plugin registered");
}

exports.queue = function (next, connection) {
    const self = this;
    const txn = connection.transaction();
    let raw = '';

    txn.message_stream.on('data', chunk => {
        raw += chunk.toString();
    });

    txn.message_stream.on('end', () => {
        const payload = {
            from: txn.mail_from.original,
            to: txn.rcpt_to.map(r => r.original),
            headers: txn.header.headers,
            raw: raw
        }
    });
    const options = {
        hostname: 'fastapi',
        port: 8000,
        path: '/entrypoint',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(raw)
        },
    }
    const req = http.request(options, (res) => {
        res.on('data', () => {});
        res.on('end', () => {
            next(OK);
        });
    });
    req.on('error', (err) => {
        self.logerror(err);
        next(DENY, "webhook failed");
    });
    req.write(postData);
    req.end();
};