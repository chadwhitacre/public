from Products.Archetypes.public import *

from Products.PlonePortlets.BasePortlet import Portlet, PortletSchema
from TemplatePortlet import TemplatePortlet, Schema

Schema = Schema.copy()
Schema['title'].default='Log in'
Schema['condition'].default='portal/portal_membership/isAnonymousUser'
Schema['template'].default='portlet_login_contents'

class LoginPortlet(TemplatePortlet):
    """A basclass for Portlets"""
    
    schema = Schema
    meta_type      = 'LoginPortlet'
    archetype_name = 'Login Portlet'

registerType(LoginPortlet)
