import json
import os
import re

from flask import Blueprint, Flask, redirect, render_template, request, url_for
from flask_mongoengine import MongoEngine
from flask_paginate import Pagination, get_page_args, get_page_parameter
from flask_sqlalchemy import SQLAlchemy
from mongoengine.queryset.visitor import Q
from pymongo import MongoClient

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'ChampionsDB',
    'host': os.environ['DB_CONNECTION_STRING'],
    'port': 27017
}
db = MongoEngine()
db.init_app(app)


class Tweet(db.EmbeddedDocument):
    '''
    The embeded Tweet collection from the db

    This belongs to the Players collection
    '''
    id = db.StringField()
    text = db.StringField()
    lang = db.StringField()
    html = db.StringField()


class Players(db.Document):
    ''' The Players collection from the db '''
    _id = db.IntField()
    name = db.StringField()
    position = db.StringField()
    team_id = db.IntField()
    team_name = db.StringField()
    media_link = db.URLField()
    media_link_2 = db.URLField()
    number = db.IntField()
    captain = db.BooleanField()

    # Twitter API
    tweets = db.ListField(db.EmbeddedDocumentField(Tweet))

    # FutDB fields
    rating_overall = db.IntField()  # -1 if scraping failed
    rating_defending = db.IntField()
    rating_dribbling = db.IntField()
    rating_pace = db.IntField()
    rating_passing = db.IntField()
    rating_physicality = db.IntField()
    rating_shooting = db.IntField()

    # Summary from match events
    goals = db.IntField()
    assists = db.IntField()
    passes = db.IntField()
    shots = db.IntField()
    shots_on_target = db.IntField()
    avg_minutes_played = db.DecimalField()
    avg_rating = db.DecimalField()
    avg_pass_accuracy = db.DecimalField()

    meta = {'indexes': [
        {'fields': ['$name', '$position', '$team_name'],
         'default_language': 'english',
         'weights': {'name': 10, 'position': 1, 'team_name': 7}
         }
    ]}


class Teams(db.Document):
    ''' The Teams collection from the db '''
    _id = db.IntField()
    name = db.StringField()
    country = db.StringField()
    city = db.StringField()
    stadium = db.StringField()
    media_link = db.URLField()
    media_link_2 = db.URLField()
    founded = db.IntField()
    stadium_surface = db.StringField()
    stadium_address = db.StringField()
    stadium_capacity = db.IntField()

    # Twitter API
    tweets = db.ListField(db.EmbeddedDocumentField(Tweet))

    meta = {'indexes': [
        {'fields': ['$name', "$country", "$city", "$stadium", "$stadium_surface", "$stadium_address"],
         'default_language': 'english',
         'weights': {'name': 10, 'country': 5, 'city': 5, 'stadium': 5, 'stadium_surface': 1, 'stadium_address': 1}
         }
    ]}


class Matches(db.Document):
    ''' The Matches collection from the db '''
    _id = db.IntField()
    date = db.DateTimeField()
    stadium = db.StringField()
    home_team_name = db.StringField()
    home_team_id = db.IntField()
    away_team_name = db.StringField()
    away_team_id = db.IntField()
    score = db.StringField()
    media_link = db.URLField()
    media_link_2 = db.URLField()
    round = db.StringField()
    referee = db.StringField()
    goals_home_team = db.IntField()
    goals_away_team = db.IntField()

    meta = {'indexes': [
        {'fields': ['$home_team_name', "$away_team_name", "$stadium", "$score", "$round", "$referee"],
         'default_language': 'english',
         'weights': {'home_team_name': 10, 'away_team_name': 10, 'stadium': 5, 'score': 1, 'round': 1, 'referee': 1}
         }
    ]}


class Events(db.Document):
    ''' The Events collection from the db '''
    _id = db.IntField()
    player_id = db.IntField()
    player_name = db.StringField()
    team_id = db.IntField()
    team_name = db.StringField()
    number = db.IntField()
    position = db.StringField()
    rating = db.StringField()
    minutes_played = db.IntField()
    captain = db.BooleanField()
    substitute = db.BooleanField()
    offsides = db.IntField(null=True)
    match_id = db.IntField()
    shots = db.IntField()
    shots_on_target = db.IntField()
    goals = db.IntField()
    assists = db.IntField()
    passes = db.IntField()
    pass_accuracy = db.IntField()


