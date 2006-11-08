import os
import socket
import sys
from optparse import OptionParser
from os.path import join, isdir, realpath

try:
    import pwd
    WINDOWS = False
except:
    WINDOWS = True

import mode


class ConfigError(StandardError):
    """This is an error in any part of our configuration.
    """

    def __init__(self, msg):
        StandardError.__init__(self)
        self.msg = msg

    def __str__(self):
        return self.msg


class Configuration:
    """Represent the configuration of an aspen server from three sources:

        - defaults  hard-wired defaults
        - env       environment variables
        - opts      command line options

    All options may be specified on the command line. Additionally, mode and
    threads may be set in the environment. Environment variables override
    defaults, and command line options override both.

    Instances of this class are callables that take a sys.argv-style list, and
    return a 5-tuple:

        address     the address to bind to
        daemonize   whether or not to daemonize the process
        log_error     if given, stdout and stderr will be sent here
        threads     the number of threads to start
        uid         the uid of the user to run as
        mode        the httpy mode
        paths       an object containing useful paths (root, __, lib)

    """

    options = ( 'address'
              , 'daemonize'
              , 'log_error'
              , 'mode'
              , 'root'
              , 'threads'
              , 'user'
               )


    # Defaults
    # ========

    address     = ('', 8080)
    daemonize   = False
    log_access  = None # when httpy provides remote IP, then support this
    log_error   = None
    mode        = 'development'
    threads     = 10
    uid         = ''
    root        = os.getcwd()


    def __init__(self, argv):

        # Environment
        # ===========

        for key in ('mode', 'threads'):
            envvar = 'HTTPY_%s' % key.upper()
            if os.environ.has_key(envvar):
                value = os.environ.get(envvar)
                validate = getattr(self, '_validate_%s' % key)
                setattr(self, key, validate('environment', value))


        # Command-line
        # ============

        usage = "http://www.zetadev.com/software/aspen/"
        parser_ = OptionParser(usage=usage)
        parser_.add_option( "-a", "--address"
                          , dest="address"
                          , help="the address to listen on [<INADDR_ANY>:8080]"
                           )
        parser_.add_option( "-d", "--daemonize"
                          , dest="daemonize"
                          , action='store_true'
                          , help="if given, daemonize the process"
                           )
        parser_.add_option( "-l", "--log_access"
                          , dest="log_access"
                          , help="not supported yet (httpy doesn't provide IP)"
                           )
        parser_.add_option( "-e", "--log_error"
                          , dest="log_error"
                          , help="if given, std{out,err} will be sent here"
                           )
        parser_.add_option( "-m", "--mode"
                          , dest="mode"
                          , help="one of: deployment, staging, development, " +
                                 "debugging [deployment]"
                           )
        parser_.add_option( "-r", "--root"
                          , dest="root"
                          , help="the publishing root directory [.]"
                           )
        parser_.add_option( "-t", "--threads"
                          , dest="threads"
                          , help="the number of worker threads to use [10]"
                           )
        parser_.add_option( "-u", "--user"
                          , dest="user"
                          , help="the user account to run as []"
                           )
        opts, args = parser_.parse_args(args=argv)

        if opts:
            for key in self.options:
                if hasattr(opts, key):
                    value = getattr(opts, key)
                    if value is not None:
                        validate = getattr(self, '_validate_%s' % key)
                        setattr(self, key, validate('command line', value))


        # Search for paths and return.
        # ============================

        class Paths:
            pass
        paths = Paths()
        paths.root = self.root
        paths.__ = join(paths.root, '__')
        if not isdir(paths.__):
            paths.__ = None
            paths.lib = None
            paths.plat = None
        else:
            lib = join(paths.__, 'lib', 'python'+sys.version[:3])
            paths.lib = isdir(lib) and lib or None
            sys.path.insert(0, lib)

            plat = join(lib, 'plat-'+sys.platform)
            paths.plat = isdir(plat) and plat or None
            sys.path.insert(0, plat)

        self.paths = paths



    # Validators
    # ==========

    def _validate_address(self, context, candidate):
        """Must be a valid address for the given socket family.
        """

        def const2name(n):
            if n==1: return 'AF_UNIX'
            if n==2: return 'AF_INET'
            if n==28: return 'AF_INET6'

        msg = "Found bad address `%s' for address family `%s'."
        self.sockfam = 2
        msg = msg % (candidate, const2name(self.sockfam))
        err = ConfigError(msg)


        if not isinstance(candidate, basestring):
            raise err

        if candidate[0] in ('/','.'):
            if WINDOWS:
                raise ConfigError("Can't use an AF_UNIX socket on Windows.")
                # but what about named pipes?
            self.sockfam = socket.AF_UNIX
            # We could test to see if the path exists or is creatable, etc.
            candidate = realpath(candidate)

        else:
            self.sockfam = socket.AF_INET
            # Here we need a tuple: (str, int). The string must be a valid
            # IPv4 address or the empty string, and the int -- the port --
            # must be between 0 and 65535, inclusive.


            # Break out IP and port.
            # ======================

            if isinstance(candidate, (tuple, list)):
                if len(candidate) != 2:
                    raise err
                ip, port = candidate
            elif isinstance(candidate, basestring):
                if candidate.count(':') != 1:
                    raise err
                ip_port = candidate.split(':')
                ip, port = [i.strip() for i in ip_port]
            else:
                raise err


            # IP
            # ==

            if not isinstance(ip, basestring):
                raise err
            elif ip != '': # Blank ip is ok, just don't try to validate it.
                try:
                    socket.inet_aton(ip)
                except socket.error:
                    raise err


            # port
            # ====
            # Coerce to int. Must be between 0 and 65535, inclusive.

            if isinstance(port, basestring):
                if not port.isdigit():
                    raise err
                else:
                    port = int(port)
            elif isinstance(port, int) and not (port is False):
                # already an int for some reason (called interactively?)
                pass
            else:
                raise err

            if not(0 <= port <= 65535):
                raise err


            # Success!
            # ========

            candidate = (ip, port)


        return candidate


    def _validate_daemonize(self, context, candidate):
        """Should only ever be True or False.
        """
        assert candidate in (True, False)
        return candidate


    def _validate_log_error(self, context, candidate):
        return candidate

    def _validate_log_access(self, context, candidate):
        return candidate


    def _validate_mode(self, context, candidate):
        """We expand abbreviations to the full term.
        """

        msg = ("Found bad mode `%s' in context `%s'. Mode must be " +
               "either `deployment,' `staging,' `development' or " +
               "`debugging.' Abbreviations are fine.")
        msg = msg % (str(candidate), context)

        if not isinstance(candidate, basestring):
            raise ConfigError(msg)

        candidate = candidate.lower()
        if candidate not in mode.__options:
            raise ConfigError(msg)
        return mode


    def _validate_root(self, context, candidate):
        """Must be a valid directory (also check perms?)
        """

        msg = "Found bad root `%s' in context `%s'. " +\
              "Root must point to a directory."
        msg = msg % (str(candidate), context)

        if isinstance(candidate, basestring):
            candidate = realpath(candidate)
        else:
            raise ConfigError(msg)

        if not isdir(candidate):
            raise ConfigError(msg)

        return candidate


    def _validate_threads(self, context, candidate):
        """Must be an integer greater than or equal to 1.
        """

        msg = ("Found bad thread count `%s' in context `%s'. " +
               "Threads must be an integer greater than or equal to one.")
        msg = msg % (str(candidate), context)

        if not isinstance(candidate, (int, long)):
            isstring = isinstance(candidate, basestring)
            if not isstring or not candidate.isdigit():
                raise ConfigError(msg)
        candidate = int(candidate)
        if not candidate >= 1:
            raise ConfigError(msg)

        return candidate


    def _validate_user(self, context, candidate):
        """Must be a valid user account on this system.
        """

        if WINDOWS:
            raise ConfigError("This option is not available on Windows.")

        msg = ("Found bad user `%s' in context `%s'. " +
               "User must be a valid user account on this system.")
        msg = msg % (str(candidate), context)

        try:
            candidate = pwd.getpwnam(candidate)[2]
        except KeyError:
            raise ConfigError(msg)

        return candidate
