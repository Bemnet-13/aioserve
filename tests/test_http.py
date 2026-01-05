import pytest
import asyncio
from aioserve.server.app import App
from aioserve.server.http import JSONResponse

@pytest.mark.asyncio
async def test_basic_routing():
    app = App()

    @app.get("/hello")
    async def hello(request):
        return "Hello, World!"

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/hello",
    }
    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}
    
    events = []
    async def send(event):
        events.append(event)

    await app(scope, receive, send)

    assert len(events) == 2
    assert events[0]["type"] == "http.response.start"
    assert events[0]["status"] == 200
    assert events[1]["type"] == "http.response.body"
    assert events[1]["body"] == b"Hello, World!"

@pytest.mark.asyncio
async def test_post_json():
    app = App()

    @app.post("/items")
    async def create_item(request):
        data = await request.json()
        return JSONResponse({"id": 1, "name": data["name"]}, status_code=201)

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/items",
    }
    
    request_body = b'{"name": "test_item"}'
    
    async def receive():
        # Simple mock that returns body once
        if not hasattr(receive, "called"):
            receive.called = True
            return {"type": "http.request", "body": request_body, "more_body": False}
        return {"type": "http.request", "body": b"", "more_body": False} # Should not be reached usually

    events = []
    async def send(event):
        events.append(event)

    await app(scope, receive, send)

    assert len(events) == 2
    assert events[0]["status"] == 201
    assert b'application/json' in [h[1] for h in events[0]["headers"] if h[0] == b'content-type']
    assert events[1]["body"] == b'{"id": 1, "name": "test_item"}'

@pytest.mark.asyncio
async def test_404():
    app = App()

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/not-found",
    }
    async def receive():
        return {"type": "http.request"}
    
    events = []
    async def send(event):
        events.append(event)

    await app(scope, receive, send)
    
    assert events[0]["status"] == 404
