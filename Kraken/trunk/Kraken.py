import os
from ConfigParser import SafeConfigParser as ConfigParser
import re
import imaplib
import smtplib
import email

class Kraken:
    """

    This guy polls an IMAP account. If a new message is from a list member, then
    it forwards the message along to the rest of the list. Otherwise it moves
    the message to the trash. Usage:

    >>> from Kraken import Kraken
    >>> k = Kraken()
    >>> k.release()

    The beauty of using IMAP for mailing list/discussion mgmt is the plugability
    and the flexibility. I can login w/ Thunderbird or a TTW client and manage
    the archives and sift through the trash. Will it scale? I expect so.

    TODO

        - Protect against 'auto-away' messages!!!

        - consider batch processing server interactions instead of hitting the
          server once per message

        - better logging

        - TTW user mgmt

        - use SSL/TSL

    """

    def __init__(self):
        """ read in config info """
        cp = ConfigParser()
        cp.read('conf/kraken.conf')
        self.imap = dict(cp.items('imap'))
        self.smtp = dict(cp.items('smtp'))
        self.list_addr = cp.get('default', 'list_addr')

        self.send_to = self.addrs('conf/send_to.conf')
        raise 'um', self.send_to
        self.accept_from = self.send_to + \
                           self.addrs('conf/also_accept_from.conf')


    def addrs(self, fn):
        """ given a filename, return a list of email addresses """
        raw = file(fn).read()
        lines = [l.strip() for l in raw.split(os.linesep)]
        return [l for l in lines
                  if not l.startswith('#') and
                     not l == '']
        # maybe eventually validate email addresses


    def release(self):
        """ get all mail from our inbox and process """

        imap = self.imap
        smtp = self.smtp

        # open the IMAP connection and get everything in the INBOX

        if imap['secure'] == 'True':
            raise 'NotImplemented', 'secure IMAP is not implemented yet'
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

            i_good = i_bad = 0

            for num in msg_nums:

                # get the From header

                typ, raw = M.fetch(num, '(BODY[HEADER.FIELDS (FROM)])')
                FROM = raw[0][1]
                pattern = r'From: .* <(.*)>'
                from_addr = re.search(pattern, FROM).group(1)


                # and compare it to our membership lists

                if from_addr in self.accept_from:

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
                       raise 'NotImplemented', 'secure SMTP is not implemented yet'
                    else:
                        server = smtplib.SMTP(smtp['server'],smtp['port'])
                        server.login(smtp['username'],smtp['password'])
                        server.sendmail(self.list_addr,self.send_to,msg.__str__())
                        server.quit()

                    # and move to archive
                    M.copy(num, 'Archive')
                    M.store(num, 'FLAGS.SILENT', '(\Deleted)')

                    i_good += 1

                else:
                    # move it to trash!
                    M.copy(num, 'Trash')
                    M.store(num, 'FLAGS.SILENT', '(\Deleted)')

                    i_bad += 1

            M.close()
            M.logout()

            print 'approved %s; rejected %s' % (i_good, i_bad)


def _test():
    import doctest, Kraken
    return doctest.testmod(Kraken)

if __name__ == "__main__":
    _test()
