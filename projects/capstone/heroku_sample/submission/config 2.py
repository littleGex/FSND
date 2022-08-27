import os


SECRET_KEY = os.urandom(32)
AUTH0_DOMAIN = 'https://capstone-movies-gex.eu.auth0.com/api/v2/'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'Auth0 Management API'

# Set number of rows from api
ROWS_PER_PAGE = 10
