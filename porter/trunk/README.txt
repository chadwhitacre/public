========================================
    TABLE OF CONTENTS
========================================

    I. INTRODUCTION

    II. DEFINITIONS

    III. SOFTWARE DEPENDENCIES

    IV. INSTALLATION & USAGE

    V. CREDITS & LEGAL

    NI. NOTES



========================================
    I. INTRODUCTION
========================================

        por·ter[1] (pôrt@r)
        n.

            1. A person employed to carry burdens, especially an attendant who
            carries travelers' baggage at a hotel or transportation station.

            2. A railroad employee who waits on passengers in a sleeping car or
            parlor car.

            3. A maintenance worker for a building or institution.

        por·ter[2] (pôrt@r)
        n. Chiefly British

            One in charge of a gate or door.


    Porter is a piece of software for mapping domain names to websites served
    from within a clustered server environment. Porter, then, is a gatekeeper
    for the server cluster, as well as the one who ferries packets to the proper
    backend server. This centralization provides certain benefits:

        - Fewer changes to DNS since all DNS always points to the cluster's
        public IP address. This means instant rerouting of domain names among
        backend servers, vastly streamlining staging, rollout, and fallback.

        - Easier log configuration

        - Easier cache configuration

    The drawback, of course, is that we have a single point of failure. In
    future versions we need to address this issue.



========================================
    II. DEFINITIONS
========================================

    DOMAIN NAME -- a domain name is a fully qualified second- or higher-level
    domain[1]. Examples:

        - zetaserver.com

        - tesm.edu

        - online.tesm.edu

        - library.tesm.edu

        - jewelryjohn.com


    WEBSITE -- A website in our clustered server is an abstraction, a purely
    logical construct, identified by a codename. Instances of this abstraction
    are uniquely identified by an id of the form:

        codename@server:port

    Note that the server and port are sufficient to distinguish the instance as
    far as Apache is concerned, but the codename is necessary in cases where we
    want to relate this instance to other instances of the website on the human
    level.

    SERVER -- A server is any IP address in /etc/hosts that returns the
    following when called via HTTP on port 80:

        https://127.0.0.1:80/websites
        https://127.0.0.1:80/open_ports

            Should return some data structure. Format yet to be decided (XML or
            pure python?) Should include: available ports, current websites



========================================
    III. SOFTWARE DEPENDENCIES
========================================

    Porter was developed with the following software:

        - Python 2.4

        - Apache 1.3.33

        - BIND 8.3.7-REL

        - FreeBSD 4.10-RELEASE

    Your mileage with others will vary.



========================================
    IV. INSTALLATION & USAGE
========================================

    Set up porter
    ----------------------------------------
    $PORTER -- the directory to which you installed porter
    prtrsrvr -- example porter server hostname
    namesrvr -- example named server hostname

    1) Install porter.

        TODO: trying to get my head around installation. I'll have to look into
        distutils ... my thinking at this point is that we would install the
        python specific bits in site-packages, and then put install-specific
        stuff (var/, bin/) in /usr/local/porter/.


    2) Install and configure Apache.

        Porter expects that httpd will do the actual routing of http requests
        to the appropriate backend server. The two interface via a dbm file at
        $PORTER/var/rewrite.db, which maps domain name to server:port. The
        intention is that this file be used in a dbm RewriteMap[2], e.g.:

            <VirtualHost *>
                RewriteEngine On
                RewriteMap  PorterMap dbm:$PORTER/var/rewrite.db
                RewriteRule ^/(.*) http://${PorterMap:%{HTTP_HOST}}/$1 [L,P]
            </VirtualHost>


    3) Install and configure BIND.

        Porter assumes that all domains will share the same SOA, MX records, and
        other configuration. This shared information is expected to be in a zone
        file at namesrvr:/etc/namedb/porter.zone. The domains themselves are
        expected to be registered in namesrvr:/etc/namedb/named.conf. Porter
        manages a named.conf fragment at $PORTER/var/named.conf.frag. It is left
        as an excercise for the implementor to append or otherwise incorporate
        this fragment into named.conf.

            In our reference implementation we will be hosting named on a box
            other than prtrsrvr. Therefore we need to setup a transfer of the
            named.conf file by giving the named server a user on prtrsrvr with
            read access to named.conf.frag.

            We will also be maintaining a porter.zone file in var/ which will be
            incorporated into named along with the conf fragment.

            We want to be sure that the system fails gracefully:

                - We want to be very careful editing named.conf.fragment, since
                we are dealing with a pure text format. DONE

                - We should keep at least one generation of backups for the two
                named files, both on namesrvr and prtrsrvr. DONE

                - Grace should abort if named.conf.frag is empty

                - Ideally the named.conf update should be transactional with the
                porter.zone update.


    Set up a website
    ----------------------------------------
    websrvr -- example web server hostname
    127.0.0.1 -- example IP address for websrvr
    cheese@websrvr:8080 -- example website id

    4) Install a website.

    5) Tell prtrsrvr about websrvr[3]:

        prtrsrvr# vi /etc/hosts
        127.0.0.1   websrvr


    Configure a domain
    ----------------------------------------

    5) Register a domain at the registrar of your choice, and set your DNS
    servers to namesrvr.

    6) Register your domain name with porter:

        prtrsrvr# sudo /usr/local/porter/porter.py
        porter> add example.com websrvr 8080

    7) Once DNS propagates, http://example.com/ should hit prtrsrvr (thanks to
    our named mgmt), which should give you your website from websrvr (thanks to
    our httpd mgmt).

    Note that porter automatically configures an additional www subdomain for each
    domain you register with it. So when you add example.com, www.example.com is
    added as well. If you added sub1.example.com, porter would also add
    www.sub1.example.com. Directly adding a www subdomain in porter is an error.

    TODO: Further usage documentation is provided inline.



========================================
    CREDITS & LEGAL
========================================

    Porter was written and is maintained by Chad Whitacre <chad zetaweb.com>.

    Porter is licensed under the BSD license (see LICENSE.txt).



========================================
    NOTES
========================================

[1] If I'm not mistaken, these actually aren't true FQDNs since they don't have
a final period.

[2] For details on dbm RewriteMaps see Apache's documentation:

    Apache 1.3 -- http://httpd.apache.org/docs/mod/mod_rewrite.html#RewriteMap

    Apache 2.0 -- http://httpd.apache.org/docs-2.0/mod/mod_rewrite.html#rewritemap

Note that Apache 2 supports multiple dbm types. You want to use ndbm. This is
the only available type in 1.3, but the default in 2.0 is sdbm. I developed with
Apache 1.3.33 because I couldn't get Apache 2.0.52 to compile --with-ndbm.

[3] In a future version of porter, the plan is to constrain the server hostnames
available in step 6 to those hosts named in /etc/hosts that provide a certain API,
and to constrain the available port numbers to those that $server tells us about
via the API.