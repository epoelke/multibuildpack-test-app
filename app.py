from functools import wraps
from flask import Flask, Response, request, json, abort, redirect


application = Flask(__name__)


def force_https(func):
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
    resp = Response(
        response='Hello World!',
        status=200,
        mimetype='application/json'
    )
    return resp


@application.route('/healthcheck', methods=['GET'])
def healthcheck():
    resp = Response(
        response='healthy',
        status=200,
        mimetype='text/plain'
    )
    return resp


@force_https
@application.route('/error')
def generate_error():
    abort(400, {'error': 'this is a error test'})


if __name__ == '__main__':
    application.debug = True
    application.run(host='0.0.0.0', port=8080)
