import os
import json
from flask import Flask, request, abort, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import db_drop_and_create_all, setup_db, Movie, Actor, Performance
from auth import AuthError, requires_auth


ROWS_PER_PAGE = 10


def paginate_result(request, selection):
    page = request.args.get('page', 1, type=int)

    start = (page - 1) * ROWS_PER_PAGE
    end = start + ROWS_PER_PAGE

    formatted_items = [object_name.format() for object_name in selection]

    return formatted_items[start:end]


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    # db_drop_and_create_all()  # uncomment this to start db a new on start
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, PATCH, POST, DELETE, OPTIONS')

        return response

    # API Endpoints
    @app.route('/')
    def greeting():
        return "Welcome to the movie/actor database"

    @app.route('/login')
    def login():
        return redirect(os.environ['AUTH0_DOMAIN'] + 'authorize?audience=' + os.environ['API_AUDIENCE'] +
                        '&response_type=token&client_id=' + os.environ['CLIENT_ID'] + '&redirect_uri=' +
                        request.host_url + 'login-results')

    @app.route('/login-results')
    def callback_handling():
        return "Logged in"

    @app.route('/logout')
    def logging_out():
        return redirect(os.environ['AUTH0_DOMAIN'] + 'v2/logout?audience=' + os.environ['API_AUDIENCE'] +
                        '&client_id=' + os.environ['CLIENT_ID'] + '&returnTo=' +
                        request.host_url + 'logout-results')

    @app.route('/logout-results')
    def logged_out():
        return "Logged out"

    # Endpoint /actors GET/POST/DELETE/PATCH
    @app.route('/actors', methods=['GET'])
    @requires_auth('read:actors')
    def get_actors(jwt):
        """
        Get a paginated object of actors.
        Tests:
        Success:
            - test_get_actors
        Failure:
            - test_get_actors_error_404
        """
        selection = Actor.query.all()
        pagination = paginate_result(request, selection)

        if len(pagination) == 0:
            abort(404, {
                'message': 'No actors found in database.'})

        return jsonify({
            'success': True,
            'actors': pagination
        }), 200

    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actors')
    def add_actor(jwt):
        """
        Add new actor to database.
        Tests:
        Success:
            - test_add_actor
        Failure:
            - test_add_actor_error_422
        """
        data = request.get_json()
        if 'name' and 'age' not in data:
            abort(422)

        name = data.get('name', None)
        age = data.get('age', None)
        gender = data.get('gender', 'Other')

        try:
            new_actor = (Actor(
                name=name,
                age=age,
                gender=gender
            ))
            new_actor.insert()

            return jsonify({
                'success': True,
                'actor_id': new_actor.id
            }), 200

        except Exception:
            abort(422)

    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth('patch:actors')
    def update_actor(jwt, actor_id):
        """
        Modify existing actor.
        Tests:
        Success:
            - test_mod_actor
        Failure:
            - test_mod_actor_error_404
        """
        actor_to_modify = Actor.query.get(actor_id)

        if actor_to_modify is None:
            abort(404)

        data = request.get_json()
        name = data.get('name')
        age = data.get('age')
        gender = data.get('gender')
        movie_id = data.get('movie_id')

        if 'name':
            actor_to_modify.name = name
        if 'age':
            actor_to_modify.age = age
        if 'gender':
            actor_to_modify.gender = gender
        if 'movie_id':
            actor_to_modify.movie_id = movie_id

        try:
            actor_to_modify.update()

            return jsonify({
                'success': True,
                'actor_id': actor_to_modify.id
            }), 200

        except Exception:
            abort(404)

    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:actor')
    def delete_actor(jwt, actor_id):
        """
        Remove existing actor from database.
        Tests:
        Success:
            - test_remove_actor
        Failure:
            - test_remove_actor_error_404
        """
        actor_to_remove = Actor.query.get(actor_id)

        if actor_to_remove is None:
            abort(404)

        try:
            actor_to_remove.delete()

            return jsonify({
                'success': True,
                'delete': actor_to_remove.id
            }), 200

        except Exception:
            abort(404)

    # Endpoint /movies GET/POST/DELETE/PATCH
    @app.route('/movies', methods=['GET'])
    @requires_auth('read:movies')
    def get_movies(jwt):
        """
        Get paginated movie object
        Tests:
        Success:
            - test_get_movies
        Failure:
            - test_get_movies_error_404
        """
        selection = Movie.query.all()
        pagination = paginate_result(request, selection)

        if len(pagination) == 0:
            abort(404, {
                'message': 'No movies found in database.'})

        return jsonify({
            'success': True,
            'movies': pagination
        }), 200

    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movies')
    def add_movie(jwt):
        """
        Add new movie to database.
        Tests:
        Success:
            - test_add_movie
        Failure:
            - test_add_movie_error_422
        """
        data = request.get_json()
        if 'title' and 'release_date' not in data:
            abort(422)

        title = data.get('title', None)
        release_date = data.get('release_date', None)

        try:
            new_movie = (Movie(
                title=title,
                release_date=release_date
            ))
            new_movie.insert()

            return jsonify({
                'success': True,
                'movie_id': new_movie.id
            }), 200

        except Exception:
            abort(422)

    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth('patch:movies')
    def update_movie(jwt, movie_id):
        """
        Modify existing movie in database.
        Tests:
        Success:
            - test_mod_movie
        Failure:
            - test_mod_movie_error_404
        """
        movie_to_modify = Movie.query.get(movie_id)

        if movie_to_modify is None:
            abort(404)

        data = request.get_json()
        title = data.get('title')
        release_date = data.get('release_date')

        if 'title':
            movie_to_modify.title = title
        if 'release_date':
            movie_to_modify.age = release_date

        try:
            movie_to_modify.update()

            return jsonify({
                'success': True,
                'movie_id': movie_to_modify.id
            }), 200

        except Exception:
            abort(404)

    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movie')
    def delete_movie(jwt, movie_id):
        """
        Delete existing movie from database.
        Tests:
        Success:
            - test_remove_movie
        Failure:
            - test_remove_movie_error_404
        """
        movie_to_remove = Movie.query.get(movie_id)

        if movie_to_remove is None:
            abort(404)

        try:
            movie_to_remove.delete()

            return jsonify({
                'success': True,
                'delete': movie_to_remove.id
            }), 200

        except Exception:
            abort(404)

    # Error Handlers
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    @app.errorhandler(400)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(404)
    def bad_request_resource(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(401)
    def bad_request_auth_error(error):
        return jsonify({
            'success': False,
            'error': 401,
            'message': 'Not Authorized'
        }), 401

    @app.errorhandler(AuthError)
    def process_auth_error(error):
        response = jsonify(error.error)
        response.status_code = error.status_code

        return response

    return app


app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
