#!/usr/local/zope/python2.3/bin/python2.3
""" provides a shell-like interface on a ZODB
"""

# python modules
import cmd, os, sys, traceback

# get our Zope connection
sys.path.append(os.environ['SOFTWARE_HOME'])
import Zope
Zope.configure('/home/whit537/zosh/testzope/etc/zope.conf')
app = Zope.app()

# set up logging
import logging
logger = logging.getLogger('zosh')
hdlr = logging.FileHandler('zosh.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

# for complete_cd
from OFS.Folder import Folder

class ZoshCmd(cmd.Cmd):
    """
    """

    def __init__(self, *args, **kw):
        self.context = app
        self.intro = 'zosh version 0.1'
        self.prompt = 'zosh: '

        # let our superclass have its way too
        cmd.Cmd.__init__(self, *args, **kw)

    def do_ls(self, line):
        """list objects
        """
        objects = self.context.objectIds()
        if objects: self.columnize(objects)


    def _getcwd(self):
        cwd = '/'.join(self.context.getPhysicalPath())
        if not cwd: cwd = '/'
        return cwd

    def do_pwd(self, line):
        """pathname of the current working directory
        """
        print self._getcwd()

    def complete_cd(self, text, line, begidx, endidx):
        """tab-completion for cd
        """
        logger.error('newcontext: %s' % 'foo')
        # get the context based on the path that has been entered so far
        if not text.startswith('/'):
            text = '/'.join((self._getcwd(), text))[1:]
        if text.endswith('/'):
            newcontext = self.context.unrestrictedTraverse(text)
        else:
            newcontext = self.context
        return newcontext.objectsIds()

        # return the list of objects in that context
        completes = []
        for obj in newtext.objectValues():
            if isinstance(obj, Folder):
                complete = '%s/' % obj.getId()
            else:
                complete = obj.getId()
            if complete.startswith(text):
                completes.append(complete)
        return completes

    def do_cd(self, line):
        """change directory
        """
        self.context = self.context.unrestrictedTraverse(line)

    def default(self, line):
        """tries a few different ways to interpret the input before giving up
        """
        try:
            try:
                print eval(line)
            except:
                try:
                    exec(line)
                except:
                    print eval('self.context.%s' % line)
        except:
            traceback.print_exc()


    ##
    # Misc
    ##

    def emptyline(self):
        pass

    def do_EOF(self, line=''):
        print >> self.stdout; return True
    def do_exit(self, *foo):
        return True
    do_q = do_quit = do_exit


if __name__ == '__main__':
    c = ZoshCmd()
    try:
        c.cmdloop()
    except KeyboardInterrupt:
        c.onecmd("EOF")

"""
zbin/
    cd
    ls
    pwd
    rm
    add

tar
grep
less

========================================
    TODO
========================================

tab completion for cd
locals should contain the current objectIds so we can operate on them directly
add should provide API similar to "Select type to add ..." dropdown

"""