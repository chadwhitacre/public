from Products.CMFCore.utils import getToolByName


##
# Portlet helpers (will move to QIHelpers)
##

def uninstallPortlets(portal, portlets):
    """ takes a sequence of (portlet_id, category) tuples """
    portlets_tool = getToolByName(portal, 'portal_portlets', None)

    for portlet in portlets:
        portlets_tool.removePortletFromSection(portlets_tool,portlet[0],portlet[1])
        portlets_tool.manage_delObjects(portlet[0])

def installPortlets(portal, portlets):
    """  """
    from Products.PlonePortlets.Extensions.utils import initializePortlet
    portlets_tool = getToolByName(portal, 'portal_portlets', None)

    for portlet in portlets:
        initializePortlet(portlets_tool,'TemplatePortlet',portlet[0],'column1',**portlet[1])
