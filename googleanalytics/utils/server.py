# encoding: utf-8

def single_serve(message=None, port=5000):
    import logging
    from werkzeug.wrappers import Request, Response
    from werkzeug.serving import run_simple

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    captured = {}

    def application(environ, start_response):
        request = Request(environ)
        request.environ.get('werkzeug.server.shutdown')()
        captured.update(dict(request.args.items()))
        if message:
            print(message)
        response = Response(message, mimetype='text/plain')
        return response(environ, start_response)

    run_simple('localhost', port, application)
    return captured
