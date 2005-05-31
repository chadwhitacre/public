#!/usr/bin/env python
"""Boilerplater adds boilerplate to a tree of files.

Boilerplater's primary use case is maintaining copyright and licensing
information for a software project. The script always operates on the current
working directory, and it takes a single argument, which is one of the
following:

  -?/-h/--help
    Print this help message.

  -r/--report
    Output a comparison of filetypes in your tree compared with filetypes that
    boilerplater knows about

  <filepath>
    Causes boilerplate to walk the current tree and apply the boilerplate found
    in the file at <filepath> to all files in the tree.

The power and convenience of boilerplater are in its smart application of your
boilerplate to various filetypes. That is, boilerplater adds boilerplate using
comment characters germane to a given filetype, and in a location in the file
suitable to the filetype.

If boilerplater doesn't know about a filetype in your tree, any files of that
type are silently ignored. By comparing the output of:

  $ boilerplater --find

With the output of:

  $ boilerplater --list

You can anticipate any filetypes for which you may need to write additional
plugins. See the source for documentation on writing plugins.

"""
__version__ = '0.1'
__author__ = 'Chad Whitacre <chad [at] zetaweb [dot] com>'

import os
import sys
from sets import Set

class File(file):
    """Represents a file to be boilerplated.

    File is intended to be subclassed for different types of files. There
    are four attributes that a subclass may want to override:

      first_line
        a string used to delimit the start of a boilerplate

      line_template
        a string used to construct the body of a boilerplate

      last_line
        a string used to delimit the end of a boilerplate

      get_appropriate_spot
        a method that tells where to insert a boilerplate

    Usage:

      >>> import File
      >>> l = File('BoilerplateMe.py')
      >>>

    """

    # These are meant to be overriden by subclasses, but are not meant to be
    # changed across instances of a particular File class.
    first_line    = '#BOILERPLATE%s\n' % ('#'*66)
    line_template = '#  %s  #\n'
    last_line     = '%sBOILERPLATE#\n' % ('#'*66)

    _filepath = ''
    _boilerplate = ''

    def __init__(self, filepath):
        """On construction, insert an empty boilerplate if not already present.

        We need to do this because Boilerplater assumes that File have a spot
        for boilerplate ready to be pasted over.

        """
        file.__init__(self, filepath, 'r+')
        self._boilerplate = self.read_boilerplate()
        if not self._boilerplate:
            self.prepare()

    def __repr__(self):
        return "<%s @ %s>" % (self.__name__, self.name)

    def read_boilerplate(self):
        """Return the current boilerplate or the empty string.
        """
        boilerplate = ''
        in_boilerplate = False
        for line in self:
            if line == self.first_line:
                in_boilerplate = True
            elif line == self.last_line:
                boilerplate += line
                break
            if in_boilerplate:
                boilerplate += line
        self.seek(0)
        return boilerplate

    def prepare(self):
        """Insert an empty boilerplate at the appropriate spot.
        """
        lines = self.readlines()
        if len(lines) > 0:
            i = self.get_appropriate_spot(lines)
        else:
            i = 0

        lines[i:i] = [self.first_line, self.last_line]

        data = ''.join(lines)
        self.save(data)

    def save(self, data):
        """Given a new file body, save it to disk and reset the cursor.
        """
        self.seek(0)
        self.truncate()
        self.write(data)
        self.seek(0)
        self._boilerplate = self.read_boilerplate()
        self.seek(0)

    def update(self, boilerplate):
        """Given some new boilerplate, format it and save it.
        """

        # Format it.
        formatted = ''
        if boilerplate <> '':
            lines = [''] + boilerplate.split('\n') + ['']
            for line in lines:
                pre, post = self.line_template.split('%s')
                width = 80 - len(pre) - len(post)
                formatted += self.line_template % line.ljust(width)[:width]
        formatted = self.first_line + formatted + self.last_line

        # Save it.
        text = self.read().replace(self._boilerplate, formatted)
        self.save(text)

    def get_appropriate_spot(self, lines):
        """Given a non-empty list of lines, return an int indicating the point
        in the sequence at which a boilerplate should be inserted.

        This is the primary method to override in File subclasses. In our
        reference implementation, we insert the boilerplate after an initial
        hashbang line.

        """
        if lines[0].startswith('#!'):
            return 1
        else:
            return 0

