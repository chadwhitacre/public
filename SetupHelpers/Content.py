from Products.CMFCore.utils import getToolByName

"""

Content creation is factored into separate scripts for folder structure and
content objects. This neatly divides testing, and configuration.

"""


def createFolders(portal, parent, folders):
    """ takes a sequence of dictionaries of {id,title,publish,children} """
    wft = getToolByName(portal, 'portal_workflow')
    for folder in folders:

        print folder['id']

        # first grab a couple magic elements; invokeFactory will
        # choke on these if we leave them in

        publish    = folder.pop('publish')
        children   = folder.pop('children')


        # now invoke the factory

        parent.invokeFactory(type_name = 'Folder',**folder)
        new_folder = parent.unrestrictedTraverse(folder['id'])


        # and finally do workflow and possibly recurse

        if publish:
            wft.doActionFor(new_folder, 'publish')
        if children:
            createFolders(portal, new_folder, children)



def createContent(portal, content):
    """ takes a parent:[content,] dictionary """
    wft = getToolByName(portal, 'portal_workflow')
    for item in content:

        # first grab a couple magic elements; invokeFactory will
        # choke on these if we leave them in

        location = item.pop('location')
        publish  = item.pop('publish')


        # now create the content object

        parent = portal.unrestrictedTraverse(location)
        parent.invokeFactory(**item)
        new_obj = parent.unrestrictedTraverse(item['id'])


        # now do workflow if needed

        if publish:
            wft.doActionFor(new_obj, 'publish')
