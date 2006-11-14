from os.path import join


class AspenError(StandardError): pass

class HandlerError(AspenError): pass
class HookError(AspenError): pass
class RuleError(AspenError): pass

class ConfigError(AspenError):
    def __init__(self, msg, lineno):
        AspenError.__init__(self)
        self.msg = msg
        self.lineno = int(lineno)
    def __str__(self):
        opts = (self.msg, self.filename, self.lineno)
        return '%s (%s, line %d)' % opts
    __repr__ = __str__

class HandlersConfError(ConfigError):
    filename = join('__', 'etc', 'handlers.conf')

class HooksConfError(ConfigError):
    filename = join('__', 'etc', 'hooks.conf')

class AppsConfError(ConfigError):
    filename = join('__', 'etc', 'apps.conf')

class MiddlewareConfError(ConfigError):
    filename = join('__', 'etc', 'middleware.conf')
