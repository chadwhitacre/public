Steve,

Ok man, here's what I did: I mercilessly refactored ZetaServerAdmin into a
Product, which is now called Cheeze and which is in the public repo. "Cheeze"
stands for "Cheap Zopes". :)

I decided to keep the vhosting and instance mgmt functionality a little more
distinct than we have been. Doing this means we can use Cheeze on our local
machines, cause we need cheap zopes for dev at least as much as for production.
I didn't remove any of your vhosting work, but it only shows up if we are on
unix (haven't actually fully tested this yet).

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

  6) In master/ZMI, add a Big Cheeze, and set the instance_root and skel_root to
     the directories you created above.

  7) Now try creating and deleting zopes. :) th (you will need to start them
     manually to confirm that they are indeed working)

  8) Also note "domains" and "documentation" tabs.


Notes:

  - Create/delete is working :)

  - "decommission" (take out of vhosting) will act as a protection against
  accidental deletion once it is in place.

  - We may want to make delete impossible on production servers. (i.e., have
  two 'modes' for Big Cheeze -- production, dev)

  - You can have multiple Big Cheezes pointing to different instance
  roots. Heck, you can even point them at same root :)

  - No tests, and interface is out of sync

  - list_zopes and list_skel are dumb! They just list the directories in
  instance_root and skel_root, regardless of whether those directories will
  actually function as zopes or skel.

  - I've been using "skel" as the plural of "skel" prolly dumb but it's late ;)



SEE ALSO: TODO.txt
