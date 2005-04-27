##parameters=inputname, inputvalue
from Products.PythonScripts.standard import structured_text as from_stx, \
                                            newline_to_br   as from_plain

fckeditor = context.portal_fckmanager.spawn(inputname)
useragent = context.REQUEST['HTTP_USER_AGENT']
fckeditor.SetCompatible(useragent)


# We are responsible to convert the value on the way from the object to the
# editor. The form action is responsible to convert back from HTML to whatever.

text_format = getattr(context, 'text_format', 'html')
transforms = { 'structured-text' : from_stx
             , 'plain'           : from_plain
             , 'html'            : lambda x: x
              }
transform = transforms.get(text_format)
fckeditor.SetProperty('Value', transform(inputvalue))

fckeditor.SetProperty('Height', 500)

return fckeditor.Create()