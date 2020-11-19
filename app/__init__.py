from flask import Flask
import logging

app = Flask(__name__)

logging.basicConfig(
    #  filename='server.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)

from app import routes
