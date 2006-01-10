#!/usr/bin/env python
"""This module defines a subclass of ServerProxy for working with MIMEdb's.
"""
from xmlrpclib import ServerProxy, Error

class _MethodWithKey:

    def __init__(self, method, key):
        self.__method = method
        self.__key = key

    def __call__(self, *args):
        args = (key,) + args
        import pdb; pdb.set_trace()
        return self.__method(*args)


class MIMEdb:

    def __init__(self, uri, key):
        self.__proxy = ServerProxy(uri)
        self.__key = key

    def __getattr__(self, name):
        base_method = getattr(self.__proxy, name)
        return _MethodWithKey(base_method, self.__key)



if __name__ == '__main__':
    url = 'http://philip:5370/'
    key = '8b0e50efb501438fa42077a360084d6a'
    db = MIMEdb(url, key)
    db.echo()
    from pprint import pprint as pp; import code; code.interact(local=locals())