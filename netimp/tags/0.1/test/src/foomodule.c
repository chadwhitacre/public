#include <Python.h>

PyMODINIT_FUNC
init_foo(void)
{
    PyObject *m;
    m = Py_InitModule("_foo", NULL); /* NULL instead of PyMethodDef, no? */
    PyDict_SetItemString( PyModule_GetDict(m)
                        , "made_it"
                        , PyString_FromString("BLAM!!!!!!!!!!!!!!!!!!!!")
                         );
}
