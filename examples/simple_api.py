from aioserve.server.app import App, app
from aioserve.server.http import JSONResponse

# Implementation Note: access the global app instance or create a new one. 
# In app.py we instantiated `app = App()`.
# Let's import that single instance or we can Create a new one.
# The user might expect `from aioserve.server import app` style if we exposed it, 
# but currently it is in `aioserve.server.app`.
# Let's just use the one we exported.

@app.get("/")
async def home(request):
    return "Welcome to Aioserve!"

@app.get("/json")
async def json_handler(request):
    return {"message": " This is JSON"}

@app.post("/echo")
async def echo(request):
    data = await request.json()
    return JSONResponse(data)
