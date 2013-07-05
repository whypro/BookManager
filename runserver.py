# -*- coding: utf-8 -*-
from flask import Flask
from frontend import frontend
from frontend.views import *

app = Flask(__name__)
app.register_blueprint(frontend, prefix='/')

app.debug = True
app.run()
