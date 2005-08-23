#!/usr/bin/env python
"""

We only have to listen for one event: when svn tells us that updates are
available to a certain site. When we receive this notification, we need to see
if we are already running that website. If so then we need to upgrade it,
otherwise we need to create it.

We do not initiate any communications with svn.

Create a website:
    checkout a working copy of the website
    install the website in daemontools


Upgrade a website:
    stop the website using daemontools
    update the working copy of the website
    start the website using daemontools

    This upgrade scheme means the website will be down during the upgrade.
    Eventually this will be ameliorated by replication, but we will live with it
    for now since working around it is a big hassle (I think).

"""

__version__ = (0,1)

import os
import base64
from popen2 import Popen4
from xmlrpclib import Fault
from StringIO import StringIO


class Faults:
    """A bucket of tuples: (faultCode, faultString).

    faultString will be formatted with three values:
        website ID
        faultCode
        command output

    """

    CHECKOUT  = ('101', "Checkout of %s failed with code: %s\n%s")
    UPDATE    = ('102', "Update of %s failed with code: %s\n%s")
    DAEMONIZE = ('103', "Daemonization of %s failed with code: %s\n%s")
    START     = ('104', "Attempt to start %s failed with code: %s\n%s")
    STOP      = ('105', "Attempt to stop %s failed with code: %s\n%s")


class www:

    def __init__(self):
        root='/usr/local/www/'
        self.root = os.path.realpath(root)
        if not os.path.isdir(self.root):
            os.makedirs(self.root, 0755)


    def deploy(self, repo_url):
        """Given an svn url, create or upgrade the website we find there.
        """

        site_id = base64.urlsafe_b64encode(repo_url)

        paths = {}
        paths['wc'] = os.path.join(self.root, site_id)
        paths['repo'] = repo_url
        paths['daemon'] = os.path.sep.join(('', 'service', site_id))

        if self._exists(paths):
            return self._upgrade(paths)
        else:
            return self._create(paths)


    def _exists(self, paths):
        """
        """
        return os.path.isdir(paths['wc'])


    def _create(self, paths):
        """Checkout and daemonize a website.
        """

        self._popen('svn co %(repo)s %(wc)s', paths, Faults.CHECKOUT)
        self._popen('ln -s %(wc)s %(daemon)s', paths, Faults.DAEMONIZE)

        return "Successfully created %(repo)s." % paths


    def _upgrade(self, paths):
        """Stop, update, and start a website.
        """

        self._popen('svc -d %(daemon)s', paths, Faults.STOP)
        self._popen('svn up %(checkout)s', paths, Faults.UPDATE)
        self._popen('svc -u %(daemon)s', paths, Faults.START)

        return "Successfully upgraded %(repo)s." % paths


    def _popen(self, command, paths, fault):
        """Given a website ID, a command and a Fault template, run the command.
        """
        process = Popen4(command)
        result = process.wait()
        output = process.fromchild.read()

        if result != 0:
            message = fault[1] % (paths['repo'], result, output)
            return Fault(fault[0], message)

        return result


"""

dns
mcp
svn -> repos
www -> websites
app -> applications


TODO

    Make notify ACID compliant.

        ACID notes:

            As much as possible, order the steps in a transaction from hardest
            to easiest.

            If at all possible, make the last step in the transaction something
            truly atomic; a mv, or an ln, or something.

            Here's a pattern: write data to a staging area, and then link that
            area as the final step of the transaction.

            You either have to anticipate errors and not do the work in the
            first place, or be able to predicatably roll back the work already
            done in the event of an error. The first is impossible, but is
            probably a good idea for the most common errors.

    Refactor for concurrency.

        Websites are a shared resource. We can create and upgrade different
        websites at the same time, but we don't want to modify any given website
        more than one thread at a time.


    Support website deletion.


    Support multiple servers, with websites replicated across them.

        Servers will need to register with us when they come online: a second
        event to listen for.

        We will need a mapping of sites to servers: a second shared resource.
        It should be persisted, and some or all of it also kept in memory.

        Updates will have to be propagated to all relevant servers.

        Servers will need to provide resource accounting to inform our decisions
        regarding new site creation.

        We should periodically initiate garbage collection of servers and
        websites, whatever this means.


    Support multiple instances of the www daemon itself.

        Site updates will potentially hit a server from more than one direction,
        so update locking will have to be pushed out to the servers. NOTE: Is
        this easy enough to implement now?

        The site:servers mapping will need to be shared by all instances. A few
        possible strategies:

            an additional storage daemon that www's communicate with

            an additional registry daemon that facilitates direct communication
            between the www's

            a peer-to-peer scheme instead of a client-server. i.e., each www
            knows about the location of all other www's.

            YES YES YES!!!!!!!!

"""