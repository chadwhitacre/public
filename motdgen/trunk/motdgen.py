#!/usr/local/bin/python
""" generate a custom motd; see man 1 motdgen for details
"""

import os, sys

args = sys.argv[1:]
if len(args) < 2:
    print __doc__.strip('\n').strip()
else:
    data = {}

    fqdn = args[0]
    data['fqdn'] = '  '.join([c for c in fqdn]).rjust(78)

    hostname = fqdn.split('.')[0]
    figlet = "figlet -S -w78 %s" % hostname
    stdin, stdout = os.popen4(figlet)
    data['hostname'] = stdout.read()
    stdin.close(), stdout.close()

    data['description'] = ' '.join(args[1:])

    motd = """\
w  e  l  c  o  m  e     t  o  .  .  .
%(hostname)s
%(fqdn)s

%(description)s""" % data

    print motd