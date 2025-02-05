# Udacity - Full stack developer - Capstone Project

## Content
[Project dependencies](#Project-dependencies) <br>
[Installation and running instructions](#Installation-and-running-instructions) <br>
[Endpoints](#Endpoints) <br>
[Roles](#Roles) <br>
[API Endpoints](#API-Endpoints) <br>
[Authentification](#Authentification)<br>
[Link to app](#Link-to-app)<br>

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
- add/update ```DATABASE_URL``` to environment variables of your system. 
On Unix systems, use ```export DATABASE_URL={username}:{password}@{host}:{port}/{database_name}```
One can use the existing setup shell script to set the main environment settings using on a mac:
- ```bash
  sh setup.sh
  ```
  NOTE:  One should take care with the `DATABASE_URL`
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
There are 3 roles assigned to the application:
- assistant:
  - GET/actors - view all actors
  - GET/movies - view all movies

- director:
  - GET/actors - view all actors
  - GET/movies - view all movies
  - POST/actors - add actor
  - PATCH/actors - modify actor
  - PATCH/movies - modify actor
  - DELETE/actors - remove actor

- producer:
  - GET actors - view all actors
  - GET movies - view all movies
  - POST actors - add actor
  - POST movies - add movie
  - PATCH/actors - modify actor
  - PATCH/movies - modify actor
  - DELETE/actors - remove actor
  - DELETE movies - remove movie

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

## Link to app:
[capstone-20220803](https://capstone-20220803.herokuapp.com/)
