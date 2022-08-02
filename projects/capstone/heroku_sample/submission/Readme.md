# Udacity - Full stack developer - Capstone Project

## Content
[Project dependencies](#Project-dependencies) <br>
[Installation and running instructions](#Installation-and-running-instructions) <br>
[Endpoints](#Endpoints) <br>
[Roles](#Roles) <br>
[API Endpoints](#API-Endpoints) <br>
[Authentification](#Authentification)<br>

## Project dependencies
- FLASK
- SQLAlchemy
- Heroku

## Installation and running instructions
- Clone project to directory of your choice.
- `cd` in to directory where the app files are located.
- Create virtual environment.  Instructions for setting up a virtual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)
- Install project requirements:
  ```bash
  $ pip install -r requirements.txt
  ```
- add ```DATABASE_URL``` to environment variables of your system. 
On Unix systems, use ```export DATABASE_URL={username}:{password}@{host}:{port}/{database_name}```
- run 
  ```bash
  $ export FLASK_APP=app.py
  ```
- type 
  ```bash
  $ flask run
  ``` 
  in terminal window.

## Endpoints for /actors and /movies
- GET /actors and /movies
- POST /actors and /movies
- PATCH /actors and /movies
- DELETE /actors and /movies

## Roles
- Contributor
  - GET 
  - POST
  - PATCH

- Admin
  - GET
  - POST
  - PATCH
  - DELETE

## API Endpoints

### GET Endpoints
Displays all movies/actors listed in the database.
Example response:
```
{
    "movies": [
        {
            "id": 1,
            "name": 2022,
            "release_date": "Horrid Henri the movie"
        },
    ],
    "success": true
}
```

### POST Endpoints
Creates a new movie/actor listed in the database.
Example response:
```
{
    "movie_id": 2,
    "success": true
}
```

### PATCH Endpoints
Updates a movie/actor using the movie_id/actor_id and the amended attribute data.
Example response:
```
{
    "actor_id": 2,
    "success": true
}
```

### DELETE Endpoints
Deletes a movie/actor from the database using the movie_id/actor_id.
Example response:
```
{
    "delete": 2,
    "success": true
}
```

## Authentification
The API endpoints are decorated with Auth0 permissions.

### Existing Roles:
There are 2 roles set up for the purposes of using this application.

1. Admin
   - GET /actor and /movies: Can see all actors/movies
   - POST /actor and /movies: Can create new actors/movies
   - PATCH /actor and /movies: Can update actors/movies in the database
   - DELETE /actor and /movies: Delete an actors/movies from the database
2. Contributor
   - GET /actor and /movies: Can see all actors/movies
   - POST /actor and /movies: Can create new actors/movies
   - PATCH /actor and /movies: Can update actors/movies in the database

