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

def installMetadata(portal, metadata):
    """ Add metadata to the catalog """
    catalog = getToolByName(portal, 'portal_catalog')
    for item in metadata:
        if item not in catalog.schema():
            catalog.addColumn(item)