class Files:

    class sh(File):
        """File for shell scripts.
        """

    class py(File):
        """File for Python scripts.
        """

        # We use the stock boilerplate formatting.

        def get_appropriate_spot(self, lines):
            """Given a non-empty list of lines, return an int indicating the
            point in the sequence at which a boilerplate should be inserted.

            For Python scripts we insert the boilerplate after an initial hashbang
            line, or after an initial ## comment block. This latter is for Zope
            Scripts (Python).

            """
            if lines[0].startswith('#!'):
                return 1
            elif lines[0].startswith('##'):
                i = 0
                while lines[i].startswith('##'):
                    i += 1
                return i
            else:
                return 0

    class html(File):
        """File for HTML pages.
        """

        first_line    = "<!--BOILERPLATE%s >\n" % ('-'*62)
        line_template = "<  %s  >\n"
        last_line     = "<%sBOILERPLATE-->\n" % ('-'*64)

        def get_appropriate_spot(self, lines):
            """Given a non-empty list of lines, return an int indicating the
            point in the sequence at which a boilerplate should be inserted.

            For HTML pages, we want to insert our boilerplate after any initial
            DOCTYPE declaration.

            """
            if not lines[0].startswith('<!'):
                # no DOCTYPE, put our boilerplate first
                return 0
            else:
                i = 0
                while not lines[i].count('>') > 0:
                    print i
                    i += 1
                return i + 1


class Boilerplater:

    def __init__(self, root):
        """
        """
        self.root = root

    def __call__(self):
        """Default behavior is to walk and boilerplate.
        """
        for path, dirs, files in os.walk(root):
            for filename in files:
                filepath = os.path.join(path, filename)
                File = getattr(Files, self.ext(filepath), None)
                if File is not None:
                    File(filepath).update(boilerplate)
            if '.svn' in dirs: # skip Subversion directories
                dirs.remove('.svn')

    def report(self):
        """But we can also print a comparison of extension in the tree with
        extensions we know about.

        """

        # Get our info.
        # =============

        # first get the types from the tree
        tree = Set()
        for path, dirs, files in os.walk(self.root):
            for filename in files:
                filepath = os.path.join(path, filename)
                tree.add(self.ext(filepath))
            if '.svn' in dirs: # skip Subversion directories
                dirs.remove('.svn')

        # then get the types we know about
        known = Set()
        for ext in dir(Files):
            if not ext.startswith('_'):
                known.add(ext)

        # do a full outer join
        all = list(tree|known)
        all.sort()
        joined = []
        for ext in all:
            a = (ext in tree) and ext or '-'
            b = (ext in known) and ext or '-'
            joined.append((a,b))



        # Write the report.
        # =================

        width = 22 # total report width in characters
        w = width/2 # column width

        print
        print "     In Tree     Known About"
        print "="*(width+8)
        for row in joined:
            print "  %s  %s  " % ( row[0].rjust(w)[:w]
                                 , row[1].rjust(w)[:w]
                                  )
        print

    def ext(self, filepath):
        """Given a filepath, return the file extension with no dot, or the
        filename in the absence of an extension.
        """
        head, tail = os.path.split(filepath)
        parts = tail.split('.')
        if len(parts) == 1:
            ext = parts[0]
        else:
            ext = parts[-1]
        return ext



if __name__ == '__main__':
    root = os.path.realpath('.')
    arg = sys.argv[1:2]
    if not arg:
        print "see man 1 boilerplater for usage"
        sys.exit(2)
    arg = arg[0]

    boilerplater = Boilerplater(root)

    if arg in ('-?', '-h', '--help'):
        print __doc__
    elif arg in ('-r', '--report'):
        boilerplater.report()
    else:
        boilerplate = file(arg).read()
        boilerplater(boilerplate)
