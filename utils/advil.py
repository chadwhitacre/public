#!/usr/bin/env python
##############################################################################
#                                                                            #
#  (c) 2005 Chad Whitacre <http://www.zetadev.com/>                          #
#  This program is beerware. If you like it, buy me a beer someday.          #
#  No warranty is expressed or implied.                                      #
#                                                                            #
##############################################################################
"""
Advil takes the headaches out of planning and executing Zope migrations.

To use advil, you will need your old instance and a new clean instance available
on TCP/IP sockets via ZEO. Advil connects to these, using a different Products
directory for each. To change these settings, edit the script. Advil assumes
that SOFTWARE_HOME is in your environment.

Once connected, you have three ways to prepare for and execute your migration:

  interactively
    If advil receives a single argument, -i, it will enter an interactive Python
    shell with 'old_app' and 'new_app' bound to the two Zope instances. This is
    useful for developing your migration strategy.

  via a script
    If advil receives a single argument that it doesn't otherwise recognize,
    then it will interpret it as a path to a python script to be executed with
    'old_app' and 'new_app' in the namespace. This is especially useful for
    executing your migration.

  through the web
    You can of course connect to the ZEO servers via standard Zope client
    instances. This can be helpful for migration development, and it also means
    you can work with a live site.


If advil receives no arguments, more than one argument, '-h', or '--help', then
it prints this help message.

"""

__version__ = '0.2'
__author__ = "Chad Whitacre <chad [at] zetaweb [dot] com>"



# Settings.
# =========
#
# *_HOST        hostname where ZEO is running
# *_PORT        port on which ZEO is running
# *_PRODUCTS    the path to the Products directory to use for that ZEO

OLD_HOST = 'localhost'
OLD_PORT = 9454
OLD_PRODUCTS = '/usr/local/zope/instances/old/Products'

NEW_HOST = 'localhost'
NEW_PORT = 9777
NEW_PRODUCTS = '/usr/local/zope/instances/new/Products'



# Import from the standard library.
# =================================

import code
import os
import sys
import time



# If we can, exit early rather than waiting for Zope to load.
# ===========================================================

if __name__ == '__main__':

    if len(sys.argv) <> 2:
        sys.exit(__doc__)

    arg = sys.argv[1]

    if arg.lower() in ('-h', '--help'):
        sys.exit(__doc__)

    if arg <> '-i':
        path = os.path.realpath(arg)
        if not os.path.isfile(path):
            sys.exit("ERROR: %s does not point to a regular file." % path)



# Import from Zope.
# =================

SOFTWARE_HOME = os.environ.get('SOFTWARE_HOME', '')
if not SOFTWARE_HOME:
    sys.exit("Please set SOFTWARE_HOME to your Zope's lib/python.")
sys.path.insert(1, SOFTWARE_HOME)

import Products
from ZEO import ClientStorage
from ZODB import DB
from OFS.Application import AppInitializer



# Initialize the two Zopes.
# =========================
# This could be sped up significantly by doing tricks a la ZopeTestCase:
#
#   https://svn.plone.org/svn/collective/ZopeTestCase/tags/trunk/ZopeLite.py
#
# It is necessary to do *some* initialization, especially when a Product
# (*cough*CMFPlone*cough*) performs circular imports; odd behavior results
# otherwise. However, since the migration logic is an open question, it is
# probably best to do the full initialization.

Products.__path__.insert(0, 'placeholder') # will be replaced in a few lines

def connect(host, port, products):
    sys.stdout.write("Opening Zope @ %s:%s ... " % (host, port))
    sys.stdout.flush()
    start = time.time()

    Products.__path__[0] = products

    storage = ClientStorage.ClientStorage((host, port))
    conn = DB(storage).open()
    app = conn.root()['Application']

    AppInitializer(app).initialize() # this is what takes so much time

    print "done (%.3fs)" % (time.time()-start,)

    return app

old_app = connect(OLD_HOST, OLD_PORT, OLD_PRODUCTS)
new_app = connect(NEW_HOST, NEW_PORT, NEW_PRODUCTS)



if __name__ == '__main__':

    if arg == '-i':
        code.interact( banner="Advil v%s -- " % __version__ +\
                              "Advil eases Zope migrations."
                     , local=globals()
                      )
    else:
        execfile(path)