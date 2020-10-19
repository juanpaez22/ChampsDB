# TeamA6: ChampionsDB 2019-2020

## To build and run from scratch:
First, install all dependencies listed in requirements.txt using pip. Next, provide the connection credentials for a running MongoDB database server populated with the model data in an environment variable named DB_CONNECTION_STRING. Optionally, you can initialize the database yourself the database with data from the API-Football API using the db_init.py script (populates with three players, 4 teams, and 3 matches for now). You can then populate the database with data from the other 2 API's using the append_data_db.py script, which uses the Twitter API and the Fifa Ultimate Team API to get more information about players. Finally, launch the application locally (or deploy to a cloud host) in app.py with the Flask framework (e.g. python app.py or flask run).

## Team Information
Team Member | UT EID | GitHub
--- | --- | ---
Juan Paez | jfp778 | juanpaez22
Ben Buhse | bwb887 | bwbuhse
Conor Flood | cf26784 | cnflood
Pearse Flood | pkf256 | pkflood


## Deployed Web Application
http://champsdb.herokuapp.com


## Phase I Completion Time
### Juan
Task | Linked Stories | Estimated Completion Time (Hrs) | Actual Completion Time (Hrs)
--- | --- | --- | ---
Initialize MongoDB database with information about 10 instances from 3 API's | 4,5,6,7,8,9 | 6 | 8
Design instance page for players | 9 | 3 | 2
Link instance pages to at least 2 other instances | 5,7 | 2 | 4


### Conor
Task | Linked Stories | Estimated Completion Time (Hrs) | Actual Completion Time (Hrs)
--- | --- | --- | ---
Create home page with navbar in base template | 1, 3 | 3 | 4 |
Help implement about page | 2 | 2 | 3 |
Help format model pages for players, teams, and matches | 6 | 3 | 4 |

### Ben
Task | Linked Stories | Estimated Completion Time (Hrs) | Actual Completion Time (Hrs)
--- | --- | --- | ---
Create the initial routing for the site and connect to the database | 1 | 6 | 4
Create the instance templates for teams and matches | 5, 6 | 3 | 3


### Pearse
Task | Linked Stories | Estimated Completion Time (Hrs) | Actual Completion Time (Hrs)
--- | --- | --- | ---
Create model pages for players, teams, and matches | 1, 6 | 3 | 4 |
Help with home page formatting | 3 | 2 | 3 |
Help implement about page | 2 | 2 | 3 |

## Phase II Completion Time
Note: new format used after feedback from Phase 1

User Story | Assigned Member(s) | Estimated Completion Time (Hrs) | Actual Completion Time (Hrs)
--- | --- | --- | ---
#1 | Juan | 6 | 12
#2 | Juan, Ben | 6 | 


## Phase III Completion Time

