class ApacheVHostManager:
    """ provides functionality to manage an apache virtual hosting setup """

    def __init__(self):
        pass

    def list_ports(self):
        """ return a list of available ports """
        if vhosting:
            avail_ports = [str(x) for x in range(8010,9000,10)]
            for zope in self.zopes_list():
                if self.port_get(zope) in avail_ports:
                    avail_ports.remove(port)
        else:
            return None
