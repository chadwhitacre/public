class Whale:
    """

    A Whale is a mailing list. Kraken eat Whales for dinner. On the filesystem,
    a Whale looks like a directory with three files in it:

        - whale.conf

        - send_to.addrs

        - accept_from.addrs

    See the example/ Whale included in the default Kraken package for details.

    """

    def __init__(self, nest):
        """ given an absolute path, initialize a Whale """

        conf_path = join(nest,'whale.conf')
        send_path = join(nest,'send_to.addrs')
        from_path = join(nest,'accept_from.addrs')

        cp = ConfigParser()
        cp.read(conf_path)
        self.imap = dict(cp.items('imap'))
        self.smtp = dict(cp.items('smtp'))
        self.list_addr = cp.get('default', 'list_addr')
        lt = self.list_type = cp.get('default', 'list_type')


        # setup permissions based on list type

        if lt == 'private discussion':
            # those explicitly named can post, as well as list members
            self.send_to = self.addrs(send_path)
            self.accept_from = self.send_to + \
                               self.addrs(from_path)

        elif lt == 'announcement':
            # only those explicitly named can post
            self.send_to = self.addrs(send_path)
            self.accept_from = self.addrs(from_path)
