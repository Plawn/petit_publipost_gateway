from gevent.monkey import patch_all
patch_all()

from app import app
from gevent.pywsgi import WSGIServer
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


PORT = int(sys.argv[1])

http_server = WSGIServer(('0.0.0.0', PORT), app)
http_server.serve_forever()
