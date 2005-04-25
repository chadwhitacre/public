from Products.FCKeditor import ZopeFCKeditor
useragent = context.REQUEST.get('HTTP_USER_AGENT','')
fck = ZopeFCKeditor('MyFCKeditor')
return fck(useragent)