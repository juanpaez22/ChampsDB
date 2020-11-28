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
    Return a model's page.

    <model> is one of: {player, team, match}
    '''
    sort_by = str(request.args.get('sort'))
    search_query = str(request.args.get('q'))
    filter_by = str(request.args.get('filter'))

    # Select which model to display then load its values
    if model == 'player':
        page, per_page, offset = get_page_args(
            page_parameter='page', per_page_parameter='per_page', per_page=12)
        pagination_players, total = Players.get_instances(
            offset=offset, per_page=12, sort_by=sort_by, search_query=search_query, filter_by=filter_by)
        pagination = Pagination(
            page=page, per_page=per_page, total=total, css_framework='bootstrap4')

        filter_options = {
            'Position': ['Goalkeeper', 'Defender', 'Midfielder', 'Forward'],
            'Club': sorted(list(set([player.team_name for player in Players.get_instances()[0]])))
        }

        return render_template('model_players.html', players=pagination_players, page=page, per_page=per_page, pagination=pagination, model=model, sort=sort_by, query=search_query, filter_options=filter_options, filter=filter_by)
    elif model == 'team':
        page, per_page, offset = get_page_args(
            page_parameter='page', per_page_parameter='per_page', per_page=12)
        pagination_teams, total = Teams.get_instances(
            offset=offset, per_page=12, sort_by=sort_by, search_query=search_query, filter_by=filter_by)
        pagination = Pagination(
            page=page, per_page=per_page, total=total, css_framework='bootstrap4')

        filter_options = {
            'Country': sorted(list(set([team.country for team in Teams.get_instances()[0]]))),
            'City': sorted(list(set([team.city for team in Teams.get_instances()[0]])))
        }

        return render_template('model_teams.html', teams=pagination_teams, page=page, per_page=per_page, pagination=pagination, model=model, sort=sort_by, query=search_query, filter_options=filter_options, filter=filter_by)

    elif model == 'match':
        page, per_page, offset = get_page_args(
            page_parameter='page', per_page_parameter='per_page', per_page=12)
        pagination_matches, total = Matches.get_instances(
            offset=offset, per_page=12, sort_by=sort_by, search_query=search_query, filter_by=filter_by)
        pagination = Pagination(
            page=page, per_page=per_page, total=total, css_framework='bootstrap4')

        filter_options = {
            'Round': sorted(list(set([match.round for match in Matches.get_instances()[0]]))),
            'Team': sorted(list(set([match.home_team_name for match in Matches.get_instances()[0]]) | set([match.away_team_name for match in Matches.get_instances()[0]]))),
            'Stadium': sorted(list(set([match.stadium for match in Matches.get_instances()[0]]))),
        }

        return render_template('model_matches.html', matches=pagination_matches, page=page, per_page=per_page, pagination=pagination, model=model, sort=sort_by, query=search_query, filter_options=filter_options, filter=filter_by)

    return not_found(404)


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

        return render_template('instance_player.html', model=model, id=id, player=player, matches=player_matches, player_events=player_events)
    elif model == 'team':
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

        return render_template('instance_team.html', model=model, id=id, team=team, matches=team_matches, players=team_players)
    elif model == 'match':
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

        return render_template('instance_match.html', model=model, id=id, match=match, teams=teams, players=players, events=events)

    return not_found(404)


@app.errorhandler(404)
def not_found(error):
    '''
    404 Handler to return our custome template and set the 404 status code
    '''
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
