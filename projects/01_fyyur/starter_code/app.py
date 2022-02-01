# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db_setup, Venue, Shows, Artist
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *


# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
db = db_setup(app)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#
def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#
@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue --> DONE
    regions = db.session.query(Venue.city, Venue.state).distinct()
    data = []

    for region in regions:
        region_venues = Venue.query.filter_by(state=region.state).filter_by(city=region.city).all()
        venues_list = []
        for venue in region_venues:
            venues_list.append({
                "id": venue.id,
                "name": venue.name,
                "no_upcoming_shows": Shows.query.filter(Shows.venue_id == venue.id).filter(Shows.start_time > datetime.now()).count()
            })
        data.append({
            "city": region.city,
            "state": region.state,
            "venues": venues_list
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive --> DONE
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term')
    data = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()

    response = {
        "count": len(data),
        "data": data
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id --> DONE
    arena = Venue.query.get(venue_id)
    show_data = Shows.query.filter_by(venue_id=venue_id)
    past_shows = []
    future_shows = []
    for show in show_data:
        if show.start_time < datetime.now():
            artist = Artist.query.get(show.artist_id)
            past_shows.append({
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time)
            })
        else:
            artist = Artist.query.get(show.artist_id)
            future_shows.append({
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time)
            })
    data = {
        "id": arena.id,
        "name": arena.name,
        "genres": arena.genres,
        "address": arena.address,
        "city": arena.city,
        "state": arena.state,
        "phone": arena.phone,
        "website": arena.website,
        "facebook_link": arena.facebook_link,
        "seeking_talent": arena.seeking_talent,
        "seeking_description": arena.seeking_description,
        "image_link": arena.image_link,
        "past_shows": past_shows,
        "upcoming_shows": future_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(future_shows)
    }

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead --> DONE
    # TODO: modify data to be the data object returned from db insertion --> DONE
    form = VenueForm()

    name = form.name.data.strip()
    city = form.city.data.strip()
    state = form.state.data
    address = form.address.data.strip()
    phone = form.phone.data
    # phone = re.sub('\D', '', phone)
    genre = form.genres.data
    seeking_talent = True if form.seeking_talent.data == 'Yes' else False
    seeking_description = form.seeking_description.data.strip()
    image_link = form.image_link.data.strip()
    website = form.website_link.data.strip()
    facebook_link = form.facebook_link.data.strip()

    if not form.validate():
        flash(form.errors)
        return redirect(url_for('create_venue_submission'))
    else:
        error_in_creation = False

        try:
            new_venue = Venue(name=name, city=city, state=state, address=address,
                              phone=phone, genre=genre, seeking_talent=seeking_talent,
                              seeking_description=seeking_description, image_link=image_link,
                              website=website, facebook_link=facebook_link)
            db.session.add(new_venue)
            db.session.commit()
        except Exception as e:
            error_in_creation = True
            print(f"Exception '{e}' in venue creation submission")
            db.session.rollback()
        finally:
            db.session.close()

        if not error_in_creation:
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
            return redirect(url_for('index'))
        else:
            flash("An error occurred. Venue " + name + " could not begin listed")
            print("Error in venue creation submission")
            abort(500)

    # # TODO: on unsuccessful db insert, flash an error instead. --> DONE
    # # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    # return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using --> DONE
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    venue = Venue.query.get(venue_id)
    if not venue:
        return redirect(url_for('index'))
    else:
        error_on_deletion = False
        venue_name = venue.name
        try:
            db.session.delete(venue)
            db.session.commit()
        except:
            error_on_deletion = True
            db.session.rollback()
        finally:
            db.session.close()
        if not error_on_deletion:
            flash(f"Successfully deleting the venue - {venue_name}.")
            return redirect(url_for('venues'))
        else:
            flash(f"An error occurred deleting the venue - {venue_name}.")
            print("Error in venue deletion")
            abort(500)

    # TODO: BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that --> added
    # clicking that button delete it from the db then redirect the user to the homepage
    # return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database  --> DONE
    artistz = Artist.query.order_by(Artist.name).all()

    data = []
    for artist in artistz:
        data.append({
            "id": artist.id,
            "name": artist.name
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive --> DONE
    # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term')
    data = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
    response = {
        "count": len(data),
        "data": data
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id  --> DONE
    artist = Artist.query.get(artist_id)
    if not artist:
        return redirect(url_for('index'))
    else:
        show_data = Shows.query.filter_by(artist_id=artist_id)
        past_shows = []
        future_shows = []
        for show in show_data:
            venue = Venue.query.get(show.venue_id)
            venue_detail = {
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": str(show.start_time)
            }
            if show.start_time < datetime.now():
                past_shows.append(venue_detail)
            else:
                future_shows.append(venue_detail)
        data = {
            "id": artist.id,
            "name": artist.name,
            "genres": artist.genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website,
            "facebook_link": artist.facebook,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": past_shows,
            "upcoming_shows": future_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(future_shows)
        }

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # TODO: populate form with fields from artist with ID <artist_id> --> DONE
    artist = Artist.query.get(artist_id)
    if not artist:
        return redirect(url_for('index'))
    else:
        form = ArtistForm(obj=artist)
    artist = {
        "id": artist_id,
        "name": artist.name,
        "genres": artist.genres,
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
    # TODO: take values from the form submitted, and update existing --> DONE
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm()

    name = form.name.data.strip()
    city = form.city.data.strip()
    state = form.state.data
    phone = form.phone.data
    genre = form.genres.data
    seeking_venue = True if form.seeking_venue.data == 'Yes' else False
    seeking_description = form.seeking_description.data.strip()
    image_link = form.image_link.data.strip()
    website = form.website_link.data.strip()
    facebook_link = form.facebook_link.data.strip()

    if not form.validate():
        flash(form.errors)
        return redirect(url_for('edit_artist_submission', artist_id=artist_id))
    else:
        error_in_update = False

        try:
            artist = Artist.query.get(artist_id)

            artist.name = name
            artist.city = city
            artist.state = state
            artist.phone = phone
            artist.genre = genre
            artist.seeking_venue = seeking_venue
            artist.seeking_description = seeking_description
            artist.image_link = image_link
            artist.website = website
            artist.facebook_link = facebook_link

            db.session.commit()
        except Exception as e:
            error_in_update = True
            print(f"Exception '{e}' in edit artist submission")
            db.session.rollback()
        finally:
            db.session.close()

    if not error_in_update:
        flash('Artist ' + request.form['name'] + ' was successfully updated')
        return redirect(url_for('show_artist', artist_id=artist_id))
    else:
        flash("An error occurred.  Artist " + name + "could not be updated")
        print("Error in artist submission")
        abort(500)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if not venue:
        return redirect(url_for('index'))
    else:
        form = VenueForm(obj=venue)
    venue = {
        "id": venue_id,
        "name": venue.name,
        "genres": venue.genres,
        "city": venue.city,
        "state": venue.state,
        "phone": (venue.phone[:3] + '-' + venue.phone[3:6] + '-' + venue.phone[6:]),
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_venue": venue.seeking_venue,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link
    }

    # TODO: populate form with values from venue with ID <venue_id> --> DONE
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing --> DONE
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm()

    name = form.name.data.strip()
    city = form.city.data.strip()
    state = form.state.data
    phone = form.phone.data
    genre = form.genres.data
    seeking_venue = True if form.seeking_venue.data == 'Yes' else False
    seeking_description = form.seeking_description.data.strip()
    image_link = form.image_link.data.strip()
    website = form.website_link.data.strip()
    facebook_link = form.facebook_link.data.strip()

    if not form.validate():
        flash(form.errors)
        return redirect(url_for('edit_venue_submission', venue_id=venue_id))
    else:
        error_in_update = False

        try:
            venue = Venue.query.get(venue_id)

            venue.name = name
            venue.city = city
            venue.state = state
            venue.phone = phone
            venue.genre = genre
            venue.seeking_venue = seeking_venue
            venue.seeking_description = seeking_description
            venue.image_link = image_link
            venue.website = website
            venue.facebook_link = facebook_link

            db.session.commit()
        except Exception as e:
            error_in_update = True
            print(f"Exception '{e}' in edit venue submission")
            db.session.rollback()
        finally:
            db.session.close()

    if not error_in_update:
        flash('venue ' + request.form['name'] + ' was successfully updated')
        return redirect(url_for('show_venue', venue_id=venue_id))
    else:
        flash("An error occurred.  venue " + name + "could not be updated")
        print("Error in venue submission")
        abort(500)


#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead --> DONE
    # TODO: modify data to be the data object returned from db insertion --> DONE
    form = ArtistForm()

    name = form.name.data.strip()
    city = form.city.data.strip()
    state = form.state.data
    phone = form.phone.data
    # phone = re.sub('\D', '', phone)
    genre = form.genres.data
    seeking_venue = True if form.seeking_venue.data == 'Yes' else False
    seeking_description = form.seeking_description.data.strip()
    image_link = form.image_link.data.strip()
    website = form.website_link.data.strip()
    facebook_link = form.facebook_link.data.strip()

    if not form.validate():
        flash(form.errors)
        return redirect(url_for('create_artist_submission'))
    else:
        error_in_artist_creation = False
        try:
            new_artist = Artist(name=name, city=city, state=state,
                                phone=phone, genre=genre, seeking_venue=seeking_venue,
                                seeking_description=seeking_description, image_link=image_link,
                                website=website, facebook_link=facebook_link)
            db.session.add(new_artist)
            db.session.commit()
        except Exception as e:
            error_in_artist_creation = True
            print(f"Exception '{e}' in creation of artist submission")
            db.session.rollback()
        finally:
            db.session.close()
        if not error_in_artist_creation:
            flash("Artist " + request.form['name'] + " was successfully listed")
        else:
            flash("An error occurred.  Artist " + name + " could not be listed")
            print("Error in creation of artist submission")
        return render_template('pages/home.html')

    # on successful db insert, flash success
    # flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead. --> DONE
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    # return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data. --> DONE
    data = []
    showz = Shows.query.all()

    for show in showz:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue_name,
            "artist_id": show.artist_id,
            "artist_name": show.artist_name,
            "artist_image_link": show.artist_image_link,
            "start_time": format_datetime(str(show.start_time))
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead --> DONE
    form = ShowForm()

    artist_id = form.artist_id.data.strip()
    venue_id = form.venue_id.data.strip()
    start_time = form.start_time.data.strip()
    error_in_show_creation = False

    try:
        new_show = Shows(artist_id=artist_id, vene_id=venue_id, start_time=start_time)
        db.session.add(new_show)
        db.session.commit()
    except Exception as e:
        error_in_show_creation = True
        print(f"Exception '{e}' in creation of show")
        db.session.rollback()
    finally:
        db.session.close()

    if error_in_show_creation:
        flash(f"An error occured.  Show could not be listed!")
        print("Error in creation of  show")
    else:
        flash('Show was successfully listed')
    return render_template('pages/home.html')

    # on successful db insert, flash success
    # flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead. --> DONE
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    # return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
