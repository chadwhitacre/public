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
    >>> mc = Kraken()
    >>> mc.release()

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

    username = 'homegroup@whit537.org'
    password = 'ihsouj'
    server   = 'imap-5.luxsci.com'
    port     = 143

    accept_from = ('whit537@gmail.com',
                   'jesslloydwhit@gmail.com',
                   )

    send_to     = ('whit537@gmail.com',
                   'chad@zetaweb.com',
                   )

    def __init__(self):
        pass

    def release(self):
        """ get all mail from our inbox and process """
        M = imaplib.IMAP4(self.server, self.port)
        M.login(self.username, self.password)
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
                typ, raw = M.fetch(num, '(BODY[HEADER.FIELDS (FROM)])')
                FROM = raw[0][1]
                pattern = r'From: .* <(.*)>'
                from_addr = re.search(pattern, FROM).group(1)
                if from_addr in self.accept_from:

                    # get the raw email
                    typ, raw = M.fetch(num, '(RFC822)')
                    raw = raw[0][1]
                    msg = email.message_from_string(raw)

                    # tweak the headers
                    msg.replace_header('Reply-To', 'homegroup@whit537.org')
                    msg.add_header('X-Released-By','THE KRAKEN!!!!!!!!1')

                    # and pass it on!
                    server = smtplib.SMTP('smtp-5.luxsci.com',25)
                    server.login(self.username,self.password)
                    server.sendmail('homegroup@whit537.org',self.send_to,msg.__str__())
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
