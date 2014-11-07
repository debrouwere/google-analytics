from copy import copy
import googleanalytics as ga


def refine_query(query, description):
    for attribute, arguments in description.items():
        if hasattr(query, attribute):
            attribute = getattr(query, attribute)
        else:
            raise ValueError("Unknown query method: " + method)

        if callable(attribute):
            method = attribute
            if isinstance(arguments, dict):
                query = method(**arguments)
            elif isinstance(arguments, list):
                query = method(*arguments)
            else:
                query = method(arguments)
        else:
            setattr(attribute, arguments)
            
    return query

def authenticate(blueprint):
    client = blueprint['client']
    scope = blueprint['scope']
    
    if isinstance(client, basestring):
        profile = ga.authenticate(name=blueprint['client'], **scope)
    elif isinstance(client, dict):
        profile = ga.authenticate(client=client, **scope)
    else:
        raise ValueError("Could not find credentials.")
    
    return profile

def parse(blueprint, profile):
    base = refine_query(profile.query(), blueprint['defaults'])

    queries = []
    for title, description in blueprint['queries'].items():
        query = refine_query(base, description)
        query.title = title
        queries.append(query)

    return queries

