"""Simplate module

A simple template that stores a text block and does python string replacement on 
it.
"""

__version__ = '0.2'

import sys
from ExtensionClass import Base

class Simplate(Base):
    "Simplate using python string replacement"

    content_type = 'text/plain'
    value_paths = []
    _v_errors = []
    _v_warnings = []
    _v_cooked = 0
    id = '(unknown)'
    _text = ''
    _value_dict = {}
    _error_start = '<!-- Simplate Diagnostics'


    def simplate_edit(self, text, content_type):
        if content_type:
            self.content_type = str(content_type)
        if hasattr(text, 'read'):
            text = text.read()
        self.write(text)

    def simplate_getContext(self):
        c = {'template': self,
             'options': {},
             'nothing': None,
             'request': None,
             'modules': ModuleImporter,
             }
        parent = getattr(self, 'aq_parent', None)
        if parent is not None:
            c['here'] = parent
            c['context'] = parent
            c['container'] = self.aq_inner.aq_parent
            while parent is not None:
                self = parent
                parent = getattr(self, 'aq_parent', None)
            c['root'] = self
        return c

    def simplate_render(self, source=0, extra_context={}):
        """Render the Simplate"""
        if not self._v_cooked:
            self._cook()

        __traceback_supplement__ = (SimplateTracebackSupplement, self)

        if self._v_errors:
            raise SimplateRuntimeError, 'Simplate %s has errors.' % self.id

        return self._replace()

#        output = self.StringIO()
#        c = self.simplate_getContext()
#        c.update(extra_context)
#
#        TALInterpreter(self._v_program, self._v_macros,
#                       getEngine().getContext(c),
#                       output,
#                       tal=not source, strictinsert=0)()
#        return output.getvalue()

    def __call__(self, *args, **kwargs):
        if not kwargs.has_key('args'):
            kwargs['args'] = args
        return self.simplate_render(extra_context={'options': kwargs})


    def simplate_errors(self):
        self._cook_check()
        err = self._v_errors
        if err:
            return err
#        if not self.expand: return
#        try:
#            self.simplate_render(source=1)
#        except:
#            return ('Macro expansion failed', '%s: %s' % sys.exc_info()[:2])

    def simplate_warnings(self):
        self._cook_check()
        return self._v_warnings

    def simplate_source_file(self):
        return None  # Unknown.

    def write(self, text):
        assert type(text) is type('')
        if self._text != text:
            self._text = text
        self._cook()

    def read(self):
        self._cook_check()
        if not self._v_errors:
            return self._text

        return ('%s\n %s\n-->\n%s' % (self._error_start,
                                      '\n '.join(['\n '.join(err) for err in self._v_errors]),
                                      self._text))

    def _replace(self):
        # First, do some escapes. Then do replacement if we have anything to replace with.
        unprocessed = self._text.replace('%','%%').replace('%%(','%(').replace('%%%(','%%(')
        if self._value_dict:
            return unprocessed % self._value_dict
        else:
            return unprocessed


    def _cook_check(self):
        if not self._v_cooked:
            self._cook()

    def _cook(self):
        """Cook the simplate, testing all the while."""

        self._v_errors = []
        self._v_warnings = []

        ##
        # 1. Get the list of paths
        ##

        self._value_dict = {}
        paths = list(self.value_paths)
        paths.reverse()
        
        ##
        # 2. Build a master dictionary from the paths
        ##
        
        for path in paths:
            if path:
                try:
                    value_obj = self.restrictedTraverse(path)
                    value = value_obj()
                    if type(value) == type({}):
                        self._value_dict.update(value)
                    else:
                        warning = "'%s' does not return a dictionary."
                        self._v_warnings.append(warning % value_obj.id)
                except 'NotFound':
                    error = "MISSING OBJECT -- %s: %s" % sys.exc_info()[:2]
                    self._v_errors.append(error)

        ##
        # 3. Attempt the substitution
        ## 
        
        try:
            self._replace()
        except KeyError: # The value_dict did not supply all the values
            error = "REPLACEMENT FAILURE -- No object supplies the value %s" % sys.exc_info()[1]
            self._v_errors.append(error)
        except:
            error = "COMPILATION FAILURE -- %s: %s" % sys.exc_info()[:2]
            self._v_errors.append(error)

        self._v_cooked = 1
        
#    def html(self):
#        if not hasattr(getattr(self, 'aq_base', self), 'is_html'):
#            return self.content_type == 'text/html'
#        return self.is_html

#class _ModuleImporter:
#    def __getitem__(self, module):
#        mod = __import__(module)
#        path = module.split('.')
#        for name in path[1:]:
#            mod = getattr(mod, name)
#        return mod
#
#ModuleImporter = _ModuleImporter()

class SimplateRuntimeError(RuntimeError):
    '''The Simplate has template errors that prevent it from rendering.'''
    pass


class SimplateTracebackSupplement:
    def __init__(self, smpt):
        self.object = smpt
        w = smpt.simplate_warnings()
        e = smpt.simplate_errors()
        if e:
            w = list(w) + list(e)
        self.warnings = w

