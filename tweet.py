from flask_mongoengine import MongoEngine
from mongoengine import EmbeddedDocument, StringField

db = MongoEngine()


class Tweet(EmbeddedDocument):
    '''
    The embeded Tweet collection from the db

    This belongs to the Players collection
    '''
    id = StringField()
    text = StringField()
    lang = StringField()
    html = StringField()
