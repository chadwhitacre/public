import time

from Testing import ZopeTestCase
ZopeTestCase.installProduct('FCKeditor')
from Products.CMFPlone.tests import PloneTestCase

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager

class FCKploneTestCase(PloneTestCase.PloneTestCase):
    """veneer"""


def customizePlone(app):
    _start = time.time()
    ZopeTestCase._print('Customizing Plone Site ... ')

    factory = app.portal.manage_addProduct['FCKeditor']
    factory.manage_addPloneFCKmanager()
    app.fckm = app.portal.portal_fckmanager

    # set up a couple users
    app.portal.acl_users._doAddUser('user1', 'secret', ['Member',], [])
    app.portal.acl_users._doAddUser('admin', 'secret', ['Manager',], [])

    # login as admin
    user = app.portal.acl_users.getUserById('admin').__of__(app.portal.acl_users)
    newSecurityManager(None, user)

    # set up some content
    """
    path/
        to/
            empty/
            one/ (private state)
                foo.DOC
            content/
                sub-content/
                foo.DOC
                bar.PPT (private state)
                bar.JPG
    """
    #app.portal.invokeFactory(type_name='Folder', id='path')
    #app.portal.path.invokeFactory('Folder','to')
    #to = app.portal.path.to
    #to.invokeFactory('Folder','empty')
    #to.invokeFactory('Folder','one')
    #to.one.invokeFactory('File','foo.DOC')
    #to.invokeFactory('Folder','content')
    #to.content.invokeFactory('Folder','sub-content')
    #to.content.invokeFactory('File','foo.DOC')
    #to.content.invokeFactory('File','bar.PPT')
    #to.content.invokeFactory('Image','bar.JPG')
    #
    ## tweak some security
    ##app.portal.portal_workflow.doActionFor(to, 'hide')
    ##bar_PPT = getattr(to.content, 'bar.PPT')
    ##app.portal.portal_workflow.doActionFor(bar_PPT, 'hide')

    # logout
    noSecurityManager()
    get_transaction().commit()

    _end = time.time() - _start
    ZopeTestCase._print('done (%.3fs)\n' % _end)


app = ZopeTestCase.app()
customizePlone(app)
ZopeTestCase.close(app)
