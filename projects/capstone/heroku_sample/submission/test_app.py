import json
import os
import unittest
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from models import setup_db
from datetime import date


rbac_tokens = {
    'director': "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlhJNmJxWlg2VjVxQlFrYWFLbkg0biJ9.eyJpc3MiOiJodHRwczovL2NhcHN0b25lLW1vdmllcy1nZXguZXUuYXV0aDAuY29tLyIsInN1YiI6IlptT1pkek1HVExnYno2UUlzbVpWdzJHUjBLamQ3Zk5NQGNsaWVudHMiLCJhdWQiOiJhc3Npc3RhbnQiLCJpYXQiOjE2NjEzNzI1MDgsImV4cCI6MTY2MTQ1ODkwOCwiYXpwIjoiWm1PWmR6TUdUTGdiejZRSXNtWlZ3MkdSMEtqZDdmTk0iLCJzY29wZSI6InJlYWQ6YWN0b3JzIHJlYWQ6bW92aWVzIiwiZ3R5IjoiY2xpZW50LWNyZWRlbnRpYWxzIiwicGVybWlzc2lvbnMiOlsicmVhZDphY3RvcnMiLCJyZWFkOm1vdmllcyJdfQ.RGBVEE6s5WX9uikIoR_Ttp3x_njs3W7Q868ZDoR5Tzgh_hVSs0gH14dQ2KG18fufjpp8mdkjhepnS_KFtcxrBQJ7nhp9BlUNwmRMy3K3akc6vMlLL4LCY6iIKagnVMMJ3gJv5Uw0x5cgMYyXXMSROmSjIECCx3qPsGWnr35709EI9oWhMigq9tXncs9po-PfHqmYah6Y_ugTw8k99LaeThJPG5f_jSP-jyDgey1R4e-R9TpnI-IwF2s80g0HvmBcwFcKxTe3P6uSu7YI--sCA8USgvOBPuHda3o5CrNL7WJbNcp9-QuJNTC6lDJmepfmA5QG0Vs4ajTO7jlg0lhewA",
    'assistant': "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlhJNmJxWlg2VjVxQlFrYWFLbkg0biJ9.eyJpc3MiOiJodHRwczovL2NhcHN0b25lLW1vdmllcy1nZXguZXUuYXV0aDAuY29tLyIsInN1YiI6IkRkTlhuNExNcjhmbkZCbE5tMjRXamFnZXI0ekV6N2FXQGNsaWVudHMiLCJhdWQiOiJkaXJlY3RvciIsImlhdCI6MTY2MTM3Mjg5OCwiZXhwIjoxNjYxNDU5Mjk4LCJhenAiOiJEZE5YbjRMTXI4Zm5GQmxObTI0V2phZ2VyNHpFejdhVyIsInNjb3BlIjoicmVhZDphY3RvcnMgcmVhZDptb3ZpZXMgcG9zdDphY3RvcnMgcGF0Y2g6YWN0b3JzIHBhdGNoOm1vdmllcyBkZWxldGU6YWN0b3IiLCJndHkiOiJjbGllbnQtY3JlZGVudGlhbHMiLCJwZXJtaXNzaW9ucyI6WyJyZWFkOmFjdG9ycyIsInJlYWQ6bW92aWVzIiwicG9zdDphY3RvcnMiLCJwYXRjaDphY3RvcnMiLCJwYXRjaDptb3ZpZXMiLCJkZWxldGU6YWN0b3IiXX0.dWnkrCKFkDMVoKcyS5Nl_7Y8EwnvdAyL_wPEJYeCjyXw3V8eQDQiT0RHtufXhFLeww7oj79MzLyGiX1RXd6dIKIHhYzXpg9WNOWzn2NARGH-PqxePEp2pvq-EaBV_Qceox_XV8oeSXM9z0kITSsPDZyJR2o0AqGaK2xZo8GBIugqaF8WFRWG9WvPJSuwBkTk8q5l8ntJaJ-9ezQ4cZZjH7xIkZzam0obgN8dWdsAujeyTJXJp2WgNbTBh-lR9HcJ9iouiXywgVA_SChOjRHecSYWZqxOSLD443T-qVbkUfIj7dWzzrcJh_8c9ftcsZtCMeyKYfwh4isvHDvzzpNiEw",
    'producer': "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlhJNmJxWlg2VjVxQlFrYWFLbkg0biJ9.eyJpc3MiOiJodHRwczovL2NhcHN0b25lLW1vdmllcy1nZXguZXUuYXV0aDAuY29tLyIsInN1YiI6Ik1ucmI0TDZlZzI0d1ZKd2cyQU9lZU9FYjc4S2ZrTTB0QGNsaWVudHMiLCJhdWQiOiJwcm9kdWNlciIsImlhdCI6MTY2MTM3MzIxNywiZXhwIjoxNjYxNDU5NjE3LCJhenAiOiJNbnJiNEw2ZWcyNHdWSndnMkFPZWVPRWI3OEtma00wdCIsInNjb3BlIjoicmVhZDphY3RvcnMgcmVhZDptb3ZpZXMgcG9zdDphY3RvcnMgcG9zdDptb3ZpZXMgcGF0Y2g6YWN0b3JzIHBhdGNoOm1vdmllcyBkZWxldGU6YWN0b3IgZGVsZXRlOm1vdmllIiwiZ3R5IjoiY2xpZW50LWNyZWRlbnRpYWxzIiwicGVybWlzc2lvbnMiOlsicmVhZDphY3RvcnMiLCJyZWFkOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwicG9zdDptb3ZpZXMiLCJwYXRjaDphY3RvcnMiLCJwYXRjaDptb3ZpZXMiLCJkZWxldGU6YWN0b3IiLCJkZWxldGU6bW92aWUiXX0.HlG_nZhsFdaWFtr5UKjqyNGcOXbZAqcgchfAAL1NQ8DdxpNztsXd7AJjgwVXZfu7Hs7Wurh4SH2qqbBWbvpzfghAcrOzHVIWZ9V6nwRoSXXKPLgg-OuX0UK3hNUmiovHZGbhcSD1wDXjLJIm5tadgODuPDS6X27AoZkRW9gn04--Azv_Jw4tq18L5qGBg69ce6i2g4G1ex2j8Y4-MLCR5POvSwBNnGpgS7woilKyKK-8qx2wO3Anrt6VYn8k_OROtTkx0P3ze8mVkTgtwTVDSws37WEzXsZRae8sAxsMgQ6ZLILxWGNX0it67zuwb0cATi9VIbX-BZEvUBHtM-YveQ"
}

