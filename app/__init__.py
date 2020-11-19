from flask import Flask
#  from flask_session import Session
import logging
import secrets
#  import redis

app = Flask(__name__)

app.secret_key = secrets.token_urlsafe(32)

#  sess = Session()
#  sess.init_app(app)

logging.basicConfig(
    #  filename='server.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)

from app import routes
