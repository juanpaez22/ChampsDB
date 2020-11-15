import pymongo
from pymongo import MongoClient
import os

def main():
    client = MongoClient(os.environ['DB_CONNECTION_STRING'], connect=False)
    db = client['ChampionsDB']
    matches = db.matches
    match_list = matches.find({})

    for match in match_list:
        matches.update_one({'_id': match['_id']}, {'$set': {'video': ''}})

if __name__ == "__main__":
    main()
