class MailChecker:
    """

    This guy polls an IMAP account and either deletes messages or forwards them
    onto a mailing list, according to a set of filters.

    """

    username = 'homegroup'
    password = 'ihsouj'
    server   = 'secure-email-5.luxsci.com'
    port     = '995'

    def __init__(self):
        pass

    def process(self):
        """

        This is the method that gets called from cron. It polls the IMAP account,
        applies the filters, and deletes or forwards.

        """

    def poll(self):
        """ get new mail from the server """
        M = imaplib.IMAP4_SSL(self.server, self.port)
        M.login(self.username, self.password)
        M.select('INBOX',True)
        msgnums = M.search(None,'NEW')
        print msgnums


    def flush(self):
        """ queue a message for deletion """
        pass

    def forward(self):
        """ queue a message for forwarding """
        pass

class UserManager:
    """ this guy  """