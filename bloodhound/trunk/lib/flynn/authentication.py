"""This module provides all our user management functionality.

We are only going to have a handful of users, logging in only periodically.
However, we need to allow users to keep multiple sessions open simultaneously
(editing in Firefox, testing in IE, e.g.).

"""

import cgi
import os
import sha
import string
import urllib
import urlparse
from Cookie import Morsel
from base64 import urlsafe_b64encode, urlsafe_b64decode
from random import choice

from Crypto.Cipher import AES
from httpy.Response import Response
from httpy.utils import log, parse_body, parse_cookie, parse_query

from acn.storage import db, USERS, USERMGMT
from acn.usermgmt import passget, userget
from rdflib import Namespace, URIRef, Literal


class User:
    """Represent a user of the system.
    """

    name = 'guest'
    role = 'guest'

    def __init__(self, username):
        """Takes a username.
        """
        self.name = username
        if username != 'guest':
            role, passwd = userget(username)
            self.role = role
        log(79, "created User %s:%s" % (username, self.role))

    def __repr__(self):
        return self.name
    __str__ = __repr__


class Auth:
    """Authentication services for applications of this website.

    We have three basic responsibilities:

        Application depends on us to provide a user for each request
        Logging in users (/login.py)
        Logging out users (/logout.py)

    """

    def __init__(self):
        """Set up some helpers for our cookie authentication.

        In deployment mode, we use a random key to see our encryption, but this
        means that every time the server restarts our login session is
        invalidated. Since we restart once every 2 seconds in dev mode, this is
        a bit cumbersome. Hence, a standard key in dev/deb mode.

        """
        mode = os.environ.get('HTTPY_MODE', 'deployment')
        self.deb_mode = mode == 'debugging'
        self.dep_mode = mode == 'deployment'
        self.dev_mode = mode == 'development'

        if self.dep_mode:
            key = ''
            for c in range(32):
                key += choice(string.printable)
        else:
            key = ('secret' * 5) + 'th'
        self.crypter = AES.new(key)
        self.boundary = "-----<|BLAM|>-----"


    def __call__(self):
        """Singleton -- http://c2.com/cgi/wiki?PythonSingleton
        """
        return self


    # Support for app.py.
    # ===================

    def get_user(self, request):
        """Given a request, return a User or None.

        We look for an authentication cookie in the request. We can fail in the
        following ways:

            - no cookie
            - empty cookie
            - cookie encrypted with different key
            - wrong username/password in cookie

        """

        username = "guest"
        cookie = parse_cookie(request)
        if not cookie:
            log(79, "No cookie.")
        elif 'gingersnap' not in cookie:
            log(79, "No gingersnap.")
        elif not cookie['gingersnap'].value:
            log(79, "Empty gingersnap.")
        else:
            gingersnap = cookie['gingersnap'].value
            try:
                gingersnap = urlsafe_b64decode(gingersnap)
                gingersnap = self.crypter.decrypt(gingersnap)
                gingersnap = gingersnap.strip()
                gingersnap = urlsafe_b64decode(gingersnap)
                username, password = gingersnap.split(self.boundary)
            except:
                log(77, "Failed to decode gingersnap.")
                self.cookie_failure("Session reset by server.")
            else:
                if not self.authenticate(username, password):
                    log(77, "Gingersnap has bad credentials.")
                    self.cookie_failure("Session out of sync.")
                else:
                    log(74, "'%s' successfully authenticated via " % username +
                            "cookie.")

        return User(username)


    def authenticate(self, username, password):
        """Given a username and password, return a boolean.
        """
        attempt = sha.new(password).hexdigest()
        actual = passget(username)

        if attempt == actual:
            log(73, "User '%s' successfully logged in." % username)
            return True
        else:
            log(73, "Failed login attempt by user '%s.'" % username)
            return False


    def cookie_failure(self, message):
        """
        """
        morsel = Morsel()
        morsel.set('gingersnap', '', '')
        morsel['max-age'] = 0 # seconds == 0 minutes
        url = "/?message=%s&msgtype=warning" %  urllib.quote_plus(message)
        self.touch_and_go(morsel,url)



    # Support for login.py and logout.py.
    # ===================================

    def redirect_to_login(self):
        response = Response(302)
        response.headers['Location'] = ("/login.py?message=You+must+login+" +
                                        "to+access+this+resource.&msgtype=" +
                                        "warning")
        raise response


    def save_login(self, username, password, back_to):
        """Encrypt and store the username and password in a cookie.

        First we join the username and password together with a separator that
        is unlikely to also be in either. Then we base64-encode it to ensure
        that there are no spaces in the string, because we need to pad the
        string with spaces to reach the necessary length for AES encryption.
        Once encrypted, we base64-encode it again for safe transport. Phew!

        When we're done, we try to send the user back where they came from.

        """

        gingersnap = self.boundary.join((username, password))
        gingersnap = urlsafe_b64encode(gingersnap)
        gingersnap += ' ' * (16 - (len(gingersnap) % 16))
        gingersnap = self.crypter.encrypt(gingersnap)
        gingersnap = urlsafe_b64encode(gingersnap)

        log(75, "Setting auth cookie: %s" % gingersnap)

        morsel = Morsel()
        morsel.set('gingersnap', gingersnap, gingersnap)
        morsel['max-age'] = 1800 # seconds == 30 minutes


        # Add our success message to the url they came from, which might
        # already have a querystring.

        parts = list(urlparse.urlparse(back_to))
        query_dict = cgi.parse_qs(parts[4], True)
        query_dict['message'] = "Login+succeeded."
        query_dict['msgtype'] = "success"
        parts[4] = urllib.urlencode(query_dict)
        url = urlparse.urlunparse(parts)

        self.touch_and_go(morsel, url)


    def logout(self):
        """Wax the auth cookie and send them back to the homepage.
        """
        morsel = Morsel()
        morsel.set('gingersnap', '', '')
        morsel['max-age'] = 0 # seconds == 0 minutes
        url = "/?message=Logout+succeeded.&msgtype=success"
        self.touch_and_go(morsel, url)


    def touch_and_go(self, morsel, url):
        """Given a Morsel and an url, set a cookie and redirect.
        """
        response = Response(302)
        response.headers['Location'] = url
        response.headers['Set-Cookie'] = morsel.OutputString()
        raise response



Auth = Auth()
