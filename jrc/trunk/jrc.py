#!/usr/local/bin/python
# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

"""jrc(1) -- start and stop jails; see man 1 jrc for details."""

import os, sys
from time import sleep

class jrc:

    def __init__(self):
        """ initialize variables
        """

        action = sys.argv.pop(-1)
        args = sys.argv[1:]

        BAD_INPUT = False

        if len(args) not in (1,2):
            BAD_INPUT = True
        else:

            if action not in ('start','stop','restart'):
                BAD_INPUT = True
            else:
                # input is valid
                if len(args) == 1:
                    DIRECTORY = args[0]
                else:
                    DIRECTORY, IP_ADDRESS = args

                DIRECTORY = os.path.realpath(DIRECTORY)
                head, tail = os.path.split(DIRECTORY)

                if len(args) == 1:
                    HOSTNAME, IP_ADDRESS = tail.split('_')
                else:
                    HOSTNAME = tail

                self.DIRECTORY  = DIRECTORY
                self.HOSTNAME   = HOSTNAME
                self.IP_ADDRESS = IP_ADDRESS
                self.ACTION     = action

        self.BAD_INPUT = BAD_INPUT

    def __call__(self):
        # sniff some variables
        whoami = self.getoutput('whoami').strip('\n')
        livejails = self.getoutput('jls lj').split('\n')

        # decide whether or not to start/stop the jail
        if whoami <> 'root':
            print "Failed: jrc must be run as root, not %s." % whoami
        elif self.BAD_INPUT:
            print __doc__
        elif self.ACTION == 'start':
            if self.HOSTNAME in livejails:
                print "Failed: '%s' is already started." % self.HOSTNAME
            else:
                self.start()
        elif self.ACTION == 'stop':
            if self.HOSTNAME not in livejails:
                print "Failed: '%s' is already stopped." % self.HOSTNAME
            else:
                self.stop()
        elif self.ACTION == 'restart':
            if self.HOSTNAME in livejails:
                # if already running, stop then start
                self.stop()
                print "'%s' will restart in 3 seconds ..." % self.HOSTNAME
                sleep(3)
                self.start()
            else:
                print "'%s' is not running, we'll start it." % self.HOSTNAME
                self.start()

    def start(self):
        """ start the jail
        """
        print "Mounting the process filesystem ... "

        # use df to determine whether proc is already mounted
        df = self.getoutput('df').split('\n')[:-1]
        proc_paths = [rec.split()[5] for rec in df]
        proc_path = "%s/proc" % self.DIRECTORY

        if proc_path not in proc_paths:
            os.system("mount -t procfs proc %s/proc" % self.DIRECTORY)
        else:
            print "Proc is already mounted (unclean shutdown?). Continuing ..."

        print "Starting the jail ... "
        c = "jail %(DIRECTORY)s %(HOSTNAME)s %(IP_ADDRESS)s /bin/sh /etc/rc"
        os.system(c % self.__dict__)

        print "'%s' was successfully " % self.HOSTNAME +\
              "started on %s." % self.IP_ADDRESS

    def stop(self):
        """ stop the jail
        """
        print "Killing all processes in '%s' ... " % self.HOSTNAME
        os.system("jkill lj %s" % self.HOSTNAME)

        print "Unmounting the process filesystem ... "
        os.system("umount %s/proc" % self.DIRECTORY)

        print "'%s' on %s was " % (self.HOSTNAME, self.IP_ADDRESS) +\
              "successfully stopped."

    def getoutput(command):
        """ given an OS command, get its output
        """
        stdin, stdout = os.popen4(command)
        return stdout.read()
    getoutput = staticmethod(getoutput)


jrc = jrc()
jrc()