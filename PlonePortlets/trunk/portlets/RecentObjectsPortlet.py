from Products.Archetypes.public import *
from Products.PlonePortlets.BasePortlet import Portlet, PortletSchema
from Products.PluginIndexes import PluggableIndex
from Products.CMFCore.utils import getToolByName

MoreSchema = Schema((
        LinesField('typestolist',
                    widget=MultiSelectionWidget(),
                    vocabulary = 'getTypesInCatalog'
                ),
        StringField('sortindex',
                    widget=SelectionWidget(label='Sort Index'),
                    vocabulary = 'getSortableIndexes'
                ),
    StringField('sortorder',
                vocabulary=(('','Ascending'),('reverse','Descending')),
                widget=SelectionWidget(label='Sort direction'),
                ),
        
        IntegerField('numberofresults')
        
    ))


class RecentObjectsPortlet(Portlet):
    """A basclass for Portlets"""
    
    schema = PortletSchema + MoreSchema
    meta_type      = 'RecentObjectsPortlet'
    archetype_name = 'Recent Objects Portlet'
    
    def getPortletEmitter(self):
        """return a template to render the contents of the portlet"""
        return 'portlet_default_contents'

    def _fetchPortletData(self):
        """ getting the content """
        ct=getToolByName(self, 'portal_catalog')
        results = ct.searchResults(sort_on=self.getSortindex(),
                                   sort_order='reverse',
                                   review_state='published',
                                   Type=self.getTypestolist(),
                                   )[:self.getNumberofresults() ]
        return results

    def getTypesInCatalog(self):
        ct=getToolByName(self, 'portal_catalog')
        alltypes = ct.uniqueValuesFor('Type')
        return alltypes    

    def getWorkflowstatesInCatalog(self):
        ct=getToolByName(self, 'portal_catalog')
        states = ct.uniqueValuesFor('review_state')
        return states

    def getCatalogSchema(self):
        ct = getToolByName(self, 'portal_catalog')
        return ct.schema()

    def getSortableIndexes(self):
        """ get Indexes for which sorting is possible"""
        ct = getToolByName(self, 'portal_catalog')
        return [i.getId() for i in ct.index_objects() if PluggableIndex.SortIndex.isImplementedBy(i)]


registerType(RecentObjectsPortlet)
