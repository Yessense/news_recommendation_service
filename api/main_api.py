import flask
from flask import jsonify
import flask_restful
from flask_restful import reqparse
from api_db import *
from flask import request



app = flask.Flask(__name__)
app.config['JSON_AS_ASCII'] = False
api = flask_restful.Api()


parser = reqparse.RequestParser()



class News(flask_restful.Resource):
    def get(self, user_type, date):
        if date == 0:
            return main_news(user_type)
        else:
            return ['hello', '123', 'пвп']

class get_trend(flask_restful.Resource):
    def get(self):
        return show_trend()


class post_trend(flask_restful.Resource):
    def post(self):
        json_data = request.get_json(force=True)
        parser.add_argument('trend', type=str)
        parser.add_argument('inside', type=str)
        args = parser.parse_args()

        return create_trend(args['trend'], args['inside'])


class show_analis(flask_restful.Resource):
    def get(self):
        return get_analis_db()

api.add_resource(News, '/api/main/<string:user_type>/<int:date>')
api.add_resource(get_trend, '/api/get_trend')
api.add_resource(post_trend, '/api/post_trend')
api.add_resource(show_analis, '/api/get_analis')
api.init_app(app)






# для запуска api
if __name__ == "__main__":
    app.run(debug=True, port=3000, host="127.0.0.1")









