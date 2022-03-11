import pymongo
from pymongo.errors import ConnectionFailure

myclient = pymongo.MongoClient("mongodb://192.168.26.138:27017/", username='root', password='example')
#mydb = myclient["mydatabase"]

try:
    myclient.admin.command('ping')
    print(True)
except ConnectionFailure:
    print(False)