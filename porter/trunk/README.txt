========================================
    INTRODUCTION
========================================

    Porter is a piece of software for mapping domain names to websites within
    Zetaserver. In this way we are the gatekeeper of the zetaserver fortress, as
    well as the one who ferries packets to the proper back-end server. Note that
    Zetaserver is only going to handle a few types of traffic:

        - HTTP/HTTPS -- All requests hit us, and we will route them dynamically
        using Apache mod_rewrite.

        - SSH/SFTP/SCP -- We should try to reserve these for admin use only.

        - possibly FTP -- Let's avoid this if we can. (although mod_proxy
        apparently can handle ftp as well)

    The only red flag at this point is our "uploaders" which are currently HTTP
    based. I had thought of using SFTP/HTTP for these, but maybe we should try
    harder to stick with an HTTP-based solution, in order to stay centralized.
    This centralization provides certain benefits:

        - Fewer changes to DNS, instant rerouting of domain names among backend
        servers

        - Easier log configuration

        - Easier cache configuration

    The drawback, of course, is that we have a single point of failure. In
    future versions we need to introduce redundancy to address this issue.


========================================
    DEFINITIONS
========================================

    Domain Name -- a domain name is a relatively expressed (i.e., not FQDN)
    second- or higher-level domain. Examples:

        - zetaserver.com

        - tesm.edu

        - online.tesm.edu

        - library.tesm.edu

        - jewelryjohn.com


    Website -- A website in Zetaserver is an abstraction. Instances of this
    abstraction are uniquely identified by an id of the form:

        site@server:port

    Server -- A server is any IP address in /etc/hosts that returns the
    following when called via HTTP on port 80:

        https://127.0.0.1:80/websites
        https://127.0.0.1:80/open_ports

    Should return some data structure. Format yet to be decided (XML or pure
    python?) Should include: available ports, current websites


========================================
    USAGE
========================================

    1) install Apache on a jail (clive)

    2) setup mod_rewrite there (just add those two lines to conf)

    3) install Zope or whatever on another jail (george:8080)

    4) clive> vim /etc/hosts
       192.168.1.x  george

    5) clive> porter
       porter> add example.com george 8080

    6) http://example.com/ should hit clive and give you george



========================================
    SOFTWARE DEPENDENCIES
========================================

    These are soft, i.e., we just haven't tested with other versions:

        - FreeBSD 4.10

        - Python 2.4

        - Apache 2.0.52

NOTE: Be sure to keep a couple IP address open for future dev and staging of
porter! How about we reserve 85-87 for this purpose.