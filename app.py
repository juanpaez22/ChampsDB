import json
import os
import re

from flask import Blueprint, Flask, redirect, render_template, request, url_for
from flask_mongoengine import MongoEngine
from flask_paginate import Pagination, get_page_args, get_page_parameter
from flask_sqlalchemy import SQLAlchemy
from mongoengine.queryset.visitor import Q
from pymongo import MongoClient

from events import Events
from matches import Matches
from players import Players
from teams import Teams

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'ChampionsDB',
    'host': os.environ['DB_CONNECTION_STRING'],
    'port': 27017
}
db = MongoEngine()
db.init_app(app)


@app.route('/')
def index():
    ''' Index route to display the home page '''
    return render_template('index.html')


@app.route('/about')
def about():
    ''' About route to display the about page '''
    return render_template('about.html')


@app.route('/model/<string:model>', methods=['POST', 'GET'])
def model(model=None):
    '''
    Determine which model to load and then call the proper function.

    <model> is one of: {player, team, match}
    '''
    sort_by = get_sort()
    filter_by = get_filter()
    search_query = get_query()

    # Select which model to display then load its values
    if model == 'player':
        return model_player(sort_by, filter_by, search_query)
    elif model == 'team':
        return model_team(sort_by, filter_by, search_query)
    elif model == 'match':
        return model_match(sort_by, filter_by, search_query)

    return not_found(404)


def model_player(sort_by, filter_by, search_query):
    '''
    Load the players model page and then return it back to model()
    '''
    page, per_page, pagination_offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page', per_page=12)
    pagination_players, total = Players.get_instances(
        pagination_offset=pagination_offset, per_page=12, sort_by=sort_by, search_query=search_query, filter_by=filter_by)
    pagination = Pagination(
        page=page, per_page=per_page, total=total, css_framework='bootstrap4')

    filter_options = {
        'Position': ['Goalkeeper', 'Defender', 'Midfielder', 'Forward'],
        'Club': sorted(list(set([player.team_name for player in Players.get_instances()[0]])))
    }

    return render_template('model_players.html', players=pagination_players, page=page, per_page=per_page, pagination=pagination, model='player', sort=sort_by, query=search_query, filter_options=filter_options, filter=filter_by)


def model_team(sort_by, filter_by, search_query):
    '''
    Load the teams model page and then return it back to model()
    '''
    page, per_page, pagination_offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page', per_page=12)
    pagination_teams, total = Teams.get_instances(
        pagination_offset=pagination_offset, per_page=12, sort_by=sort_by, search_query=search_query, filter_by=filter_by)
    pagination = Pagination(
        page=page, per_page=per_page, total=total, css_framework='bootstrap4')

    filter_options = {
        'Country': sorted(list(set([team.country for team in Teams.get_instances()[0]]))),
        'City': sorted(list(set([team.city for team in Teams.get_instances()[0]])))
    }

    return render_template('model_teams.html', teams=pagination_teams, page=page, per_page=per_page, pagination=pagination, model='team', sort=sort_by, query=search_query, filter_options=filter_options, filter=filter_by)


def model_match(sort_by, filter_by, search_query):
    '''
    Load the matches model page and then return it back to model()
    '''
    page, per_page, pagination_offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page', per_page=12)
    pagination_matches, total = Matches.get_instances(
        pagination_offset=pagination_offset, per_page=12, sort_by=sort_by, search_query=search_query, filter_by=filter_by)
    pagination = Pagination(
        page=page, per_page=per_page, total=total, css_framework='bootstrap4')

    filter_options = {
        'Round': sorted(list(set([match.round for match in Matches.get_instances()[0]]))),
        'Team': sorted(list(set([match.home_team_name for match in Matches.get_instances()[0]]) | set([match.away_team_name for match in Matches.get_instances()[0]]))),
        'Stadium': sorted(list(set([match.stadium for match in Matches.get_instances()[0]]))),
    }

    return render_template('model_matches.html', matches=pagination_matches, page=page, per_page=per_page, pagination=pagination, model='match', sort=sort_by, query=search_query, filter_options=filter_options, filter=filter_by)


@app.route('/instance/<string:model>/<int:id>', methods=['POST', 'GET'])
def instance(model=None, id=0):
    '''
    Return a instance's page.

    <model> is one of: {player, team, match}
        404 error if <model> is not one of these three posibilities
    <id> is the integer id of the specific instance
        404 error if <id> does not exist in the model
    '''

    # Select which model the instance is from and then load the instance page
    if model == 'player':
        return instance_player(id)
    elif model == 'team':
        return instance_team(id)
    elif model == 'match':
        return instance_match(id)

    return not_found(404)


def instance_player(id):
    '''
    Load the correct instance page and then return it back to instance()
    '''
    player = [player for player in Players.get_instances()[0]
              if player._id == id]

    if len(player) == 0:
        return not_found(404)

    player = player[0]
    player_matches = [match for match in Matches.get_instances(
    )[0] if player.team_id == match.home_team_id]
    player_matches += [match for match in Matches.get_instances()
                       [0] if player.team_id == match.away_team_id]
    player_events = [event for event in Events.get_instances()[
        0] if event.player_id == id]

    return render_template('instance_player.html', model='player', id=id, player=player, matches=player_matches, player_events=player_events)


def instance_team(id):
    '''
    Load the correct instance page and then return it back to instance()
    '''
    team = [team for team in Teams.get_instances()[0] if team._id == id]

    if len(team) == 0:
        return not_found(404)

    team = team[0]
    team_players = [player for player in Players.get_instances()[
        0] if player.team_id == team._id]
    team_matches = [match for match in Matches.get_instances()[
        0] if match.home_team_id == team._id]
    team_matches += [match for match in Matches.get_instances()
                     [0] if match.away_team_id == team._id]

    return render_template('instance_team.html', model='team', id=id, team=team, matches=team_matches, players=team_players)


def instance_match(id):
    '''
    Load the correct instance page and then return it back to instance()
    '''
    match = [match for match in Matches.get_instances()[0]
             if match._id == id]

    if len(match) == 0:
        return not_found(404)

    match = match[0]
    teams = [team for team in Teams.get_instances(
    )[0] if match.home_team_id == team._id]
    teams += [team for team in Teams.get_instances()[0]
              if match.away_team_id == team._id]
    players = [player for player in Players.get_instances(
    )[0] if player.team_id == match.home_team_id]
    players += [player for player in Players.get_instances()[0]
                if player.team_id == match.away_team_id]
    events = [event for event in Events.get_instances()[0]
              if event.match_id == id]

    return render_template('instance_match.html', model='match', id=id, match=match, teams=teams, players=players, events=events)


@app.errorhandler(404)
def not_found(error):
    '''
    404 Handler to return our custome template and set the 404 status code
    '''
    return render_template('404.html'), 404


def get_sort():
    ''' Determine the sorting requested by the user '''
    return str(request.args.get('sort'))


def get_filter():
    ''' Get the filters requested by the user '''
    return str(request.args.get('filter'))

def get_query():
    ''' Get the search query requested by the user '''
    return str(request.args.get('q'))


if __name__ == '__main__':
    app.run(debug=True)
