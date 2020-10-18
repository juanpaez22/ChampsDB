# Script used incrementally to scrape the FUT API for player data
# Used on the production DB, needed in addition to coalesce_players.py due to request quota issues.
# Note that it is necessary to manually review, since matches are based on last name only.

import requests
import json
import pymongo
from pymongo import MongoClient
import config

def main():
    client = MongoClient(config.prod_db_connection_string, connect=False)
    db = client['ChampionsDB']
    players = list(db.players.find({}))

    request_count = 50
    for player in players:
        if player['rating_overall'] != -1:
            continue
        request_count -= 1
        if request_count < 0:
            break
        name = player['name'].split(' ')[-1]
        print(f'Getting FUT data with query {name}')
        try:
            headers = {"X-AUTH-TOKEN": config.fut_db_key}
            body = {"name": name}
            response = requests.post("https://futdb.app/api/players", json=body, headers=headers).json()
            stats = response['items'][0]
            
            new_data = {
                'rating_overall': stats['rating'],
                'rating_pace': stats['pace'],
                'rating_shooting': stats['shooting'],
                'rating_passing': stats['passing'],
                'rating_dribbling': stats['dribbling'],
                'rating_defending': stats['defending'],
                'rating_physicality': stats['physicality']
            }

            db.players.update_one({'_id': player['_id']}, {'$set': new_data})
            print("Successfully updated data for player " + player['name'])
        except Exception as e:
            print(e)
            print("WARNING: Failed to update player " + player['name'])


if __name__ == "__main__":
    main()