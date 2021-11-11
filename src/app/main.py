from fastapi import FastAPI

import routers.tasks
import routers.messages
import routers.lessons

app = FastAPI(title="daymap-getter")
app.include_router(routers.tasks.router)
app.include_router(routers.messages.router)
app.include_router(routers.lessons.router)
