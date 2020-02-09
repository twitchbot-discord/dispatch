import logging
from .utils import amqp, rethink

from flask import Flask, g, redirect, request
from flask_login import LoginManager
from os import name, getenv
from rethinkdb import RethinkDB
from rethinkdb.errors import ReqlDriverError
from .modules import general
from .utils.login import User

r = RethinkDB()
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.debug = name == 'nt'
app.config['SECRET_KEY'] = getenv('SECRET_KEY')
app.login_manager = LoginManager()
app.login_manager.init_app(app)

general.setup(app)

amqp_thread = amqp.AmqpConsumerThread()
amqp_thread.run()


def is_path_db_blacklist(req):
    if request.method == 'GET':
        if request.path == '/logout':
            return False
    return False


@app.login_manager.user_loader
def load_user(user_id):
    if user_id == 'admin':
        return User.get('admin')
    return None


@app.context_processor
def process_ctx():
    return dict(
        _app_version='0.1.0'
    )


@app.before_request
def before_request():
    if not is_path_db_blacklist(request):
        app.logger.info('Connecting to RethinkDB')
        try:
            g.rethinkdb = rethink.connect()
        except ReqlDriverError:
            app.logger.exception('Failed to connect')
            return 'Database connection failed', 502
        app.logger.info('Connected to db')


@app.teardown_request
def teardown_request(exc):
    if hasattr(g, 'rethinkdb'):
        try:
            g.rethinkdb.close()
            app.logger.info('Closed db connection')
        except Exception:
            pass


@app.errorhandler(401)
def unauthorized(*args):
    return redirect('/login')


# gunicorn
application = app