# Source used to help with pagination: https://gist.github.com/mozillazg/69fb40067ae6d80386e10e105e6803c9
def get_players(offset=0, per_page=12, sort_by="-goals", search_query=None):
    if sort_by == None or sort_by == "None":
        sort_by = "-goals"

    players = None
    if search_query is None or len(search_query) == 0 or search_query == "None":
        players = Players.objects().order_by(sort_by)
    else:
        players = Players.objects().search_text(search_query).order_by(sort_by)
    return players[offset: offset + per_page], len(players)


def get_teams(offset=0, per_page=12, sort_by="name", search_query=None):
    if sort_by == None or sort_by == "None":
        sort_by = "name"

    teams = None
    if search_query is None or len(search_query) == 0 or search_query == "None":
        teams = Teams.objects().order_by(sort_by)
    else:
        teams = Teams.objects().search_text(search_query).order_by(sort_by)

    return teams[offset: offset + per_page], len(teams)


def get_matches(offset=0, per_page=12, sort_by="-date", search_query=None):
    if sort_by is None or sort_by == "None":
        sort_by = "-date"

    matches = None
    if search_query is None or len(search_query) == 0 or search_query == "None":
        matches = Matches.objects().order_by(sort_by)
    else:
        matches = Matches.objects().search_text(search_query).order_by(sort_by)

    return matches[offset: offset + per_page], len(matches)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/model/<string:model>', methods=['POST', 'GET'])
def model(model=None):
    '''
    Return a model's page.

    <model> is one of: {player, team, match}
    '''
    sort_by = str(request.args.get('sort'))
    search_query = str(request.args.get('q'))

    if model == 'player':
        page, per_page, offset = get_page_args(
            page_parameter='page', per_page_parameter='per_page', per_page=12)
        pagination_players, total = get_players(
            offset=offset, per_page=12, sort_by=sort_by, search_query=search_query)
        pagination = Pagination(
            page=page, per_page=per_page, total=total, css_framework='bootstrap4')

        return render_template('model_players.html', players=pagination_players, page=page, per_page=per_page, pagination=pagination, model=model)
    elif model == 'team':
        page, per_page, offset = get_page_args(
            page_parameter='page', per_page_parameter='per_page', per_page=12)
        pagination_teams, total = get_teams(
            offset=offset, per_page=12, sort_by=sort_by, search_query=search_query)
        pagination = Pagination(
            page=page, per_page=per_page, total=total, css_framework='bootstrap4')

        return render_template('model_teams.html', teams=pagination_teams, page=page, per_page=per_page, pagination=pagination, model=model)

    elif model == 'match':
        page, per_page, offset = get_page_args(
            page_parameter='page', per_page_parameter='per_page', per_page=12)
        pagination_matches, total = get_matches(
            offset=offset, per_page=12, sort_by=sort_by, search_query=search_query)
        pagination = Pagination(
            page=page, per_page=per_page, total=total, css_framework='bootstrap4')

        return render_template('model_matches.html', matches=pagination_matches, page=page, per_page=per_page, pagination=pagination, model=model)

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
    if model == 'player':
        player = Players.objects(_id=id)

        if len(player) == 0:
            return not_found(404)

        player = player[0]
        player_matches = Matches.objects(
            Q(home_team_id=player.team_id) | Q(away_team_id=player.team_id))
        player_events = Events.objects(Q(player_id=id))

        return render_template('instance_player.html', model=model, id=id, player=player, matches=player_matches, player_events=player_events)
    elif model == 'team':
        team = Teams.objects(_id=id)

        if len(team) == 0:
            return not_found(404)

        team = team[0]
        team_players = Players.objects(team_id=team._id)
        team_matches = Matches.objects(
            Q(home_team_id=team._id) | Q(away_team_id=team._id))

        return render_template('instance_team.html', model=model, id=id, team=team, matches=team_matches, players=team_players)
    elif model == 'match':
        match = Matches.objects(_id=id)

        if len(match) == 0:
            return not_found(404)

        match = match[0]
        teams = Teams.objects(Q(_id=match.home_team_id) |
                              Q(_id=match.away_team_id))
        players = Players.objects(
            Q(team_id=match.home_team_id) | Q(team_id=match.away_team_id))
        events = Events.objects(Q(match_id=id))

        return render_template('instance_match.html', model=model, id=id, match=match, teams=teams, players=players, events=events)

    return not_found(404)


@app.errorhandler(404)
def not_found(error):
    ''' 404 Handler to return our custome template and set the 404 status code '''
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
