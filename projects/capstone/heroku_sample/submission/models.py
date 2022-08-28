import os
import json
from sqlalchemy import Column, String, create_engine, Integer, Date
from flask_sqlalchemy import SQLAlchemy
from datetime import date

database_path = os.environ['DATABASE_URL']
if database_path.startswith("postgres://"):
    database_path = database_path.replace("postgres://", "postgresql://", 1)

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


def db_drop_and_create_all():
    """
    Resets the database tables with a clean database.
    """
    db.drop_all()
    db.create_all()
    db_reset_records()


def db_reset_records():
    """
    Example entries to reset database
    """
    new_actor = (Actor(
        name='Ryan',
        gender='Male',
        age=43
    ))

    new_movie = (Movie(
        title='Ryan in a Movie',
        release_date=date.today()
    ))

    new_performance = Performance.insert().values(
        Movie_id=new_movie.id,
        Actor_id=new_actor.id,
        actor_charge=145.00
    )

    new_actor.insert()
    new_movie.insert()
    db.session.execute(new_performance)
    db.session.commit()


# Create table with associations
Performance = db.Table('Performance', db.Model.metadata,
                       db.Column('Movie_id', db.Integer, db.ForeignKey('movies.id')),
                       db.Column('Actor_id', db.Integer, db.ForeignKey('actors.id')),
                       db.Column('actor_fee', db.Float)
                       )


# Actor model
class Actor(db.Model):
    __tablename__ = 'actors'

    id = db.Column(db.Integer, db.Sequence('actors_id_seq'), primary_key=True)
    name = db.Column(db.String)
    gender = db.Column(db.String)
    age = db.Column(db.Integer)

    def __init__(self, name, gender, age):
        self.name = name
        self.gender = gender
        self.age = age

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'age': self.age
        }


# Movie model
class Movie(db.Model):
    __tablename__ = 'movies'

    id = db.Column(db.Integer, db.Sequence('movies_id_seq'), primary_key=True)
    title = db.Column(db.String)
    release_date = db.Column(db.Integer)
    actors = db.relationship('Actor', secondary=Performance, backref=db.backref('performances', lazy='joined'))

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.title,
            'release_date': self.release_date,
        }
