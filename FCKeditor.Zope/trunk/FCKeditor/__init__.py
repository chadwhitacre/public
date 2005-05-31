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
# Imports
# =======

from AccessControl import allow_class
from FCKexception import FCKexception  # the next import imports this from here
from FCKeditor import FCKeditor as ZopeFCKeditor # so import order is important



# Conditional Imports
# ===================

# Do we have CMFCore?
try:
    from Products.CMFCore.DirectoryView import registerDirectory
    CMFCore = True
except ImportError:
    CMFCore = False

# Do we have CMFPlone?
try:
    from Products import CMFPlone
    Plone = True
    from Products.FCKeditor.PloneFCKeditor import PloneFCKeditor
    from Products.FCKeditor import PloneFCKconnector
except ImportError:
    Plone = False



# Expose PloneFCKeditor to restricted Python.
# ===========================================

if Plone:
    allow_class(PloneFCKeditor)



# Initialize the Product.
# =======================

FCKglobals = globals()
def initialize(registrar):

    if CMFCore:
        registerDirectory('skins', FCKglobals)

    if Plone:
        PloneFCKconnector.initialize(registrar)
