from Products.Archetypes.public import *
from Products.PlonePortlets.BasePortlet import Portlet, PortletSchema
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_chain , aq_base

NavTreeSchema = Schema((
    StringField('sortAttribute',
                vocabulary='getCatalogSchema',
                widget=SelectionWidget(label='attribute to order results by'),
                ),
    StringField('sortOrder',
                vocabulary=['asc','desc'],
                widget=SelectionWidget(label='sort direction: asc or desc'),
                ),
    IntegerField('sitemap_depth',
                accessor='getSitemapDepth',
                default=3,
                widget=StringWidget(label='Depth of sitemap'),
                ),
    ))
class NavTreePortlet(Portlet):
    """A navigation portlet"""
    
    schema = PortletSchema + NavTreeSchema
    meta_type =  archetype_name = 'NavTreePortlet'

    def getPortletEmitter(self):
        """return a template to render the contents of the portlet"""
        return 'portlet_navtree_template'

    def _fetchPortletData(self):
        """ getting the content """
        ct=getToolByName(self, 'portal_catalog')
        context = self.getCallingContext()
        currentPath = None
        rawresult = []
        if context == self:
            currentPath = getToolByName(self, 'portal_url').getPortalPath()
            rawresult = ct(path={'query':currentPath, 'depth':self.getSitemapDepth()})
        else:
            currentPath = '/'.join(context.getPhysicalPath())
            rawresult = ct(path={'query':currentPath, 'navtree':1})
        
        # Build result dict
        result = {}
        for item in rawresult:
            path = item.getPath()
            data = {'Title':item.Title or item.getId,
                    'currentItem':path == currentPath,
                    'absolute_url': item.getURL(),
                    'getURL':item.getURL(),
                    'path': path,
                    'icon':item.getIcon,
                    'creation_date': item.CreationDate,
                    'review_state': item.review_state,
                    'Description':item.Description,
                    'children':[]}
            parentpath = '/'.join(path.split('/')[:-1])
            # Tell parent about self
            if result.has_key(parentpath):
                result[parentpath]['children'].append(data)
            else:
                result[parentpath] = {'children':[data]}
            # If we have processed a child already, make sure we register it
            # as a child
            if result.has_key(path):
                data['children'] = result[path]['children']
            result[path] = data

        portalpath = getToolByName(self, 'portal_url').getPortalPath()
        if result.has_key(portalpath):
            return result[portalpath]
        else:
            return {}

    def getMoreLink(self):
        if len(self.getPortletData()) > self.getCropLength():
            return "%s/portal_portlets/%s/%s" % (self.getCallingContext().absolute_url(),self.getId(),'sitemap_view')
        else:
            return None

    def getCatalogSchema(self):
        ct = getToolByName(self, 'portal_catalog')
        return ct.schema()

        
registerType(NavTreePortlet)
