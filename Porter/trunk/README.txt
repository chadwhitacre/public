========================================
    TABLE OF CONTENTS
========================================

    I. INTRODUCTION

    II. DEFINITIONS

    III. SOFTWARE DEPENDENCIES

    IV. INSTALLATION & USAGE

    V. CREDITS & LEGAL

    VI. NOTES



========================================
    I. INTRODUCTION
========================================

    From http://dictionary.reference.com/search?q=porter:

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


    Porter is a piece of software for managing the interface between the public
    Internet and a server cluster set up according to the Cambridge distributed
    http server architecture. All of the above definitions can be helpful in
    understanding what Porter is about, but given that Cambridge's namesake is
    Cambridge University, the second definition is the most apt.

    TODO: For more on Cambridge, see http://www.zetaweb.com/software



========================================
    II. DEFINITIONS
========================================

    These definitions are part of Cambridge.

    DOMAIN NAME -- To register a domain name with Porter it must have at least
    two levels, i.e., sub.example.com or example.com, but not example.

    SERVER -- A server is an IP address which will be serving websites.

    WEBSITE -- A website in Cambridge is an abstraction, a purely logical
    construct, identified by a codename. Within Porter, instances of this
    abstraction are uniquely identified by an id of the form: server:port, e.g.
    websrvr:8080.



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

    Set up Porter
    ----------------------------------------
    $PKG_HOME -- the parent directory of your Porter installation
    $INSTANCE_HOME -- the directory which contains all of your installation-
                      specific porter data and config
    prtrsrvr -- example porter server hostname
    namesrvr -- example named server hostname


    1) Install Porter[1].

        a. Get Porter from svn and put it in your Python's site-packages.

        b. Create a directory to house your data and configuration (e.g.,
        /usr/local/porter). This is $INSTANCE_HOME. Porter requires that
        $INSTANCE_HOME have a subdirectory var/, otherwise it will not start.
        You may also choose to maintain your Apache configuration, etc. in
        $INSTANCE_HOME as well.

        c. Follow the instructions in $PKG_HOME/bin/porter to install the
        executable.


    2) Install and configure Apache.

        See APACHE.txt.


    3) Install and configure BIND.

        Porter assumes that all domains will share the same SOA, MX records, and
        other configuration. This shared information is expected to be in a zone
        file at namesrvr:/etc/namedb/porter.zone. The domains themselves are
        expected to be registered in namesrvr:/etc/namedb/named.conf. Porter
        manages a named.conf fragment at $PKG_HOME/var/named.porter.conf. It is left
        as an excercise for the implementor to append or otherwise incorporate
        this fragment into named.conf.


    Set up a website
    ----------------------------------------
    websrvr -- example web server hostname
    127.0.0.1 -- example IP address for websrvr
    fooCodename@websrvr:8080 -- example website id

    4) Install a website.

    5) Tell prtrsrvr about websrvr[2]:

        prtrsrvr# vi /etc/hosts
        127.0.0.1   websrvr


    Configure a domain
    ----------------------------------------

    5) Register a domain at the registrar of your choice, and set your DNS
    servers to namesrvr.

    6) Register your domain name with Porter:

        prtrsrvr# sudo porter
        porter> add example.com websrvr 8080

    7) Once DNS propagates, http://example.com/ should hit prtrsrvr (thanks to
    our named mgmt), which should give you your website from websrvr (thanks to
    our httpd mgmt).

    Note that Porter automatically configures an additional www subdomain for
    each domain you register with it. So when you add example.com,
    www.example.com is added as well. If you added sub1.example.com, Porter
    would also add www.sub1.example.com. Directly adding a www subdomain in
    Porter is an error.

    TODO: Further usage documentation is provided inline.



========================================
    V. CREDITS & LEGAL
========================================

    Porter was written and is maintained by Chad Whitacre <chad zetaweb com>.

    Porter is licensed under the BSD license (see LICENSE.txt).



========================================
    VI. NOTES
========================================

[1] I'll look at using distutils in future versions.

[2] In a future version of Porter, the plan is to constrain the server hostnames
available in step 6 to those hosts named in /etc/hosts that provide a certain
API, and to constrain the available port numbers to those that each server tells
us about via the API.