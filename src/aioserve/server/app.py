import asyncio
from .http import handle_http

async def app(scope, receive, send):
    protocol = scope['type']

    if protocol == "http":
        await handle_http(scope, receive, send)
    elif protocol == "websocket":
        pass
    elif protocol == "lifespan":
        pass