import os
from Globals import InitializeClass, DTMLFile, package_home
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from BTrees.OOBTree import OOBTree, OOSet
from Acquisition import aq_base, aq_chain
from Globals import InitializeClass
from DateTime import DateTime

from Products.CMFCore.utils import UniqueObject, getToolByName

from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.Expression import Expression

from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFPlone.PloneFolder import BasePloneFolder
from Products.CMFPlone.PloneUtilities import log as debug_log

from AccessControl import getSecurityManager

from types import StringType

from BTrees.OOBTree import OOBTree

from ComputedAttribute import ComputedAttribute
from Products.PlonePortlets.interfaces import IPortletsTool
from Products.PlonePortlets.Permissions import *

class PortletsTool( CatalogTool, BasePloneFolder, UniqueObject):
    """ Tool for managing portlets """
    id = 'portal_portlets'
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/book_icon.gif'
  
    meta_type = 'PortletsTool'
    archetype_name = 'PortletsTool'

    __implements__ = (IPortletsTool, CatalogTool.__implements__)

    security = ClassSecurityInfo()

    actions = (
        {
        'id': 'view',
        'name': 'View',
        'action': 'string:${object_url}/folder_contents',
        'permissions': (ModifyPortalContent,)
        },
        )

    
 
    def _getPortalTypeName(self):
        """hack"""
        return "PortletsTool"

    def manage_afterAdd(self, item, container):
        self.memberPortlets = OOBTree()
        self.groupPortlets = {}
        self.portletsdata = {}

    def __call__(self):
        """ Invokes the default view. """
        return self.folder_contents()

    def index_html(self):
        """ Acquire if not present. """
        return self.folder_contents()

    index_html = ComputedAttribute(index_html, 1)

    security.declareProtected(VIEW_PERMISSION, 'getAvailablePortlets')
    def getAvailablePortlets(self):
        """return available portlets"""
        return self.searchResults()

    security.declareProtected(VIEW_PERMISSION, 'getHelperCSS')
    def getHelperCSS(self, context):
        """helper css for all rendered portlets"""
        raise NotImplemented

    security.declareProtected(VIEW_PERMISSION, 'getHelperJs')
    def getHelperJs(self, context):
        raise NotImplemented

    def findPortletsForContext(self, context):
        """return available portlet UIDS sorted"""
        #if hasattr(self,'_v_pdata'):
        #    return self._v_pdata
        structures = []
        # traverse the aquisition chain to find portlets added/filtered by context
        for item in aq_chain(context):
            if hasattr(aq_base(item),'portletsdata'):
                structures.append(item.portletsdata.copy())
        # add the portets registered in the tool
        if self.portletsdata:
            structures.append(self.portletsdata)
        structures.reverse()

        # look up and add the portlets for groups the current user belongs to
        structures.extend(self.getMyGroupPortlets()[:])

        # finally the users own personal preferences. 
        structures.append(self.getPersonalPortlets().copy())
        pdata = {}
        for struct in structures:
            filterOut = struct.get('filterOut',[])[:]
            if filterOut:
                del struct['filterOut']
            # filter out all the uids in filterOut
            for filteritem in filterOut:
                for categories in pdata.values():
                    if filteritem in categories:
                        cat = list(categories[:])
                        cat.remove(filteritem)
                        categories = cat
            
            for key,val in struct.items():
                l = pdata.get(key,[])
                l.extend(val)
                pdata[key]= l
        #self._v_pdata = pdata
        return pdata

    security.declareProtected(VIEW_PERMISSION, 'getPortletsSection')
    def getPortletsSection(self,context,section):
        """ gets all portlet objects in a category"""
        portletsToRender = self.findPortletsForContext(context).get(section,[])
        results = self.searchResults(UID = portletsToRender)
        return results

    security.declareProtected(VIEW_PERMISSION, 'getPortletsSectionExplicit')
    def getPortletsSectionExplicit(self,context, section):
        """ gets all portlet objects in a category"""
        if hasattr(context.aq_base,'portletsdata'):
            data = getattr(context.aq_base,'portletsdata')
            uids = data.get(section,[])
            results = self.searchResults(UID = uids)
            return results
        else:
            return []
    
    def _rewrapPortlet(self,portlet,context):
        """ wraps a portlet in the current aquisition context, regardless of where it is located"""
        unwrapped = aq_base(portlet)
        rewrapped = unwrapped.__of__(context)
        return rewrapped

    def wrapAndFilterSection(self,context, section):
        """takes a section (left/right), acquisition-wraps it and returns it"""
        results = self.getPortletsSection(context,section)
        out = []
        for i in results: 
            o=i.getObject()
            if o == context:
                continue
            rewrapped = self._rewrapPortlet(o,context)
            # This can make cache less efficient, if it executes queries anyway.
