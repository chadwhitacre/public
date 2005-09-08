========================================
    FORK -- flynn.pub
========================================
do something smart with DOC_TYPE
    make it a config option
    with smart names -- `xhtml transitional'
if frame.pt throws an error then the path isn't checked?
probably encoding issues here as well


========================================
    FORK -- flynn.app
========================================
supporting on-the-fly reloading of apps in dev mode
document apps
tests



from httpy.app import DynamicMixin


class Transaction(DynamicMixin):





        # defaults
        # ========
        # Coerce to a tuple. Must be filenames only, no paths.

        if d.has_key('defaults'):

            msg = "Found bad defaults '%s' in context '%s'. Defaults " +\
                  "must be a whitespace- or comma-separated list of filenames."
            msg = msg % (str(d['defaults']), context)

            if isinstance(d['defaults'], basestring):
                if ',' in d['defaults']:
                    d['defaults'] = tuple(d['defaults'].split(','))
                else:
                    d['defaults'] = tuple(d['defaults'].split())
            elif isinstance(d['defaults'], tuple):
                pass # already a tuple for some reason (called interactively?)
            else:
                raise ConfigError(msg)

            for filename in d['defaults']:
                if os.sep in filename:
                    raise ConfigError(msg)


        # extensions
        # ==========
        # Coerce to a tuple. Only allow alphanumeric characters

        if d.has_key('extensions'):

            msg = "Found bad defaults '%s' in context '%s'. Extensions " +\
                  "must be a whitespace- or comma-separated list of " +\
                  "alphanumeric filename extensions."
            msg = msg % (str(d['extensions']), context)

            if isinstance(d['extensions'], basestring):
                if ',' in d['extensions']:
                    d['extensions'] = tuple(d['extensions'].split(','))
                else:
                    d['extensions'] = tuple(d['extensions'].split())
            elif isinstance(d['extensions'], tuple):
                pass # already a tuple for some reason (called interactively?)
            else:
                raise ConfigError(msg)

            for ext in d['extensions']:
                if not ext.isalnum():
                    raise ConfigError(msg)











    # defaults
    # ========

    def testGoodDefaults(self):
        d = {'defaults':('index.html', 'index.pt')}
        expected = d.copy()
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

    def testStringCoercedToTuple(self):
        d = {'defaults':'index.html index.pt'}
        expected = {'defaults':('index.html', 'index.pt')}
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

    def testFilenameWithPathSepsRaisesError(self):
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'defaults':'/etc/master.passwd'}
                          )

    def testDefaultsErrorMessage(self):
        d = {'defaults':None}
        try:
            self.config._validate('test', d)
        except ConfigError, err:
            expected = "Found bad defaults `None' in context ('test'. " +\
                       "Defaults must be a whitespace- or comma-separated " +\
                       "list of filenames."
            actual = err.msg
            self.assertEqual(expected, actual)


    # extensions
    # ==========

    def testGoodExtensions(self):
        d = {'extensions':('pt',)}
        expected = d.copy()
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

    def testStringCoercedToTuple(self):
        d = {'extensions':'html pt'}
        expected = {'extensions':('html', 'pt')}
        actual = self.config._validate('test', d)
        self.assertEqual(expected, actual)

    def testNonAlphanumExtensionsRaisesError(self):
        self.assertRaises( ConfigError
                         , self.config._validate
                         , 'test', {'extensions':'$pt'}
                          )

    def testExtensionsErrorMessage(self):
        d = {'extensions':None}
        try:
            self.config._validate('test', d)
        except ConfigError, err:
            expected = "Found bad defaults `None' in context ('test'. " +\
                       "Extensions must be a whitespace- or comma-" +\
                       "separated list of alphanumeric filename extensions."
            actual = err.msg
            self.assertEqual(expected, actual)


