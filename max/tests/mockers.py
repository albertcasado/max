from hashlib import sha1
# -*- coding: utf-8 -*-
# ===============================================================
# Format com deurien estar guardades les dades a la base de dades
# ===============================================================

# Un usuari de demo1
demouser1 = {
    'username': 'victor',
    'url': 'http://max.upc.edu/profiles/victor',
    'objectType': 'person',
    'following': {
        'totalItems': 0,
        'items': []
    },
    'subscribedTo': {
        'totalItems': 0,
        'items': []
    }
}

# Un usuari de demo2
demouser2 = {
    'username': 'javier',
    'url': 'http://max.upc.edu/profiles/javier',
    'objectType': 'person',
    'following': {
        'totalItems': 0,
        'items': []
    },
    'subscribedTo': {
        'totalItems': 0,
        'items': []
    }
}

# Una activity de demo
demostatus = {
    "actor": {
        "objectType": "person",
        "username": "victor"
    },
    "verb": "post",
    "object": {
        "objectType": "note",
        "content": "Avui sera un gran dia!"
    },
    "published": "2011-08-31T13:45:55Z"
}

demostatus_with_context = {
    "actor": {
        "objectType": "person",
        "username": "victor"
    },
    "verb": "post",
    "object": {
        "objectType": "note",
        "content": "[AC] Activitat amb contexte"
    },
    "target": {
        "objectType": "service",
        "username": "Introduccio als computadors",
        "url": "http://atenea.upc.edu/introcomp"
    },
    "published": "2011-08-31T13:45:55Z"
}

# =============================================================================
# Format dels requests que es fa als web services REST, es a dir, el que rep el
# web service com a arguments
# =============================================================================



create_context = {

    'url': 'http://atenea.upc.edu',
    'displayName': 'Atenea',
}


create_context_full = {

    'url': 'http://atenea.upc.edu',
    'displayName': 'Atenea',
    'twitterHashtag': 'atenea',
    'twitterUsername': 'atenaupc',
}

create_context_private_rw = {

    'url': 'http://atenea.upc.edu',
    'displayName': 'Atenea',
    'permissions': {'read':'subscribed',
                    'write':'subscribed',
                    'join':'restricted',
                    'invite':'restricted'}
}

create_context_private_r = {

    'url': 'http://atenea.upc.edu',
    'displayName': 'Atenea',
    'permissions': {'read':'subscribed',
                    'write':'restricted',
                    'join':'restricted',
                    'invite':'restricted'}

}

create_contextA = {

    'url': 'http://atenea.upc.edu/A',
    'displayName': 'Atenea A',
}

create_contextB = {

    'url': 'http://atenea.upc.edu/B',
    'displayName': 'Atenea B',
}


# Revisat i actualitzat
subscribe_context = {
    "object": {
        "objectType": "context",
        "url": create_context['url'],
        'displayName': create_context['displayName']       #displayName not needed, only for assertEquals comparison purposes
    }
}

# Revisat i actualitzat
subscribe_contextA = {
    "object": {
        "objectType": "context",
        "url": create_contextA['url'],
        'displayName': create_contextA['displayName']       #displayName not needed, only for assertEquals comparison purposes
    }
}

# Revisat i actualitzat
subscribe_contextB = {
    "object": {
        "objectType": "context",
        "url": create_contextB['url'],
        'displayName': create_contextB['displayName']       #displayName not needed, only for assertEquals comparison purposes
    }
}

# Un usuari crea una activitat de canvi d'estat
# Revisat i actualitzat
user_status = {
    "object": {
        "objectType": "note",
        "content": "<p>[A] Testejant la creació d'un canvi d'estatus</p>"
    },
}

user_status_context_with_hashtag = {
    "contexts": [
        subscribe_context['object']['url']
    ],
    "object": {
        "objectType": "note",
        "content": "<p>[A] Testejant la creació d'un #canvi d'estatus</p>"
    },
}


user_status_context = {
    "contexts": [
        subscribe_context['object']['url']
    ],
    "object": {
        "objectType": "note",
        "content": "<p>[A] Testejant la creació d'un canvi d'estatus</p>"
    },
}


user_status_context_generator = {
    "contexts": [
        subscribe_context['object']['url']
    ],
    "object": {
        "objectType": "note",
        "content": "<p>[A] Testejant la creació d'un canvi d'estatus</p>"
    },
    "generator": "Twitter"
}


user_status_contextA = {
    "contexts": [
        subscribe_contextA['object']['url']
    ],
    "object": {
        "objectType": "note",
        "content": "<p>[A] Testejant la creació d'un canvi d'estatus</p>"
    },
}

user_status_contextB = {
    "contexts": [
        subscribe_contextB['object']['url']
    ],
    "object": {
        "objectType": "note",
        "content": "<p>[A] Testejant la creació d'un canvi d'estatus</p>"
    },
}

user_status_contextAB = {
    "contexts": [
        subscribe_contextA['object']['url'],
        subscribe_contextB['object']['url'],
    ],
    "object": {
        "objectType": "note",
        "content": "<p>[A] Testejant la creació d'un canvi d'estatus</p>"
    },
}

context_query = {
    "context": sha1(subscribe_context['object']['url']).hexdigest()
}

context_query_kw_search = {
    "context": sha1(subscribe_context['object']['url']).hexdigest(),
    "keyword": ['Testejant','creació']
}

context_query_author_search = {
    "context": sha1(subscribe_context['object']['url']).hexdigest(),
    "author": 'messi'
}


context_queryA = {
"context": sha1(subscribe_contextA['object']['url']).hexdigest()}


# Un usuari crea un comentari
user_comment = {
    "object": {
        "objectType": "comment",
        "content": "<p>[C] Testejant un comentari nou a una activitat</p>"
    }
}

user_comment_with_hashtag = {
    "object": {
        "objectType": "comment",
        "content": "<p>[C] Testejant un #comentari #nou a una activitat</p>"
    }
}

follow = {
    "actor": {
        "objectType": "person",
        "username": "victor"
    },
    "verb": "follow",
    "object": {
        "objectType": "person",
        "username": "javier"
    },
}

unfollow = {
    "actor": {
        "objectType": "person",
        "id": "4e6e1243aceee91143000000",
        "username": "victor"
    },
    "verb": "unfollow",
    "object": {
        "objectType": "person",
        "id": "4e6e1243aceee91143000001",
        "username": "javier"
    },
}



unfollow_context = {
        "actor": {
            "objectType": "person",
            "id": "4e6e1243aceee91143000000",
            "username": "victor"
        },
        "verb": "unfollow",
        "object": {
            "objectType": "service",
            "username": "Introduccio als computadors",
            "url": "http://atenea.upc.edu/introcomp"
        },
    }

like = {
        "actor": {
            "objectType": "person",
            "id": "4e6e1243aceee91143000000",
            "username": "javier"
        },
        "verb": "like",
        "object": {
            "objectType": "activity",
            "id": "4e707f80aceee94f49000002"
        },
    }

share = {
    "actor": {
        "objectType": "person",
        "id": "4e6e1243aceee91143000000",
        "username": "javier"
    },
    "verb": "share",
    "object": {
        "objectType": "activity",
        "id": "4e6eefc5aceee9210d000004",
    },
  }
