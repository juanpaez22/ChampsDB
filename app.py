import json
import os
from flask import Flask, redirect, render_template, request, url_for
from flask_mongoengine import MongoEngine
from pymongo import MongoClient
from mongoengine.queryset.visitor import Q

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'ChampionsDB',
    'host': os.environ['DB_CONNECTION_STRING'],
    'port': 27017
}
db = MongoEngine()
db.init_app(app)


class Tweet(db.EmbeddedDocument):
    id = db.StringField()
    text = db.StringField()
    lang = db.StringField()
    html = db.StringField()


class Players(db.Document):
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
    


class Teams(db.Document):
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


class Matches(db.Document):
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
    if model == 'player':
        players = Players.objects()
        return render_template('model_players.html', model=model, players=players)
    elif model == 'team':
        teams = Teams.objects()
        return render_template('model_teams.html', model=model, teams=teams)
    elif model == 'match':
        matches = Matches.objects()
        return render_template('model_matches.html', model=model, matches=matches)

    return render_template('404.html')


@app.route('/instance/<string:model>/<int:id>', methods=['POST', 'GET'])
def instance(model=None, id=0):
    '''
    Return a instance's page.

    <model> is one of: {player, team, match}
        404 error if <model> is not one of these three posibilities
    <id> is the integer id of the specific instance
        404 error if <id> does not exist in the model
    '''
    # TODO: The templates may need to be split up for each model
    if model == 'player':
        player = Players.objects(_id=id)

        if len(player) == 0:
            return render_template('404.html')

        player = player[0]
        player_matches = Matches.objects(Q(home_team_id=player.team_id) | Q(away_team_id=player.team_id))

        return render_template('instance_player.html', model=model, id=id, player=player, matches=player_matches)
    elif model == 'team':
        team = Teams.objects(_id=id)

        if len(team) == 0:
            return render_template('404.html')

        team = team[0]
        team_players = Players.objects(team_id=team._id)
        team_matches = Matches.objects(Q(home_team_id=team._id) | Q(away_team_id=team._id))

        return render_template('instance_team.html', model=model, id=id, team=team, matches=team_matches, players=team_players)
    elif model == 'match':
        match = Matches.objects(_id=id)

        if len(match) == 0:
            return render_template('404.html')

        match = match[0]
        teams = Teams.objects(Q(_id=match.home_team_id) | Q(_id=match.away_team_id))
        players = Players.objects(Q(team_id=match.home_team_id) | Q(team_id=match.away_team_id))
        return render_template('instance_match.html', model=model, id=id, match=match, teams=teams, players=players)

    return render_template('404.html')


if __name__ == '__main__':
    app.run(debug=True)
