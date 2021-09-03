from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

db= SQLAlchemy()

class Genre(db.Model):
    __tablename__= 'Genre'

    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String)

genre_artist_table= db.Table('genre_artist_table',
    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
)

genre_venue_table= db.Table('genre_venue_table',
    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
)    

class Venue(db.Model):
    __tablename__= 'Venue'

    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String)
    city= db.Column(db.String(120))
    state= db.Column(db.String(120))
    address= db.Column(db.String(120))
    phone= db.Column(db.String(120))
    image_link= db.Column(db.String(500))
    facebook_link= db.Column(db.String(120))
    genres= db.relationship('Genre', secondary=genre_venue_table, backref= db.backref('venues'))
    website= db.Column(db.String(120))
    seeking_talent= db.Column(db.Boolean, default=False)
    seeking_description= db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy='joined', cascade="all, delete")
    def __repr__(self):
      return f'<Venue {self.id} {self.name}>'

    # : implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__= 'Artist'

    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String)
    city= db.Column(db.String(120))
    state= db.Column(db.String(120))
    phone= db.Column(db.String(120))
    image_link= db.Column(db.String(500))
    facebook_link= db.Column(db.String(120))
    genres= db.relationship('Genre', secondary=genre_artist_table, backref=db.backref('artists'))
    website= db.Column(db.String(120))
    seeking_venue= db.Column(db.Boolean, default=False)
    seeking_description= db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy='joined', cascade="all, delete")
    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'
    # : implement any missing fields, as a database migration using Flask-Migrate

#  Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__= 'Show'

    id= db.Column(db.Integer, primary_key=True)
    start_time= db.Column(db.DateTime, nullable=False, default=datetime.utcnow)    
    artist_id= db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)   
    venue_id= db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

    def __repr__(self):
        return f'<Show {self.id} {self.start_time} artist_id={self.artist_id} venue_id={self.venue_id}>'

