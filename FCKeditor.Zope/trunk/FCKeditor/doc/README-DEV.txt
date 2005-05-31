This document contains information about developing the FCKeditor.Zope package.
For information about using FCKeditor.Zope, including using it as a basis for
your own custom FCKeditor integration, please see ../README.txt.

Notes:

    The FCKeditor base distribution is incorporated into this package via an
    svn:externals on trunk/. However, the main FCKeditor does not use version
    control, so we also provide storage of base FCKeditor releases at _storage/

    The skins/fckeditor_base directory is ignored by the repo, as is archives/.

    You will need to generate the skins/fckeditor_base/FCKeditor directory. This
    is done with the base2zope.py script found in the utils/ directory. There is
    also a script called testTemplates.py in utils/ that helps identify any
    problems with the base2zope transformation. Please see the source of those
    scripts for more information.

    A Makefile is included with the following targets:

        clean
            removes *.pyc files and the staging archives

        squeaky
            above, plus deletes and recreates the src/ and skin/fckeditor_base/
            directories

        dist
            packages FCKeditor.Zope for distribution, outputting tgz, tbz, and
            zip files in archives/; archives don't include the Makefile, nor
            the doc, src, and util directories


    This package makes use of the following utilites:

        boilerplater -- adds boilerplate to a tree of files
          http://svn.zetadev.com/repos/public/boilerplater/trunk/

        svneol -- a line endings toolkit for Subversion
          http://svn.zetadev.com/repos/public/svneol/trunk/
