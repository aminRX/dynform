from flask import Flask, request, Response
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"

parser = reqparse.RequestParser()
parser.add_argument('username', type=str, help='username')
parser.add_argument('email', type=str, help='Email')

db = SQLAlchemy(app)
ma = Marshmallow(app)


class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = UserModel

    id = ma.auto_field()
    username = ma.auto_field()
    email = ma.auto_field()


class User(Resource):
    def get(self, user_id):
        user_schema = UserSchema()
        user = UserModel.query.get(user_id)
        return user_schema.dump(user)

    def put(self, user_id):
        user_schema = UserSchema()
        args = parser.parse_args()
        user = UserModel.query.get(user_id)
        user.username = args['username']
        user.email = args['email']
        db.session.add(user)
        db.session.commit()
        return user_schema.dump(user)

    def delete(self, user_id):
        user_schema = UserSchema()
        user = UserModel.query.get(user_id)
        db.session.delete(user)
        db.session.commit()
        return user_schema.dump(user)


class UserList(Resource):
    def get(self):
        users_schema = UserSchema(many=True)
        users = UserModel.query.all()
        return users_schema.dump(users)

    def post(self):
        user_schema = UserSchema()
        args = parser.parse_args()
        new_user = UserModel(**args)
        db.session.add(new_user)
        db.session.commit()
        return user_schema.dump(new_user)


api.add_resource(UserList, '/users/')
api.add_resource(User, '/users/<int:user_id>')

if __name__ == '__main__':
    app.run(debug=True)
