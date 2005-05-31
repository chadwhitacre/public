========================================
    QUICK START
========================================

This package includes pure-Python base classes, and a full integration for a
stock Plone 2.0.5 portal. The intention is that you will use the base classes
and the Plone example to build a custom integration for your Zope-based
application. Here's how to use the Plone integration:

    1. Install Plone 2.0.5 <http://plone.org/download/>.

    2. Unpack the FCKeditor.Zope archive in your Zope Products/ directory.

    3. Restart Zope.

    4. Install FCKeditor using portal_quickinstaller.

    5.



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
        editor. For example, the Plone integration delivers different toolbars
        to users based on their role.

    2. An FCKconnector object which handles the backend for the file browser.

        FCKeditor provides an abstracted file browser frontend that communicates
        with the server via XMLHttpRequest.


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

If you checked FCKeditor.Zope out of Subversion, you will need to manually
generate the skin/fckeditor_base/FCKeditor directory. This is done with the
base2zope.py script found in the utils/ directory. There is also a script called
testTemplates.py in utils/ that helps identify any problems with the base2zope
transformation. Please see the source of those scripts for more information.



========================================
    TWO ZOPE INTEGRATIONS?
========================================

This package is the second attempt at integrating FCKeditor with Zope. Jean-Mat
Grimaldi <http://www.macadames.com/> did the first integration, which is listed
on fckeditor.net under FCKeditor.Plone but is also called FCKeditor.ZopeCMF.
IMO, this package is closer in culture to FCKeditor than to Zope/Plone:

    - It is not under version control.

    - It is not unit tested.

    - It is released primarily as a Windows ZIP file.

    - It uses VBScript.

    - It has a single maintainer (Jean-Mat prefers not to host it in the
    Collective, e.g.).


There are other issues as well:

    - It doesn't provide integration with FCKeditor's file browser.

    - It doesn't interface cleanly with the FCKeditor base distribution.

    - I can't read French. :-(


For all of these reasons, I decided to start from scratch with FCKeditor.Zope. I
used some of Jean-Mat's ideas in Install.py, but other than that pretty much all
of the code is new.



========================================
    NOTES
========================================

FCKeditor.Zope and You

    1. base2zope.py

    2. testing



========================================
    CONCLUSION
========================================

Of the FOSS WYSIWYG editors, FCKeditor appears to have the most momentum behind
it, and the broadest appeal, though the cultural differences can make it
uncomfortable to work with. Both FCKeditor and FCKeditor.Zope are young, but
over the next 12-18 months I anticipate that they will mature into a compelling
solution for certain audiences to the heart of the CMS problem.
