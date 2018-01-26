#!/usr/bin/env python
import logging
import socket
import os.path
import pkg_resources
from flask import Flask, request
app = Flask(__name__)
try:
    __version__ = pkg_resources.require("echo")[0].version
except pkg_resources.DistributionNotFound:
    __version__ = 'dev'
except:
    raise
# Load Conf
app.config.from_pyfile('default.cfg')
if os.path.isfile('/etc/echo.cfg'):
    app.config.from_pyfile('/etc/echo.cfg')
@app.route('/', methods=['POST', 'PUT'])
def echo():
    """Echo data"""
    return request.get_data() + '\n'
@app.route('/', methods=['GET'])
def whoami():
    """Echo hostname and version"""
    return '''<body style="background: {};">
    hostname: {}
</body>
'''.format(app.config['BACKGROUND'], socket.gethostname())
@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500
if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host=app.config['HOST'], 
            port=app.config['PORT'], 
            debug=True)
# [END app]

