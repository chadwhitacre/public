from StringIO import StringIO
from Products.CMFCore.utils import getToolByName, manage_addTool
import Products.ATRatings as ATRatings

import sys, os, string

#def uninstall(self):
#    out=StringIO()
#    return out.getvalue()


def install(self):
    out=StringIO()

    if not hasattr(self,'portal_ratings'):
        m = self.manage_addProduct['ATRatings']
        manage_addTool(m, 'Ratings Tool')

    return out.getvalue()