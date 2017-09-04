import os
from functools import wraps
from flask import Flask, Response, request, json, abort, redirect


application = Flask(__name__)


def force_https(func):
    """Decorator function force HTTPS connections for specific endpoints."""
    @wraps(func)
    def wrapped_f(*args, **kwargs):
        if not request.is_secure:
             url = request.url.replace('http://', 'https://', 1)
             return redirect(url, 302)
        return func(*args, **kwargs)
    return wrapped_f


@application.errorhandler(400)
@application.errorhandler(422)
def json_error_response(e):
    return Response(
        response=json.dumps(e.description),
        status=e.code,
        mimetype='application/json'
    )


@force_https
@application.route('/', methods=['GET'])
def hello_world():
    """Your basic hello world endpoint."""
    resp = Response(
        response='Hello World!',
        status=200,
        mimetype='application/json'
    )
    return resp


@force_https
@application.route('/instance-guid', methods=['GET'])
def instance_guid():
    """This endpoint demonstrates load balancing in working in Cloud Foundry by
    returning the app instance specific GUID to the client.
    """
    resp = Response(
        response=os.getenv('INSTANCE_GUID', 'unknown'),
        status=200,
        mimetype='text/plain'
    )
    return resp


@application.route('/healthcheck', methods=['GET'])
def healthcheck():
    """This endpoint is used by Cloud Foundry healthchecking to determine if
    the application should be considered healthly.  It should be polled every
    two seconds, if 200 is not returned the application will be restarted.  See
    Cloud Foundry documentation for more detailed documentation on healthchecks.
    """
    resp = Response(
        response='healthy',
        status=200,
        mimetype='text/plain'
    )
    return resp


@force_https
@application.route('/error')
def generate_error():
    """Always returns a 400"""
    abort(400, {'error': 'this is a error test'})


if __name__ == '__main__':
    application.debug = True
    application.run(host='0.0.0.0', port=8080)
