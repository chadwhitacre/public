"""Simplate module

A simple template that stores a text block and does python string replacement on 
it.
"""

#__version__='$Revision: 1.30.10.1 $'[11:-2] I wonder where this comes from?

from ExtensionClass import Base

class Simplate(Base):
    "Simplate using python string replacement"

    content_type = 'text/plain'
    expand = 0
    _v_errors = ()
    _v_warnings = ()
    _v_cooked = 0
    id = '(unknown)'
    _text = ''

    def StringIO(self):
        # Third-party products wishing to provide a full Unicode-aware
        # StringIO can do so by monkey-patching this method.
        return FasterStringIO()

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

        return self._text

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
        if not self._v_cooked:
            self._cook()
        err = self._v_errors
        if err:
            return err
        if not self.expand: return
#        try:
#            self.simplate_render(source=1)
#        except:
#            return ('Macro expansion failed', '%s: %s' % sys.exc_info()[:2])

    def simplate_warnings(self):
        if not self._v_cooked:
            self._cook()
        return self._v_warnings

#    def simplate_macros(self):
#        if not self._v_cooked:
#            self._cook()
#        if self._v_errors:
#            __traceback_supplement__ = (SimplateTracebackSupplement, self)
#            raise SimplateRuntimeError, 'Simplate %s has errors.' % self.id
#        return self._v_macros

    def simplate_source_file(self):
        return None  # Unknown.

    def write(self, text):
        assert type(text) is type('')
#        if text[:len(self._error_start)] == self._error_start:
#            errend = text.find('-->')
#            if errend >= 0:
#                text = text[errend + 4:]
        if self._text != text:
            self._text = text
        self._cook()

    def read(self):
        self._cook_check()
        if not self._v_errors:
#            if not self.expand:
#                return self._text
#            try:
#                return self.simplate_render(source=1)
#            except:
#                return ('%s\n Macro expansion failed\n %s\n-->\n%s' %
#                        (self._error_start, "%s: %s" % sys.exc_info()[:2],
#                         self._text) )
            return self._text

        return ('%s\n %s\n-->\n%s' % (self._error_start,
                                      '\n '.join(self._v_errors),
                                      self._text))

    def _cook_check(self):
        if not self._v_cooked:
            self._cook()

    def _cook(self):
        """Do the string replacement.

        Cooking must not fail due to compilation errors in templates.
        """
        source_file = self.simplate_source_file()
#        if self.html():
#            gen = TALGenerator(getEngine(), xml=0, source_file=source_file)
#            parser = HTMLTALParser(gen)
#        else:
#            gen = TALGenerator(getEngine(), source_file=source_file)
#            parser = TALParser(gen)

        self._v_errors = ()
#        try:
#            parser.parseString(self._text)
#            self._v_program, self._v_macros = parser.getCode()
#        except:
#            self._v_errors = ["Compilation failed",
#                              "%s: %s" % sys.exc_info()[:2]]
#        self._v_warnings = parser.getWarnings()
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
    #__implements__ = ITracebackSupplement

    def __init__(self, smpt):
        self.object = smpt
        w = smpt.simplate_warnings()
        e = smpt.simplate_errors()
        if e:
            w = list(w) + list(e)
        self.warnings = w

