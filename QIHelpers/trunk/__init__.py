from Skins      import  installSkins, uninstallSkins
from Properties import  installFolderTypes
from Catalog    import  installIndices \
                        installMetadata

try:
    from Products.Archetypes.Extensions.utils import installTypes
except:
    pass
