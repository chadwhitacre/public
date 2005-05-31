========================================
    QUICK START
========================================

This package includes pure-Python base classes, and a full integration for a
stock Plone 2.0.5 portal. If you are not using stock Plone 2.0.5 content types,
then you will need to use the base classes and the Plone example to build a
custom integration for your Zope-based application.

Here's how to test-drive the bundled Plone integration:

    1. Install Plone 2.0.5 <http://plone.org/download/>.

    2. Unpack the FCKeditor.Zope archive in your Zope Products/ directory.

    3. Restart Zope.

    4. Add a Plone Site.

    4. Install FCKeditor using portal_quickinstaller.

    5. Browse to /index_html/document_edit_form. The body field should be an
       FCKeditor widget.


FCKeditor.Zope is (c) Chad Whitacre <http://www.zetadev.com/>, and is licensed
under the LGPL.



========================================
    INTRODUCTION
========================================

The heart of any content management system is its WYSIWYG editor, the rich-text
widget that makes using the web to write the web practical for the masses.
FCKeditor <http://www.fckeditor.net/> is one such widget. FCKeditor hews closely
to an MS Word model, making it much more comfortable for many users than Zope's
usual Epoz or Kupu. However, there are some cultural differences in the way it
is developed:

    - no version control

    - no unit testing

    - more VBScript than Python

    - more Windows-centric

    - communication is via SourceForge forums rather than mailings lists and
      freenode

    - single primary maintainer rather than distributed authority


These make the project somewhat awkward to interface with Zope, but I think
we've managed to find a workable situation in this Product.



========================================
    INTEGRATION NOTES
========================================

There are two two main points of integration for FCKeditor:

    1. An FCKeditor object that creates instances of the editor.

        You can use the fckeditor.js in the base distribution for client side
        creation, or you can use a server-side tool. The advantage of doing it
        server side is that you have greater control over configuration of the
        editor. For example, the bundled Plone integration delivers different
        toolbars to users based on their role.

    2. An FCKconnector object which handles the backend for the file browser.

        FCKeditor provides an abstracted file browser frontend that communicates
        with the server via XMLHttpRequest. This browser is used for inserting
        images and links into a document, but it also allows users to create
        folders and upload files.


And there are two basic integration strategies:

    1. "Light" integrations can be included in the base distribution.

        These allow you to create FCKeditor objects using the language
        of your choice. Currently supported options are: ASP, ColdFusion
        (both cfm and cfc), JavaScript, PHP, and Perl. The JavaScript
        implementation is the easiest to use, since it is client-side.
        The advantage to the others is tighter integration with your
        existing platform, and a marginal performance increase since the
        browser does not have to load the fckeditor.js file (6 kB).

    2. "Heavy" integrations repackage FCKeditor in a framework-specific
       distribution.

        There are currently packages for Java, .NET, and Plone. These provide
        the advantages of light server-side integrations, but in cases where the
        requirements of the framework make it difficult to incorporate the
        integration code with the main distribution.


This present package is a so-called "heavy" integration of FCKeditor. The base
distribution is included at the directory src/. A Zope-friendly version of the
base distribution is available at skins/fckeditor_base/FCKeditor. If CMFCore is
installed, then the skins directory will be available as a FileSystem Directory
View. There is also an fckeditor_plone directory in skins/, which the Plone
installer will add to portal_skins along with fckeditor_base.

A full test suite is included at tests/. ZopeTestCase and Plone are required to
run the tests.

If you checked FCKeditor.Zope out of Subversion, you will find developer-related
information at doc/README-DEV.txt. FCKeditor.Zope is developed in the Plone
Collective:

    https://svn.plone.org/svn/collective/FCKeditor.Zope/



========================================
    TWO ZOPE INTEGRATIONS?
========================================

This package is the second attempt at integrating FCKeditor with Zope. Jean-Mat
Grimaldi <http://www.macadames.com/> did the first integration, which is listed
on fckeditor.net under FCKeditor.Plone but is also called FCKeditor.ZopeCMF.
IMO, Jean-Mat's package is closer in culture to FCKeditor than to Zope/Plone:

    - no version control

    - no unit tests

    - released primarily as a Windows ZIP file

    - uses VBScript

    - single maintainer (Jean-Mat prefers not to host in the Collective)


There are other issues as well:

    - no server-side FCKeditor object

    - no integration with FCKeditor's file browser

    - no clean interface with the FCKeditor base distribution

    - I can't read French. :-(


For all of these reasons, I decided to start from scratch with FCKeditor.Zope. I
used some of Jean-Mat's ideas in Install.py, but other than that pretty much all
of the code is new.



========================================
    CUSTOMIZATION
========================================

Customizations can be performed at two levels:

    1. Filesystem

        If your Zope application doesn't use the stock Plone 2.0.5 content types
        then you will need to write a subclass of FCKconnector. The FCKeditor
        file browser reproduces fundamental CMS functionality, and decisions
        regarding content types and permissions are very application-specific.
        Rather than developing what would amount to a mini-language to describe
        this interface, it is easier and safer to just do it in Python.

    2. Plone-space

        If you plan on using FCKeditor.Zope with the stock Plone 2.0.5 content
        types, then you won't need to touch the Python modules. You can still
        customize some behavior by overriding the fckeditor_plone templates and
        scripts in portal_skins.


For both of these types of customization, please refer to the bundled Plone
integration for examples, and to the FCKeditor documentation for API:

    http://fckeditor.wikiwikiweb.de/



========================================
    FEEDBACK
========================================

Please direct inquiries regarding FCKeditor.Zope to the following locations:

    FCKeditor forums on SourceForge:
    http://sourceforge.net/forum/?group_id=75348

    plone-users mailing list:
    http://plone.org/contact/#users

    #plone chatroom
    http://plone.org/contact/chat
