from copy import copy
from googleanalytics import oauth


def single_serve(message, port=5000):
    import logging
    from flask import Flask, Response, request

    app = Flask(__name__)

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    captured = {}

    @app.route('/')
    def main():
        request.environ.get('werkzeug.server.shutdown')()
        captured.update(dict(request.args.items()))
        print message
        return Response(message, mimetype='text/plain')

    app.run(port=port)
    return captured