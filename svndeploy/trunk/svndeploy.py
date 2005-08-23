#!/usr/bin/env python
# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

import os
import socket
from popen2 import Popen4
from xmlrpclib import ServerProxy
from urlparse import urlsplit

path = os.path.realpath('.')
server_url = 'http://josemaria:5370'
scheme, hostname, port, query, frag = urlsplit(server_url)

def _popen(command):
    process = Popen4(command)
    result = process.wait()
    output = process.fromchild.read()
    return (result, output)


result, output = _popen('svn st')
if output == "svn: '.' is not a working copy":
    print "ERROR: The current directory is not a subversion working copy."
    raise SystemExit

if output: # note that this will bork when there are svn:externals
    print "ERROR: Please commit all changes before deploying."
    raise SystemExit

result, output = _popen('svn info')
svn_url = output.split(os.linesep)[1][5:]

server = ServerProxy(server_url)
print "Deploying %s on %s ..." % (svn_url, server_url)
print server.deploy(svn_url)
