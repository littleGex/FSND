import json
from flask import request
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'capstone-movies-gex.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'movies'
CLIENT_ID = 'wQr3MmktwvuGQ8HScfkV6vtsaNE684Lc'


# AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header
'''
Attempt to get the header from the request, raising an AuthError if no header is present.
It attempts to split bearer and the token, raising an AuthError if the header is malformed returning
the token part of the header.
'''


def get_token_auth_header():
    """
    Gets access token from authorisation header.
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorisation header is expected.'
        }, 401)

    parts = auth.split()

    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorisation header must start with "Bearer".'
        }, 401)
    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found'
        }, 401)
    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorisation header must be bearer token.'
        }, 401)

    token = parts[1]
    return token


'''
Check permissions, raising an AuthError if permissions are not included in the payload.
Raise an AuthError if the requested permission string is not in the payload permissions array return true otherwise
'''


def check_permissions(permission, payload):
    """
    Check if pyload contains permission.
    :param permission: For example 'post:actor'
    :param payload: decoded jwt payload
    :return: True if conditions met
    """
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permission not included in JWT'
        }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorised',
            'description': 'Permissions not included'
        }, 403)

    return True


'''
Verify and decode jwt(token) method
The token:
- should be an Auth0 token with key id (kid)
- should verify the token using Auth0 /.well-known/jwks.json
- should decode the payload from the token
- should validate the claims
Returning the decoded payload
'''


def verify_decode_jwt(token):
    """
    Decodes jwt or raises error message.
    :param token: jwt (json web token)
    :return: Decoded jwt
    """
    jsonurl = urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())

    unverified_header = jwt.get_unverified_header(token)

    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorisation malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f'https://{AUTH0_DOMAIN}/'
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)
        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims.  Please check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find appropriate key.'
    }, 400)


'''
Requires authorisation method:
- should use the get_token_auth_header method to get the token
- should use the verify_decode_jwt method to decode the jwt
- should use the check_permissions method validate claims and check the requested permission
Returning the decorator which passes the decoded payload to the decorated method.
'''


def requires_auth(permission=''):
    """
    Authenification wrapper to decorate endpoints.
    :param permission: Requested action i.e. 'post:actor'
    :return: wrapper - decoded jwt to the decorator method.
    """
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except BaseException as e:
                print(e)
                raise AuthError({
                    'code': 'invalid_token',
                    'description': 'Unable to verify token'
                }, 401)

            check_permissions(permission, payload)

            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
