import pymongo


host = "mongodb+srv://lucasi"
senha = "qjwbbBmpdwmmRrDK"
connection = host + ":" + senha + \
    "@cluster0.e09jbjl.mongodb.net/?retryWrites=true&w=majority"
print(connection)
# client = pymongo.MongoClient(
#     "mongodb+srv://lucasi:<password>)
# db = client.test

mongo = pymongo.MongoClient(connection, maxPoolSize=50, connect=False)

db = pymongo.database.Database(mongo, 'mydatabase')
