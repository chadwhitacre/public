from Products.CMFCore.utils import getToolByName

def installIndices(portal, indices, out):
    """Add indices to the catalog on install"""
    catalog = getToolByName(portal, 'portal_catalog')
    for index in indices.keys():
        if index in catalog.indexes():
            print >> out, 'Warning: %s %s is already in the portal_catalog.' % (indices[index], index)
        else:
            catalog.addIndex(index, indices[index], extra=None)
            try:
                catalog.reindexIndex(index, None)
            except:
                pass
            print >> out, 'Successfully added %s %s to portal_catalog.' % (indices[index], index)
    
def installMetadata(portal, metadata, out):
    """Add metadata to the catalog on install"""
    catalog = getToolByName(portal, 'portal_catalog')
    for item in metadata:
        if item in catalog.schema():
            print >> out, 'Warning: %s is already in catalog metadata.' % item
        else:
            catalog.addColumn(item)
            print >> out, 'Successfully added %s to catalog metadata.' % item
