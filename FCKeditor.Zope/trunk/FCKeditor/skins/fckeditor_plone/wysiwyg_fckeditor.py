##parameters=inputname, inputvalue, tabindex=0
#BOILERPLATE###################################################################
#                                                                             #
#  This package wraps FCKeditor for use in the Zope web application server.   #
#  Copyright (C) 2005 Chad Whitacre <http://www.zetadev.com/>                 #
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
###################################################################BOILERPLATE#

# Imports
# =======

import AccessControl
from Products.PythonScripts.standard import structured_text as stx2html, \
                                            newline_to_br   as plain2html
from Products.FCKeditor import PloneFCKeditor



# Instantiate an FCKeditor.
# =========================

fckeditor = PloneFCKeditor(inputname)



# Configure the instance.
# =======================

fckeditor.SetConfig('CustomConfigurationsPath', '/fckcustom.js')
fckeditor.SetCompatible(context.REQUEST['HTTP_USER_AGENT'])
fckeditor.SetProperty('Height', 500) # default is 200 -- too small
fckeditor.SetProperty('tabindex', tabindex)

user = AccessControl.getSecurityManager().getUser()
if user.has_role(['Manager',]):
    fckeditor.SetProperty('ToolbarSet', 'Default')
else:
    fckeditor.SetProperty('ToolbarSet', 'Basic')



# Set the initial value.
# ======================
# FCKeditor is only useful to edit content in HTML, so in the case where our
# object's data is in a different format, we have to convert it HTML. However,
# this conversion is a one way street, because we always pass data back to the
# object as HTML. Unless, that is, the object wants to transform from HTML,
# but that is its responsibility.

text_format = getattr(context, 'text_format', 'html')
if text_format == 'html':
    HTML = inputvalue
elif text_format == 'plain':
    HTML = plain2html(inputvalue)
elif text_format == 'structured-text':
    HTML = stx2html(inputvalue)
#elif text_format == 'restructured-text':
#    HTML = rest2html(inputvalue)
else:
    HTML = inputvalue
fckeditor.SetProperty('Value', HTML)



# Return an HTML snippet.
# =======================

return fckeditor.Create()
