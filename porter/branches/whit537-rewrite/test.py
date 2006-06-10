#!/usr/bin/env python -u
import os, sys
from porter import Porter
from testosterone import testosterone

def rm_rf(path):
    """ equivalent to rm -rf on Unix -- be careful!
    """
    if os.path.realpath(path) == '/':
        print 'will not rm -rf /'
        sys.exit(1)
    else:
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(path)

##
# create a testing fixture in the current directory
##

# set up a sandbox
root = os.path.realpath('.')
root = os.path.join(root, 'PORTER-TESTING-SANDBOX')
if os.path.exists(root): rm_rf(root)
os.mkdir(root); os.chdir(root)
os.mkdir('domains'); droot = os.path.join(root, 'domains')
os.mkdir('servers'); sroot = os.path.join(root, 'servers')

# set up some servers w/ websites
os.chdir('servers')
os.mkdir('foo')
os.system('touch %s' % os.path.join(sroot, 'foo', 'website_8010'))
os.system('touch %s' % os.path.join(sroot, 'foo', 'website_8020'))
os.mkdir('bar')
os.system('touch %s' % os.path.join(sroot, 'bar', 'website_8810'))
os.mkdir('baz')
os.system('touch %s' % os.path.join(sroot, 'baz', 'website_8080'))

# set up some canonical domains
os.chdir(os.path.join('..','domains'))
os.symlink( os.path.join(sroot, 'foo', 'website_8010')
          , os.path.join(droot, 'example.com')
           )
os.symlink( os.path.join(sroot, 'bar', 'website_8810')
          , os.path.join(droot, 'example.net')
           )
os.symlink( os.path.join(sroot, 'baz', 'website_8090')
          , os.path.join(droot, 'example.org')
           )

# set up some domain aliases
os.symlink( os.path.join(droot, 'example.com')
          , os.path.join(droot, 'alias.example.com')
           )
os.symlink( os.path.join(droot, 'example.com')
          , os.path.join(droot, 'alias.example.net')
           )
os.symlink( os.path.join(droot, 'example.org')
          , os.path.join(droot, 'alias.example.org')
           )

# instantiate Porter with our fake domain root
porter = Porter(droot)



##
# ok, now run some tests!
##
testosterone("""\

# if already canonical then we get NULL
porter.canonicalize('example.com') == 'NULL'
porter.canonicalize('example.net') == 'NULL'
porter.canonicalize('example.org') == 'NULL'

# test some real live aliases
#print porter.canonicalize('alias.example.com')
porter.canonicalize('alias.example.com') == 'example.com'
porter.canonicalize('alias.example.net') == 'example.com'
porter.canonicalize('alias.example.org') == 'example.org'

# also test some orphans
porter.canonical['example.com'] == 'foo:8010'
porter.canonical['example.net'] == 'bar:8810'
porter.canonical['example.org'] == 'baz:8090'

""", globals(), locals())



if os.path.exists(root): rm_rf(root)