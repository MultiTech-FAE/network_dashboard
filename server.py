## Written by Russel Ndip, Benjamin Lindeen, Austin Jacobson

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse
from werkzeug.security import generate_password_hash, check_password_hash
from data import *
import os, json, io.sqlite3
from os import environ as env
from dotenv import load_dotenv
from datetime import datetime

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__, static_url_path='/static')
db = SQLAlchemy(app)
api = Api(app)


# Create the application instance
@app.route('/')
def home():
    return render_template('home.html')


class LoraMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deviceName = db.Column(db.String(50))
    deveui = db.Column(db.String(23))
    appeui = db.Column(db.String(23))
    data = db.Column(db.String(50))
    size = db.Column(db.Integer)
    timestamp = db.Column(db.Integer)
    sqn = db.Column(db.Integer)


#### next set of classes use flask restful to define endpoints and request methods
class UserList(Resource):
    ##get all users##
    def get(self):
        UserList = Users.query.all()
        output = []

        for users in UserList:
            user_data = {}
            user_data['username'] = users.username
            user_data['password'] = users.password

            output.append(user_data)
        ## returns the list of users
        return jsonify({'users': output})

    ## create new user##
    def post(self):
        # initialize request parser, set parameter arguments
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True)
        parser.add_argument('password', required=True)
        # save arguments into object
        args = parser.parse_args()
        password = args['password']
        username = args['username']
        # hash the password
        hash_password = generate_password_hash(password, method='sha256')

        new_user = Users(username=username, password=hash_password)
        db.session.add(new_user)
        db.session.commit()

        return ({'message': 'User Created', 'data': args}, 201)


class User(Resource):
    def get(self, identifier):
        # get user if exists
        user = Users.query.filter_by(username=identifier).first()
        # handle if user doesn't exist
        if not user:
            return jsonify({'message': 'No user found'})
        user_data = {}
        user_data['username'] = user.username
        user_data['password'] = user.password

        return jsonify({'user': user_data})

    def delete(self, identifier):
        user = Users.query.filter_by(username=identifier).first()
        if not user:
            # return on failure
            return jsonify({'message': 'No user found'})
        db.session.delete(user)
        db.session.commit()
        # return on success
        return jsonify({'message': 'The user has been deleted'})


class LoraMessageList(Resource):
    def get(self):
        LoraMessageList = LoraMessage.query.all()
        output = []
        for LoraMessage in LoraMessageList:
            LoraMessage_data = {}
            LoraMessage_data["deviceName"] = LoraMessage.deviceName
            LoraMessage_data["deveui"] = LoraMessage.deveui
            LoraMessage_data["appeui"] = LoraMessage.appeui
            LoraMessage_data["data"] = LoraMessage.data
            LoraMessage_data["size"] = LoraMessage.size
            LoraMessage_data["timestamp"] = LoraMessage.timestamp
            LoraMessage_data["sqn"] = LoraMessage.sqn

            output.append(LoraMessage_data)

        return jsonify({'LoraMessages': output})

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('deviceName', required=True)
        parser.add_argument('deveui', required=True)
        parser.add_argument('appeui', required=True)
        parser.add_argument('data', required=True)
        parser.add_argument('size', required=True)
        parser.add_argument('timestamp', required=True)
        parser.add_argument('sqn', required=True)

        args = parser.parse_args()
        deviceName = args['deviceName']
        deveui = args['deveui']
        appeui = args['appeui']
        data = args['data']
        size = args['size']
        timestamp = args['timestamp']
        sqn = args['sqn']

        new_LoraMessage = LoraMessage(deviceName=deviceName, deveui=deveui, appeui=appeui, data=data,
                                      size=size, timestamp=timestamp, sqn=sqn)
        db.session.add(new_LoraMessage)
        db.session.commit()
        ##return message
        return ({'message': 'Lora Message Added', 'data': args}, 201)


class LoraMessage(Resource):
    def get(self, identifier):
        LoraMessage = LoraMessage.query.filter_by(deveui=identifier).first()

        if not LoraMessage:
            return jsonify({'message': 'Device not found'})
        LoraMessage_data = {}
        LoraMessage_data["deviceName"] = LoraMessage.deviceName
        LoraMessage_data["deveui"] = LoraMessage.deveui
        LoraMessage_data["appeui"] = LoraMessage.appeui
        LoraMessage_data["data"] = LoraMessage.data
        LoraMessage_data["size"] = LoraMessage.size
        LoraMessage_data["timestamp"] = LoraMessage.timestamp
        LoraMessage_data["sqn"] = LoraMessage.sqn

        return jsonify({'LoraMessage': LoraMessage_data})


# add api routes and endpoints
api.add_resource(LoraMessageList, '/LoraMessage')
api.add_resource(LoraMessage, '/LoraMessage/<string:identifier>')
api.add_resource(UserList, '/users')
api.add_resource(User, '/users/<string:identifier>')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=env.get("PORT", 5000))