#            if rewrapped.portletVisibilityInContext(context):
#                out.append(rewrapped)
            out.append(rewrapped)
        return out

    security.declareProtected(VIEW_PERMISSION, 'renderPortletsSection')
    def renderPortletsSection(self,context,section): 
        """return string of html, rendering a group of portlets"""
        portlets = self.wrapAndFilterSection(context, section)
        out = ''
        for p in portlets:
            try:
                portletoutput = p()
                if portletoutput:
                    out += portletoutput
            except KeyError, AttributeError:
                getToolByName(self, 'plone_utils').logException()
        return out

    security.declareProtected(MANAGE_PORTAL_PERMISSION, 'addPortletToSection')
    def addPortletToSection(self,context,portletUID,section):
        """ adds a portlet to a category/column"""
        data = {}
        if hasattr(aq_base(context),'portletsdata'):
            data = context.portletsdata.copy()
            if data.has_key(section):
                l = list(data[section][:])
                l.append(portletUID)
                data[section]=tuple(l)
            else:
                data[section]=(portletUID,)
            
        else: 
            data = {section:(portletUID,)}
        context.portletsdata = data

    security.declareProtected(MANAGE_PORTAL_PERMISSION, 'removePortletFromSection')
    def removePortletFromSection(self,context,portletUID,section):
        """ removes a portlet from a category/column"""
        data = {}
        if hasattr(aq_base(context),'portletsdata'):
            data = context.portletsdata.copy()
            if data.has_key(section):
                if portletUID in data[section]:
                    l = list(data[section][:])
                    l.remove(portletUID)
                    data[section] = tuple(l)
        context.portletsdata = data

    def addPortletToFilter(self,context,portletUID,section):
        """ adds a portlet to the ones filtered out in context"""
        pass

    # the personal settings
    #REMOVEME    
    def addPersonalPortletToSection(self,portletUID,section):
        pd = self.getPersonalPortlets()
        gr = pd.get(section,[])[:]
        if not portletUID in gr:
            gr.append(portletUID)
        pd[section] = gr
        self.setPersonalPortlets(pd)
        #not done

    def setPersonalFilter(self,portletUIDs):
        data = self.getPersonalPortlets()
        if not data.has_key('filterOut'):
            data[filterOut]=[]
        data[filterOut] = tuple(portletUIDs)
        self.setPersonalPortlets(data)

    security.declareProtected(SET_OWN_PROPERTIES_PERMISSION, 'setPersonalPortlets')
    def setPersonalPortlets(self,data):
        username = getSecurityManager().getUser().getUserName()
        self.memberPortlets[username]=data

    security.declareProtected(SET_OWN_PROPERTIES_PERMISSION, 'getPersonalPortlets')
    def getPersonalPortlets(self):
        username = getSecurityManager().getUser().getUserName()
        return self.memberPortlets.get(username,{}).copy()

    security.declareProtected(SET_OWN_PROPERTIES_PERMISSION, 'setPersonalPortletsBySection')
    def setPersonalPortletsBySection(self,portletUIDs, section):
        data = self.getPersonalPortlets()
        portlets = data.get(section,[])
        portlets = tuple(portletUIDs)
        data[section] = portlets
        self.setPersonalPortlets(data)
        # notify the persistence-machinery
        self._p_changed = 1

    security.declareProtected(VIEW_PERMISSION, 'getPersonalPortletsBySection')
    def getPersonalPortletsBySection(self,section):
        ps = self.getPersonalPortlets().get(section,[])
        results = self.searchResults(UID = ps )
        return results

    # GROUP METHODS

    security.declareProtected(MANAGE_PORTAL_PERMISSION, 'getMyGroupPortlets')
    def getMyGroupPortlets(self):
        grouptool = getToolByName(self,'portal_groups')
        username = getSecurityManager().getUser().getUserName()
        groupids = [i.getGroupId() for i in grouptool.getGroupsByUserId(username)]
        portletdefinitions =[]
        for gr in groupids:
            data = self.getPortletsForUserGroup(gr)
            if data:
                portletdefinitions.append(data.copy())
        return portletdefinitions

    security.declareProtected(MANAGE_PORTAL_PERMISSION, 'getPortletsForUserGroup')
    def getPortletsForUserGroup(self,usergroup):
        prefix = self.acl_users.getGroupPrefix()
        if prefix and not usergroup.startswith(prefix):
            usergroup = prefix+usergroup
        return self.groupPortlets.get(usergroup,{})

    security.declareProtected(MANAGE_PORTAL_PERMISSION, 'getPortletsForUserGroupBySection')
    def getPortletsForUserGroupBySection(self,usergroup,section):
        data = self.getPortletsForUserGroup(usergroup)
        portletuids = data.get(section,[])
        if not portletuids:
            return []
        return self.searchResults(UID = portletuids)

    security.declareProtected(MANAGE_PORTAL_PERMISSION, 'setPortletsForUserGroup')
    def setPortletsForUserGroup(self,usergroup,data):
        prefix = self.acl_users.getGroupPrefix()
        #self.groupPortlets[prefix+usergroup] = data
        groupportlets = self.groupPortlets.copy()
        groupportlets[prefix+usergroup] = data
        self.groupPortlets = groupportlets

    security.declareProtected(MANAGE_PORTAL_PERMISSION, 'setPortletsSection')
    def setPortletsSection(self, portletUIDs, section, context=None, usergroup=None):
        if usergroup:
            gd = self.getPortletsForUserGroup(usergroup)
            gd[section] = portletUIDs
            self.setPortletsForUserGroup(usergroup,gd)
        else:
            if context is None:
                context = self
            portletsdata = context.portletsdata.copy()
            portletsdata[section] = portletUIDs
            context.portletsdata = portletsdata

    def _verifyObjectPaste(self, object, validate_src=1):
        return BasePloneFolder._verifyObjectPaste(self, object, validate_src=1)


InitializeClass( PortletsTool )
