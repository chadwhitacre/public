from Products.Archetypes.public import *

from Products.PlonePortlets.BasePortlet import Portlet, PortletSchema

class WorklistsPortlet(Portlet):
    """A basclass for Portlets"""
    
    schema = PortletSchema
    meta_type      = 'WorklistsPortlet'
    archetype_name = 'Worklists Portlet'
    
    def getPortletEmitter(self):
        """return a template to render the contents of the portlet"""
        return 'portlet_worklist_contents'

    def _fetchPortletData(self):
        """ getting the content """
        return self.aq_parent.my_worklist()
    
registerType(WorklistsPortlet)
