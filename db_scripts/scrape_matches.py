# Scrapes information about UCL 2019-2020 matches and adds to DB.
import requests
import json
import pymongo
from pymongo import MongoClient
import config

def main():
    # Get matches from DB and clear old.
    client = MongoClient(config.db_connection_string, connect=False)
    db = client['ChampionsDB']
    match_collection = db.matches
    match_collection.remove({})

    # Get all matches for UCL 2019-2020
    api_football_uri = "https://api-football-v1.p.rapidapi.com/v2"
    api_football_headers = {'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
           'x-rapidapi-key': config.api_football_key}
    response = requests.get(f"{api_football_uri}/fixtures/league/530/", headers=api_football_headers).json()

    match_list = response["api"]["fixtures"]
    for match in match_list:
        match.pop("league", None)
        match.pop("league_id", None)
        match["_id"] = match.pop("fixture_id", None)
        match["stadium"] = match.pop("venue", None)
        match["home_team_id"] = match["homeTeam"]["team_id"]
        match["away_team_id"] = match["awayTeam"]["team_id"]
        match["home_team_name"] = match["homeTeam"]["team_name"]
        match["away_team_name"] = match["awayTeam"]["team_name"]
        match["media_link"] = match["homeTeam"]["logo"]
        match["media_link_2"]  = match["awayTeam"]["logo"]
        match.pop("homeTeam", None)
        match.pop("awayTeam", None)
        score = match.pop("score", None)["fulltime"]
        match["score"] = score
        match.pop("elapsed", None)
        match.pop("statusShort", None)
        match.pop("status", None)
        match.pop("event_timestamp", None)
        match.pop("firstHalfStart", None)
        match.pop("secondHalfStart", None)
        match["date"] = match.pop("event_date", None)
        match["goals_home_team"] = match.pop("goalsHomeTeam", None)
        match["goals_away_team"] = match.pop("goalsAwayTeam", None)

    match_collection.insert_many(match_list)
    print("Match count: {}".format(match_collection.count_documents({})))


if __name__ == "__main__":
    main()
