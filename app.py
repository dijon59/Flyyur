# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import sys

import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
from flask_migrate import Migrate
from datetime import datetime
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#
from sqlalchemy import PickleType

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(PickleType)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String())
    facebook_link = db.Column(db.String(120))
    venue_shows = db.relationship('Show', back_populates='venue', lazy=True)


class Artist(db.Model):
    __tablename__ = 'Artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    genres = db.Column(PickleType)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String())
    facebook_link = db.Column(db.String(120))
    artist_shows = db.relationship('Show', back_populates='artist', lazy='dynamic')


class Show(db.Model):
    __tablename__ = 'Shows'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venues.id'), nullable=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artists.id'), nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    venue = db.relationship('Venue', back_populates='venue_shows')
    artist = db.relationship('Artist', back_populates='artist_shows')


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


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
    venues = Venue.query.all()
    return render_template('pages/venues.html', areas=venues)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_str = request.form.get('search_term')
    venue_query = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_str))).all()
    response = {
        "count": len(venue_query),
        "data": venue_query
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    upcoming_show_query = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()
    past_show_query = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()

    upcoming_shows_list = []
    for show in upcoming_show_query:
        show_dict = {}
        show_dict['venue_id'] = show.venue_id
        show_dict['artist_id'] = show.artist_id
        show_dict['venue_name'] = show.venue.name
        show_dict['artist_name'] = show.artist.name
        show_dict['artist_image_link'] = show.artist.image_link
        show_dict['start_time'] = str(show.start_time)
        upcoming_shows_list.append(show_dict)

    past_shows_list = []
    for show in past_show_query:
        show_dict = {}
        show_dict['venue_id'] = show.venue_id
        show_dict['artist_id'] = show.artist_id
        show_dict['venue_name'] = show.venue.name
        show_dict['artist_name'] = show.artist.name
        show_dict['artist_image_link'] = show.artist.image_link
        show_dict['start_time'] = str(show.start_time)
        past_shows_list.append(show_dict)

    venue_show = {
        'venue_upcoming_shows': upcoming_shows_list,
        'upcoming_shows_count': len(upcoming_shows_list),
        'past_shows': past_shows_list,
        'past_shows_count': len(past_shows_list)
    }
    return render_template('pages/show_venue.html', venue=venue, venue_show=venue_show)


#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm()
    if form.validate():
        try:
            venues = Venue(name=form.name.data,
                           genres=form.genres.data,
                           city=form.city.data,
                           state=form.state.data,
                           address=form.address.data,
                           phone=form.phone.data,
                           seeking_talent=form.seeking_talent.data,
                           seeking_description=form.seeking_description.data,
                           image_link=form.image_link.data,
                           website=form.website.data,
                           facebook_link=form.facebook_link.data
                           )
            db.session.add(venues)
            db.session.commit()
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        except:
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
    else:
        flash('There is a form error')
        return render_template('forms/new_venue.html', form=form)
    return render_template('pages/home.html')


@app.route('/venues/delete/<int:venue_id>', methods=['GET'])
def delete_venue(venue_id):
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = Artist.query.all()
    return render_template('pages/artists.html', artists=artists)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_str = request.form.get('search_term')
    artist_query = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_str))).all()
    response = {
        "count": len(artist_query),
        "data": artist_query
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    upcoming_show_query = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(
        Show.start_time > datetime.now()).all()
    past_show_query = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(
        Show.start_time < datetime.now()).all()

    upcoming_shows_list = []
    for show in upcoming_show_query:
        show_dict = {}
        show_dict['venue_id'] = show.venue_id
        show_dict['artist_id'] = show.artist_id
        show_dict['venue_name'] = show.venue.name
        show_dict['artist_name'] = show.artist.name
        show_dict['venue_image_link'] = show.artist.image_link
        show_dict['start_time'] = str(show.start_time)
        upcoming_shows_list.append(show_dict)

    past_shows_list = []
    for show in past_show_query:
        show_dict = {}
        show_dict['venue_id'] = show.venue_id
        show_dict['artist_id'] = show.artist_id
        show_dict['venue_name'] = show.venue.name
        show_dict['artist_name'] = show.artist.name
        show_dict['venue_image_link'] = show.artist.image_link
        show_dict['start_time'] = str(show.start_time)
        past_shows_list.append(show_dict)

    artist_show = {
        'artist_upcoming_shows': upcoming_shows_list,
        'upcoming_shows_count': len(upcoming_shows_list),
        'past_shows': past_shows_list,
        'past_shows_count': len(past_shows_list)
    }
    return render_template('pages/show_artist.html', artist=artist, artist_show=artist_show)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm()
    if form.validate():
        try:
            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.genres = form.genres.data
            artist.seeking_venue = form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data
            artist.image_link = form.image_link.data
            artist.website = form.website.data
            artist.facebook_link = form.facebook_link.data
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()
    else:
        flash('There is a form error')
        return render_template('forms/edit_artist.html', form=form, artist=artist)
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm()
    if form.validate():
        try:
            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.phone = form.phone.data
            venue.genres = form.genres.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data
            venue.image_link = form.image_link.data
            venue.website = form.website.data
            venue.facebook_link = form.facebook_link.data
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()
    else:
        flash('There is a form error')
        return render_template('forms/edit_venue.html', form=form, venue=venue)
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm()
    if form.validate():
        try:
            artists = Artist(name=form.name.data,
                             genres=form.genres.data,
                             city=form.city.data,
                             state=form.state.data,
                             phone=form.phone.data,
                             seeking_venue=form.seeking_venue.data,
                             image_link=form.image_link.data,
                             seeking_description=form.seeking_description.data,
                             website=form.website.data,
                             facebook_link=form.facebook_link.data
                             )
            db.session.add(artists)
            db.session.commit()
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
        except:
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
    else:
        flash('ERROR: Venue not added, please check errors below:')
        return render_template('forms/new_artist.html', form=form)
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = db.session.query(Show).all()
    shows_list = []
    for show in shows:
        show_dict = {}
        show_dict['venue_id'] = show.venue_id
        show_dict['artist_id'] = show.artist_id
        show_dict['venue_name'] = show.venue.name
        show_dict['artist_name'] = show.artist.name
        show_dict['artist_image_link'] = show.artist.image_link
        show_dict['start_time'] = str(show.start_time)
        shows_list.append(show_dict)
    return render_template('pages/shows.html', shows=shows_list)


@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm()
    if form.validate():
        try:
            shows = Show(artist_id=request.form['artist_id'],
                         venue_id=request.form['venue_id'],
                         start_time=request.form['start_time']
                         )
            db.session.add(shows)
            db.session.commit()
            flash('Show was successfully listed!')
        except:
            flash('An error occurred. Show could not be listed.')
            db.session.rollback()
        finally:
            db.session.close()
    else:
        flash('There is a form error')
        render_template('forms/new_show.html', form=form)
    return render_template('pages/home.html')


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
