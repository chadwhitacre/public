from Skins      import  installSkins
from Properties import  installFolderTypes, \
                        installRootProps
from Catalog    import  installIndices, \
                        installMetadata
from Portlets   import  uninstallPortlets, installPortlets
from Actions    import  uninstallActions, installActions
from Types      import  uninstallTypes
from Content    import  createFolders, createContent

def deleteObjects(portal, ids):
    for id in ids:
        parent = portal.unrestrictedTraverse(id).aq_parent
        parent.manage_delObjects(id)
