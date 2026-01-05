import pytest
from aioserve.server.app import App
from aioserve.server.http import JSONResponse

class SimpleMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            scope["headers"].append((b"x-middleware", b"true"))
        await self.app(scope, receive, send)

class EarlyReturnMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["path"] == "/intercept":
            response = JSONResponse({"intercepted": True})
            await response(scope, receive, send)
        else:
            await self.app(scope, receive, send)

@pytest.mark.asyncio
async def test_middleware_modifies_request():
    app = App()
    app.add_middleware(SimpleMiddleware)

    @app.get("/check-middleware")
    async def handler(request):
        headers = dict(request.scope["headers"])
        return JSONResponse({"has_middleware": b"x-middleware" in headers})

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/check-middleware",
        "headers": [],
    }
    
    events = []
    async def send(event):
        events.append(event)
    
    async def receive():
        return {"type": "http.request", "body": b""}

    await app(scope, receive, send)

    assert len(events) == 2
    assert b'{"has_middleware": true}' == events[1]["body"]

@pytest.mark.asyncio
async def test_middleware_intercept():
    app = App()
    app.add_middleware(EarlyReturnMiddleware)

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/intercept",
        "headers": [],
    }
    
    events = []
    async def send(event):
        events.append(event)
    
    async def receive():
         return {"type": "http.request", "body": b""}

    await app(scope, receive, send)
    
    assert len(events) == 2
    assert b'{"intercepted": true}' == events[1]["body"]
