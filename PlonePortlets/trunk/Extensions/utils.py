
from Products.CMFCore.utils import getToolByName
from AccessControl import ModuleSecurityInfo

security = ModuleSecurityInfo( 'Products.PlonePortlets.Extensions.utils' )

# fixme, declareprotected, 
security.declarePublic('registerPortlets')

def registerPortlets(self,types):
    """ register portlets """
    typesTool = getToolByName(self,'portal_types')
    PortletsToolTypeInfo = getattr(typesTool, 'PortletsTool', None)
    if not PortletsToolTypeInfo:
        raise AttributeError('PortletsTool')
    typeslist = list(PortletsToolTypeInfo.allowed_content_types)[:]
    for t in types:
        typename = t['portal_type']
        typeslist.append(typename)
    PortletsToolTypeInfo.allowed_content_types = tuple(typeslist)

def instantiatePortlet(self,portlettype,portletid,**kwargs):
    """ instantiate one portlet of the designated type"""
    portlets_tool = getToolByName(self,'portal_portlets')
    portlets_tool.invokeFactory( type_name=portlettype, id=portletid, **kwargs)
    portlet = getattr( portlets_tool, portletid )
    return portlet.UID()

def initializePortlet(self,portlettype,portletid,section,**kwargs):
    """ instantiate portlet and append it to a section immediately"""
    portlets_tool = getToolByName(self,'portal_portlets')
    newportletuid = instantiatePortlet(self,portlettype,portletid,**kwargs)
    portlets_tool.addPortletToSection(portlets_tool,newportletuid,section)