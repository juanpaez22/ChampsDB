
from flask_mongoengine import MongoEngine
from mongoengine import (Document, EmbeddedDocumentField, IntField, ListField,
                         StringField, URLField)

from tweet import Tweet

db = MongoEngine()


class Teams(Document):
    ''' The Teams collection from the db '''
    _id = IntField()
    name = StringField()
    country = StringField()
    city = StringField()
    stadium = StringField()
    media_link = URLField()
    media_link_2 = URLField()
    founded = IntField()
    stadium_surface = StringField()
    stadium_address = StringField()
    stadium_capacity = IntField()

    # Twitter API
    tweets = ListField(EmbeddedDocumentField(Tweet))

    meta = {'indexes': [
        {'fields': ['$name', "$country", "$city", "$stadium", "$stadium_surface", "$stadium_address"],
         'default_language': 'english',
         'weights': {'name': 10, 'country': 5, 'city': 5, 'stadium': 5, 'stadium_surface': 1, 'stadium_address': 1}
         }
    ]}

    __instances = None

    @staticmethod
    def get_instances(pagination_offset=0, per_page=-1, sort_by="name", search_query=None, filter_by=None):
        if Teams.__instances is None:
            Teams.__instances = Teams.objects()

        teams = Teams.__instances

        if sort_by is None or sort_by == "None":
            sort_by = "name"

        if search_query is None or len(search_query) == 0 or search_query == "None":
            teams = teams.order_by(sort_by)
        else:
            teams = teams.search_text(search_query).order_by(sort_by)

        if filter_by is not None and len(filter_by) > 0 and filter_by != "None":
            key = filter_by.split('_')[0]
            val = filter_by.split('_')[1]
            if key == 'Country':
                teams = [team for team in teams if team.country == val]
            if key == 'City':
                teams = [team for team in teams if team.city == val]

        if per_page == -1:
            return list(teams), len(teams)

        return teams[pagination_offset: pagination_offset + per_page], len(teams)
