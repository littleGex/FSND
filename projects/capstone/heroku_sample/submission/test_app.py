import json
import os
import unittest
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from models import setup_db
from datetime import date


class AppTestCase(unittest.TestCase):
    def setUp(self):
        """
        Test variable definition and app initialisation
        """
        self.app = create_app()
        self.client = self.app.test_client()
        self.database = os.environ['DATABASE_URL']
        setup_db(self.app, self.database)
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # Create database tables
            self.db.create_all()

    # Run Actor testing
    # Test /actor GET
    def test_get_actors(self):
        """
        Test for GET all actors
        """
        response = self.client().get('/actors?page=1')

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['actors']) > 0)

    def test_get_actors_error_404(self):
        """
        Test for GET all actors error
        """
        response = self.client().get('/actors?page=1938462829')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'], False)
        self.assertEqual(data['message'], 'No actors found in database')

    # Test /actors/new POST
    def test_add_actor(self):
        """
        Test for POST new actor
        """
        create_actor_json = {
            'name': 'Dommy Dom',
            'age': 7,
            'gender': 'male'
        }
        response = self.client().post('/actors/new', json=create_actor_json)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['actor_id']) > 0)

    def test_add_actor_error_422(self):
        """
        Test for POST new actor without name error
        """
        create_actor_json = {
            'age': 23
        }
        response = self.client().post('/actors/new', json=create_actor_json)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertFalse(data['success'], False)
        self.assertTrue(data['message'], ['No name given.'])

    # Test modify actor PATCH
    def test_mod_actor(self):
        """
        Test for PATCH of existing actor
        """
        edit_actor_json = {
            'age': 21
        }

        response = self.client().patch('/actor/update/1', json=edit_actor_json)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['actor_id']) > 0)

    def test_mod_actor_error_404(self):
        """
        Test for PATCH of existing actor out of range error
        """
        edit_actor_json = {
            'age': 87
        }
        response = self.client().patch('/actors/update/3400', json=edit_actor_json)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'], False)
        self.assertTrue(data['message'], ['Actor with id 3400 not found in database'])

    # Test delete actor DELETE
    def test_remove_actor(self):
        """
        Test for DELETE of existing actor
        """
        response = self.client().delete('/actors/delete/2')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['delete'])

    def test_remove_actor_error_404(self):
        """
        Test for DELETE of existing movie out of range error
        """
        response = self.client().delete('/actors/delete/34009999')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'], False)
        self.assertTrue(data['message'], ['Actor with id 34009999 not found in database'])

    # Run Movie testing
    # Test /movies GET
    def test_get_movies(self):
        """
        Test for GET all movies
        """
        response = self.client().get('/movies?page=1')

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['movies']) > 0)

    def test_get_movies_error_404(self):
        """
        Test for GET all movies error
        """
        response = self.client().get('/movies?page=1938462829')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'], False)
        self.assertEqual(data['message'], 'No movies found in database')

    # Test /movies/new POST
    def test_add_movie(self):
        """
        Test for POST new movie
        """
        create_movie_json = {
            'title': 'Horrid Henri the movie',
            'release_date': date.today()
        }
        response = self.client().post('/movies/new', json=create_movie_json)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['movie_id']) > 0)

    def test_add_movie_error_422(self):
        """
        Test for POST new movie without name error
        """
        create_movie_json = {
            'release_date': date.today()
        }
        response = self.client().post('/movies/new', json=create_movie_json)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertFalse(data['success'], False)
        self.assertTrue(data['message'], ['No title given.'])

    # Test modify movie PATCH
    def test_mod_movie(self):
        """
        Test for PATCH of existing movie
        """
        edit_movie_json = {
            'release_date': date.today()
        }

        response = self.client().patch('/movie/update/1', json=edit_movie_json)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['movie_id']) > 0)

    def test_mod_movie_error_404(self):
        """
        Test for PATCH of existing movie out of range error
        """
        edit_movie_json = {
            'release_date': date.today()
        }
        response = self.client().patch('/movies/update/3400', json=edit_movie_json)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'], False)
        self.assertTrue(data['message'], ['Movie with id 3400 not found in database'])

    # Test delete movie DELETE
    def test_remove_movie(self):
        """
        Test for DELETE of existing movie
        """
        response = self.client().delete('/movies/delete/2')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['delete'])

    def test_remove_movie_error_404(self):
        """
        Test for DELETE of existing movie out of range error
        """
        response = self.client().delete('/movies/delete/34009999')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'], False)
        self.assertTrue(data['message'], ['Movie with id 34009999 not found in database'])


if __name__ == '__main__':
    os.environ['DATABASE_URL'] = "postgres@localhost:5432/movies"

    unittest.main()
