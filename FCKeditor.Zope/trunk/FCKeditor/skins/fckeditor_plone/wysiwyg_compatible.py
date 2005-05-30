from Products.FCKeditor import ZopeFCKeditor
return ZopeFCKeditor.IsCompatible(context.REQUEST['HTTP_USER_AGENT'])