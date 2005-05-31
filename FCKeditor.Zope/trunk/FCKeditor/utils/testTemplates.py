#BOILERPLATE###################################################################
#                                                                             #
#  This package wraps FCKeditor for use in the Zope web application server.   #
#  Copyright (C) 2005 Chad Whitacre < http://www.zetadev.com/ >               #
#                                                                             #
#  This library is free software; you can redistribute it and/or modify it    #
#  under the terms of the GNU Lesser General Public License as published by   #
#  the Free Software Foundation; either version 2.1 of the License, or (at    #
#  your option) any later version.                                            #
#                                                                             #
#  This library is distributed in the hope that it will be useful, but        #
#  WITHOUT ANY WARRANTY; without even the implied warranty of                 #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser    #
#  General Public License for more details.                                   #
#                                                                             #
#  You should have received a copy of the GNU Lesser General Public License   #
#  along with this library; if not, write to the Free Software Foundation,    #
#  Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA                #
#                                                                             #
#                                                                             #
###################################################################BOILERPLATE#

"""This script walks the tree at ../skins/fckeditor_base/FCKeditor and compiles
all of the files with extension .pt as page templates. With no arguments it
prints out a summary of errors and warnings for all files. Files with errors are
indexed in the summary. Pass one of those integers to the script for details on
that file. Examples:

  $ python testTemplates.py
   #  File                                                          Err  Warn
  ===========================================================================
   1  editor/fckdialog.html.pt                                       x
   2  editor/fckdebug.html.pt                                        x
   3  editor/dialog/fck_about.html.pt                                x
  ...
  $ python testTemplates.py 8
  file: editor/filemanager/browser/default/frmresourceslist.html.pt

  error: ['Compilation failed', 'TAL.HTMLTALParser.NestingError: Open tags
  ...

Note that there appear to be some red herrings, especially with XML page
templates. I.e., files that throw an error in this script, although they appear
to work fine in real life. I didn't take the time to track down what was going
on.

"""

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], '..', 'tests', 'framework.py'))


from Products.PageTemplates.PageTemplate import PageTemplate

fileindex = sys.argv[1:2]
if fileindex:
    fileindex = fileindex[0]

top = os.path.join(sys.path[0],'..','skins','fckeditor_base','FCKeditor')
baddies = {}; i=0

# walk the tree looking for bad page templates
for path, dirs, files in os.walk(top):

    for filename in files:
        ext = filename.split('.')[-1]
        if ext == 'pt':
            text = file(os.path.join(path, filename)).read()
            ZPT = PageTemplate(); ZPT.write(text)
            errors = ZPT._v_errors
            warnings = ZPT._v_warnings

            if len(errors) + len(warnings) > 0:
                i += 1
                filepath = os.path.join(path[len(top)+1:], filename)
                if len(errors) > 0: haserrors = 'x'
                else:               haserrors = ' '
                if len(warnings) > 0:   haswarnings = 'x'
                else:                   haswarnings = ' '
                baddies[i] = { 'index'      : str(i).rjust(2)
                             , 'filepath'   : filepath.ljust(64)
                             , 'errors'     : errors
                             , 'haserrors'  : haserrors
                             , 'warnings'   : warnings
                             , 'haswarnings': haswarnings
                              }

    if '.svn' in dirs: dirs.remove('.svn')

if baddies:
    if fileindex:
        # show all errors for one file
        baddie = baddies[int(fileindex)]
        print """
file: %(filepath)s

error: %(errors)s

warnings: %(warnings)s
""" % baddie

    else:
        # show a summary of all errors

        print """
 #  File                                                              Err  Warn"""
        print "="*79
        keys = baddies.keys(); keys.sort()
        for key in keys:
            print """\
%(index)s  %(filepath)s   %(haserrors)s    %(haswarnings)s""" % baddies[key]
        print
