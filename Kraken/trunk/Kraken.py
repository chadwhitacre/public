# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE":
# <chad@zetaweb.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return. --Chad Whitacre
# ----------------------------------------------------------------------------

import os, re, imaplib, smtplib, email
from os.path import abspath
from Whale import Whale

class Kraken:
    """

    This guy polls an IMAP account. It either re-sends or trashes messages based
    on the From header. Usage:

    >>> k = Kraken()
    >>> k.release()

    """

    carcasses = []

    def __init__(self, lair='.'):
        """ read in config info """

        # (almost) all directories are assumed to be mailing lists
        lists = [abspath(o) for o in os.listdir(lair)
                             if os.path.isdir(o) and
                                not o.startswith('.') and
                                not o == 'example']

        for l in lists:
            # create an object representing the list config, and store it away
            # maybe someday we will grow up and have persistent storage!
            whale = Whale(l)
            self.carcasses.append(whale)



    def release(self):
        """ loop through all mailing lists and process """

        for whale in self.carcasses:
            self.devour(whale)



    def devour(self, whale):
        """ given a mailing list, get all mail from our inbox and process it """

        imap = whale.imap
        smtp = whale.smtp

        # open the IMAP connection and get everything in the INBOX

        if imap['secure'] == 'True':
            raise 'NotImplemented', 'sorry, secure IMAP is not implemented yet'
        else:
            M = imaplib.IMAP4(imap['server'], int(imap['port']))
            M.login(imap['username'], imap['password'])
            M.select()
            typ, raw = M.search(None, 'ALL')
            msg_nums = raw[0].split()


        if len(msg_nums) == 0:

            # print '/me twiddles its thumbs'
            # only do something -- and only tell us -- if you actually
            # have something to do

            return

        else:

            i_good = i_bad = 0 # track what we do for the 'log' message

            for num in msg_nums:

                # get the From header and compare it to our membership lists

                if self.from_addr(M,num) not in self.accept_from:

                    # move it to the trash!
                    M.copy(num, 'Trash')
                    M.store(num, 'FLAGS.SILENT', '(\Deleted)')

                    i_bad += 1

                else:

                    # get the raw email
                    typ, raw = M.fetch(num, '(RFC822)')
                    raw = raw[0][1]
                    msg = email.message_from_string(raw)

                    # tweak the headers
                    try:
                        msg.replace_header('Reply-To', self.list_addr)
                    except KeyError:
                        msg.__setitem__('Reply-To', self.list_addr)
                    msg.add_header('X-Released-By','THE KRAKEN!!!!!!!!1')

                    # and pass it on!
                    if smtp['secure'] == 'True':
                       raise 'NotImplemented', 'sorry, secure SMTP is not implemented yet'
                    else:
                        server = smtplib.SMTP(smtp['server'],smtp['port'])
                        server.login(smtp['username'],smtp['password'])
                        server.sendmail(self.list_addr,self.send_to,msg.__str__())
                        server.quit()

                    # and move to archive
                    M.copy(num, 'Archive')
                    M.store(num, 'FLAGS.SILENT', '(\Deleted)')

                    i_good += 1

            M.close()
            M.logout()

            print '%s: approved %s; rejected %s' % (whale.id, i_good, i_bad)


    def from_addr(self, M=None, num=None, test_str=None):
        """

        Given an IMAP connection and a message number, return an email address.

        >>> k = Kraken()
        >>> k.from_addr(test_str='From: Chad Whitacre <chad.whitacre@zetaweb.com>')
        'chad.whitacre@zetaweb.com'

        >>> k.from_addr(test_str='From: chad@zetaweb.com')
        'chad@zetaweb.com'

        """
        if test_str is None:
            typ, raw = M.fetch(num, '(BODY[HEADER.FIELDS (FROM)])')
            FROM = raw[0][1]
        else:
            FROM = test_str
        pattern = r'From:.* <?(.*@.*\.[A-Za-z]*)>?'
        from_addr = re.search(pattern, FROM).group(1)
        return from_addr



def _test():
    import doctest, Kraken
    return doctest.testmod(Kraken)

if __name__ == "__main__":
    _test()
