from Interface import Base

class IBigCheeze(Base):
    """ Basically, a Zope instance manager """

    ##
    # vhost wrappers
    ##

    def waxit(self):
        "clear out the vhosts"

    def delete_vhosts(self, vhostname):
        "deletes a vhost given a name"


    ##
    # Helpers for the domains pt
    ##

    def domains_info(self, troubleshoot=0):
        "populate the domains pt"

    def domains_list(self):
        "list the available domains"


    ##
    # Helpers for the domains pt
    ##

    def zopes_list(self):
        "list available zopes"

    def zopes_info(self, troubleshoot=0):
        "populate the zopes pt"

    def zopes_process(self):
        "this processes the zopes pt"
