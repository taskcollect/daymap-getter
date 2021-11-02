# import platform
# from aiohttp import web

# routes = web.RouteTableDef()

# @routes.get('/')
# async def hello(request):
#     return web.Response(text="Hello, world")

# app = web.Application()
# app.add_routes(routes)

# if __name__ == '__main__':
#     print(f"Hello! I'm running on {platform.node()}!")
#     web.run_app(app)

from datetime import datetime
import datetime as dt

from daymap.clean import clean_lesson_object
from daymap.net import get_daymap_resource

from server.server import run_app

import json

from daymap.util import get_all_lessons_and_clean

if __name__ == '__main__':
    while run_app():
        pass