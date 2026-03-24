#include "Python.h"

#include "danish.h"
#include "dutch.h"
#include "english.h"
#include "french.h"
#include "german.h"
#include "italian.h"
#include "finnish.h"
#include "norwegian.h"
#include "porter.h"
#include "portuguese.h"
#include "russian.h"
#include "spanish.h"
#include "swedish.h"
#include "porter.h"
#include "header.h"


typedef struct
{
    PyObject_HEAD
    struct SN_env *env;
    char * language;
    char * encoding;
    int (* stem_func)(struct SN_env *);
}
Stemmer;

static void
Stemmer_dealloc(Stemmer *self)
{
    if (!strcmp(self->language,"porter")) {
        porter_close_env(self->env);
    } else if (!strcmp(self->language,"german")) {
        german_close_env(self->env);
    } else if (!strcmp(self->language,"finnish")) {
        finnish_close_env(self->env);
    } else if (!strcmp(self->language,"french")) {
        french_close_env(self->env);
    } else if (!strcmp(self->language,"dutch")) {
        dutch_close_env(self->env);
    } else if (!strcmp(self->language,"spanish")) {
        spanish_close_env(self->env);
    } else if (!strcmp(self->language,"english")) {
        english_close_env(self->env);
    } else if (!strcmp(self->language,"swedish")) {
        swedish_close_env(self->env);
    } else if (!strcmp(self->language,"italian")) {
        italian_close_env(self->env);
    } else if (!strcmp(self->language,"portuguese")) {
        portuguese_close_env(self->env);
    } else if (!strcmp(self->language,"danish")) {
        danish_close_env(self->env);
    } else if (!strcmp(self->language,"russian")) {
        russian_close_env(self->env);
    } else if (!strcmp(self->language,"norwegian")) {
        norwegian_close_env(self->env);
    }

    free(self->language);
    free(self->encoding);
    PyMem_DEL(self);
}


static PyObject *Stemmer_availableStemmers(Stemmer *self,PyObject*args)
{
    PyObject *list;

    list = PyList_New(0);

    PyList_Append(list,PyString_FromString("german"));
    PyList_Append(list,PyString_FromString("finnish"));
    PyList_Append(list,PyString_FromString("french"));
    PyList_Append(list,PyString_FromString("porter"));
    PyList_Append(list,PyString_FromString("english"));
    PyList_Append(list,PyString_FromString("dutch"));
    PyList_Append(list,PyString_FromString("spanish"));
    PyList_Append(list,PyString_FromString("portuguese"));
    PyList_Append(list,PyString_FromString("swedish"));
    PyList_Append(list,PyString_FromString("italian"));
    PyList_Append(list,PyString_FromString("russian"));
    PyList_Append(list,PyString_FromString("danish" ));
    PyList_Append(list,PyString_FromString("norwegian"));
    PyList_Sort(list);

    return list;
}

static PyObject *Stemmer_language(Stemmer *self,PyObject*args)
{
    PyObject *language;

    language = PyString_FromString(self->language);
    return language;
}


static PyObject *stem_unicode(Stemmer *self,PyObject *pyword)
{
    int wordlen;
    unsigned char * word;
    PyObject *stemmed=NULL;

    word    = (unsigned char * ) PyUnicode_AS_DATA(pyword);
    wordlen = PyUnicode_GET_DATA_SIZE(pyword);

    SN_set_current(self->env, wordlen/2, (symbol *) word);
    self->stem_func(self->env);

    stemmed = Py_BuildValue("u#",self->env->p,self->env->l);

    return stemmed;
}


static PyObject *Stemmer_stem(Stemmer *self,PyObject *args)
{
    PyObject *stemmed,*obj;

    if (self==NULL) {
        PyErr_SetString(PyExc_TypeError, "can not call stem() on unbound method");
        return NULL;
    }

    if (! (PyArg_ParseTuple(args,"O",&obj)))
        return NULL;

    if (PyString_Check(obj)) {
        PyObject * u_word;

        u_word = PyUnicode_FromEncodedObject(obj, self->encoding, "strict");
        stemmed = stem_unicode(self, u_word);
        Py_DECREF(u_word);

        return stemmed;

    } else if (PyUnicode_Check(obj)) {

        stemmed = stem_unicode(self, obj);
        return stemmed;

    } else if (PySequence_Check(obj)) {

        PyObject * item;
        PyObject * list;
        int i, len;

        list = PyList_New(0);

        obj = PySequence_Fast(obj, "argument must be a sequence");
        len = PyObject_Length(obj);

        for (i=0; i<len;i++) {

            item = PySequence_Fast_GET_ITEM(obj, i);

            if (PyString_Check(item)) {
                PyObject * u_word;

                u_word = PyUnicode_FromEncodedObject(item, self->encoding, "strict");
                stemmed = stem_unicode(self, u_word);
                Py_DECREF(u_word);
            } else if (PyUnicode_Check(item))
                stemmed = stem_unicode(self, item);
            else {
                PyErr_SetString(PyExc_TypeError, "Unsupported datatype found in list (neither string nor unicode)");
                return NULL;
            }

            PyList_Append(list, stemmed);
            Py_DECREF(stemmed);
        }

        Py_DECREF(obj);
        return list;
    } else {
        PyErr_SetString(PyExc_TypeError, "Unsupported datatype (must be unicode, string or sequence of strings, unicode)");
        return NULL;
    }
}


static struct PyMethodDef Stemmer_methods[] =
    {
        { "language", (PyCFunction)Stemmer_language, METH_VARARGS,
            "language() -- Returns the language of the stemmer object",
        } ,
        { "stem", (PyCFunction)Stemmer_stem, METH_VARARGS,
          "stem(word) -- Return stemmed word",
        },
        { NULL, NULL }		/* sentinel */
    };

