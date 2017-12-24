import pymongo
import json
import sys

# Local Files
sys.path.append("..")
from scripts import settings

client = pymongo.MongoClient(settings.mongo_server, settings.mongo_id)
db = client[settings.mongo_client]
db.authenticate(settings.mongo_user, settings.mongo_pass)

def save(account, datatype, data):
    d = db.positions.find_one({'account': account})
    if d is not None:
        d[datatype] = json.dumps(data)
        db.positions.save(d)
    else:
        db.positions.insert_one({'account': account, datatype: json.dumps(data)})

def load(account, datatype):
    d = db.positions.find_one({'account': account})
    return json.loads(d[datatype])
