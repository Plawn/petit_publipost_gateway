from app import app
from gevent.pywsgi import WSGIServer


http_server = WSGIServer(('', 5000), app)
http_server.serve_forever()

# app.run(host='0.0.0.0', port=5000)