#!/usr/local/bin/python
# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

import os, re, sys
from glob import glob
from sets import Set
from ConfigParser import RawConfigParser



def confgen(top):
    """given a tree root, walk the tree and generate an auto-props section
    based on the filenames found
    """

    globs = Set()
    for path, dirs, files in os.walk(top):
        for filename in files:
            parts = filename.split('.')
            if len(parts) > 1:
                glob = '*.%s' % parts[-1]
            else:
                glob = parts[-1]
            globs.add(glob)

        # skip svn directories
        if '.svn' in dirs: dirs.remove('.svn')
    globs = list(globs); globs.sort()

    print '[miscellany]'
    print 'enable-auto-props = yes'
    print
    print '[auto-props]'
    for glob in globs:
        print "%s = svn:eol-style=native" % glob.ljust(12)



def clean(top):
    """given a tree root, walk the tree, find all the text files, and clean up
    their newlines
    """

    ##
    # Parse the config file into a list of patterns that match text files
    ##

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



    ##
    # Walk the tree and get a list of paths for all the text files.
    ##

    textfiles = Set()
    i = 0; sys.stdout.write('locating text files ...')

    for path, dirs, foo in os.walk(top):
        for pattern in globlist:
            fullpattern = '%s/%s' % (path, pattern)
            for textfile in glob(fullpattern):
                # indicate progress
                i += 1
                if i % 50 == 0:
                    sys.stdout.write('.')
                    sys.stdout.flush()
                textfiles.add(textfile)

        # skip svn directories
        if '.svn' in dirs: dirs.remove('.svn')

    textfiles = tuple(textfiles)
    print ' %s found' % len(textfiles)



    ##
    # Now actually do the replacement.
    ##

    win = re.compile(r'\r\n') # not worrying about mac for now
    j = 0; sys.stdout.write('scrubbing newlines ...')

    for path in textfiles:
        textfile = file(path, 'r+')
        tmp = textfile.read()
        dirty = len(win.findall(tmp))
        if dirty > 0:
            # indicate progress
            j += 1
            if j % 50 == 0:
                sys.stdout.write('.')
                sys.stdout.flush()

            # progress
            tmp = win.sub('\n', tmp)
            textfile.seek(0); textfile.truncate(); textfile.write(tmp)
        textfile.close()

    print ' %s files cleaned' % j



if __name__ == '__main__':

    # get our subcommand
    subcommand = sys.argv[1:2]
    if not subcommand:
        print "see man 1 svneol for usage"
        sys.exit(2)
    elif subcommand not in (['clean'], ['confgen']):
        print "'%s' command not available; " % subcommand +\
              "see man 1 svneol for usage"
        sys.exit(2)
    else:
        subcommand = subcommand[0]

    # determine the root of the tree
    arg = sys.argv[2:3]
    if arg: top = arg[0]
    else:   top = '.'
    top = os.path.realpath(top)

    # call the appropriate function
    vars()[subcommand](top)


