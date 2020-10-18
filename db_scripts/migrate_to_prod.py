# Migrates data from dev database to prod.
# Assumes that dev database may have more teams or matches than necessary, but players are correct.

import pymongo
from pymongo import MongoClient
import config


def main():
    client = MongoClient(config.db_connection_string, connect=False)
    db = client['ChampionsDB']

    # Get documents from dev
    players = list(db.players.find({}))
    matches = list(db.matches.find({}))
    teams = list(db.teams.find({}))
    events = list(db.filtered_events.find({}))

    team_ids = set()
    for player in players:
        team_ids.add(player['team_id'])

    teams = [team for team in teams if team['_id'] in team_ids]
    matches = [match for match in matches if match['home_team_id'] in team_ids and match['away_team_id'] in team_ids]

    print(f"Number of players to migrate: {len(players)}")
    print(f"Number of teams to migrate: {len(teams)}")
    print(f"Number of matches to migrate: {len(matches)}")
    print(f"Number of events to migrate: {len(events)}")

    client_prod = MongoClient(config.prod_db_connection_string, connect=False)
    db_prod = client_prod['ChampionsDB']

    # remove all previous info from prod
    db_prod.players.remove({})
    db_prod.matches.remove({})
    db_prod.teams.remove({})
    db_prod.events.remove({})

    # add new info to prod
    db_prod.players.insert_many(players)
    db_prod.matches.insert_many(matches)
    db_prod.teams.insert_many(teams)
    db_prod.events.insert_many(events)

    print("\nPlayer count: {}".format(db_prod.players.count_documents({})))
    print("Team count: {}".format(db_prod.matches.count_documents({})))
    print("Match count: {}".format(db_prod.teams.count_documents({})))
    print("Event count: {}".format(db_prod.events.count_documents({})))


if __name__ == "__main__":
    main()

