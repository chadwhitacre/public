from httpy.apps.XMLRPC import XMLRPCApp


class Application(XMLRPCApp):
    """This server exposes the MIMEdb API.
    """

    def all(self, key):
        """Return a list of all message IDs.
        """
        raise NotImplementedError


    def find(self, key, criteria):
        """Given criteria, returning message IDs of matching messages.
        """
        raise NotImplementedError


    def headers(self, key, msg_id):
        """Given a message ID, retrieve the message's headers.
        """
        raise NotImplementedError


    def remove(self, key, msg_id):
        """Given a message ID, remove the message.
        """
        raise NotImplementedError


    def replace(self, key, msg_id, msg):
        """Replace one message with another.

        This does a store and a remove within one transaction, and is
        effectively an update operation. The wrinkle is that to us, the contents
        of the file determine its uniqueness, but any given application will
        undoubtedly impute identity to messages that according to our definition
        are not identical. Since any such imputation is application dependant,
        we don't support it beyond this convenience method.

        """
        raise NotImplementedError


    def retrieve(self, key, msg_id):
        """Given a message ID, return a MIME message.
        """
        raise NotImplementedError


    def store(self, key, msg):
        """Given a MIME message, store it.
        """
        raise NotImplementedError


    def set_crypt_key(self, key):
        """
        """
