from Products.Archetypes.public import *

from Products.PlonePortlets.BasePortlet import Portlet, PortletSchema

Schema = PortletSchema + Schema((
        TextField('body',
              required=0,
              primary=1,
              default_output_type='text/html',
              allowable_content_types=('text/restructured',
                                       'text/plain',
                                       'text/html',
                                       'application/msword'),
              widget=RichWidget(),
              ),
        
    ))

class StaticPortlet(Portlet):
    """A basclass for Portlets"""
    schema = Schema
    
    meta_type      = 'StaticPortlet'
    archetype_name = 'Static Portlet'
    
    def getPortletEmitter(self):
        """return a template to render the contents of the portlet"""
        return 'portlet_static_contents'

    def _fetchPortletData(self):
        """ getting the content """
        return self.getBody()

registerType(StaticPortlet)
