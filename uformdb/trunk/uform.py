"""

This module provides a uform class. Uforms are dictionaries that have a read-
only, non-deletable UUID associated with them.

    >>> u = uform()
    >>> uuid = u.uuid
    >>> u.uuid = 'cheese monkey'
    Traceback (most recent call last):
        ...
    uform error: you cannot change a uuid post-creation
    >>> u.__delattr__('uuid')
    Traceback (most recent call last):
        ...
    uform error: you cannot delete a uuid

Unfortunately, we can still operate on __dict__ directly. There are things we
could do with metaclasses to lock this down further if needed. It may be enough
to make it a matter of procedure.

    >>> u.__dict__['uuid'] = 'cheese monkey'
    >>> u.uuid
    'cheese monkey'

D'oh!

"""

from utils import uuidgen

class uform(dict):
    """ object representation of a uform """

    def __init__(self,data={},uuid = None):
        dict.__init__(self)
        if not uuid: uuid = uuidgen()
        self.__dict__['uuid'] = uuid
        dict.update(self, data)


    def __setattr__(self, name, value):
        if name == 'uuid':
            raise 'uform error','you cannot change a uuid post-creation'
        else:
            dict.__setattr__(self, name, value)

    def __delattr__(self, name):
        """  """
        if name == 'uuid':
            raise 'uform error','you cannot delete a uuid'
        else:
            dict.__delattr__(self, name)


def _test():
    import doctest, uform
    return doctest.testmod(uform)

if __name__ == "__main__":
    _test()