# encoding: utf-8

from copy import copy
import googleanalytics as ga


class Blueprint(object):
    def __init__(self, description):
        self.raw = description
        self.scope = description.get('scope')
        self.defaults = description.get('defaults')
        self._identity = description.get('identity')
        self._queries = description.get('queries')
    
    @property
    def identity(self):
        data = self._identity
        if data:
            if isinstance(data, ga.utils.basestring):
                return dict(identity=data)
            elif isinstance(data, dict):
                return data
        
        return None
    
    def queries(self, profile):
        base = ga.query.describe(profile, self.defaults)

        queries = []
        for title, description in self._queries.items():
            query = ga.query.refine(base, description)
            query.title = title
            queries.append(query)

        return queries
