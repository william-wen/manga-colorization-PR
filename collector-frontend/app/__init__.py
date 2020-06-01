from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from app.exceptions.Error import Error

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.Config")

    db.init_app(app)

    # import all the blueprints
    from app.views.colorizer import colorizer
    app.register_blueprint(colorizer)

    # error handler
    app.register_error_handler(Error, handle_error)

    with app.app_context():
        db.create_all()

    return app

def handle_error(e):
    response = e.to_dict()
    return response