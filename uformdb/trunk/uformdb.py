"""

This is the main uformdb class. It moves uforms between storage and application
context.

    >>> udb = uformdb(root = 'testdb')
    >>> u = uform({'foo': 'bar'})
    >>> u
    {'foo': 'bar'}
    >>> udb.save(u)
    >>> u2 = udb.load(u.uuid)
    >>> u2
    {'foo': 'bar'}

Now what we need is a way to declare schemata, and instantiate those schemata in
uforms. Then we would have adaptors that transform data for various outputs.

How does this all relate to RDF/SW?

"""

import os
from os.path import join, isfile, exists
import cPickle
from uform import uform

class uformdb:

    def __init__(self, root='uforms'):
        self.root = os.path.abspath(root)

    def save(self, uf):
        """ given a uform, write it to disk """
        path = join(self.root, uf.uuid)
        f = file(path,'w')
        cPickle.dump(uf,f)
        f.close()

    def load(self, uuid):
        """ given a uuid, return a uform """
        path = join(self.root, uuid)
        if isfile(path):
            # first try to get it from disk
            f = file(path)
            uf = cPickle.load(f)
            return uf
        else:
            # if it doesn't exist create it
            nuform = uform(uuid=uuid)
            self.save(nuform)
            self.load(nuform.uuid)


def _test():
    import doctest, uformdb
    return doctest.testmod(uformdb)

if __name__ == "__main__":

    # setup
    if not exists('testdb'):
        os.mkdir('testdb')

    _test()

    # teardown
    for filename in os.listdir('testdb'):
        os.remove(join('testdb',filename))
    os.rmdir('testdb')
