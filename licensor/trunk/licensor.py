#!/usr/local/bin/python
# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

__version__ = '0.1'
__author__ = 'Chad Whitacre <chad [at] zetaweb [dot] com>'

import os
import sys

class Licensee(file):
    """Represents a file to be licensed.

    Licensee is intended to be subclassed for different types of files. There
    are four attributes that a subclass will want to override:

      first_line -- a string used to delimit the start of a license
      last_line -- a string used to delimit the end of a license
      line_template -- a string used to construct the body of a license
      get_appropriate_spot -- a method that tells where to insert a license

    Usage:

      >>> import Licensee
      >>> l = Licensee('LicenseMe.py')
      >>>

    """

    # These are meant to be overriden by subclasses, but are not meant to be
    # changed across instances of a particular Licensee class.
    first_line = '#LICENSOR%s\n' % ('#'*70)
    last_line = '%sLICENSOR#\n' % ('#'*70)
    line_template = '#  %s  #\n'

    _filepath = ''
    _license = ''

    def __init__(self, filepath):
        """On construction, insert an empty license if not already present.

        We need to do this because Licensor assumes that Licensees have a spot
        for a license ready to be pasted over. I.e., that they've "filled out
        their application," so to speak.

        """
        file.__init__(self, filepath, 'r+')
        self._license = self.read_license()
        if not self._license:
            self.prepare()

    def __repr__(self):
        return "<Licensee @ %s>" % self.name

    def __str__(self):
        return self._license
    __call__ = __str__

    def read_license(self):
        """Return the current license or the empty string.
        """
        license = ''
        in_license = False
        for line in self:
            if line == self.first_line:
                in_license = True
            elif line == self.last_line:
                license += line
                break
            if in_license:
                license += line
        self.seek(0)
        return license

    def prepare(self):
        """Insert an empty license at the appropriate spot.
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
        self._license = self.read_license()
        self.seek(0)


    def update(self, license):
        """Given a new license, format it and save it.
        """

        # Format it.
        formatted = ''
        if license <> '':
            lines = [''] + license.split('\n') + ['']
            for line in lines:
                pre, post = self.line_template.split('%s')
                width = 80 - len(pre) - len(post)
                formatted += self.line_template % line.ljust(width)[:width]
        formatted = self.first_line + formatted + self.last_line

        # Save it.
        text = self.read().replace(self._license, formatted)
        self.save(text)

    def get_appropriate_spot(self, lines):
        """Given a non-empty list of lines, return an int indicating the point
        in the sequence at which a license should be inserted.

        This is the primary method to override in Licensee subclasses. In our
        reference implementation, we insert the license after an initial
        hashbang line.

        """
        if lines[0].startswith('#!'):
            return 1
        else:
            return 0

class sh(Licensee):
    """Licensee for shell scripts.
    """

class Licensor:

    registry = { 'sh':sh
               ,
                }

    def __init__(self, top, license):
        """Given tree root and a license, apply the license to the tree.
        """
        self.license = license
        for path, dirs, files in os.walk(top):
            for filename in files:
                filepath = os.path.join(path, filename)
                self.apply_license(filepath)

            if '.svn' in files: # skip Subversion directories
                dirs.remove('.svn')

    def apply_license(self, filepath):
        """Given a filepath, update the license on the file.
        """
        head, tail = os.path.split(filepath)
        parts = tail.split('.')
        if len(parts) == 1:
            ext = parts[0]
        else:
            ext = parts[-1]

        licensee = self.registry.get(ext, None)
        if licensee is None:
            return
        else:
            licensee(filepath).update(self.license)


if __name__ == '__main__':

    # Determine the root of the tree we are licensing.
    # ================================================

    top = os.path.realpath('.')



    # Get the text of our license.
    # ============================

    license = sys.argv[1:2]
    if not license:
        print "see man 1 licensor for usage"
        sys.exit(2)
    else:
        license = file(license[0]).read()



    # Invoke the Licensor.
    # ====================================

    Licensor(top, license)
