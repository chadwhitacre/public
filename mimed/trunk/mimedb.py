#!/usr/bin/env python
"""This module defines a subclass of ServerProxy for working with MIMEdb's.
"""
from xmlrpclib import ServerProxy

class _MethodWithKey:
    """Represent a callable on a MIMEdb server.
    """

    def __init__(self, method, key):
        """Takes a callable, and a string.
        """
        self.__method = method
        self.__key = key

    def __call__(self, *args):
        """Override to add the API key to the call.
        """
        args = (key,) + args
        return self.__method(*args)


class MIMEdb:
    """Represent a connection to a MIMEdb server.

    Once instantiated, it exposes the MIMEdb API, transparently inserting your
    API key on each request.

    """

    def __init__(self, uri, key):
        """Takes the URI of the MIMEdb server, and an API key.
        """
        self.__proxy = ServerProxy(uri)
        self.__key = key

    def __getattr__(self, name):
        base_method = getattr(self.__proxy, name)
        return _MethodWithKey(base_method, self.__key)



# test
# ====

if __name__ == '__main__':
    url = 'http://philip:5370/'
    key = '8b0e50efb501438fa42077a360084d6a'
    db = MIMEdb(url, key)
    db.echo()
    from pprint import pprint as pp; import code; code.interact(local=locals())