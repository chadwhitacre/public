## Script (Python) "setPersonalPortletConfig"
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

portletstool.setPersonalPortletsBySection(form.get('column1',[]),'column1')
portletstool.setPersonalPortletsBySection(form.get('column2',[]),'column2')


return context.REQUEST.RESPONSE.redirect(context.portal_url()+'/personalize_portlets')
