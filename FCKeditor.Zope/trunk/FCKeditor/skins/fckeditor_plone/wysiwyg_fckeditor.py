##parameters=inputname, inputvalue
import AccessControl
from Products.PythonScripts.standard import structured_text as stx2html, \
                                            newline_to_br   as plain2html
from Products.FCKeditor import ZopeFCKeditor


# instantiate an FCKeditor
fckeditor = ZopeFCKeditor(inputname)

# tell FCKeditor about our custom runtime config file:
fckeditor.SetConfig('CustomConfigurationsPath', '/fckcustom.js')

# decide whether the user's browser can support a WYSIWidget
useragent = context.REQUEST['HTTP_USER_AGENT']
fckeditor.SetCompatible(useragent)

return fckeditor.Create()

# default height is 200px -- too short
fckeditor.SetProperty('Height', 500)

# We convert from whatever format the text is stored in to HTML. The FCKeditor
# object is responsible for HTML-encoding the value. And then the form action is
# responsible to convert back from HTML to whatever.
text_format = getattr(context, 'text_format', 'html')
if text_format == 'html':
    HTML = inputvalue
if text_format == 'plain':
    HTML = plain2html(inputvalue)
elif text_format == 'structured-text':
    HTML = stx2html(inputvalue)
else:
    HTML = inputvalue
fckeditor.SetProperty('Value', HTML)

# pick a toolbar set based on user role
user = AccessControl.getSecurityManager().getUser()
if user.has_role(['Manager',]):
    fckeditor.ToolbarSet = 'Default'
else:
    fckeditor.ToolbarSet = 'Basic'

# return an HTML snippet
return fckeditor.Create()