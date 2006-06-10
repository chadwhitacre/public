#!/usr/bin/env python -u
"""

    servers -- A server is any host on the internet, specified by IP address,
    hostname, or fully qualified domain name

    websites -- A website instance is an HTTP service on an arbitrary port on a
    server

    domains -- A domain is an Internet domain name.

        canonical -- a domain name which points directly at a website

        alias -- a domain name which points at another domain name

            implicit -- Porter recognizes the www subdomain as an implicit alias
            for the primary domain. In addition, all non-lowercase domains are
            aliases for their lowercase counterparts. However, implicit aliases
            should be handled at the apache level, not in porter

            explicit -- The user may specify alias domains using Unix symlinks.

Given a set of relationships between domains, servers, and websites encoded in a
certain way using the Unix filesystem, porter will produce a dbm file useful as
a back-end for an Apache rewrite map. Apache can then be used as a proxy server
to organize the various various back-end servers into a cluster, so that the
websites are presented to the public Internet as coming from a single server.

1. porter redirect
2. porter proxy
3. porter dump?

2. apache rewrites the hostname on all requests to lowercase
3. apache

We could have another process which monitors the state of the tree, and if
anything changes writes an empty file to ./refresh; then the porter daemon can
check for the presence of that file and rebuild the map accordingly.

cost of refresh() vs. cost of build_map()

ok, so I think that since dictionaries are mutable, then we could run our
build_map method in a separate process or thread (?) and when it updates the
dictionaries, those changes will be instantly available to the daemon methods?

"""
################################################################################
#                                                                              #
#   PROGRAM                                                                    #
#                                                                              #
################################################################################

import os, sys

class Porter:

    domain_root = ''

    def __init__(self, domain_root='.'):
        # read in from /usr/local/etc/proxy.conf'
        self.domain_root = os.path.realpath(domain_root)
        self.build_map()

    def build_map(self):
        """set three dictionaries on self:
            canonical = { canonical domains : websites }
            aliases   = { domain aliases    : canonical domains }
            orphans   = { all domains       : a boolean, True = orphaned }
        """
        canonical = {}
        aliases = {}
        orphans = {}
        for domain in os.listdir(self.domain_root):
            path = os.path.join(self.domain_root, domain)
            if os.path.islink(path):

                # Regardless of whether links are relative or absolute, we assume that
                # they work from the domain_root. However, we only want server paths
                # to be realpath'd, since we want domain aliases to point to their
                # canonical domains, not the actual websites.

                linkpath = os.readlink(path)
                if linkpath.count('/servers/'):
                    website = os.path.join(self.domain_root, linkpath)

                    # now meta-canonicalize our symlinks ;^)
                    website = os.path.realpath(website)
                    os.unlink(path)
                    os.symlink(website, path)

                    parts = os.path.basename(website).split('_')
                    BAD = True
                    if len(parts) == 2:
                        port = parts[1]
                        if port.isdigit():
                            BAD = False
                    server = os.path.basename(os.path.dirname(website))

                    if not BAD:
                        canonical[domain] = '%s:%s' % (server, port)
                    else:
                        orphans[domain] = True
                else:
                    aliases[domain] = os.path.basename(linkpath)

                orphans[domain] = not os.path.exists(path)

        self.canonical = canonical
        self.aliases = aliases
        self.orphans = orphans

    def canonicalize(self, domain):
        """given a candidate domain, return a canonicalized domain or 'NULL'
        """

        if domain in self.canonical: return 'NULL'

        # ok, get smart: check on a www. variant
        if domain.lower().startswith('www.'):
            variant = domain[4:]
        else:
            variant = 'www.%s' % domain
        if variant in self.canonical:
            return variant

        # hrm ... ok, check lowercase versions too
        domain = domain.lower()
        variant = variant.lower()
        if domain in self.canonical:
            return domain
        elif variant in self.canonical:
            return variant

        # finally check for explicit aliases
        elif domain in self.aliases:
            return self.aliases[domain]
        elif variant in self.aliases:
            return self.aliases[variant]

        # and if we failed completely ...
        return 'NULL'

    def proxy(self, domain):
        """given a canonical domain, return a domain:port to be proxied
        """
        print self.canonical[domain]

    def daemon(self, function):
        """turns a function into a daemon
        """
        while 1:
            domain = sys.stdin.readline()
            print function(domain)

def main():
    arg = sys.argv[1:2]
    if not arg:
        print "man 1 porter for usage"
        sys.exit(1)
    else:
        porter = Porter()
        if arg[0] == 'canonicalize':
            porter.daemon(porter.canonicalize)
        elif arg[0] == 'proxy':
            porter.daemon(porter.proxy)
        else:
            print "man 1 porter for usage"
            sys.exit(1)

if __name__ == '__main__':
    main()