headers_assistant = {'Authorisation': rbac_tokens['assistant']}
headers_director = {'Authorisation': rbac_tokens['director']}
headers_producer = {'Authorisation': rbac_tokens['producer']}


class AppTestCase(unittest.TestCase):
    def setUp(self):
        """
        Test variable definition and app initialisation
        """
        self.app = create_app()
        self.client = self.app.test_client()
        self.database = os.environ['DATABASE_2_URL']
        setup_db(self.app, self.database)
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # Create database tables
            self.db.create_all()

    # Run Actor testing
    # Test /actor GET
    def test_get_actors_error_401(self):
        """
        Test for authorisation using GET method for actors.
        """
        response = self.client().get('/actors?page=1')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertFalse(data['success'], False)
        self.assertEqual(data['message'], 'Authorisation header is expected')

    def test_get_actors(self):
        """
        Test for GET all actors
        """
        response = self.client().get('/actors?page=1', headers=headers_assistant)

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['actors']) > 0)

    def test_get_actors_error_404(self):
        """
        Test for GET all actors error
        """
        response = self.client().get('/actors?page=1938462829', headers=headers_director)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'], False)
        self.assertEqual(data['message'], 'Actors found in database')

    # Test /actors/new POST
    def test_add_actors_error_401(self):
        """
        Test for authorisation using POST method for actors.
        """
        create_actor_json = {
            'name': 'Bengal Tiger',
            'gender': 'Male',
            'age': 23
        }
        response = self.client().post('/actors', json=create_actor_json)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertFalse(data['success'], False)
        self.assertTrue(data['message'], 'Authorisation header is expected')

    def test_add_actor(self):
        """
        Test for POST new actor
        """
        create_actor_json = {
            'name': 'Dommy Dom',
            'age': 7,
            'gender': 'male'
        }
        response = self.client().post('/actors', json=create_actor_json, headers=headers_director)
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
        response = self.client().post('/actors', json=create_actor_json, headers=headers_director)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertFalse(data['success'], False)
        self.assertTrue(data['message'], 'No name given.')

    # Test modify actor PATCH
    def test_mod_actor_error_401(self):
        """
        Test for authorisation using PATCH method for actors.
        """
        edit_actor_json = {
            'age': 76
        }
        response = self.client().patch('/actors/2', json=edit_actor_json, headers=headers_assistant)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'Permission not found')

    def test_mod_actor(self):
        """
        Test for PATCH of existing actor
        """
        edit_actor_json = {
            'age': 21
        }

        response = self.client().patch('/actor/1', json=edit_actor_json, headers=headers_director)
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
        response = self.client().patch('/actors/3400', json=edit_actor_json, headers=headers_director)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'], False)
        self.assertTrue(data['message'], 'Actor with id 3400 not found in database')

    # Test delete actor DELETE
    def test_remove_actor_error_401(self):
        """
        Test for authorisation using PATCH method for actors.
        """
        response = self.client().delete('/actors/34009999')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertFalse(data['success'], False)
        self.assertTrue(data['message'], 'Authorisation header is expected')

    def test_remove_actor(self):
        """
        Test for DELETE of existing actor
        """
        response = self.client().delete('/actors/2', headers=headers_director)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['delete'])

    def test_remove_actor_error_404(self):
        """
        Test for DELETE of existing movie out of range error
        """
        response = self.client().delete('/actors/34009999', headers=headers_director)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'], False)
        self.assertTrue(data['message'], 'Actor with id 34009999 not found in database')

    # Run Movie testing
    # Test /movies GET
    def test_get_movies_error_401(self):
        """
        Test for authorisation using GET method.
        """
        response = self.client().get('/movies?page=1938462829')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertFalse(data['success'], False)
        self.assertEqual(data['message'], 'Authorisation header is expected')

    def test_get_movies(self):
        """
        Test for GET all movies
        """
        response = self.client().get('/movies?page=1', headers=headers_director)

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['movies']) > 0)

    def test_get_movies_error_404(self):
        """
        Test for GET all movies error
        """
        response = self.client().get('/movies?page=1938462829', headers=headers_director)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'], False)
        self.assertEqual(data['message'], 'No movies found in database')

    # Test /movies/new POST
    def test_add_movie_error_401(self):
        """
        Test for authorisation using the POST method for movies.
        """


    def test_add_movie(self):
        """
        Test for POST new movie
        """
        create_movie_json = {
            'title': 'Horrid Henri the movie',
            'release_date': date.today()
        }
        response = self.client().post('/movies', json=create_movie_json, headers=headers_director)
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
        response = self.client().post('/movies', json=create_movie_json, headers=headers_director)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertFalse(data['success'], False)
        self.assertTrue(data['message'], 'No title given.')

    # Test modify movie PATCH
    def test_mod_movie_error_401(self):
        """
        Test for authorisation using PATCH method for movies.
        """
        edit_movie_json = {
            'release_date': date.today()
        }
        response = self.client().patch('/movies/3400', json=edit_movie_json)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertFalse(data['success'], False)
        self.assertTrue(data['message'], 'Authorisation header expected')

    def test_mod_movie(self):
        """
        Test for PATCH of existing movie
        """
        edit_movie_json = {
            'release_date': date.today()
        }

        response = self.client().patch('/movie/1', json=edit_movie_json, headers=headers_director)
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
        response = self.client().patch('/movies/3400', json=edit_movie_json, headers=headers_director)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'], False)
        self.assertTrue(data['message'], 'Movie with id 3400 not found in database')

    # Test delete movie DELETE
    def test_remove_movie_error_401(self):
        """
        Test for authorisation using DELETE methog for movies.
        """
        response = self.client().delete('/movies/34009999', headers=headers_assistant)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertFalse(data['success'], False)
        self.assertTrue(data['message'], 'Permissions not found')

    def test_remove_movie(self):
        """
        Test for DELETE of existing movie
        """
        response = self.client().delete('/movies/2', headers=headers_director)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['delete'])

    def test_remove_movie_error_404(self):
        """
        Test for DELETE of existing movie out of range error
        """
        response = self.client().delete('/movies/34009999', headers=headers_director)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'], False)
        self.assertTrue(data['message'], 'Movie with id 34009999 not found in database')


if __name__ == '__main__':
    os.environ['DATABASE_URL'] = "postgres@localhost:5432/movies"

    unittest.main()
