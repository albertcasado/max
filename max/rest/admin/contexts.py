# -*- coding: utf-8 -*-
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNoContent

from max.oauth2 import oauth2
from max.decorators import MaxResponse, requirePersonActor
from max.MADMax import MADMaxDB, MADMaxCollection
from max.models import Context
from max.rest.utils import searchParams
from max.exceptions import InvalidPermission, Unauthorized, ObjectNotFound
from max.rest.ResourceHandlers import JSONResourceEntity, JSONResourceRoot


@view_config(route_name='contexts', request_method='GET', restricted='Manager')
@MaxResponse
@oauth2(['widgetcli'])
def getContexts(context, request):
    """
    """
    mmdb = MADMaxDB(context.db)
    found_contexts = mmdb.contexts.search({}, flatten=1, **searchParams(request))
    handler = JSONResourceRoot(found_contexts)
    return handler.buildResponse()


@view_config(route_name='context', request_method='DELETE', restricted='Manager')
@MaxResponse
@oauth2(['widgetcli'])
def DeleteContext(context, request):
    """
    """
    mmdb = MADMaxDB(context.db)
    chash = request.matchdict.get('hash', None)
    found_contexts = mmdb.contexts.getItemsByhash(chash)

    if not found_contexts:
        raise ObjectNotFound("There's no context matching this url hash: %s" % chash)

    ctx = found_contexts[0]
    ctx.removeUserSubscriptions()
    ctx.removeActivities(logical=True)
    ctx.delete()
    return HTTPNoContent()


@view_config(route_name='context', request_method='GET', restricted='Manager')
@MaxResponse
@oauth2(['widgetcli'])
def getContext(context, request):
    """
        /contexts/{hash}

        [RESTRICTED] Return a context by its hash.
    """
    mmdb = MADMaxDB(context.db)
    chash = request.matchdict.get('hash', None)
    found_context = mmdb.contexts.getItemsByhash(chash)

    if not found_context:
        raise ObjectNotFound("There's no context matching this url hash: %s" % chash)

    handler = JSONResourceEntity(found_context[0].flatten())
    return handler.buildResponse()


@view_config(route_name='contexts', request_method='POST', restricted='Manager')
@MaxResponse
@oauth2(['widgetcli'])
def addContext(context, request):
    """
        /contexts

        Adds a context.
    """
    request.actor = None

    # Initialize a Context object from the request
    newcontext = Context(request)
    newcontext.fromRequest(request)

    # If we have the _id setted, then the object already existed in the DB,
    # otherwise, proceed to insert it into the DB
    # In both cases, respond with the JSON of the object and the appropiate
    # HTTP Status Code

    if newcontext.get('_id'):
        # Already Exists
        code = 200
    else:
        # New context
        code = 201
        contextid = newcontext.insert()
        newcontext['_id'] = contextid

    handler = JSONResourceEntity(newcontext.flatten(), status_code=code)
    return handler.buildResponse()


@view_config(route_name='context', request_method='PUT', restricted='Manager')
@MaxResponse
@oauth2(['widgetcli'])
def ModifyContext(context, request):
    """
        /contexts/{hash}

        Modify the given context.
    """
    chash = request.matchdict['hash']
    contexts = MADMaxCollection(context.db.contexts)
    maxcontext = contexts.getItemsByhash(chash)
    if maxcontext:
        maxcontext = maxcontext[0]
    else:
        raise ObjectNotFound('Unknown context: %s' % chash)

    properties = maxcontext.getMutablePropertiesFromRequest(request)
    maxcontext.modifyContext(properties)
    maxcontext.updateUsersSubscriptions()
    handler = JSONResourceEntity(maxcontext.flatten())
    return handler.buildResponse()


@view_config(route_name='context_user_permission', request_method='PUT', restricted='Manager')
@MaxResponse
@requirePersonActor(force_own=False)
@oauth2(['widgetcli'])
def grantPermissionOnContext(context, request):
    """ [RESTRICTED]
    """
    permission = request.matchdict.get('permission', None)
    if permission not in ['read', 'write', 'subscribe', 'invite']:
        raise InvalidPermission("There's not any permission named '%s'" % permission)

    chash = request.matchdict.get('hash', None)
    subscription = None
    pointer = 0
    while subscription is None and pointer < len(request.actor.subscribedTo['items']):
        if request.actor.subscribedTo['items'][pointer]['hash'] == chash:
            subscription = request.actor.subscribedTo['items'][pointer]
        pointer += 1

    if not subscription:
        raise Unauthorized("You can't set permissions on a context where you are not subscribed")

    #If we reach here, we are subscribed to a context and ready to set the permission

    permissions = subscription['permissions']
    if permission in permissions:
        #Already have the permission
        code = 200
    else:
        #Assign the permission
        code = 201
        request.actor.grantPermission(subscription, permission)
        permissions.append(permission)

    handler = JSONResourceEntity(subscription, status_code=code)
    return handler.buildResponse()


@view_config(route_name='context_user_permission', request_method='DELETE', restricted='Manager')
@MaxResponse
@requirePersonActor(force_own=False)
@oauth2(['widgetcli'])
def revokePermissionOnContext(context, request):
    """ [RESTRICTED]
    """
    permission = request.matchdict.get('permission', None)
    if permission not in ['read', 'write', 'subscribe', 'invite']:
        raise InvalidPermission("There's not any permission named '%s'" % permission)

    chash = request.matchdict.get('hash', None)
    subscription = None
    pointer = 0
    while subscription is None and pointer < len(request.actor.subscribedTo['items']):
        if request.actor.subscribedTo['items'][pointer]['hash'] == chash:
            subscription = request.actor.subscribedTo['items'][pointer]
        pointer += 1

    if not subscription:
        raise Unauthorized("You can't remove permissions on a context where you are not subscribed")

    #If we reach here, we are subscribed to a context and ready to remove the permission

    code = 200
    permissions = subscription['permissions']
    if permission in permissions:
        #We have the permission, let's delete it
        request.actor.revokePermission(subscription, permission)
        subscription['permissions'] = [a for a in permissions if permission != a]

    handler = JSONResourceEntity(subscription, status_code=code)
    return handler.buildResponse()
