#!/usr/local/zope/python2.3/bin/python2.3
""" provides a shell-like interface on a ZODB
"""

# python modules
import cmd, os, sys, traceback

class Zosh(cmd.Cmd):
    """
    """

    def __init__(self, INSTANCE_HOME = None, *args, **kw):

        # get SOFTWARE_HOME from the environment

        SOFTWARE_HOME = os.environ.get('SOFTWARE_HOME')
        if SOFTWARE_HOME is None:
            print "Please set SOFTWARE_HOME to your Zope's lib/python."
            sys.exit(2)
        sys.path.append(SOFTWARE_HOME)


        # If we are given an INSTANCE_HOME, use the ZODB there. Otherwise
        # assume we are being tested either interactively or from a test
        # runner and use a stub ZODB.

        if INSTANCE_HOME is not None:
            import Zope
            INSTANCE_HOME = os.path.realpath(INSTANCE_HOME)
            Zope.configure('%s/etc/zope.conf' % INSTANCE_HOME)
        else:
            sys.stderr = file('/dev/null', 'r+')
            from Testing.ZopeTestCase import base as Zope
            sys.stderr = sys.__stderr__

        self.context = Zope.app()
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
        from OFS.Folder import Folder

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

    # determine the INSTANCE_HOME if possible
    if len(sys.argv) == 2:
        INSTANCE_HOME = sys.argv.pop(1)
    else:
        INSTANCE_HOME = os.environ.get('INSTANCE_HOME')

    shell = Zosh(INSTANCE_HOME)
    try:
        shell.cmdloop()
    except KeyboardInterrupt:
        shell.onecmd("EOF")





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

_refresh command reimports the Zosh obj so we don't have to kill and restart Zope for testing
tab completion for cd
locals should contain the current objectIds so we can operate on them directly
add should provide API similar to "Select type to add ..." dropdown
commands should be passed through from a bin/ directory in the distribution
"""

##
# automated testing -- run these tests using runtests.py or make test
##

from StringIO import StringIO
testout = StringIO()

def test_test():
    zosh = Zosh(stdout=testout)
    zosh.onecmd("ls")
    assert testout.getvalue() == "acl_users  Control_Panel\n"
    zosh.onecmd("cd acl_users")
    assert testout.getvalue() == "acl_users  Control_Panel\n"
