##############################################################################
#                                                                            #
#  (c) 2005 Chad Whitacre <http://www.zetadev.com/>                          #
#  This program is beerware. If you like it, buy me a beer someday.          #
#  No warranty is expressed or implied.                                      #
#                                                                            #
##############################################################################
"""This module contains three functions:

    zalk
        an implementation of os.walk for Zope

    isdir
        an example function for determining whether an object is a directory

    demo
        a demonstration of zalk usage

"""

from DateTime import DateTime
from StringIO import StringIO

out = StringIO()


def zalk(top, topdown=True):
    """Implement os.walk for Zope.

    The Python standard library includes a generator for walking arbitrary
    directory trees. Here is the documentation:

        http://www.python.org/doc/2.3.5/lib/os-file-dir.html#l2h-1477

    Zalk acts similarly, with the following changes:

        - Instead of returning strings (paths and file/directory names), zalk
          returns the full objects.

        - Zalk doesn't support the `onerror' parameter.

        - Since the definition of a directory in Zope is application-specific,
          isdir must be locally defined.

    """

    objs = top.objectValues()

    dirs, nondirs = [], []
    for obj in objs:
        if isdir(obj):
            dirs.append(obj)
        else:
            nondirs.append(obj)

    if topdown:
        yield top, dirs, nondirs
    for obj in dirs:
        for x in zalk(obj, topdown):
            yield x
    if not topdown:
        yield top, dirs, nondirs



# Define isdir.
# =============
# Here we will define directories in terms of their meta_type. You could also
# test for implementation of an interface, for example.

def isdir(obj):
    """Given an object, return a boolean indicating whether it is a directory.

    The definition of a directory in Zope is application-specific, so this
    function will need to be overriden for most cases.

    """
    if obj.meta_type == 'Folder':
        return True
    else:
        return False



# Use zalk.
# =========

def demo(self):
    """Zalk the tree rooted at '/' and reporting on what we find.
    """

    # Obtain the object at the root of our tree.
    # ==========================================

    root = self.restrictedTraverse('/')


    # Walk the tree with zalk, printing paths and subobject paths.
    # ============================================================

    for obj, dirs, files in zalk(root):
        path = '/'.join(obj.getPhysicalPath()) or '/'
        print >> out, path
        for child in dirs + files:
            childpath = '/'.join(child.getPhysicalPath())
            print >> out, "    %s" % childpath


    # Finish and return.
    # ==================

    print >> out, "\ndone @ %s" % DateTime().strftime('%I:%M.%S %p')
    return out.getvalue()
