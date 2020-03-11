from app import app
from gevent.pywsgi import WSGIServer
import sys

import logging
logging.basicConfig(level=logging.INFO)

PORT = int(sys.argv[1])

http_server = WSGIServer(('0.0.0.0', PORT), app)
http_server.serve_forever()
