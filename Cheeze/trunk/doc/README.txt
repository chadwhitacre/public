CHEEZE

    'Cheeze' stands for 'Cheap Zope'.


INTRO

    Cheap Zope instances are the foundation of efficient Zope hosting, both for
    development and production environments. Cheeze makes cheap zopes a reality
    by providing TTW Zope instance management tools. Using Cheeze, you can
    create, update, and delete (crud) zopes across multiple servers, and you can
    pave roads to your zopes using mod_rewrite and etc/hosts -- all from within
    the ZMI. Furthermore, functionality degrades gracefully based on your
    configuration. Cheeze is therefore very flexible, and can be used to set up
    a variety of Zope hosting environments.



DESIGN

    - three levels of abstraction: servers, zopes, and websites

    - master/slave configuration

    - master level:

        - services: firewall, DNS, caching, https, rewriting (mapping domain
        name to IP:port)

        - tools: ipfw, BIND, etc/hosts, Apache (mod_rewrite, mod_proxy, mod_ssl)
        Squid, Squirm, IIS?

    - At the master level, there are many tools available to provide the needed
    services. The Cheeze user interface should be unchanged or at least
    consistent for different back-end tools.

    - slave level: individual Zope instances, vhosting w/in zopes

        - services: http, cheeze

        - tools: ZServer, Cheeze



ROADMAP

    Version 0.6

        - crud zopes for local server

        - manage DNS using etc/hosts

        - manage rewrites using mod_rewrite



    Version 0.8

        - dynamic population of Servers tab



    Version 1.0

        - manage DNS using BIND



    Version 1.2

        - crud zopes for remote servers via RPC



    Future Versions

        - ldap

        - manage https using mod_ssl

        - manage caching using mod_proxy

        - manage rewrites using Squirm

        - manage caching using Squid

        - IIS for backend?





GLOSSARY

    server (pl. servers)

    zope (pl. zopes)

    Zope (pl. Zopes)

    skel (pl. skel)

    Cheeze (pl. Cheezen)


INSTALLATION

So here's how to set up a Cheeze server (dev or production):

    1) Install Zope

    2) Create a folder structure for instances. Here is my recommendation:

       zopes/
       zopes/instances
       zopes/skel

    3) Use stock mkzopeinstance.py to create a "master" instance in zopes/

    4) Manually tweak master/etc/zope.conf, etc. to your liking (I am using port
    8000 for master, 80 for dev instances)

    5) Optionally, add a custom skel or two to skel/.

    6) In master/ZMI, add a Big Cheeze, and set the instance_root and skel_root
    to the directories you created above.

    7) Now try creating and deleting zopes. :) th (you will need to start them
    manually to confirm that they are indeed working)