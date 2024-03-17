from fastapi import FastAPI, WebSocket
from pyinstrument import Profiler
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()

class ProfilerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        profiler = Profiler()
        profiler.start()
        response = await call_next(request)
        profiler.stop()
        print(profiler.output_text(unicode=True, color=True))
        return response

app.add_middleware(ProfilerMiddleware)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message received: {data}")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)
