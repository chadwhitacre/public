## Script (Python) "setPortletConfig"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
portal = context.portal_url.getPortalObject()
portletstool = getattr(portal ,'portal_portlets')
form = context.REQUEST.form

usergroup = form.get('usergroup',None)  

portletstool.setPortletsSection(form.get('column1',[]),'column1',usergroup=usergroup)
portletstool.setPortletsSection(form.get('column2',[]),'column2',usergroup=usergroup)

if usergroup:
    return context.REQUEST.RESPONSE.redirect(context.portal_url()+'/prefs_portlets_groups?groupname='+usergroup)
return context.REQUEST.RESPONSE.redirect(context.portal_url()+'/prefs_portlets')
