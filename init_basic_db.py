import requests
import json
import pymongo
from pymongo import MongoClient
import config

"""
Creates a local MongoDB database and populates it with 3 instances for each model.
Bootstraps info from the 2019-2020 Champions League (id=530) for the following players, teams, and matches:
- Matches: Bayern vs. PSG (591151), Bayern vs. Lyon (589197), PSG vs. Leipzing (589000)
- Teams: Bayern Munich (157), PSG (85), RB Leipzig (173), Lyon (80)
- Players: Kylian Mbappe (278), Robert Lewandowski (521), Memphis Depay (667)
"""

api_uri = "https://api-football-v1.p.rapidapi.com/v2/"
headers = {'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
           'x-rapidapi-key': config.api_football_key}


def get_player_data(playerid):
    response = requests.get(
        api_uri + "/players/player/{}".format(playerid), headers=headers).json()
    player_json = [player for player in response["api"]
                   ["players"] if player["season"] == "2019-2020"][0]
    player = {}
    player["_id"] = player_json["player_id"]
    player["name"] = player_json["player_name"]
    player["position"] = player_json["position"]
    player["dob"] = player_json["birth_date"]
    player["nationality"] = player_json["nationality"]
    player["height"] = player_json["height"]
    player["weight"] = player_json["weight"]
    player["team_id"] = player_json["team_id"]
    player["team_name"] = player_json["team_name"]
    player["media_link"] = ""
    return player


def get_team_data(teamid):
    response = requests.get(
        api_uri + "/teams/team/{}".format(teamid), headers=headers).json()
    team_json = response["api"]["teams"][0]
    team = {}
    team["_id"] = team_json["team_id"]
    team["name"] = team_json["name"]
    team["country"] = team_json["country"]
    team["city"] = team_json["venue_city"]
    team["stadium"] = team_json["venue_name"]
    team["media_link"] = team_json["logo"]
    return team


def get_match_data(matchid):
    response = requests.get(
        api_uri + "/fixtures/id/{}".format(matchid), headers=headers).json()
    match_json = response["api"]["fixtures"][0]
    match = {}
    match["_id"] = match_json["fixture_id"]
    match["date"] = match_json["event_date"]
    match["stadium"] = match_json["venue"]
    match["home_team_name"] = match_json["homeTeam"]["team_name"]
    match["home_team_id"] = match_json["homeTeam"]["team_id"]
    match["away_team_name"] = match_json["awayTeam"]["team_name"]
    match["away_team_id"] = match_json["awayTeam"]["team_id"]
    match["score"] = match_json["score"]["fulltime"]
    # TODO: there's a lot mroe to matches that we can scrape-- events, lineups, statistics, etc.
    return match


def main():
     client = MongoClient(config.db_connection_string, connect=False)
     db = client['ChampionsDB']
     players = db.players
     teams = db.teams
     matches = db.matches

    # Get 3 players
     players.insert_many(
         [get_player_data(278), get_player_data(521), get_player_data(667)])
     print("Player count: {}".format(players.count_documents({})))

    # Get 4 teams
     teams.insert_many([get_team_data(157), get_team_data(
         173), get_team_data(85), get_team_data(80)])
     print("Team count: {}".format(teams.count_documents({})))

    # Get 3 matches
     matches.insert_many(
         [get_match_data(591151), get_match_data(589197), get_match_data(589000)])
     print("Match count: {}".format(matches.count_documents({})))


if __name__ == "__main__":
    main()
