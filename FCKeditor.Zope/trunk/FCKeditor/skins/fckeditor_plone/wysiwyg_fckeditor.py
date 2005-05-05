##parameters=inputname, inputvalue
from Products.PythonScripts.standard import structured_text as from_stx, \
                                            newline_to_br   as from_plain

# instantiate an FCKeditor
fckeditor = context.portal_fckmanager.spawn(inputname)

# default height is too low; 200px
fckeditor.SetProperty('Height', 500)

# decide whether the user's browser can support a WYSIWidget
useragent = context.REQUEST['HTTP_USER_AGENT']
fckeditor.SetCompatible(useragent)


# We convert from whatever format the text is stored in to HTML. The FCKeditor
# object is responsible for HTML-encoding the value. And then the form action is
# responsible to convert back from HTML to whatever.

text_format = getattr(context, 'text_format', 'html')
default_transform = lambda x: x
transforms = { 'structured-text' : from_stx
             , 'plain'           : from_plain
             , 'html'            : default_transform
              }
transform = transforms.get(text_format, default_transform)
HTML = transform(inputvalue)
fckeditor.SetProperty('Value', HTML)


# return an HTML snippet
return fckeditor.Create()