# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE":
# <chad@zetaweb.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return. --Chad Whitacre
# ----------------------------------------------------------------------------

import os
from os.path import join
from ConfigParser import SafeConfigParser as ConfigParser

class Whale:
    """

    A Whale is a mailing list. Kraken eat Whales for dinner. On the filesystem,
    a Whale looks like a directory with three files in it:

        - whale.conf

        - send_to.addrs

        - accept_from.addrs

    See the example/ Whale included in the default Kraken package for details.

    >>> import os
    >>> path = os.path.abspath('example')
    >>> w = Whale(path)
    >>> w.imap['username']
    'mylist@example.com'

    """

    def __init__(self, nest):
        """ given an absolute path, initialize a Whale """

        conf_path = join(nest,'whale.conf')
        send_path = join(nest,'send_to.addrs')
        from_path = join(nest,'accept_from.addrs')

        self.id   = os.path.split(nest)[1]
        self.nest = nest

        cp = ConfigParser()
        cp.read(conf_path)
        self.imap = dict(cp.items('imap'))
        self.smtp = dict(cp.items('smtp'))
        self.list_addr = cp.get('default', 'list_addr')
        lt = self.list_type = cp.get('default', 'list_type')


        # setup permissions based on list type

        if lt == 'private discussion':
            # all list members can post, as well as certain others
            self.send_to = self.addrs(send_path)
            self.accept_from = self.send_to + \
                               self.addrs(from_path)

        elif lt == 'announcement list':
            # only those explicitly named can post
            self.send_to = self.addrs(send_path)
            self.accept_from = self.addrs(from_path)


    def addrs(self, fn):
        """ given a filename, return a list of email addresses """
        raw = file(fn).read()
        lines = [l.strip() for l in raw.split(os.linesep)]
        return [l for l in lines
                  if not l.startswith('#') and
                     not l == '']
        # maybe eventually validate email addresses




def _test():
    import doctest, Whale
    return doctest.testmod(Whale)

if __name__ == "__main__":
    _test()
