#!/usr/bin/env python3
from flask import Flask
import time

import endpoints.lessons
import endpoints.messages
import endpoints.tasks

app = Flask(__name__)
app.register_blueprint(endpoints.lessons.blueprint)
app.register_blueprint(endpoints.messages.blueprint)
app.register_blueprint(endpoints.tasks.blueprint)


if __name__ == '__main__':
    app.run('0.0.0.0', 9000, debug=False)
