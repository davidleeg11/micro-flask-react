# services/users/project/__init__.py


import os

from flask import Flask  # new
from flask_sqlalchemy import SQLAlchemy


# instantiate the db
db = SQLAlchemy()


# new
def create_app(script_info=None):

    # instantiate the app
    app = Flask(__name__)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # set up extensions
    db.init_app(app)

    # register blueprints
    from project.api.users import users_blueprint
    app.register_blueprint(users_blueprint)

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}

    return app


## services/users/project/__init__.py
#
#
#from flask import Flask, jsonify
#from flask_sqlalchemy import SQLAlchemy  # new
#import os
#
## instantiate the app
#app = Flask(__name__)
#
## set config
#app_settings = os.getenv('APP_SETTINGS')  # new
#app.config.from_object(app_settings)      # new
#
## instantiate the db
#db = SQLAlchemy(app)  # new
#
## model
#class User(db.Model):  # new
#    __tablename__ = 'users'
#    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#    username = db.Column(db.String(128), nullable=False)
#    email = db.Column(db.String(128), nullable=False)
#    active = db.Column(db.Boolean(), default=True, nullable=False)
#
#    def __init__(self, username, email):
#        self.username = username
#        self.email = email
#
#@app.route('/users/ping', methods=['GET'])
#def ping_pong():
#    return jsonify({
#        'status': 'success',
#        'message': 'pong!'
#    })
