from Products.Archetypes.public import *
from Acquisition import aq_base, aq_chain
from Products.PlonePortlets.BasePortlet import Portlet, PortletSchema
from DateTime import DateTime
Schema = PortletSchema 

class ClockPortlet(Portlet):
    """This is an example of how simple portlet can be. 
	   A clock portlet is not much fun, but it kinda shows you how it all works"""
    schema = Schema
    
    meta_type      = 'ClockPortlet'
    archetype_name = 'ClockPortlet'
    
    def getPortletEmitter(self):
        """return a template to render the contents of the portlet"""
        return 'portlet_static_contents'

    def _fetchPortletData(self):
        """ getting the content """
        return str(DateTime())

registerType(ClockPortlet)
