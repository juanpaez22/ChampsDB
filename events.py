from flask_mongoengine import MongoEngine

db = MongoEngine()


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

    __instances = None

    @staticmethod
    def get_instances():
        if Events.__instances is None:
            Events.__instances = Events.objects()

        return Events.__instances, len(Events.__instances)
