#!/usr/bin/env python
"""This module defines objects for working with MIMEdb's.
"""
from xmlrpclib import ServerProxy


CLUSTER_API = ( 'create'
              , 'drop'
              , 'dump'
              , 'load'
               )
DB_API = ( 'all'
         , 'find'
         , 'headers'
         , 'remove'
         , 'replace'
         , 'retrieve'
         , 'single'
         , 'store'
          )


class _MethodWithToken:
    """Represent a callable on an XMLRPC server that requires an auth token.
    """

    def __init__(self, method, token):
        """Takes a callable, and a string.
        """
        self.__method = method
        self.__token = token

    def __call__(self, *args):
        """Override to add the auth token as the first argument to the call.
        """
        args = (self.__token,) + args
        return self.__method(*args)


class Cluster:
    """Represent a MIMEdb cluster.
    """

    def __init__(self, uri, key):
        """Takes the URI of the MIMEdb server, and a master key.
        """
        self.__proxy = ServerProxy(uri)
        self.__key = key

    def __getattr__(self, attr):
        if attr in DB_API:
            raise AttributeError("Please use a db object.")
        base_method = getattr(self.__proxy, attr)
        return _MethodWithToken(base_method, self.__key)


class DB:
    """Represent a MIMEdb database.
    """

    def __init__(self, uri, name):
        """Takes the URI of the MIMEdb server, and a database name.
        """
        self.__proxy = ServerProxy(uri)
        self.__name = name

    def __getattr__(self, attr):
        if attr in CLUSTER_API:
            raise AttributeError("Please use a cluster object.")
        base_method = getattr(self.__proxy, attr)
        return _MethodWithToken(base_method, self.__name)



# test
# ====

if __name__ == '__main__':
    url = 'http://philip:5370/'

    raw = ServerProxy(url)
    print raw.echo('Greetings, program!')

    key = 'a6d9b24e-496c-4255-928b-987995ac88b5'
    cluster = Cluster(url, key)

    name = cluster.create()
    print name

    from pprint import pprint as pp; import code; code.interact(local=locals())