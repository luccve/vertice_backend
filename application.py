import requests
import datetime
import os
import certifi
import asyncio
import httpx
from flask import Flask, make_response, jsonify, request, render_template, Response
from flask_cors import CORS
from bson import ObjectId, json_util
from dotenv import load_dotenv
from pymongo import MongoClient
import smtplib
from email.message import EmailMessage

application = Flask(__name__)
application.config['JSON_SORT_KEYS'] = False
CORS(application)


# configurando email


ca = certifi.where()
# Load config from a .env file:
load_dotenv()
PASSWORD_GMAIL = os.environ['PASSWORD_GMAIL']
EMAIL = os.environ['EMAIL']

MONGODB_URI = os.environ['MONGODB_URI']
# Connect to your MongoDB cluster:
client = MongoClient(MONGODB_URI, ssl=True,
                     tlsCAFile=ca)


async def remove_transaction_DB(id):
    client.db.transactions.delete_one({"_id": ObjectId(id)})


async def change_transaction_DB(id, type, date, cash, desc, type_especify, latitude, longitude):
    client.db.transactions.update_one({"_id": ObjectId(id)}, {"$set": {
        "type": type,
        "date": date,
        "cash": cash,
        "desc": desc,
        "type_especify": type_especify,
        "latitude": latitude,
        "longitude": longitude
    }})


async def transactionsDB(uid):
    response = client.db.transactions.find({"uid": uid})
    return response


async def insert_transaction(uid, type, type_especify, date, cash, desc, latitude, longitude):
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


async def usuariosbd(uid):

    transaction = client.db.users.find({"uid": uid})
    response = json_util.dumps(transaction)

    return response


async def changeDBuser(uid, display_name, photoURL, sexo):
    client.db.users.update_one({'uid': uid}, {"$set": {
        'name': display_name,
        'photo': photoURL,
        'sexo': sexo,
    }})


async def inserDBuser(display_name, email, photoURL, sexo, uid):
    client.db.users.insert_one({
        'name': display_name,
        'email': email,
        'photo': photoURL,
        'sexo': sexo,
        'uid': uid,
    })


def dropDB():
    for collection in client.list_database_names():
        client.drop_database(collection)


async def send_email(MSG):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL, PASSWORD_GMAIL)
        smtp.send_message(MSG)


async def insert_email(email, MSG):
    a = client.db.email.find({"email": email})
    b = json_util.dumps(a)
    if (int(len(b)) > 2):
        return False
    elif (int(len(b)) <= 2):
        client.db.email.insert_one({
            'email': email,
        })

        return True


@application.route('/email', methods=['POST'])
async def getEmail():
    try:
        email = request.json['email']
        MSG = EmailMessage()
        MSG['Subject'] = 'Cadastro com sucesso!'
        MSG['From'] = EMAIL
        MSG['To'] = email
        MSG.set_content(
            'Olá você se cadastrou na VERTICE para recever promoções')
        await send_email(MSG)
        Flag = await insert_email(email, MSG)
        if (Flag):
            await send_email(MSG)
            data = 'Email adicionado com sucesso no banco de dados'
        else:
            data = 'Email já adicionado no banco de dados'
        return make_response(jsonify(message="Email adicionado",
                                     data=data))

    except:
        return bad_request()


@application.route('/dbdrop', methods=['GET'])
def db():
    dropDB()
    return make_response(jsonify(message="Database dropped",
                                 data="Todo os banco de dados foi dropado"))


@application.route('/vertice/docs', methods=['GET'])
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


@application.route('/getUser', methods=['GET'])
async def get_user():
    try:
        headers = {"Content-Type": "application/json"}
        uid = request.args.get('uid')
        response = await usuariosbd(uid)
        return Response(response, mimetype='application/json', headers=headers)
    except:
        return bad_request()


@application.route('/user', methods=['POST', 'PUT', 'DELETE'])
async def insert():

    try:
        display_name = request.json['displayName']
        email = request.json['email']
        photoURL = request.json['photoURL']
        sexo = request.json['sexo']
        uid = request.json['uid']
        haveuser = await usuariosbd(uid)

        if request.method == 'POST' and (email and uid and len(haveuser) <= 2):

            await inserDBuser(display_name, email, photoURL, sexo, uid)

            return make_response(jsonify(message=f"User added successfully"))
        elif request.method == 'PUT' and uid:
            await changeDBuser(uid, display_name, photoURL, sexo)
            return make_response(jsonify(message=f"User changed successfully"))
        elif request.method == 'DELETE' and uid:
            client.db.users.delete_one({'uid': uid})
            return make_response(jsonify(message=f"User removed successfully"))
        else:
            return not_found()

    except:
        return bad_request()


@application.route('/transaction', methods=['POST'])
async def transaction():
    try:
        uid = request.json["uid"]
        type = request.json["type"]
        type_especify = request.json["type_especify"]
        date = request.json["date"]
        cash = request.json["cash"]
        desc = request.json["desc"]
        latitude = request.json["latitude"]
        longitude = request.json["longitude"]

        if (len(uid) > 0):

            await insert_transaction(uid, type, type_especify, date, cash, desc, latitude, longitude)
            return make_response(jsonify(message=f'Transação do tipo {uid} added successfully'))
        else:
            return not_found()
    except:
        return bad_request()


@application.route('/getTransaction', methods=['GET'])
async def get_transaction():
    try:
        uid = request.args.get('uid')
        transactions = await transactionsDB(uid)
        response = json_util.dumps(transactions)

        return Response(response, mimetype='application/json')

    except:
        return not_found()


@application.route('/changeTransaction', methods=['PUT', 'DELETE'])
async def change_transaction():
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
            await remove_transaction_DB(id)
            return make_response(jsonify(message="Registro deletado!"))
        elif request.method == 'PUT' and id:
            await change_transaction_DB(id, type, date, cash, desc, type_especify, latitude, longitude)
            return make_response(jsonify(message="Registro alterado!"))
        else:
            return bad_request()
    except:
        return not_found()


@application.errorhandler(404)
def not_found(error=None):
    response = jsonify({
        'message': 'Resource not found: ' + request.url,
        'status': 404
    })
    response.status_code = 404
    return make_response(response)


@application.errorhandler(400)
def bad_request(error=None):
    response = jsonify({
        'message': 'Malformed request syntax, invalid request message framing, or misleading request routing ' + request.url,
        'status': 400
    })
    response.status_code = 400
    return make_response(response)


if __name__ == '__main__':
    application.run(debug=True)
