Scripts to initialize ChampionsDB database to different extents.

Basic Database (phase 1):
1. init_basic_db.py: hardcodes 10 instances into database
2. append_data_db.py: adds more data to the hardcoded instances

Full Database (phase 2-4):
1. scrape_matches.py: scrapes matches from API-Football
2. scrape_teams.py: scrapes teams from API-Football and Twitter
3. scrape_player_events.py: scrapes player events (goals, cards, substitutes) from API-Football
4. coalesce_players.py: coalesces player events into players and brings in data from FutDB
