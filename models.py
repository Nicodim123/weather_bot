from peewee import *
db = SqliteDatabase("weather_database.db")

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    user_id = IntegerField(primary_key=True)
    username = CharField(null=True)
    first_name = CharField()
    last_name = CharField(null=True)
    latitude = IntegerField()
    longitude = IntegerField()

def create_models():
    db.create_tables(BaseModel.__subclasses__())