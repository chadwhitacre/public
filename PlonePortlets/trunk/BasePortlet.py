from Products.Archetypes.public import *
from Acquisition import aq_base, aq_parent, aq_inner
from AccessControl import ClassSecurityInfo
from Products.CMFCore.CMFCorePermissions import ModifyPortalContent
from Products.CMFCore.CMFCorePermissions import View
from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import createExprContext
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import cookString
from OFS.Cache import Cacheable
from interfaces import IPortlet


PortletSchema = BaseSchema + Schema((
        StringField('id',
               widget=IdWidget(visible={ 'edit' :'hidden', 'view' : 'hidden' })
                ),
        StringField('condition',
                    default='object/hasPortletData',
                    widget=StringWidget()
                ),
    ))


class Portlet(BaseContent, Cacheable):
    """A baseclass for Portlets"""
    schema = PortletSchema

    meta_type      = 'Portlet'
    archetype_name = 'Portlet'

    __implements__ = (IPortlet,) + BaseContent.__implements__

    actions = (
        {
        'id': 'edit',
        'name': 'Edit',
        'action': 'string:${object_url}/base_edit',
        'permissions': (ModifyPortalContent,)
        },
        )



    def __call__(self, callingcontext=None):
        """ render the portlet when called"""
        callingcontext = self.getCallingContext(callingcontext)
        if self.portletVisibilityInContext(callingcontext):
            return self.portlet_wrapper(callingcontext=callingcontext)
        return None

    security = ClassSecurityInfo()
    global_allow = 0

    helper_css = ''
    helper_js = ''
    default_template = 'portlet_default_contents'

    security.declarePrivate('getCallingContext')
    def getCallingContext(self, callingcontext=None):
        """Get the calling context"""
        if callingcontext is None:
            callingcontext = aq_parent(self)
        if callingcontext == getToolByName(self, 'portal_portlets'):
            callingcontext = getToolByName(self, 'portal_url').getPortalObject()
        return callingcontext

    security.declareProtected(View, 'portletName')    
    def portletName(self):
        """a sanitized name for the portlet for use in templates"""
        return cookString(self.Title())

    security.declareProtected(View, 'getPortletEmitter')    
    def getPortletEmitter(self):
        """return a template to render the contents of the portlet"""
        return self.default_template

    security.declarePublic('portletVisibilityInContext')
    def portletVisibilityInContext(self, context):
        """ this one should evaluate expressions"""
        context = self.getCallingContext(context)
        try:
            if self.condition and context is not None:
                folder = context
                portal = getToolByName(self, 'portal_url').getPortalObject()
                object = self
                __traceback_info__ = (portal, portal, object, self.condition)
                ec = createExprContext(folder, portal, object)
                return Expression(self.condition)(ec)
            else:
                return 0
        except AttributeError:
            return 0

        return self.hasPortletData()

    security.declareProtected(View, 'getPortletData')
    def getPortletData(self):
        """make sure we only fetch the portlet contents once in every request"""
        cachekey = self.UID()
        if self.REQUEST.has_key(cachekey):
#            self.plone_log(self.absolute_url(), 'cache hit in getPortletData %s' % self.getId())
            return self.REQUEST.get(cachekey)

        contents = self._fetchPortletData()

        self.REQUEST.set(cachekey, contents)
        return contents

    security.declareProtected(View, 'hasPortletData')
    def hasPortletData(self):
        """ condition to check whether we should render at all"""
        return self.getPortletData() and 1 or 0

    def _fetchPortletData(self):
        """ fetch the main contents of the portlet,
            this one should be overridden for subclasses
            so that it can easily be determined whether to
            show the portlet or not in context.
            Not to be called directly, call getPortletData"""
        
        return []

    def __url(self):
        return '/'.join( self.getPhysicalPath() )

    # we force these to catalog themselves in the portlets tool
    security.declareProtected(ModifyPortalContent, 'indexObject')
    def indexObject(self):
        pt = getToolByName(self, 'portal_portlets', None)
        pt.catalog_object(self, self.__url())

    security.declareProtected(ModifyPortalContent, 'unindexObject')
    def unindexObject(self):
        pt = getToolByName(self, 'portal_portlets', None)
        pt.uncatalog_object(self.__url())
        # Specially control reindexing to UID catalog
        # the pathing makes this needed
        self._uncatalogUID(self)

    security.declareProtected(ModifyPortalContent, 'reindexObject')
    def reindexObject(self, idxs=[]):
        if idxs == []:
            if hasattr(aq_base(self), 'notifyModified'):
                self.notifyModified()
        pt = getToolByName(self, 'portal_portlets', None)
        if pt is not None:
            #We want the intersection of the catalogs idxs
            #and the incoming list
            lst = idxs
            indexes = pt.indexes()
            if idxs:
                lst = [i for i in idxs if i in indexes]
            pt.catalog_object(self, self.__url(), idxs=lst)

        # Specially control reindexing to UID catalog
        # the pathing makes this needed
        self._catalogUID(self)


registerType(Portlet)
