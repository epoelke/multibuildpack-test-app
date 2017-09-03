from flask import Flask, Response, request, json, abort, redirect


application = Flask(__name__)


@application.before_request
def before_request():
    if not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, 302)


@application.errorhandler(400)
@application.errorhandler(422)
def json_error_response(e):
    return Response(
        response=json.dumps(e.description),
        status=e.code,
        mimetype='application/json'
    )

@application.route('/', methods=['GET'])
def hello_world():
    resp = Response(
        response='Hello World!',
        status=200,
        mimetype="application/json"
    )
    return resp


@application.route('/error')
def generate_error():
    abort(400, {'error': 'this is a error test'})


if __name__ == '__main__':
    application.debug = True
    application.run(host='0.0.0.0', port=8080)
