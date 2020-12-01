from flask_mongoengine import MongoEngine
from mongoengine import (BooleanField, DecimalField, Document,
                         EmbeddedDocumentField, IntField, ListField,
                         StringField, URLField)

from tweet import Tweet



class Players(Document):
    ''' The Players collection from the db '''
    _id = IntField()
    name = StringField()
    position = StringField()
    team_id = IntField()
    team_name = StringField()
    media_link = URLField()
    media_link_2 = URLField()
    number = IntField()
    captain = BooleanField()

    # Twitter API
    tweets = ListField(EmbeddedDocumentField(Tweet))

    # FutDB fields
    rating_overall = IntField()  # -1 if scraping failed
    rating_defending = IntField()
    rating_dribbling = IntField()
    rating_pace = IntField()
    rating_passing = IntField()
    rating_physicality = IntField()
    rating_shooting = IntField()

    # Summary from match events
    goals = IntField()
    assists = IntField()
    passes = IntField()
    shots = IntField()
    shots_on_target = IntField()
    avg_minutes_played = DecimalField()
    avg_rating = DecimalField()
    avg_pass_accuracy = DecimalField()

    meta = {'indexes': [
        {'fields': ['$name', '$position', '$team_name'],
         'default_language': 'english',
         'weights': {'name': 10, 'position': 1, 'team_name': 7}
         }
    ]}

    __instances = None

    @staticmethod
    def get_instances(pagination_offset=0, per_page=-1, sort_by="-goals", search_query=None, filter_by=None):
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
                players = [
                    player for player in players if player.team_name == val]
            if key == 'Position':
                players = [
                    player for player in players if player.position == val[0]]

        if per_page == -1:
            return list(players), len(players)

        return players[pagination_offset: pagination_offset + per_page], len(players)
