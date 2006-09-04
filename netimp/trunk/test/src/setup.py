from distutils.core import setup, Extension
setup(ext_modules=[Extension('_foo', sources = ['foomodule.c'])])