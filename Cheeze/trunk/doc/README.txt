Steve,

Ok man, here's what I did: I mercilessly refactored ZetaServerAdmin into a
Product, which is now called Cheeze and which is in the public repo. "Cheeze"
stands for "Cheap Zopes". :)

I decided to keep the vhosting and instance mgmt functionality more distinct
than we have been. Doing this means we can use Cheeze on our local machines,
cause we need cheap zopes for dev as well as for production. I didn't remove any
of your vhosting work, but it only shows up if we are on unix (haven't actually
fully tested this yet).

So here's how to set up a Cheeze server (dev or production):

  1) Install Zope

  2) Create a folder structure for instances. Here is my recommendation:

       zopes/
       zopes/instances
       zopes/skel

  3) Use stock mkzopeinstance.py to create a "master" instance in zopes/

  4) Manually tweak master/etc/zope.conf, etc.

  5) Right now it expects a

  6) In master/ZMI, add a Big Cheeze, and set the instance_root and skel_root to
     the directories you created above.




Notes:

  - I've been using "skel" as the plural of "skel" prolly dumb but it's late ;)

  - "decommission" (take out of vhosting) will act as a protection against
  accidental deletion once it is in place.

  - We may want to make delete impossible on production servers.

  - You can have multiple Big Cheezes pointing to different instance
  roots. Heck, you can even point them at same root :)

  - No tests, interfaces are out of sync





CheapZopeManager will handle several tasks:

    - creation of new zope instances

    - registering instances with apache



    - registering domains with dns



    - centralized error management

    - per site bandwith, storage, and memory usage




    - serving up data for zeta client apps, such as an app that would browse and
    download instances for local dev purposes
