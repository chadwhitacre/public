import os.path
from Globals import package_home
import Products.CMFCore

import Products.CMFCore.CMFCorePermissions as CMFCorePermissions

PKG_NAME = 'ATRatings'

GLOBALS = globals()

def getVersion():
    src_path = package_home(GLOBALS)
    f =  file(os.path.join(src_path, 'version.txt'))
    return f.read()


VERSION = getVersion()


def initialize(context):
    ##Import Types here to register them
    import RatingsTool
    
    Products.CMFCore.utils.ToolInit('Ratings Tool', tools=( RatingsTool.RatingsTool, ),
                   product_name=PKG_NAME,
                   icon='../CMFPlone/tool.gif',
                   ).initialize(context)
#                   icon='../CMFPlone/skins/plone_images/favorite_icon.gif'
                  