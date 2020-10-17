# Scrapes information about UCL 2019-2020 players from fixture events and adds to events DB.
# Prerequisite: scrape_matches.py
# Because there are 210 games and only 100 free calls, this will need to be done over several iterations.

import requests
import json
import pymongo
from pymongo import MongoClient
import config
import time

def main():
    # Get players from DB. Does NOT clear old, unlike other scraping scripts.
    client = MongoClient(config.db_connection_string, connect=False)
    db = client['ChampionsDB']
    event_collection = db.events
    
    # First, get list of all match ids (reverse chronological)
    match_list = list(db.matches.find({}))
    match_ids = [match["_id"] for match in match_list]
    match_ids.sort()
    match_ids.reverse()

    # ************************************* IMPORTANT *************************************
    # Make sure to set this limit BEFORE running this script, or API might charge absurdly.

    call_limit = 80     # API call limit
    start = 160         # Match index at which we left off last time

    events = []
    match_ids = match_ids[start:start + call_limit]

    # Danger zone: fetch fixture statistics for each match
    # Theoretically does not make more calls than call_limit
    print(f"WARNING: Making {len(match_ids)} calls to API")
    api_football_uri = "https://api-football-v1.p.rapidapi.com/v2"
    api_football_headers = {'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
           'x-rapidapi-key': config.api_football_key}

    call_count = 0
    for match_id in match_ids:
        try:
            call_count += 1
            time.sleep(3)
            print(f"Request #{call_count}     Match ID={match_id}")
            response = requests.get(f"{api_football_uri}/players/fixture/{match_id}", headers=api_football_headers).json()
            match_events = response["api"]["players"]
            for event in match_events:
                event["match_id"] = match_id  # Add match id to the event
            events = events + match_events
            print(f"Received {len(match_events)} events!")
        except:
            print(f"WARNING: failed after {call_count} calls at match_id {match_id}. Proceeding")
            call_count -= 1
            break

    
    # Clean event information
    for event in events:
        try:
            event["_id"] = event.pop("event_id", None) * 100000000 + event["player_id"] # Janky way to produce unique id
            event.pop("updateAt", None)

            shots = event.pop("shots", None)
            event["shots"] = shots["total"]
            event["shots_on_target"] = shots["on"]

            goals = event.pop("goals", None)
            event["goals"] = goals["total"]
            event["assists"] = goals["assists"]

            passes = event.pop("passes", None)
            event["passes"] = passes["total"]
            event["pass_accuracy"] = passes["accuracy"]

            event.pop("tackles")
            event.pop("duels")
            event.pop("dribbles")
            event.pop("fouls")
            event.pop("penalty")
            event.pop("cards")
        except:
            print('WARNING: failed to clean an event.')
            print(event)
            continue

    # Store events back to DB
    try:
        event_collection.insert_many(events)
    except:
        event_collection.insert_many(events, {'ordered': False})
    print("Event count: {}".format(event_collection.count_documents({})))
    print("NOTE: Next starting index-- " + str(start + call_count))


if __name__ == "__main__":
    main()

