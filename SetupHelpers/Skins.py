import os
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.DirectoryView import addDirectoryViews

def getSkins(top):
    skins = []
    for r,d,f in os.walk(top):
        r = r.replace(top, '', 1)
        if r and not r.count('.svn'):
            skins.append(r.replace('\\','/')[1:])
    return skins

def installSkins(portal, skins_abspath, GLOBALS):
    skins_tool = getToolByName(portal, 'portal_skins')
    addDirectoryViews(skins_tool, 'skins', GLOBALS)

    skins = skins_tool.getSkinSelections()
    for skin in skins:
        path = skins_tool.getSkinPath(skin)
        #split up the skin path and  insert the current one just after custom if its not already in there
        path = [s.strip() for s in path.split(',') if s]
        skins_to_add = getSkins(skins_abspath)
        skins_to_add.reverse()
        for n in skins_to_add:
            if n not in path:
                try:
                    path.insert(path.index('custom')+1, n)
                except ValueError:
                    path.append(n)
        path = ','.join(path)
        # addSkinSelection will replace existing skins as well.
        skins_tool.addSkinSelection(skin, path)
