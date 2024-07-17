from flask import (
    Flask, render_template, url_for, redirect, request, g, session
)

import os
import datetime

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=1)
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from . import chat
    
    

    # a simple page that says hello
    app.register_blueprint(chat.bp)
    app.add_url_rule('/', endpoint='index')
    return app