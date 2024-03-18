from aiohttp import web, WSMsgType
from pyinstrument import Profiler

async def handle(request):
    data = request.match_info.get('name', "Anonymous")
    text = f"Message received: {data}"
    return web.Response(text=text)

async def websocket_handler(request):    
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    print('websocket connection ready')
    print( )

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                await ws.send_str(msg.data )
        elif msg.type == WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                ws.exception())

    print('websocket connection closed')
    return ws

# Middleware for profiling request handlers
async def profiler_middleware(app, handler):
    async def middleware_handler(request):
        profiler = Profiler()
        profiler.start()
        try:
            response = await handler(request)
            return response
        finally:
            profiler.stop()
            print(profiler.output_text(unicode=True, color=True))
    return middleware_handler

# app = web.Application(middlewares=[profiler_middleware])
app = web.Application()
app.add_routes([web.get('/', handle)])
app.add_routes([web.get('/ws', websocket_handler)])

if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(web._run_app(app, host='localhost', port=8080))
        loop.run_forever()
    finally:
        loop.close()
