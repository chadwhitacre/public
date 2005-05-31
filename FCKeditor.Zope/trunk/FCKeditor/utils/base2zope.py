#!/usr/bin/env python
""" takes the FCKeditor base distribution in ../src/ and massages it for use in
Zope, outputting to ../skins/fckeditor_base/FCKeditor/
"""

import os
import re
import shutil
import sys


##
# initialize some variables
##

PRODUCT_ROOT = os.path.realpath(os.path.join('.','..'))
SRC_ROOT     = os.path.join(PRODUCT_ROOT, 'src')
DEST_ROOT    = os.path.join(PRODUCT_ROOT, 'skins', 'fckeditor_base', 'FCKeditor')



##
# decide what to do if DEST_ROOT is already there
##

def rm_rf(path):
    """ equivalent to rm -rf on Unix
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

if os.path.exists(DEST_ROOT):
    force = sys.argv[1:2] == ['--force']
    if not force:
        answer = raw_input( "destination directory already exists; " +\
                            "delete and recreate? (y/n) [n] "
                            )
        force = answer.lower() == 'y'
    if force:   rm_rf(DEST_ROOT)
    else:       sys.exit(1)
else:
    os.makedirs(DEST_ROOT)



##
# now walk the tree and transfer data to our output directory
##

METADATA = """\
[default]
cache = FCKcache"""

def metadata(filepath):
    """ given a filepath, write a complementary metadata file
    """
    mdpath = '.'.join((filepath, 'metadata'))
    mdfile = file(mdpath,'w+')
    mdfile.write(METADATA)
    mdfile.close()

cache_me  = ('css','gif','html','js','xml')
dont_want = ('asp','aspx','cfc','cfm','cgi','exe','htaccess','htc','php','pl')

for path, dirs, files in os.walk(SRC_ROOT):

    # determine and maybe create the destination
    relpath = path[len(SRC_ROOT)+1:]
    destpath = os.path.join(DEST_ROOT, relpath)
    if not os.path.exists(destpath):
        os.mkdir(destpath)

    for filename in files:

        src = os.path.join(path, filename)

        # alter the output filename if necessary
        ext = filename.split('.')[-1]
        if ext in ('html', 'xml'):
            filename += '.pt'
        dest = os.path.join(destpath, filename)

        # create the new file if we want it
        if (not filename.startswith('_')) and (ext not in dont_want):

            if ext == 'html':
                # Since Zope 2.7.2 we can't have '</' in javascript strings in page
                #  templates. It appears that FCKeditor only does this in <script>
                #  blocks, never in HTML attributes.

                inputfile = file(src)
                outputfile = file(dest, 'w+')

                SCRIPT = False
                for line in inputfile.readlines():

                    if line.count('<script'):   SCRIPT = True
                    if line.count('</script>'): SCRIPT = False

                    if SCRIPT:
                        line = line.replace(r'</', "<'+'/")

                    outputfile.write(line)

                inputfile.close()
                outputfile.close()

            else:
                # non-HTML files don't need any processing
                shutil.copy(src, dest)

            if ext in cache_me:
                metadata(dest)

    # skip svn directories
    if '.svn' in dirs: dirs.remove('.svn')

    # also skip extra FCKeditor directories
    for dirname in dirs[:]:
        if dirname.startswith('_'):
            dirs.remove(dirname)

"""
    from FCKeditor.ZopeCMF:

    Changes in Zope Package 03/04/05

    1. added : CPS compatibility
    2. added : FCK HHTP Cache for better compatibility with others Zope 2.xx based CMS
    3. added : ZPT example for CPS integration (popup_rte_form.pt)

    ##
    # change fckconfig.js -- shouldn't do this in fckeditor_base, maybe have an
    #  fckeditor_common?
    ##
    Change file fckconfig.js  (line 29 for skinPath)
    Change fonts in fckconfig.js
    Added default basepath in fckconfig.js
    Customization of toolbars in fckconfig.js


    ##
    # this will be in fckeditor_plone
    ##
    Added wysiwyg_support files (CMF template) for CMF integration
"""
