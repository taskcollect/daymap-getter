import platform
from aiohttp import web

routes = web.RouteTableDef()

@routes.get('/')
async def hello(request):
    return web.Response(text="Hello, world")

app = web.Application()
app.add_routes(routes)

if __name__ == '__main__':
    print(f"Hello! I'm running on {platform.node()}!")
    web.run_app(app)
    