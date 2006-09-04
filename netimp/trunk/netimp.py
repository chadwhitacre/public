"""Import Python modules directly over the network.

Usage:

    >>> import foo
    Traceback (most recent call last):
    ...
    ImportError: No module named foo
    >>> import netimp
    >>> netimp.path = ['http://www.zetadev.com/svn/public/netimp/test']
    >>> import foo
    >>>

"""
import base64
import httplib # urllib2 can't do HEAD requests?
import imp
import imputil
import os
import sha
import sys
import traceback
import urlparse
from os.path import join

'foo'.encode("idna") # trigger lazy import that causes infinite loop
                     # otherwise (called from httplib)


# Define.
# =======

class URL:
    """Represent a URL, including the 'username:password@' convention.

    urlparse doesn't recognize 'username:password@', so we have to do that
    manually. We assume no ':' in username. Should check some RFC.

    """

    def __init__(self, url):
        self._url = url
        parts = urlparse.urlparse(url)

        self.scheme = parts[0]
        self.netloc = parts[1]
        self.path = parts[2]
        self.parameters = parts[3]
        self.query = parts[4]
        self.fragment = parts[5]

        username = None
        password = None

        if '@' in self.netloc:
            username, self.netloc = self.netloc.split('@', 1)[0]
            if ':' in username:
                username, password = username.split(':', 1)

        self.username = username
        self.password = password


    def __str__(self):
        """Return the original URL, with any password zeroed out.
        """
        return _url.replace(self.password+'@', '******@')


class NetworkImporter(imputil.Importer):

    path = ()
    verbose = False
    cachedir = ''

    def get_code(self, parent, modname, fqname):
        """Given 3 args, return a 3-tuple or None.
        """

        if self.verbose:
            print >> sys.stderr, '-'*78
            print >> sys.stderr, "Importing %s from the network ..." % fqname
            print >> sys.stderr, '-'*78


        out = None
        found = False
        for baseurl in self.path:

            proto_url = '/'.join([baseurl] + fqname.split('.'))


            # Is this a package?
            # ==================
            # If so, we want to look for __init__.py.

            index = self.download(proto_url + '/')
            is_package = index is not None
            if is_package:
                proto_url += '/__init__'


            # Try to find some code.
            # ======================

            for suffix in imp.get_suffixes():
                url = proto_url + suffix[0]
                found = self.download(url)
                if found is not False:

                    # Prepare elements for imputil.Importer.
                    # ======================================

                    mod = imp.load_module(modname, found, found.name, suffix)
                    out = (is_package, mod, {})
                    break

            if out is not None:
                break

        return out


    def download(self, url):
        """Given a URL, download it locally and return a file object.

        The most efficient downloading algorithm is protocol-dependent, so we
        implement different protocols with their own method.

        The response body will presumably contain Python code (interpretable or
        compiled). If the download fails, this method should return False. This
        manifests to the caller as ImportError. To see the reason for the
        failure, set netimp.verbose to True and watch stderr.

        """
        url = URL(url)
        downloader = getattr(self, 'download_%s' % url.scheme, None)
        if downloader is None:
            msg = "We haven't implemented the '%s' protocol yet." % url.scheme
            raise NotImplementedError(msg)
            fp = None
        else:
            fp = downloader(url)
        return fp


    def download_http(self, url):
        """Downloader specific to HTTP.
        """

        # Set things up.
        # ==============

        out = False
        headers = {}
        if (url.username is not None) and (url.password is not None):
            tmp = base64.b64encode(':'.join([url.username, url.password]))
            headers['Authorization'] = "Basic %s" % tmp


        # Toe the waters.
        # ===============
        # We start with an HTTP HEAD request to check the status.

        conn = httplib.HTTPConnection(url.netloc)
        conn.request("HEAD", url.path, '', headers)
        r = conn.getresponse()
        conn.close()
        if self.verbose:
            print >> sys.stderr, url, r.status, ''


        # Bail.
        # =====
        # Short-cut when we just care whether it's a package.

        if url.path.endswith('/'):
            out = r.status == '200 OK'

        elif r.status == '200 OK':

            # Wade in.
            # ========
            # If the status is positive we check to see if we've already
            # downloaded the latest copy.

            etag = r.getheader('etag', '')
            lm = r.getheader('last-modified', '')
            key = sha.new(url + etag + lm).hexdigest()

            if not os.isdir(self.cachedir):
                raise IOError( "netimp.importer.cachedir not found "
                             + "(%s)" % self.cachedir
                              )

            path = join(self.cachedir, key)
            if os.isfile(path):
                out = open(path, 'rb')
            else:

                # Dive in!
                # ========
                # We don't have this module locally yet: download it for real.

                conn = httplib.HTTPConnection(url.netloc)
                conn.request("GET", url.path, '', headers)
                r = conn.getresponse()
                conn.close()
                if r.status == '200 OK': # just in case!
                    fp = open(path, 'w+b')
                    fp.write(response.get_body())
                    fp.flush()
                    fp.close()
                    out = open(path, 'rb')

        return out


# Configure.
# ==========

importer = NetworkImporter()
if 'NETIMP_CACHEDIR' in os.environ:
    importer.cachedir = os.environ['NETIMP_CACHEDIR']
if 'NETIMP_PATH' in os.environ:
    importer.path = list(os.environ['NETIMP_PATH'].split())
importer.verbose = 'NETIMP_VERBOSE' in os.environ


# Install.
# ========

imputil.ImportManager().install()
sys.path.append(importer)


# Test.
# =====

if __name__ == '__main__':
    """Test against the test data in our SVN repo.

    NB: _foo.so is compiled on FreeBSD 6.0-RELEASE.

    """
    importer.path = ['http://www.zetadev.com/svn/public/netimp/trunk/test']

    # module: foo.py
    import foo
    assert foo.made_it == 'BLAM!!!!!!!!!!'

    try: # most likely to fail
        # extension: _foo.so
        import _foo
        assert _foo.made_it == 'BLAM!!!!!!!!!!!!!!!!!!!!'
    except:
        print traceback.format_exc()

    # bytecode: blim.pyc
    import blim
    assert blim.made_it == 'yep'

    # package: bar/__init__.py
    import bar
    assert bar.made_it == 'BAR!!!!!!'

    # submodule: bar/baz.py
    from bar import baz
    assert baz.made_it == 'BAZ!!!!!!!!'

    # subpackage: bar/really/__init__.py
    from bar import really
    assert really.made_it == 'REALLY!!!!!!'

    # subsubmodule: bar/really/BLAM.py
    from bar.really import BLAM
    assert BLAM.made_it == 'BLAM!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1'

    # direct
    import bar.really.BLAM
    assert BLAM.made_it == bar.really.BLAM.made_it
