## Script (Python) "fck_browseImages"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.CMFCore.utils import getToolByName
results=[]
self=context
user=context.REQUEST['AUTHENTICATED_USER']
props=getToolByName(self,'portal_properties')
if hasattr(props,'navtree_properties'):
    props=props.navtree_properties
rolesSeeUnpublishedContent=getattr(props,'rolesSeeUnpublishedContent',  ['Manager','Reviewer','Owner'])
for object in self.objectValues(['Plone Folder','Workgroup','Portal Image','Photo','Large Plone Folder','Photo Album','CMF ZPhoto','CMF ZPhotoSlides','CMF ZPhotoSlides Folder','Plone Site']):
      review_state=container.portal_workflow.getInfoFor(object, 'review_state', '')
      start_pub=getattr(object,'effective_date',None)
      end_pub=getattr(object,'expiration_date',None)
      if (review_state=='published' or review_state=='announced' or review_state=='visible4group') and not ((start_pub and start_pub > DateTime()) or (end_pub and DateTime() > end_pub)):
          results.append(object)
      elif user.has_role(rolesSeeUnpublishedContent,object) :
          results.append(object)
return results