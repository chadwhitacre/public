from Products.Archetypes.public import *

from Products.PlonePortlets.BasePortlet import Portlet, PortletSchema

Schema = PortletSchema + Schema((
        StringField('template',
              required=0),
        
    ))

class TemplatePortlet(Portlet):
    """A basclass for Portlets"""
    
    schema = Schema
    meta_type      = 'TemplatePortlet'
    archetype_name = 'Template Portlet'
    
    def getPortletEmitter(self):
        """return a template to render the contents of the portlet"""
        return self.getTemplate() or 'portlet_default_contents'

    def _fetchPortletData(self):
        """ getting the content """
        return "default"

registerType(TemplatePortlet)
