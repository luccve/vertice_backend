from flask import Flask, make_response, jsonify, request, render_template, Response
from flask_cors import CORS
from bson import ObjectId, json_util
import requests
import datetime
import os
import certifi
from dotenv import load_dotenv
from pymongo import MongoClient


application = Flask(__name__)
application.config['JSON_SORT_KEYS'] = False
CORS(application)


ca = certifi.where()
# Load config from a .env file:
load_dotenv()
MONGODB_URI = os.environ['MONGODB_URI']

# Connect to your MongoDB cluster:
client = MongoClient(MONGODB_URI, ssl=True,
                     tlsCAFile=ca)


def dropDB():
    for collection in client.list_database_names():
        client.drop_database(collection)


@application.route('/dbdrop', methods=['GET'])
def db():
    dropDB()
    return make_response(jsonify(message="Database dropped",
                                 data="Todo os banco de dados foi dropado"))


@application.route('/', methods=['GET'])
def host():

    return render_template('index.html')


@application.route('/cnpj', methods=['GET'])
def get_cnpj():
    cnpj = request.args.get('cnpj')
    print(cnpj)
    url = f"https://receitaws.com.br/v1/cnpj/{cnpj}"

    headers = {"Content-Type": "application/json"}

    response = requests.request("GET", url, headers=headers)

    return make_response(response.text)


@application.route('/user', methods=['POST', 'PUT', 'DELETE'])
def insert():
    try:
        display_name = request.json['displayName']
        email = request.json['email']
        photoURL = request.json['photoURL']
        sexo = request.json['sexo']
        uid = request.json['uid']
        if request.method == 'POST' and (email and uid):

            client.db.users.insert_one({
                'name': display_name,
                'email': email,
                'photo': photoURL,
                'sexo': sexo,
                'uid': uid,
            })

            return make_response(jsonify(message=f"User {uid} added successfully"))
        elif request.method == 'PUT' and uid:
            client.db.users.update_one({'uid': uid}, {"$set": {
                'name': display_name,
                'photo': photoURL,
                'sexo': sexo,
            }})
            return make_response(jsonify(message=f"User {uid} changed successfully",
                                         data=uid))
        elif request.method == 'DELETE' and uid:
            client.db.users.delete_one({'uid': uid})
            return make_response(jsonify(message=f"User {uid} removed successfully"))
        else:
            return bad_request()
    except:
        return not_found()


@ application.route('/transaction', methods=['POST'])
def transaction():
    try:
        uid = request.json["uid"]
        type = request.json["type"]
        type_especify = request.json["type_especify"]
        date = request.json["date"]
        cash = request.json["cash"]
        desc = request.json["desc"]
        latitude = request.json["latitude"]
        longitude = request.json["longitude"]

        if (uid):
            client.db.transactions.insert_one({
                "uid": uid,
                "type": type,
                "type_especify": type_especify,
                "date": date,
                "cash": cash,
                "desc": desc,
                "latitude": latitude,
                "longitude": longitude
            })

            return make_response(jsonify(message='Transaction added successfully'))

        else:
            return bad_request()
    except:
        return not_found()


@ application.route('/getTransaction', methods=['GET'])
def get_transaction():
    try:
        uid = request.args.get('uid')
        transactions = client.db.transactions.find({"uid": uid})
        response = json_util.dumps(transactions)

        return Response(response, mimetype='application/json')

    except:
        return not_found()


@ application.route('/changeTransaction', methods=['PUT', 'DELETE'])
def change_transaction():
    try:
        id = request.json['_id']
        id = id['$oid']
        uid = request.json["uid"]
        type = request.json["type"]
        type_especify = request.json["type_especify"]
        date = request.json["date"]
        cash = request.json["cash"]
        desc = request.json["desc"]
        latitude = request.json["latitude"]
        longitude = request.json["longitude"]

        if request.method == 'DELETE' and id:
            client.db.transactions.delete_one({"_id": ObjectId(id)})
            return make_response(jsonify(message="Registro deletado!"))
        elif request.method == 'PUT' and id:
            client.db.transactions.update_one({"_id": ObjectId(id)}, {"$set": {
                "type": type,
                "date": date,
                "cash": cash,
                "desc": desc,
                "type_especify": type_especify,
                "latitude": latitude,
                "longitude": longitude
            }})
            return make_response(jsonify(message="Registro alterado!"))
        else:
            return bad_request()
    except:
        return not_found()


@ application.errorhandler(404)
def not_found(error=None):
    response = jsonify({
        'message': 'Resource not found: ' + request.url,
        'status': 404
    })
    response.status_code = 404
    return make_response(response)


@ application.errorhandler(400)
def bad_request(error=None):
    response = jsonify({
        'message': 'Malformed request syntax, invalid request message framing, or misleading request routing ' + request.url,
        'status': 400
    })
    response.status_code = 400
    return make_response(response)


if __name__ == '__main__':
    application.run(debug=True)
