#!/usr/local/bin/python
# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

import os, re, sys
from glob import glob
from sets import Set
from ConfigParser import RawConfigParser

arg = sys.argv[1:2]
if arg: top = arg[0]
else:   top = '.'
top = os.path.realpath(top)

# parse the config file into a list of patterns matching text files
config = RawConfigParser()
config.read(os.path.expanduser('~/.subversion/config'))
if not config.has_section('auto-props'):
    print 'your subversion config file has no auto-props section'
else:
    autoprops = config.options('auto-props')
    globlist = []
    for pattern in autoprops:
        if 'svn:eol-style' in config.get('auto-props', pattern):
            globlist.append(pattern)
    globlist.sort()

# walk the tree and get a list of paths to text files
textfiles = Set()
for path, dirs, files in os.walk(top):
    for filename in files:
        for pattern in globlist:
            fullpattern = '%s/%s' % (path, pattern)
            for textfile in glob(fullpattern):
                textfiles.add(textfile)
    if '.svn' in dirs: dirs.remove('.svn')
textfiles = tuple(textfiles)

print 'found %s text files; cleaning...' % len(textfiles)

# now actually do the replacement
win = re.compile(r'\r\n') # not worrying about mac for now
i = 0
for path in textfiles:
    textfile = file(path, 'r+')
    tmp = textfile.read()
    dirty = len(win.findall(tmp))
    if dirty > 0:
        i += 1
        print '  %s' % path
        tmp = win.sub('\n', tmp)
        textfile.seek(0); textfile.truncate(); textfile.write(tmp)
    textfile.close()

print 'done; cleaned up %s files' % i
