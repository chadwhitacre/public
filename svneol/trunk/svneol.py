#!/usr/bin/env python
# (c) 2005-2009 Chad Whitacre <http://www.zetadev.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

import os, re, sys
from glob import glob
try:
    set
except NameError: # pre-2.6 (post-2.3)
    from sets import Set as set
from ConfigParser import RawConfigParser


nix = re.compile(r'(?<!\r)\n')
win = re.compile(r'\r\n')
mac = re.compile(r'\r(?!\n)')


class EOLToolkit:
    """This is a toolkit for cleaning up line endings in a tree.
    """

    __version__ = '1.0'

    def __init__(self):
        pass


    def _confglobs(self):
        """Get a list of patterns that match text files from the svn config.
        """

        config = RawConfigParser()
        config.optionxform = lambda x: x # stock parser is case-insensitive

        config.read(os.path.expanduser('~/.subversion/config'))
        if not config.has_section('auto-props'):
            print 'Your subversion config file has no auto-props section.'
            sys.exit(1)

        autoprops = config.options('auto-props')
        globs = Set()
        for pattern in autoprops:
            if 'svn:eol-style' in config.get('auto-props', pattern):
                globs.add(pattern)
        globs = list(globs); globs.sort()
        return globs


    def confgen(self, top):
        """Given a tree root, walk the tree and generate an auto-props section
        based on the filenames found.
        """

        globs = Set()
        for path, dirs, files in os.walk(top):
            for filename in files:
                parts = filename.split('.')
                if len(parts) > 1:
                    pattern = '*.%s' % parts[-1]
                else:
                    pattern = parts[-1]
                globs.add(pattern)

            # Skip svn directories.
            if '.svn' in dirs:
                dirs.remove('.svn')

        globs = list(globs)
        globs.sort()

        print '[miscellany]'
        print 'enable-auto-props = yes'
        print
        print '[auto-props]'
        for pattern in globs:
            print "%s = svn:eol-style=native" % pattern.ljust(12)


    def clean(self, top, to_windows):
        """Given a tree root, clean up newlines in all text files.
        """

        sys.stdout.write('scrubbing newlines ...')
        sys.stdout.flush()
        j = 0

        for path in self._find(top):

            # Do the replacements.
            # ====================

            textfile = file(path, 'r+')
            tmp = textfile.read()

            if to_windows:
                cleaned, k = nix.subn('\r\n', tmp)
                cleaned, l = mac.subn('\r\n', cleaned)
            else:
                cleaned, k = win.subn('\n', tmp)
                cleaned, l = mac.subn('\n', cleaned)


            # Indicate progress.
            # ==================

            if k + l > 0:

                textfile.seek(0)
                textfile.truncate()
                textfile.write(cleaned)
                textfile.close()

                j += 1
                if j % 50 == 0:
                    sys.stdout.write('.')
                    sys.stdout.flush()

        print ' %s file%s cleaned' % (j, (j != 1) and 's' or '')


    def find_dirty(self, top, to_windows):
        """Given a tree root, find all text files that have unclean newlines.
        """
        for path in self._find(top):
            tmp = file(path, 'r').read()
            if to_windows:
                if nix.search(tmp):
                    print path
                elif mac.search(tmp):
                    print path
            else:
                if win.search(tmp):
                    print path
                elif mac.search(tmp):
                    print path


    def find(self, top, to_windows_ignored):
        """Given a tree root, walk the tree and find all text files.
        """
        for filepath in self._find(top):
            print filepath


    def _find(self, top):
        """Generator that yields paths of text files.
        """
        globs = self._confglobs()
        for path, dirs, filenames in os.walk(top):
            for pattern in globs:
                fullpattern = '%s/%s' % (path, pattern)
                for textfile in glob(fullpattern):
                    if not os.path.isfile(textfile):
                        continue # could be dir, eh?
                    yield textfile
            if '.svn' in dirs:
                dirs.remove('.svn')


if __name__ == '__main__':

    # Get our subcommand.
    # ===================

    subcommand = sys.argv[1:2]
    if not subcommand:
        print "see man 1 svneol for usage"
        sys.exit(2)
    elif subcommand not in (['clean'], ['confgen'], ['find_dirty'], ['find']):
        print "'%s' command not available; " % subcommand[0] +\
              "see man 1 svneol for usage"
        sys.exit(2)
    else:
        subcommand = subcommand[0]


    # Decide if we want to convert to windows newlines.
    # =================================================

    to_windows = False
    if '-w' in sys.argv:
        to_windows = True
        sys.argv.remove('-w')


    # Determine the root of the tree.
    # ===============================

    arg = sys.argv[2:3]
    if arg:
        path = arg[0]
    else:
        path = '.'
    path = os.path.realpath(path)


    # Instantiate and invoke the toolkit.
    # ===================================

    toolkit = EOLToolkit()
    func = getattr(toolkit, subcommand)
    try:
        func(path, to_windows)
    except IOError:
        pass # play nice with less(1)
