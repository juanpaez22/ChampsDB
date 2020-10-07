import requests
import json
import pymongo
from pymongo import MongoClient
import config

"""
Appends existing data in ChampionsDB with tweets from the Twitter API and stats from FutDB API.
"""

def main():
    client = MongoClient(config.db_connection_string, connect=False)
    db = client['ChampionsDB']
    players = db.players

    errors = []
    player_list = players.find({})
    for player in player_list:
        try:
            name = player['name'].split(' ')[-1]

            # Get Tweets for the player:
            headers = {'Authorization': 'Bearer {}'.format(config.twitter_api_bearer)}
            print(f"Fetching tweets matching the query: {name} #ChampionsLeague")
            params = {
                'query': f'{name} #ChampionsLeague',
                'max_results': '10',
                'tweet.fields': 'lang'}
            response = requests.get('https://api.twitter.com/2/tweets/search/recent', headers=headers, params=params).json()
            tweets = [{'id': tweet['id'], 'text': tweet['text'], 'lang': tweet['lang']} for tweet in response['data']]
            # Get HTML embedding for tweets
            for tweet in tweets:
                response = requests.get(f'https://publish.twitter.com/oembed?url=https://twitter.com/notused/status/{tweet["id"]}').json()
                tweet['html'] = response['html']

            # Get FUT data for the player
            print(f'Getting FUT data with query {name}')
            headers = {"X-AUTH-TOKEN": config.fut_db_key}
            body = {"name": name}
            response = requests.post("https://futdb.app/api/players", json=body, headers=headers).json()
            stats = response['items'][0]
            
            new_data = {
                'tweets': tweets,
                'rating_overall': stats['rating'],
                'rating_pace': stats['pace'],
                'rating_shooting': stats['shooting'],
                'rating_passing': stats['passing'],
                'rating_dribbling': stats['dribbling'],
                'rating_defending': stats['defending'],
                'rating_physicality': stats['physicality']
            }

            players.update_one({'_id': player['_id']}, {'$set': new_data})
            
        except Exception as e:
            print(e)
            print('ERROR: Data fetch failed')
            print(f'Unable to add data for player {player["name"]}')
            errors.append(player["name"])
            break

    if len(errors) > 0:
        print('ALL ERRORS:')
        print(errors)
    

if __name__ == "__main__":
    main()
