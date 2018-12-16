from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from werkzeug.routing import Rule
from flask_restful import Api
from sanaButtonJson import getCategory, getContents
app = Flask(__name__)
CORS(app)
api = Api(app)

# エラーハンドラ


@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(500)
def error_handler(error):
    msg = 'Error: {code}'.format(code=error.code)
    return jsonify({
        "result": "Failed",
        "message": msg,
        "errorcode": error.code
    })


# apiの登録
api.add_resource(getCategory, "/api/sana/category")
api.add_resource(getContents, "/api/sana/contents")

if __name__ == "__main__":
    # app.run(host="0.0.0.0", debug=True)
    app.run(host="0.0.0.0", debug=False)