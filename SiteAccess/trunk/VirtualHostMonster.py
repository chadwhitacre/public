"""VirtualHostMonster module

Defines the VirtualHostMonster class
"""

from Globals import DTMLFile, MessageDialog, Persistent
from OFS.SimpleItem import Item
from Acquisition import Implicit, ImplicitAcquisitionWrapper
from ExtensionClass import Base
from string import split, strip, join, find, lower, replace
from ZPublisher import BeforeTraverse
import os

from AccessRule import _swallow

class VirtualHostMonster(Persistent, Item, Implicit):
    """Provide a simple drop-in solution for virtual hosting.
    """
    
    meta_type='Virtual Host Monster'
    priority = 25

    title = ''

    __ac_permissions__=(('View', ('manage_main',)),('Add Site Roots', ('manage_edit', 'set_dp_map')))

    manage_options=({'label':'View', 'action':'manage_main'},{'label':'Edit', 'action':'manage_edit'})

    manage_main = DTMLFile('www/VirtualHostMonster', globals())
    manage_edit = DTMLFile('www/manage_edit', globals())
    
    def show_help(self):
        "Just shows whether show_help_attr is set to 0 or 1"
        try:
          return self.show_help_attr
        except AttributeError:
           self.show_help_attr=1
           self._p_changed = 1
           return self.show_help_attr
    
    def change_show_help(self):
        "Toggles show_help_attr from 0 to 1 or vice versa"
        if self.show_help_attr == 0:
           self.show_help_attr = 1
        else:
           self.show_help_attr = 0
        self._p_changed = 1
        
    
    def set_dp_map(self, domain, path, REQUEST=None):
        "Sets domain to path mappings. Returns a status message."
        self.message = {}
        if REQUEST:
          for name in REQUEST.form.keys():
            if self.domain_path.has_key(name):
               self.check_path(name, REQUEST.form[name])
               if self.message.has_key(name):
                  del self.domain_path[name]
               else:
                  self.domain_path[name] = REQUEST.form[name]
        if domain:
           try:
               int(replace(domain,'.',''))
               self.message[domain] = "IP addresses are not mappable"
           except ValueError:
               self.check_path(domain, path)
               if not self.message.has_key(domain):
                  self.domain_path[lower(domain)] = path
        self._p_changed=1
        status = []
        for domain in self.message.keys():
            status.append((domain,self.message[domain]))
        return status
                  
    def check_path(self,domain,path):
        if not path:
           self.message[domain] = "Path is empty."
           return
        if path[-1] == '/':
           if len(path) == 1:
              return
           else:
              path = path[:-1]
        try:
            leaf_object = self.unrestrictedTraverse(path)
        except:
            self.message[domain] = "The path %s was not found." % path
            return
        if not getattr(leaf_object.aq_base,'isAnObjectManager', None):
            self.message[domain] = "The path, %s , must end in a container: %s isn't one." % ( path, split(path,'/')[-1] )
        self._p_changed = 1

    def display_rules(self):
        "Returns list of tuples of access rule domains and paths"
        retlist = []
        if getattr(self, 'domain_path',None) != None:
           for domain in self.domain_path.keys():
               retlist.append((domain, self.domain_path[domain]))
        else:
           self.domain_path = {}
           retlist = []
           self._p_changed = 1
        
        def compare_domains(a,b):
            www=0
            a = a[0].strip().split('.')
            b = b[0].strip().split('.')
            if a[:4]=='www.':
                x = a[4:]    
                www=1
            else:
                x = a
            if b[:4]=='www.':
                y = b[4:]
                www=1
            else:
                y = b
            try:
                domain = cmp(x[-2], y[-2])
            except:
                return cmp(x[-1], y[-1])
            if domain == 0:
                tld = cmp(x[-1], y[-1])
                if tld == 0:
                    for i in range(-3,-(min(len(x),len(y))+1),-1):
                        if x[i]<y[i]:
                            return -1
                        elif x[i]>y[i]:
                            return 1
                    if len(x)<len(y):
                        return -1
                    elif len(x)>len(y):
                        return 1
                    if www:
                        return cmp(a,b)
                    return 0
                else:
                    return tld
            else:
                return domain
        
        retlist.sort(compare_domains)
        return retlist
        
    def addToContainer(self, container):
        container._setObject(self.id, self)
        self.manage_afterAdd(self, container)

    def manage_addToContainer(self, container, nextURL=''):
        self.addToContainer(container)
        if nextURL:    
            return MessageDialog(title='Item Added',
              message='This object now has a %s' % self.meta_type, 
              action=nextURL)

    def manage_beforeDelete(self, item, container):
        if item is self:
            BeforeTraverse.unregisterBeforeTraverse(container, self.meta_type)

    def manage_afterAdd(self, item, container):
        if item is self:
            id = self.id
            if callable(id): id = id()

            # We want the original object, not stuff in between
            container = container.this()
            hook = BeforeTraverse.NameCaller(id)
            BeforeTraverse.registerBeforeTraverse(container, hook,
                                                  self.meta_type,
                                                  self.priority)
    def _setId(self, id):
        id = str(id)
        if id != self.id:
            BeforeTraverse.unregisterBeforeTraverse(container,
            self.meta_type)
            hook = BeforeTraverse.NameCaller(id)
            BeforeTraverse.registerBeforeTraverse(container, hook,
                                                  self.meta_type,
                                                  self.priority)

    def __call__(self, client, request, response=None):
        '''Traversing at home'''
        stack = request['TraversalRequestNameStack']
        host = ''
        if stack and stack[-1] == 'VirtualHostBase':
            stack.pop()
            protocol = stack.pop()
            host = stack.pop()
            if ':' in host:
                host, port = split(host, ':')
                request.setServerURL(protocol, host, port)
            else:
                request.setServerURL(protocol, host)
        if host == '':
           host = split(request['HTTP_HOST'], ':')[0]
        # If a domain to path mapping applies, invoke it now.
        if not stack.count('VirtualHostRoot'):
            if getattr(self, 'domain_path', None):
               real_host=None
               l_host = lower(host)
               if self.domain_path.has_key(l_host):
                  real_host=l_host
               else:
                  for hostname in self.domain_path.keys():
                      if hostname[:2] == '*.':
                          if find(l_host, hostname[2:]) != -1:
                              real_host = hostname
               if real_host:
                   path = self.domain_path[real_host]
                   if path != '/':
                      list_path = split(path, '/')[1:]
                      stack.append('/')
                      stack.append(self.id)
                      for i in range(len(list_path)):
                         stack.append(list_path.pop())
     
              
        # Find and convert VirtualHostRoot directive
        # If it is followed by one or more path elements that each
        # start with '_vh_', use them to construct the path to the
        # virtual root.
        vh = -1
        for ii in range(len(stack)):
            if stack[ii] == 'VirtualHostRoot':
                if vh >= 0:
                    pp = ['']
                    for jj in range(vh, ii):
                        pp.insert(1, stack[jj][4:])
                    stack[vh:ii + 1] = [join(pp, '/'), self.id]
                elif ii > 0 and stack[ii - 1][:1] == '/':
                    stack[ii] = self.id
                else:
                    stack[ii] = self.id
                    stack.insert(ii, '/')
                break
            elif vh < 0 and stack[ii][:4] == '_vh_':
                vh = ii

    def __bobo_traverse__(self, request, name):
        '''Traversing away'''
        if name[:1] != '/':
            return getattr(self, name)
        parents = request.PARENTS
        parents.pop() # I don't belong there

        if len(name) > 1:
            request.setVirtualRoot(split(name[1:], '/'))
        else:
            request.setVirtualRoot([])
        return parents.pop() # He'll get put back on

def manage_addVirtualHostMonster(self, id, REQUEST=None, **ignored):
    """ """
    vhm = VirtualHostMonster()
    vhm.id = str(id)
    if REQUEST:
        return vhm.manage_addToContainer(self.this(),
                                        '%s/manage_main' % REQUEST['URL1'])
    else:
        vhm.addToContainer(self.this())

constructors = (
  ('manage_addVirtualHostMonsterForm', DTMLFile('www/VirtualHostMonsterAdd', globals())),
  ('manage_addVirtualHostMonster', manage_addVirtualHostMonster),
)
