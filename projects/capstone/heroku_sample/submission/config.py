import os


SECRET_KEY = os.urandom(32)
AUTH0_DOMAIN = 'capstone-movies-gex.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'Auth0 Management API'

# Set number of rows from api
ROWS_PER_PAGE = 10
