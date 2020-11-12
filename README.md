# TeamA6: ChampionsDB 2019-2020

![Tests](https://github.com/UT-SWLab/TeamA6/workflows/Python%20application/badge.svg)

## To build and run the web server on your local machine:
1. Clone this repository
2. Install dependencies with "pip install -r requirements.txt"
3. Export the environment variable DB_CONNECTION_STRING with the connection string for the ChampionsDB database. We host ours on Google Cloud Platform, but if you would like to test it out with your own (local or remote), you can use the scripts in /scripts/--.py to populate the database to different extents (this requires that you store your API keys in /scripts/config.py-- be mindful of quota limits). Make sure your database's fields match the fields for players, matches, teams, and events listed in app.py.
4. Run the web application with "flask run" or "python app.py", which will host the web application on localhost.

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
#2 | Juan, Ben | 6 | 8
#3 | Ben, Conor | 9 | 7
#4 | Pearse, Conor | 8 | 10
#5 | Pearse | 2 | 1
#6 | Ben | 2 | 2

## Phase III Completion Time

