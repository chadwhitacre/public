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

def installSkins(portal, skins_abspath, GLOBALS, out):
    skins_tool = getToolByName(portal, 'portal_skins')
    addDirectoryViews(skins_tool, 'skins', GLOBALS)
    out.write("Added 'skins' directory view to portal_skins\n")
    
    skins = skins_tool.getSkinSelections()
    for skin in skins:
        path = skins_tool.getSkinPath(skin)
        #split up the skin path and  insert the current one just after custom if its not already in there
        path = [s.strip() for s in path.split(',') if s]
        skins_to_add = getSkins(skins_abspath)
        skins_to_add.reverse()
        for n in skins_to_add:
            if n not in path:
                try: path.insert(path.index('custom')+1, n)
                except ValueError:
                    path.append(n)
                print >> out, "Added '%s' to %s skin\n" % (n,skin)
            else:
                print >> out, "Skipping '%s' for %s skin\n" % (n,skin)
        path = ','.join(path)
        # addSkinSelection will replace existing skins as well.
        skins_tool.addSkinSelection(skin, path)


def uninstallSkins(portal, skins_abspath, out):
    skins_tool = getToolByName(portal, 'portal_skins')
    
    # Go through the skin configurations and remove our skins
    skins = skins_tool.getSkinSelections()
    for skin in skins:
        path = skins_tool.getSkinPath(skin)
        path = [s.strip() for s in path.split(',') if s]
        for n in getSkins(skins_abspath):
            if n in path:
                path.remove(n)
                print >> out, "Removing '%s' from %s skin\n" % (n,skin)
        path = ','.join(path)
        # addSkinSelection will replace existing skins as well.
        skins_tool.addSkinSelection(skin, path)