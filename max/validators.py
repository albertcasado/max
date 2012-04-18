import re
from max.regex import RE_VALID_HASHTAG
from max.regex import RE_VALID_TWITTER_USERNAME

from max.exceptions import MissingField, ObjectNotSupported, ObjectNotFound, DuplicatedItemError, UnknownUserError, Unauthorized, InvalidSearchParams, InvalidPermission, ValidationError
from max.exceptions import JSONHTTPUnauthorized, JSONHTTPBadRequest
from pyramid.httpexceptions import HTTPInternalServerError
from bson.errors import InvalidId
from max.MADMax import MADMaxDB
from max.resources import Root
from max.rest.resources import RESOURCES
from max.rest.utils import isOauth, isBasic, getUsernameFromXOAuth, getUsernameFromURI, getUsernameFromPOSTBody, getUrlHashFromURI
from max.models import User, Context

"""
    Validators accept ONE parameter containing the value of the field to be validated
    Validators respond with a 2-element tuple (success, message)

    - success MUST be a boolean indicating were the validation succeded or not
    - message MUST be a message indicating a description of why the validation didn't succeded
"""


def isValidHashtag(text, message='Invalid hashtag'):
    """
        Is a valid hashtag?
        See max.regex for more info on the regex
    """
    match = re.match(RE_VALID_HASHTAG, text)
    success = match is not None
    return (success, message)


def isValidTwitterUsername(text, message='Invalid twitter username'):
    """
        Is a valid twitter username?
        See max.regex for more info on the regex
    """
    match = re.match(RE_VALID_TWITTER_USERNAME, text)
    success = match is not None
    return (success, message)


def MaxRequest(request):

    actor = None
    db = request.registry.max_store
    mmdb = MADMaxDB(db)
    admin_ws = [('admin_users', 'GET'), ('admin_activities', 'GET'), ('admin_contexts', 'GET'), ('admin_user', 'DELETE'), ('admin_activity', 'DELETE'), ('admin_context', 'DELETE')]
    allowed_ws_without_username = admin_ws + [('contexts', 'POST'), ('context', 'GET'), ('context', 'PUT'), ('context', 'DELETE')]
    allowed_ws_without_actor = [('user', 'POST')] + allowed_ws_without_username

    # If Oauth authorization is used, The actor that will perform the actions will be
    # the one specified in oauth headers, so for routes that match username
    # parameter in the URI, we only allow this username to be the same as oauth username
    # for validation purposes. Same thing from actor defined in post request body
    if isOauth(request):
        oauth_username = getUsernameFromXOAuth(request)
        rest_username = getUsernameFromURI(request)

        # XXX TODO Define cases where oauth_username MAY/CAN be different
        # to rest_username/post_username
        if rest_username and oauth_username != rest_username:
            raise Unauthorized, "You don't have permission to access %s resources" % (rest_username)
        post_username = getUsernameFromPOSTBody(request)
        if post_username and oauth_username != post_username:
            raise Unauthorized, "You don't have permission to access %s resources" % (post_username)
        # If user validation is successfull, try to load the oauth User from DB
        try:
            actor = mmdb.users.getItemsByusername(oauth_username)[0]
        except:
            request.errors.add('url', 'UnknownUserError', 'Unknown user "%s"' % oauth_username)

    # If Basic auth is used, actor username can be any username, as we are
    # impersonating him. We will search for this username in several places:

    elif isBasic(request):
        actorType = 'person'
        #Try to get the username from the REST URI
        username = getUsernameFromURI(request)
        #Try to get the username from the POST body
        if not username and request.method == 'POST':
            username = getUsernameFromPOSTBody(request)

        # If no actor specified anywhere, raise an error
        # except when allowed not having a username
        # or when adding a context activity
        if not username:
            if (request.matched_route.name, request.method) == ('admin_context_activities', 'POST'):
                contexthash = getUrlHashFromURI(request)
                actorType = 'context'
            elif not ((request.matched_route.name, request.method) in allowed_ws_without_username):
                request.errors.add('url', 'UnknownUserError', 'No user specified as actor')

        # Raise only if we are NOT adding a user or a context. These are the only cases
        # Were we permit not specifing an ator:
        #   - Creating a user, beacause the user doesn't exists
        #   - Creating a context, because context is actor-agnostic
        #   - Getting a context, because context is actor-agnostic

        #try to load the user actor from DB
        if actorType == 'person':
            try:
                actor = mmdb.users.getItemsByusername(username)[0]
            except:
                if not ((request.matched_route.name, request.method) in allowed_ws_without_actor):
                    raise UnknownUserError, 'Unknown actor identified by username: %s' % username

        #try to load the context actor from DB
        if actorType == 'context':
            try:
                actor = mmdb.contexts.getItemsByurlHash(contexthash)[0]
            except:
                raise UnknownUserError, 'Unknown actor identified by context : %s' % contexthash

    # Raise an error if no authentication present
    else:
        raise JSONHTTPUnauthorized(error=dict(error='Unauthorized', error_description="There are no supported authentication methods present in this request"))

    # If we arrive at this point, we have a valid user in actor.
    # (Except in the case of a new users explained 10 lines up)
    # Define a callable to prepare the actor in order to inject it in the request
    def getActor(request):
        try:
            if isinstance(actor, User):
                actor.setdefault('displayName', actor['username'])
            if isinstance(actor, Context):
                actor.setdefault('displayName', actor['url'])
            return actor
        except:
            return None

    request.set_property(getActor, name='actor', reify=True)



def MaxResponse(response):

    # Handle exceptions throwed in the process of executing the REST method and
    # issue proper status code with message

    try:
        return response
    except InvalidId, message:
        return JSONHTTPBadRequest(error=dict(error=InvalidId.__name__, error_description=message.value))
    except ObjectNotSupported, message:
        return JSONHTTPBadRequest(error=dict(error=ObjectNotSupported.__name__, error_description=message.value))
    except ObjectNotFound, message:
        return JSONHTTPBadRequest(error=dict(error=ObjectNotFound.__name__, error_description=message.value))
    except MissingField, message:
        return JSONHTTPBadRequest(error=dict(error=MissingField.__name__, error_description=message.value))
    except DuplicatedItemError, message:
        return JSONHTTPBadRequest(error=dict(error=DuplicatedItemError.__name__, error_description=message.value))
    except UnknownUserError, message:
        return JSONHTTPBadRequest(error=dict(error=UnknownUserError.__name__, error_description=message.value))
    except Unauthorized, message:
        return JSONHTTPUnauthorized(error=dict(error=Unauthorized.__name__, error_description=message.value))
    except InvalidSearchParams, message:
        return JSONHTTPBadRequest(error=dict(error=InvalidSearchParams.__name__, error_description=message.value))
    except InvalidPermission, message:
        return JSONHTTPBadRequest(error=dict(error=InvalidPermission.__name__, error_description=message.value))
    except ValidationError, message:
        return JSONHTTPBadRequest(error=dict(error=ValidationError.__name__, error_description=message.value))

    # JSON decode error????
    except ValueError:
        return JSONHTTPBadRequest(error=dict(error='JSONDecodeError', error_description='Invalid JSON data found on requests body'))
    except:
        return HTTPInternalServerError()
    else:
        try:
            # Don't cache by default, get configuration from resource if any
            route_cache_settings = RESOURCES.get(request.matched_route.name).get('cache', 'must-revalidate, max-age=0, no-cache, no-store')
            response.headers.update({'Cache-Control': route_cache_settings})
        except:
            pass
        return response
