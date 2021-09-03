#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, abort, jsonify ,Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import FileHandler , Formatter
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
import re
from operator import itemgetter 
from classes import db, Genre, Venue, Artist, Show
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

from flask_wtf.csrf import CSRFProtect
app= Flask(__name__)
moment= Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate= Migrate(app, db)
csrf = CSRFProtect(app)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date= dateutil.parser.parse(value)
  if format== 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format== 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime']= format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  #:replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues= Venue.query.all()
  data= []
  states_cities= set()
  for venue in venues:
      states_cities.add( (venue.state , venue.city) ) 
    
  states_cities= list(states_cities)
  states_cities.sort(key=itemgetter(1,0))    
  now= datetime.now()    
    
  for location in states_cities:
      venues_list= []
      for venue in venues:
          if (venue.city== location[0]) and (venue.state== location[1]):
              venue_shows= Show.query.filter_by(venue_id=venue.id).all()
              upcoming= 0
              for show in venue_shows:
                  if show.start_time > now:
                      upcoming += 1

              venues_list.append({
                  "id": venue.id,
                  "name": venue.name,
                  "num_upcoming_shows": upcoming
                })

      data.append({
          "city": location[0],
          "state": location[1],
          "venues": venues_list
      })  
  return render_template('pages/venues.html', areas=data)        
  
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # : implement search on artists with partial string search. Ensure it is case-insensitive.
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search= request.form.get('search', '').strip()
    venues= Venue.query.filter(Venue.name.ilike('%' + search + '%')).all() 
    venue_list= []
    now= datetime.now()
    for venue in venues:
        venue_shows= Show.query.filter_by(venue_id=venue.id).all()
        upcoming= 0
        for show in venue_shows:
            if show.start_time > now:
                upcoming += 1

        venue_list.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": upcoming  
        })

    response= {
        "count": len(venues),
        "data": venue_list
      }
    return render_template('pages/search_venues.html', results=response, search_term=search)
      
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
    venue = Venue.query.get_or_404(venue_id)
    print(venue)
    if not venue:
        return redirect(url_for('index'))
    else:
        past_shows = []
        upcoming_shows = []
        genres = [ genre.name for genre in venue.genres ]

        for show in venue.shows:
            temp_show = {
                'artist_id': show.artist_id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
            }
            if show.start_time <= datetime.now():
                past_shows.append(temp_show)
            else:
                upcoming_shows.append(temp_show)

        data = {
            "id": venue_id,
            "name": venue.name,
            "genres": genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": (venue.phone[:3] + '-' + venue.phone[3:6] + '-' + venue.phone[6:]),
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": past_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows": upcoming_shows,
            "upcoming_shows_count": len(upcoming_shows)
        }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form= VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # : insert form data as a new Venue record in the db, instead
  # : modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  # : on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    form= VenueForm(request.form, meta={'csrf': False})
    name= form.name.data.strip()
    city= form.city.data.strip()
    state= form.state.data
    address= form.address.data.strip()
    phone= form.phone.data
    phone= re.sub('\D', '', phone)
    genres= form.genres.data                  
    if form.seeking_talent.data== 'Yes' :
        seeking_talent= True
    else :
        seeking_talent= False
    seeking_description= form.seeking_description.data.strip()
    image_link= form.image_link.data.strip()
    website= form.website.data.strip()
    facebook_link= form.facebook_link.data.strip()
    
    if form.validate():
        error_in_insert= False
        try:
            new_venue= Venue(name=name, city=city, state=state, address=address, phone=phone, \
                seeking_talent=seeking_talent, seeking_description=seeking_description, image_link=image_link, \
                website=website, facebook_link=facebook_link)
            for genre in genres:
                fetchGener= Genre.query.filter_by(name=genre).one_or_none() 
                if fetchGener:
                    new_venue.genres.append(fetchGener)
                else:
                    new_genre= Genre(name=genre)
                    db.session.add(new_genre)
                    new_venue.genres.append(new_genre)  
        except Exception as e:
            error_in_insert= True
            print(f'Exception "{e}" in create_venue_submission()')
            db.session.rollback()
        finally:
            db.session.close()

        if not error_in_insert:
            flash('Venue ' + request.form['name'] + ' was successfully listed')
            return redirect(url_for('index'))
        else:
            flash('An error occurred. Venue ' + name + ' could not be listed')
            print("Error in create_venue_submission()")
            abort(500)
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))

    return render_template('pages/home.html')                

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # : Complete this endpoint for taking a venue_id, and using
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    venue= Venue.query.get(venue_id)
    if not venue:
        return redirect(url_for('index'))
    else:
        error_on_delete= False
        venue_name= venue.name
        try:
            db.session.delete(venue)
            db.session.commit()
        except:
            error_on_delete= True
            db.session.rollback()
        finally:
            db.session.close()
        if error_on_delete:
            flash(f'An error occurred on deleting venue {venue_name}')
            print("Error in delete_venue()")
            abort(500)
        else:
            return jsonify({
                'deleted': True,
                'url': url_for('venues')
            })

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # : replace with real data returned from querying the database
  artists= Artist.query.order_by(Artist.name).all()  
  data= []
  for artist in artists:
      data.append({
          "id": artist.id,
          "name": artist.name
      })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # : implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
    search_term= request.form.get('search_term', '').strip()
    artists= Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()   
    artist_list= []
    now= datetime.now()
    for artist in artists:
        artist_shows= Show.query.filter_by(artist_id=artist.id).all()
        upcoming= 0
        for show in artist_shows:
            if show.start_time > now:
                upcoming += 1

        artist_list.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": upcoming  
        })

    response= {
        "count": len(artists),
        "data": artist_list
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # : replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get_or_404(artist_id)
    print(artist)
    if not artist:
        return redirect(url_for('index'))
    else:
        past_shows = []
        upcoming_shows = []
        genres = [ genre.name for genre in artist.genres ]
        for show in artist.shows:
            temp_show = {
                'venue_id': show.venue_id,
                'venue_name': show.venue.name,
                'venue_image_link': show.venue.image_link,
                'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
            }
            if show.start_time <= datetime.now():
                past_shows.append(temp_show)
            else:
                upcoming_shows.append(temp_show)

        data = {
            "id": artist_id,
            "name": artist.name,
            "genres": genres,
            "city": artist.city,
            "state": artist.state,
            "phone": (artist.phone[:3] + '-' + artist.phone[3:6] + '-' + artist.phone[6:]),
            "website": artist.website,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": past_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows": upcoming_shows,
            "upcoming_shows_count": len(upcoming_shows)
        }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # : populate form with fields from artist with ID <artist_id>

  artist= Artist.query.get(artist_id)  
  if not artist:
      return redirect(url_for('index'))
  else:
      form= ArtistForm(obj=artist)
  genres= [ genre.name  for genre in artist.genres ]  
  artist= {
        "id": artist_id,
        "name": artist.name,
        "genres": genres,
        "city": artist.city,
        "state": artist.state,
        "phone": (artist.phone[:3] + '-' + artist.phone[3:6] + '-' + artist.phone[6:]),
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link
    }
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # : take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    form= ArtistForm(request.form, meta={'csrf': False})
    name= form.name.data.strip()
    city= form.city.data.strip()
    state= form.state.data
    phone= form.phone.data
    phone= re.sub('\D', '', phone) 
    genres= form.genres.data                  
    if form.seeking_venue.data== 'Yes':
        seeking_venue= True
    else :
         seeking_venue= False
    seeking_description= form.seeking_description.data.strip()
    image_link= form.image_link.data.strip()
    website= form.website.data.strip()
    facebook_link= form.facebook_link.data.strip()
    
    if form.validate() :
        error_in_update= False
        try:
            artist= Artist.query.get(artist_id)
            artist.name= name
            artist.city= city
            artist.state= state
            artist.phone= phone
            artist.seeking_venue= seeking_venue
            artist.seeking_description= seeking_description
            artist.image_link= image_link
            artist.website= website
            artist.facebook_link= facebook_link
            artist.genres= []
            for genre in genres:
                fetchGener= Genre.query.filter_by(name=genre).one_or_none()  
                if fetchGener:
                    artist.genres.append(fetchGener)

                else:
                    new_genre= Genre(name=genre)
                    db.session.add(new_genre)
                    artist.genres.append(new_genre)  

            db.session.commit()
        except Exception as e:
            error_in_update= True
            print(f'Exception "{e}" in edit_artist_submission()')
            db.session.rollback()
        finally:
            db.session.close()

        if not error_in_update:
            flash('Artist ' + request.form['name'] + ' was successfully updated')
            return redirect(url_for('show_artist', artist_id=artist_id))
        else:
            flash('An error occurred. Artist ' + name + ' could not be updated')
            print("Error in edit_artist_submission()")
            abort(500)
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))

    return render_template('pages/home.html')            

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # : populate form with values from venue with ID <venue_id>
    venue= Venue.query.get(venue_id)  
    if not venue:
        return redirect(url_for('index'))
    else:
        form= VenueForm(obj=venue)

    genres= [ genre.name  for  genre in venue.genres ]
    venue= {
        "id": venue_id,
        "name": venue.name,
        "genres": genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": (venue.phone[:3] + '-' + venue.phone[3:6] + '-' + venue.phone[6:]),
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link
    }

    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # : take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
    form= VenueForm(request.form, meta={'csrf': False})
    name= form.name.data.strip()
    city= form.city.data.strip()
    state= form.state.data
    address= form.address.data.strip()
    phone= form.phone.data
    phone= re.sub('\D', '', phone)
    genres= form.genres.data                  
    seeking_talent= True 
    if form.seeking_talent.data== 'Yes':
        seeking_talent= True 
    else :
        seeking_talent= False
    seeking_description= form.seeking_description.data.strip()
    image_link= form.image_link.data.strip()
    website= form.website.data.strip()
    facebook_link= form.facebook_link.data.strip()
    
    if form.validate():
        try:
            venue= Venue.query.get(venue_id)
            venue.name= name
            venue.city= city
            venue.state= state
            venue.address= address
            venue.phone= phone
            venue.seeking_talent= seeking_talent
            venue.seeking_description= seeking_description
            venue.image_link= image_link
            venue.website= website
            venue.facebook_link= facebook_link
            venue.genres= []
            for genre in genres:
                fetchGener= Genre.query.filter_by(name=genre).one_or_none() 
                if fetchGener:
                    venue.genres.append(fetchGener)

                else:
                    new_genre= Genre(name=genre)
                    db.session.add(new_genre)
                    venue.genres.append(new_genre) 

            db.session.commit()
        except Exception as e:
            error_in_update= True
            print(f'Exception "{e}" in edit_venue_submission()')
            db.session.rollback()
        finally:
            db.session.close()

        if not error_in_update:
            flash('Venue ' + request.form['name'] + ' was successfully updated')
            return redirect(url_for('show_venue', venue_id=venue_id))
        else:
            flash('An error occurred. Venue ' + name + ' could not be updated')
            print("Error in edit_venue_submission()")
            abort(500)
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))

    return render_template('pages/home.html')            
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form= ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # : insert form data as a new Venue record in the db, instead
  # : modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  # : on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed')
    form= ArtistForm(request.form, meta={'csrf': False})
    name= form.name.data.strip()
    city= form.city.data.strip()
    state= form.state.data
    phone= form.phone.data
    phone= re.sub('\D', '', phone) 
    genres= form.genres.data                  
    if form.seeking_venue.data== 'Yes':
        seeking_venue= True
    else :
        seeking_venue= False

    seeking_description= form.seeking_description.data.strip()
    image_link= form.image_link.data.strip()
    website= form.website.data.strip()
    facebook_link= form.facebook_link.data.strip()
    
    if form.validate():
        error_in_insert= False
        try:
            new_artist= Artist(name=name, city=city, state=state, phone=phone, \
                seeking_venue=seeking_venue, seeking_description=seeking_description, image_link=image_link, \
                website=website, facebook_link=facebook_link)
            for genre in genres:
                fetchGener= Genre.query.filter_by(name=genre).one_or_none()
                if fetchGener:
                    new_artist.genres.append(fetchGener)

                else:
                    new_genre= Genre(name=genre)
                    db.session.add(new_genre)
                    new_artist.genres.append(new_genre)  

            db.session.add(new_artist)
            db.session.commit()
        except Exception as e:
            error_in_insert= True
            print(f'Exception "{e}" in create_artist_submission()')
            db.session.rollback()
        finally:
            db.session.close()

        if not error_in_insert:
            flash('Artist ' + request.form['name'] + ' was successfully listed')
            return redirect(url_for('index'))
        else:
            flash('An error occurred. Artist ' + name + ' could not be listed')
            print("Error in create_artist_submission()")
            abort(500)
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))

    return render_template('pages/home.html')            

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # : replace with real venues data.
  data= []
  shows= Show.query.all()

  for show in shows:
        data.append({
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": format_datetime(str(show.start_time))
        })  

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create' , methods=['GET'])
def create_shows():
  # renders form. do not touch.
  form= ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # : insert form data as a new Show record in the db, instead
  # on successful db insert, flash success
  # : on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    form= ShowForm()
    artist_id= form.artist_id.data.strip()
    venue_id= form.venue_id.data.strip()
    start_time= form.start_time.data
    error_in_insert= False
    try:
        new_show= Show(start_time=start_time, artist_id=artist_id, venue_id=venue_id)
        db.session.add(new_show)
        db.session.commit()
    except Exception as e:
        error_in_insert= True
        print(f'Exception "{e}" in create_show_submission()')
        db.session.rollback()
    finally:
        db.session.close()

    if error_in_insert:
        flash(f'An error occurred.  Show could not be listed')
        print("Error in create_show_submission()")
    else:
        flash('Show was successfully listed')
    
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler= FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__== '__main__':
    app.run()

# Or specify port manually:
'''
if __name__== '__main__':
    port= int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
