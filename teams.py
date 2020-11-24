
from flask_mongoengine import MongoEngine
from tweet import Tweet

db = MongoEngine()

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

    instances = None

    @staticmethod
    def get_instances(offset=0, per_page=-1, sort_by="name", search_query=None, filter_by=None):
        if Teams.instances is None:
            Teams.instances = Teams.objects()

        teams = Teams.instances

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

        return teams[offset: offset + per_page], len(teams)


