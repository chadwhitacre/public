INTRO

Cheap Zope instances are the foundation of efficient Zope hosting, both for
development and production environments. Cheeze makes cheap Zopes a reality by
providing TTW Zope instance management tools. 'Cheeze' stands for 'Cheap
Zope'.

Using a Big Cheeze object, you can manage the following TTW:

    - Zope instances

    - DNS

    - virtual hosting with Apache



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