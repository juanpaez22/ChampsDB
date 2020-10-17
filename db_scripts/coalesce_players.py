# Coalesces information from player events into standalone players.
# Prerequisite: scrape_matches.py, scrape_player_events.py

import requests
import json
import pymongo
from pymongo import MongoClient
import config
import selenium
from selenium import webdriver
import time


def main():
    client = MongoClient(config.db_connection_string, connect=False)
    db = client['ChampionsDB']
    player_collection = db.players
    player_collection.remove({})
    event_collection = db.filtered_events  # Filtered for captains and goalscorers only (this step not included in script)

    events = list(event_collection.find({}))
    player_to_events = {}

    wd = webdriver.Chrome(executable_path=config.DRIVER_PATH)

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

        # Get images for the player
        try:
            print('Fetching images for ' + player['name'])
            result = list(fetch_image_urls(player['name'], 2, wd, 1))
            player["media_link"] = result[0]
            player["media_link_2"] = result[1]
        except:
            # default media links
            player["media_link"] = 'https://www.telegraph.co.uk/content/dam/football/spark/FootballIndex/footballer-kicking-ball-on-pitch-xlarge.jpg'
            player["media_link_2"] = 'https://www.telegraph.co.uk/content/dam/football/spark/FootballIndex/footballer-kicking-ball-on-pitch-xlarge.jpg'
        
        
        try:
            player_collection.insert_one(player)
            print("Success! Inserted player " + player['name'])
        except:
            print("Warning! Failed to insert player " + player['name'])


def fetch_image_urls(query:str, max_links_to_fetch:int, wd:webdriver, sleep_between_interactions:int=1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)    
    
    # build the google query
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    # load the page
    wd.get(search_url.format(q=query))

    image_urls = set()
    image_count = 0
    results_start = 0
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)
        
        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")
        
        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get the real image behind it
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls    
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.add(actual_image.get_attribute('src'))

            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                print(f"Found: {len(image_urls)} image links, done!")
                break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(30)
            return
            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        # move the result startpoint further down
        results_start = len(thumbnail_results)

    return image_urls

if __name__ == "__main__":
    main()
