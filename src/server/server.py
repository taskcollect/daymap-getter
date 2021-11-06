import os
import sys
import signal
import asyncio
import logging
from datetime import datetime
from concurrent.futures import CancelledError

from aiohttp import web

from server.endpoints.lessons import endpoint_lessons
from server.endpoints.messages import endpoint_messages
from server.endpoints.tasks import endpoint_tasks_current
from server.errors import GracefulExitException, ResetException

def handle_sighup() -> None:
    logging.warning("Received SIGHUP")
    raise ResetException("Application reset requested via SIGHUP")


def handle_sigterm() -> None:
    logging.warning("Received SIGTERM")
    raise ResetException("Application exit requested via SIGTERM")


def cancel_tasks() -> None:
    for task in asyncio.Task.all_tasks():
        task.cancel()

def run_app() -> bool:
    """Run the application

    Return whether the application should restart or not.
    """
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGHUP, handle_sighup)
    loop.add_signal_handler(signal.SIGTERM, handle_sigterm)

    web_app = web.Application()
    web_app.router.add_get("/lessons", endpoint_lessons)
    web_app.router.add_get("/messages", endpoint_messages)
    web_app.router.add_get("/tasks", endpoint_tasks_current)

    try:
        web.run_app(web_app, handle_signals=True)
    except ResetException:
        logging.warning("Reloading...")
        cancel_tasks()
        asyncio.set_event_loop(asyncio.new_event_loop())
        return True
    except GracefulExitException:
        logging.warning("Exiting...")
        cancel_tasks()
        loop.close()

    return False