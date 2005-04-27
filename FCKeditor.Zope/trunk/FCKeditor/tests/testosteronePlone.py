"""Plone-specific tests, requires PloneTestCase
"""

import os, sys, time
from testosterone import testosterone
from pprint import pprint

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))


##
# Tweak the test fixture
##

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

ZopeTestCase.installProduct('FCKeditor')

from Products.FCKeditor.CMFFCKmanager import CMFFCKmanager
from Products.FCKeditor.ZopeFCKeditor import ZopeFCKeditor
from data import testdata

app = ZopeTestCase.app()



##
# Define our tests
##

testosterone("""\

# test installation w/ QuickInstaller
exec app.portal.portal_quickinstaller.installProduct('FCKeditor')
app.portal.portal_quickinstaller.isProductInstalled('FCKeditor')
isinstance(app.portal.portal_fckmanager, CMFFCKmanager)

# were skins installed properly?
hasattr(app.portal.portal_skins, 'fckeditor_base')
hasattr(app.portal.portal_skins, 'fckeditor_cps')
hasattr(app.portal.portal_skins, 'fckeditor_plone')

fckeditor = app.portal.portal_fckmanager.spawn('fieldname')
isinstance(fckeditor, ZopeFCKeditor)

# request here doesn't have a valid useragent, so we just get the plain textarea
foo = app.portal.restrictedTraverse('portal_skins/fckeditor_plone/wysiwyg_fckeditor')
foo('MyField', '') == testdata.TEXTAREA


""", globals(), locals())
