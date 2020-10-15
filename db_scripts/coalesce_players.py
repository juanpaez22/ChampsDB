# Coalesces information from player events into standalone players.
# Prerequisite: scrape_matches.py, scrape_player_events.py

import requests
import json
import pymongo
from pymongo import MongoClient
import config

def main():
    client = MongoClient(config.db_connection_string, connect=False)
    db = client['ChampionsDB']
    player_collection = db.players
    event_collection = db.events

    events = list(event_collection.find({}))
    player_to_events = {}

    # Map player ID to list of events
    for event in events:
        pid = event["player_id"]
        if pid not in player_to_events:
            player_to_events[pid] = []
        player_to_events[pid].append(event)

    # Coalesce list of events into player dictionary
    players = []
    failed = []
    for pid in player_to_events:
        try:
            player = {}

            e = player_to_events[pid][0]
            player["_id"] = e["player_id"]
            player["team_id"] = e["team_id"]
            player["team_name"] = e["team_name"]
            player["name"] = e["player_name"]
            player["number"] = e["number"]
            player["position"] = e["position"]
            player["captain"] = e["captain"]

            # To aggregate: rating, minutes played, shots, passes, etc.
            player["shots"] = 0
            player["shots_on_target"] = 0
            player["goals"] = 0
            player["assists"] = 0
            player["passes"] = 0
            player["avg_minutes_played"] = 0
            player["avg_rating"] = 0
            player["avg_pass_accuracy"] = 0
            events = player_to_events[pid]
            for e in events:
                player["shots"] += int(e["shots"])
                player["shots_on_target"] += int(e["shots_on_target"])
                player["goals"] += int(e["goals"])
                player["assists"] += int(e["assists"])
                player["passes"] += int(e["passes"])
                player["avg_minutes_played"] += float(e["minutes_played"])
                if e["rating"] != "-":
                    player["avg_rating"] += float(e["rating"])
                player["avg_pass_accuracy"] += float(e["pass_accuracy"])

            player["avg_minutes_played"] /= len(events)
            player["avg_rating"] /= len(events)
            player["avg_pass_accuracy"] /= len(events)

            
        except Exception as e:
            print(e)
            print("WARNING: Failed to add player " + str(pid))
            failed.append(pid)
            continue

        # TODO: If too many players, and player is uninteresting (e.g. no goals, not captain, etc.), continue here and don't add.

        # Get Tweets for the player:
        try:
            name = player['name'].split(' ')[-1]
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
            player["tweets"] = tweets
        except Exception as e:
            print(e)
            print("WARNING: Failed to add tweets for player " + str(pid))
            player["tweets"] = []

        # Get FUT data for the player
        try:
            print(f'Getting FUT data with query {name}')
            headers = {"X-AUTH-TOKEN": config.fut_db_key}
            body = {"name": name}
            response = requests.post("https://futdb.app/api/players", json=body, headers=headers).json()
            stats = response['items'][0]
            player['rating_overall'] = stats['rating']
            player['rating_pace'] = stats['pace']
            player['rating_shooting'] = stats['shooting']
            player['rating_passing'] = stats['passing']
            player['rating_dribbling'] = stats['dribbling']
            player['rating_defending'] = stats['defending']
            player['rating_physicality'] = stats['physicality']
        except Exception as e:
            print(e)
            print("WARNING: Failed to add FUT data for player " + str(pid))
            player['rating_overall'] = -1
            player['rating_pace'] = -1
            player['rating_shooting'] = -1
            player['rating_passing'] = -1
            player['rating_dribbling'] = -1
            player['rating_defending'] = -1
            player['rating_physicality'] = -1

        # Add default media link
        player["media_link"] = 'https://www.telegraph.co.uk/content/dam/football/spark/FootballIndex/footballer-kicking-ball-on-pitch-xlarge.jpg'
        player["media_link_2"] = 'https://www.telegraph.co.uk/content/dam/football/spark/FootballIndex/footballer-kicking-ball-on-pitch-xlarge.jpg'
        players.append(player)

    try:
        player_collection.insert_many(players, {'ordered': False})
    except:
        player_collection.insert_many(players)
    print("Player count: {}".format(player_collection.count_documents({})))


if __name__ == "__main__":
    main()
