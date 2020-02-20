from app import app
from gevent.pywsgi import WSGIServer
import sys

PORT = int(sys.argv[1])

http_server = WSGIServer(('', PORT), app)
http_server.serve_forever()

# app.run(host='0.0.0.0', port=5000)