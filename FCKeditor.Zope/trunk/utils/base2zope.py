#!/usr/bin/env python
""" takes the FCKeditor base distribution in ../src/ and massages it for use in
Zope, outputting to ../skins/fckeditor_base/
"""

import os, shutil, sys



##
# initialize some variables
##

PRODUCT_ROOT = os.path.realpath(os.path.join('.','..'))
SRC_ROOT = os.path.join(PRODUCT_ROOT, 'src')
DEST_ROOT = os.path.join(PRODUCT_ROOT, 'skins', 'fckeditor_base')



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



##
# now walk the tree and transfer data to our output directory
##

METADATA = """\
[default]
cache = HTTPCache"""

def metadata(filepath):
    """ given a filepath, write a complementary metadata file
    """
    mdpath = '.'.join((filepath, 'metadata'))
    mdfile = file(mdpath,'w+')
    mdfile.write(METADATA)
    mdfile.close()

dont_want = ('asp','aspx','cfc','cfm','cgi','exe','htc','php','pl')

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
        if ext not in dont_want:
            shutil.copy(src, dest)
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

    Changes in FCK 2.0 FC-Preview for Plone/CMF integration :

    ##
    # rename certain files, create metadata files
    ##
    #The folder skins is renamed fck_skins because 'skins' is reserved in Zope CMF -- is this true?
        Change all files in ".html" as ".html.html"
        Rename fckstyles.xml in fckstyles.xml.pt for Zope compatibility
        Added a .metadata file for each file (for Zope HttpCache)
            [default]
            cache = HTTPCache
    Since Zope 2.7.2 Zope doesn't accept anymore "</" in javascript strings
    inside html files, for example we must change '</div>' in '<'+ '/div>'
    The ideal would be to have these changed in the base distribution
        Details : files and lines with corrections
        editor/fckdialog.html 40
        editor/fckdebug.html 38 46 78
        filemanager/browser/default/frmfolders.html 60 65 70
        filemanager/browser/default/frmresourceslist.html 47 52 58 67 75 79
        editor/dialog/fck_anchor.html  57
        editor/dialog/fck_specialchar.html  76 81 85 86 89
        editor/dialog/fck_smiley.html  70 76 77 80 81 84
        editor/dialog/fck_about.html  119
        editor/dialog/fck_spellerpages/spellchecker.html  many lines
"""





"""
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
