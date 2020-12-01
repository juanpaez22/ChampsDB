from flask_mongoengine import MongoEngine
from mongoengine import BooleanField, Document, IntField, StringField



class Events(Document):
    ''' The Events collection from the db '''
    _id = IntField()
    player_id = IntField()
    player_name = StringField()
    team_id = IntField()
    team_name = StringField()
    number = IntField()
    position = StringField()
    rating = StringField()
    minutes_played = IntField()
    captain = BooleanField()
    substitute = BooleanField()
    offsides = IntField(null=True)
    match_id = IntField()
    shots = IntField()
    shots_on_target = IntField()
    goals = IntField()
    assists = IntField()
    passes = IntField()
    pass_accuracy = IntField()

    __instances = None

    @staticmethod
    def get_instances():
        if Events.__instances is None:
            Events.__instances = Events.objects()

        return Events.__instances, len(Events.__instances)
