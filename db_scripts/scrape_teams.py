# Scrapes information about UCL 2019-2020 teams and adds to DB.

import requests
import json
import pymongo
from pymongo import MongoClient
import config

def main():
    # Get teams from DB and clear old.
    client = MongoClient(config.db_connection_string, connect=False)
    db = client['ChampionsDB']
    team_collection = db.teams
    team_collection.remove({})

    # Get all teams for UCL 2019-2020
    api_football_uri = "https://api-football-v1.p.rapidapi.com/v2"
    api_football_headers = {'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
           'x-rapidapi-key': config.api_football_key}
    response = requests.get(f"{api_football_uri}/teams/league/530/", headers=api_football_headers).json()
    
    team_list = response["api"]["teams"]
    for team in team_list:
        team["_id"] = team.pop("team_id", None)
        team["media_link"] = team.pop("logo", None)
        team["media_link_2"] = team["media_link"]
        team["stadium"] = team.pop("venue_name", None)
        team["stadium_surface"] = team.pop("venue_surface", None)
        team["stadium_address"] = team.pop("venue_address", None)
        team["city"] = team.pop("venue_city", None)
        team["stadium_capacity"] = team.pop("venue_capacity", None)
        team.pop("code", None)
        team.pop("is_national", None)

        # Scrape tweets regarding 2018-2019 UCL season for this team
        headers = {'Authorization': 'Bearer {}'.format(config.twitter_api_bearer)}
        try:
            print(f'Fetching tweets matching the query: {team["name"]} #ChampionsLeague')
            params = {
                'query': f'{team["name"]} #ChampionsLeague',
                'max_results': '10',
                'tweet.fields': 'lang'
                }
            response = requests.get('https://api.twitter.com/2/tweets/search/recent', headers=headers, params=params).json()
            print(json.dumps(response, indent=1))
            tweets = [{'id': tweet['id'], 'text': tweet['text'], 'lang': tweet['lang']} for tweet in response['data']]
            # Get HTML embedding for tweets
            for tweet in tweets:
                response = requests.get(f'https://publish.twitter.com/oembed?url=https://twitter.com/notused/status/{tweet["id"]}').json()
                tweet['html'] = response['html']

            team["tweets"] = tweets
        except:
            print("WARNING: No tweets found. Setting tweets to empty array.")
            team["tweets"] = []
    
        

    team_collection.insert_many(team_list)
    print("Team count: {}".format(team_collection.count_documents({})))


if __name__ == "__main__":
    main()
