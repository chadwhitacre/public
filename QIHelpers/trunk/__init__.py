from Skins      import  installSkins, uninstallSkins
from Properties import  installProperties
from Catalog    import  installIndices, uninstallIndices, \
                        installMetadata, uninstallMetadata

try:
    from Products.Archetypes.Extensions.utils import installTypes
except:
    pass
