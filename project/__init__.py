import os

from werkzeug.contrib.fixers import ProxyFix
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # set config
    app_setings = os.getenv('APP_SETTINGS', 'project.config.ProductionConfig')
    app.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')
    app.config.from_object(app_setings)
    app.wsgi_app = ProxyFix(app.wsgi_app)

    # set up db
    db.init_app(app)

    # register blueprints
    from project.api.views import users_blueprint
    app.register_blueprint(users_blueprint)

    return app

