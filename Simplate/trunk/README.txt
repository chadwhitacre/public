This is a very simple wrapper around the stock Zope File product that allows you 
to do python string formatting on your file body. Our immediate use case is 
dynamic CSS files: no more DTML CSS files in Plone! Yay!

Here's how it works:

  - There is an additional property called 'values' which is a list of paths to 
    objects that return dictionaries.

  - Those paths are restrictedTraversed and a dictionary is built from the 
    dictionaries they return.

  - The paths are prioritized top to bottom, so that items returned by calling 
    the first path override items with the same key returned by subsequent 
    paths.

  - The only special character is '%(', which can be escaped thus: '%%('.


String formatting is documented here:

    http://www.python.org/doc/current/lib/typesseq-strings.html


INSTALL
---------------------------
Put it in your Products directory and smoke it.


TODO
---------------------------
FSSimplate for use in Filesystem Directory Views
PloneSimplate for use in Plone
Rewrite the ZMI interface in ZPT :p


CREDITS
---------------------------
Steven Brown    steve@zetaweb.com   beren1hand
Chad Whitacre   chad@zetaweb.com    whit537