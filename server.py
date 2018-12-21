from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from werkzeug.routing import Rule
from flask_restful import Api
import sanaButtonJson
import onyankoButtonJson
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
api.add_resource(sanaButtonJson.getCategory, "/api/sana/category")
api.add_resource(sanaButtonJson.getContentsNames, "/api/sana/names")
api.add_resource(sanaButtonJson.getContentsURL, "/api/sana/voiceurl")
# api.add_resource(onyankoButtonJson.getCategory1, "/api/onyanko/category")
# api.add_resource(onyankoButtonJson.getContentsNames1, "/api/onyanko/names")
# api.add_resource(onyankoButtonJson.getContentsURL1, "/api/onyanko/voiceurl")
if __name__ == "__main__":
    # app.run(host="0.0.0.0", debug=True)
    app.run(host="0.0.0.0", debug=False)