from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
from json import loads as jsonloads, dumps as jsondumps
#import os
#databaseName = os.environ['DB_NAME']

databaseName = "netflowDB"

logger = logging.getLogger("netflow-collector")
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

myclient = MongoClient("192.168.26.139", 27017,
                                username="root", 
                                password="example")

def checkDBConnection():
    try:
        myclient.admin.command('ping')
        return True
    except ConnectionFailure:
        return False


def insertIntoDB(workflowVersion, data):
    while True:
        if checkDBConnection() is True:
            mydb = myclient[databaseName]
            colList = mydb.list_collection_names()
            mycol = mydb[str("database_Netflow_V" + str(workflowVersion))]
            mycol.insert_one(data)
            break
        else: 
            logger.error("DB server not available")
