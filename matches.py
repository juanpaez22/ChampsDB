from flask_mongoengine import MongoEngine
from mongoengine import Document, IntField, DateTimeField, StringField, URLField

db = MongoEngine()


class Matches(Document):
    ''' The Matches collection from the db '''
    _id = IntField()
    date = DateTimeField()
    stadium = StringField()
    home_team_name = StringField()
    home_team_id = IntField()
    away_team_name = StringField()
    away_team_id = IntField()
    score = StringField()
    media_link = URLField()
    media_link_2 = URLField()
    round = StringField()
    referee = StringField()
    goals_home_team = IntField()
    goals_away_team = IntField()
    video = StringField()

    meta = {'indexes': [
        {'fields': ['$home_team_name', "$away_team_name", "$stadium", "$score", "$round", "$referee"],
         'default_language': 'english',
         'weights': {'home_team_name': 10, 'away_team_name': 10, 'stadium': 5, 'score': 1, 'round': 1, 'referee': 1}
         }
    ]}

    __instances = None

    @staticmethod
    def get_instances(offset=0, per_page=-1, sort_by="-date", search_query=None, filter_by=None):
        if Matches.__instances is None:
            Matches.__instances = Matches.objects()

        matches = Matches.__instances

        if sort_by is None or sort_by == "None":
            sort_by = "-date"

        if search_query is None or len(search_query) == 0 or search_query == "None":
            matches = matches.order_by(sort_by)
        else:
            matches = matches.search_text(search_query).order_by(sort_by)

        if filter_by is not None and len(filter_by) > 0 and filter_by != "None":
            key = filter_by.split('_')[0]
            val = filter_by.split('_')[1]
            if key == 'Round':
                matches = [match for match in matches if match.round == val]
            if key == 'Team':
                matches = [match for match in matches if match.home_team_name ==
                           val] + [match for match in matches if match.away_team_name == val]
            if key == 'Stadium':
                matches = [match for match in matches if match.stadium == val]

        if per_page == -1:
            return list(matches), len(matches)

        return matches[offset: offset + per_page], len(matches)
