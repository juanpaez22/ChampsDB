from flask_mongoengine import MongoEngine
from tweet import Tweet

db = MongoEngine()

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

    __instances = None

    @staticmethod
    def get_instances(offset=0, per_page=-1, sort_by="-goals", search_query=None, filter_by=None):
        if Players.__instances is None:
            Players.__instances = Players.objects()

        players = Players.__instances

        if sort_by is None or sort_by == "None":
            sort_by = "-goals"

        if search_query is None or len(search_query) == 0 or search_query == "None":
            players = players.order_by(sort_by)
        else:
            players = players.search_text(search_query).order_by(sort_by)

        if filter_by is not None and len(filter_by) > 0 and filter_by != "None":
            key = filter_by.split('_')[0]
            val = filter_by.split('_')[1]
            if key == 'Club':
                players = [player for player in players if player.team_name == val]
            if key == 'Position':
                players = [player for player in players if player.position == val[0]]

        if per_page == -1:
            return list(players), len(players)

        return players[offset: offset + per_page], len(players)
