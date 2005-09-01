from httpy.app import FilesystemMixin


class Transaction(FilesystemMixin):





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




