========================================
    INTRO
========================================

Simplates are like Page Templates that do Python string replacement instead of
TAL compilation. They are great for dynamic plain-text templating. Here's how it
works:

  - There is an additional property called 'values' which is a list of paths to
    objects that return dictionaries.

  - Those paths are restrictedTraversed and a dictionary is built from the
    dictionaries they return.

  - The paths are prioritized top to bottom, so that items returned by calling
    the first path override items with the same key returned by subsequent
    paths.

  - The only special character is '%(', which can be escaped thus: '%%('.


For more information, see http://simplates.zetaweb.com.

String formatting is documented here:

    http://www.python.org/doc/current/lib/typesseq-strings.html



========================================
    INSTALL
========================================

Put it in your Products directory and smoke it. Requires CMFCore.



========================================
    CREDITS & LEGAL
========================================

Simplates was written by Steven Brown and Chad Whitacre of Zeta Design &
Development, based on the Zope Page Templates package released by Zope
Corporation.

Simplates is licensed under the ZPL 2.1, see LICENSE.txt and COPYRIGHT.txt.
