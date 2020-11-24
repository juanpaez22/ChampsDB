from flask_mongoengine import MongoEngine

db = MongoEngine()

class Tweet(db.EmbeddedDocument):
    '''
    The embeded Tweet collection from the db

    This belongs to the Players collection
    '''
    id = db.StringField()
    text = db.StringField()
    lang = db.StringField()
    html = db.StringField()
