try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface


class IPortlet(Interface):
    """
    A Portlet is a small piece of the visual display, usually containing information,
    links or lists of objects. 
    """

    def portletName(self):
        """
        A sanitized name for the portlet for use in templates.
        """
    
    def getPortletEmitter():
        """
        The method getPortletEmitter takes no parameters, and returns a string
        that is the name of the output emitter, typically a page template,
        that will be used for rendering the portlet's contents.
        """

    def getPortletData():
        """
        This method returns the portlet contents, as strings, objects, brains, whatever.
        """

    def hasPortletData():
        """
        Returns true if the Portlet has any contents and should be rendered.
        """

    def portletVisibilityInContext(context):
        """ 
        True/false whether to render the portlet in a particular context.
        """

        
class IPortletsTool(Interface):
    """
    A tool to handle the Portlets 
    """
    
##    Methods from PortletsTool class (used while working on syncing interface)
##    getAvailablePortlets
##    getPortletsInContext
##    rewrapPortlet
##    renderPortletGroup
##    addPortletToGroup
##    removePortletFromGroup
##    addPortletToFilter
##    addPersonalPortletToGroup
##    addPersonalFilter
##    setPersonalPortlets
##    getPersonalPortlets
##    getPersonalPortletsGroup

    def getAvailablePortlets():
        """
        return all available portlet objects
        """
        
    def findPortletsForContext(context):
        """
        return all UIDs of portlets to render for a category, given the current calling context.
        """

    def getPortletsSection(context,section):
        """
        get all portlets in a given section by context
        """

    def getPortletsSectionExplicit(self,context, section):
        """
        get all portlets assigned to a secition in this excplicit context.
        avoiding acquisition
        """

    def renderPortletsSection(context,section):
        """
        render one section of portlets on screen
        """

    def getHelperCSS(self, context):
        """
        return the names of linked CSS files to include for the portlets
        that are currently being rendered
        """

    def getHelperJs(self,context):
        """
        return the names of linked Javascript files to include for the portlets
        that are currently being rendered
        """

    def addPortletToSection(context,portletUID,section):
        """
        appends a portlet to a category for rendering. 
        """

    def removePortletFromSection(context,portletUID,section):
        """
        removes a portlet UID from a category
        """ 

    def addPortletToFilter(context,portletUID):
        """
        add a portlet to the contextual filter
        """

    def addPersonalPortletToSection(portletUID,section):
        """
        add a portlet UID to a section to render per user
        """

    def setPersonalPortlets(data):
        """
        set the personal portlets for the current user
        """

    def getPersonalPortlets(self):
        """
        get the personal portlets for the current user
        returns a dict {section:[uids], etc}
        """

    def setPersonalPortletsBySection(portletUIDs, section):
        """
        set the personal portlets for the current users for a section
        portletUIDs is suppoed to be a list of UIDs
        """

    def getPersonalPortletsBySection(self,section):
        """
        get the personal portlets for a user for a section
        a list of uids
        """

    def getMyGroupPortlets(self):
        """
        get the portlets assigned to all groups the current user is
        a member of.
        returns a dict {section:[uids], etc}
        """

    def getPortletsForUserGroup(usergroup):
        """
        gets the portlets assigned to an arbitrary group
        returns a dict {section:[uids], etc}
        """

    def getPortletsForUserGroupBySection(usergroup,section):
        """
        gets the portlets assigned to an arbitrary group for a sepcified section
        returns a list of UIDs
        """        
        
    def setPortletsForUserGroup(usergroup,data):
        """
        set portlets for a defined group of users
        data is a dict with {section:[uids], etc}
        """

    def setPortletsSection(self, portletUIDs, section, context=None, usergroup=None):
        """
        save a list of portletUIDs for a defined section
        for either a group or an acquisition context
        """


