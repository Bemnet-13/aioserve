import asyncio

async def handle_http(scope, receive, send):
    body = b""

    while True:
        event = await receive()
        if event["type"] == "http.request":
            body += event.get("body", b"")
            if not event.get("more_body", False):
                break

    if scope.get("path", "/") == "/":
        status = 200; content = b"Hello, ASGI!"
    else:
        status = 404; content = b"Not Found"

    # Send HTTP response start (status and headers)
    await send({
        "type":  "http.response.start",
        "status": status,
        "headers": [
            (b"content-type", b"text/plain"),
            (b"content-length", str(len(content)).encode())
        ],
    })
    # Send HTTP response body (final message with more_body=False by default)
    await send({
        "type":  "http.response.body",
        "body":  content,
    })