static  PyObject *
Stemmer_getattr(Stemmer *self, char *name)
{
    return Py_FindMethod(Stemmer_methods, (PyObject *)self, name);
}

static char StemmerType__doc__[] = "Stemmer object";

static PyTypeObject StemmerType = {
                                      PyObject_HEAD_INIT(NULL)
                                      0,                            /*ob_size*/
                                      "Stemmer",                    /*tp_name*/
                                      sizeof(Stemmer),              /*tp_basicsize*/
                                      0,                            /*tp_itemsize*/
                                      /* methods */
                                      (destructor)Stemmer_dealloc,  /*tp_dealloc*/
                                      (printfunc)0,                 /*tp_print*/
                                      (getattrfunc)Stemmer_getattr, /*tp_getattr*/
                                      (setattrfunc)0,               /*tp_setattr*/
                                      (cmpfunc)0,                   /*tp_compare*/
                                      (reprfunc)0,                  /*tp_repr*/
                                      0,                            /*tp_as_number*/
                                      0,                            /*tp_as_sequence*/
                                      0,                            /*tp_as_mapping*/
                                      (hashfunc)0,                  /*tp_hash*/
                                      (ternaryfunc)0,               /*tp_call*/
                                      (reprfunc)0,                  /*tp_str*/

                                      /* Space for future expansion */
                                      0L,0L,0L,0L,
                                      StemmerType__doc__            /* Documentation string */
                                  };



static PyObject *
newStemmer(PyObject *modinfo, PyObject *args)
{
    Stemmer *self=NULL;
    char *language;

    if (! (self = PyObject_NEW(Stemmer, &StemmerType)))
        return NULL;

    if (! (PyArg_ParseTuple(args,"s",&language)))
        return NULL;

    strcpy(self->language = malloc(strlen(language)+1),language);
    self->encoding = malloc(255);

    if (!strcmp(language,"porter")) {
        self->env = porter_create_env();
        self->stem_func = porter_stem;
        strcpy(self->encoding, "iso-8859-15");
    } else if (!strcmp(language,"german")) {
        self->env = german_create_env();
        self->stem_func = german_stem;
        strcpy(self->encoding, "iso-8859-15");
    } else if (!strcmp(language,"french")) {
        self->env = french_create_env();
        self->stem_func = french_stem;
        strcpy(self->encoding, "iso-8859-15");
    } else if (!strcmp(language,"finnish")) {
        self->env = finnish_create_env();
        self->stem_func = finnish_stem;
        strcpy(self->encoding, "iso-8859-15");
    } else if (!strcmp(language,"dutch")) {
        self->env = dutch_create_env();
        self->stem_func = dutch_stem;
        strcpy(self->encoding, "iso-8859-15");
    } else if (!strcmp(language,"spanish")) {
        self->env = spanish_create_env();
        self->stem_func = spanish_stem;
        strcpy(self->encoding, "iso-8859-15");
    } else if (!strcmp(language,"english")) {
        self->env = english_create_env();
        self->stem_func = english_stem;
        strcpy(self->encoding, "iso-8859-15");
    } else if (!strcmp(language,"swedish")) {
        self->env = swedish_create_env();
        self->stem_func = swedish_stem;
        strcpy(self->encoding, "iso-8859-15");
    } else if (!strcmp(language,"italian")) {
        self->env = italian_create_env();
        self->stem_func = italian_stem;
        strcpy(self->encoding, "iso-8859-15");
    } else if (!strcmp(language,"portuguese")) {
        self->env = portuguese_create_env();
        self->stem_func = portuguese_stem;
        strcpy(self->encoding, "iso-8859-15");
    } else if (!strcmp(language,"danish")) {
        self->env = danish_create_env();
        self->stem_func = danish_stem;
        strcpy(self->encoding, "iso-8859-15");
    } else if (!strcmp(language,"russian")) {
        self->env = russian_create_env();
        self->stem_func = russian_stem;
        strcpy(self->encoding, "koi8-r");
    } else if (!strcmp(language,"norwegian")) {
        self->env = norwegian_create_env();
        self->stem_func = norwegian_stem;
        strcpy(self->encoding, "iso-8859-15");
    } else {
        char err[255];
        sprintf(err,"PyStemmer: Unsupported language '%s'",language);
        PyErr_SetString(PyExc_TypeError, err);
        goto err;
    }

    return (PyObject*)self;

err:
    Py_DECREF(self);

    return NULL;
}

static struct PyMethodDef Stemmer_module_methods[] =
    {
        { "availableStemmers", (PyCFunction) Stemmer_availableStemmers, METH_VARARGS,
            "availableStemmers() -- Return a list of all available stemmers"
        },
        { "Stemmer", (PyCFunction)newStemmer,
          METH_VARARGS,
          "Stemmer(language) "
          "-- Return a new language specific stemmer"
        },
        { NULL, NULL }
    };


void
initStemmer(void)
{
    PyObject *m, *d;
    char *rev="$Revision: 1.1.1.1 $";

    /* Create the module and add the functions */
    m = Py_InitModule3("Stemmer", Stemmer_module_methods,
                       "Stemmer module for eleven different languages");

    /* Add some symbolic constants to the module */
    d = PyModule_GetDict(m);
    PyDict_SetItemString(d, "__version__",
                         PyString_FromStringAndSize(rev+11,strlen(rev+11)-2));

    if (PyErr_Occurred())
        Py_FatalError("can't initialize module Stemmer");
}
