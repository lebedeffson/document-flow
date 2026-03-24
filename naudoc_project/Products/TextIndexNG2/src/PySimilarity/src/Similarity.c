/*
 
 TextIndexNG                The next generation TextIndex for Zope
 
 This software is governed by a license. See
 LICENSE.txt for the terms of this license.
 
*/

/*
   This Python extension implements similarity functionality
   using the Soundex and Metaphone algorithm.
 
   The soundex() and metaphone() method accept a string or
   unicode string or a sequence of strings/unicode strings.
   The result is always an ASCII string or a list of ASCII
   strings.
*/


#include "Python.h"
#include "double_metaphone.h"

extern int metaphone(char *word, int max_phonemes, char **phoned_word, int traditional);
extern char * soundex(char *word);
extern int levenshtein(char *word1, char *word2);

static PyObject *
PyAvailableAlgorithms(PyObject *modinfo, PyObject *args)
{
    return Py_BuildValue("[sss]", "double_metaphone","metaphone","soundex");
}


static PyObject *
PyMetaphone(PyObject *modinfo, PyObject *args)
{

    PyObject *data;
    char * meta;
    int    meta_len = 6;

    if (! (PyArg_ParseTuple(args,"O",&data)))
        return NULL;

    if (PyString_Check(data)) {
        PyObject *encoded;
        char *word;

        word = PyString_AsString(data);

        metaphone(word,meta_len,&meta, 0);

        encoded= Py_BuildValue("s",meta);
        free(meta);

        return encoded;

    } else if (PyUnicode_Check(data)) {

        PyObject * pyWord, *encoded;
        char * word;

        pyWord = PyUnicode_AsEncodedString(data,"ascii","ignore");

        word = PyString_AsString(pyWord);
        Py_DECREF(pyWord);

        metaphone(word, meta_len, &meta, 0);

        encoded = Py_BuildValue("s",meta);
        free(meta);

        return encoded;

    } else if (PySequence_Check(data)) {

        PyObject * list=NULL;
        int i;

        list = PyList_New(0);

        data = PySequence_Fast(data, "must be sequence");

        for (i=0; i<PyObject_Size(data);i++) {
            PyObject * encoded, *item;

            item = PySequence_Fast_GET_ITEM(data,i);

            if (PyString_Check(item)) {
                char *word ;

                word = PyString_AsString(item);
                metaphone(word,meta_len,&meta,0);

                encoded = Py_BuildValue("s",meta);
                free(meta);

            } else if (PyUnicode_Check(item)) {

                PyObject * pyWord;
                char * word;

                pyWord = PyUnicode_AsEncodedString(item,"ascii","ignore");
                word = PyString_AsString(pyWord);
                Py_DECREF(pyWord);

                metaphone(word, meta_len, &meta, 0);
                encoded = Py_BuildValue("s",meta);
                free(meta);

            } else {
                PyErr_SetString(PyExc_TypeError, "Unsupported datatype found in list (only strings allowed)");
                return NULL;
            }

            PyList_Append(list, encoded);
            Py_DECREF(encoded);
        }

        Py_DECREF(data);
        return list;

    } else {

        PyErr_SetString(PyExc_TypeError, "Unsupported datatype (must be string or sequence of strings)");

        return NULL;
    }
}

static PyObject *
PyDoubleMetaphone(PyObject *modinfo, PyObject *args)
{

    PyObject *data;

    if (! (PyArg_ParseTuple(args,"O",&data)))
        return NULL;

    if (PyString_Check(data)) {
        PyObject *encoded;
        char *word, *codes[2];

        word = PyString_AsString(data);

        DoubleMetaphone(word, codes);

        encoded = Py_BuildValue("(ss)",codes[0],codes[1]);
        free(codes[0]);
        free(codes[1]);

        return encoded;

    } else if (PyUnicode_Check(data)) {

        PyObject * pyWord, *encoded;
        static char * word, *codes[2];

        pyWord = PyUnicode_AsEncodedString(data,"ascii","ignore");

        word = PyString_AsString(pyWord);

        DoubleMetaphone(word, codes);
        Py_DECREF(pyWord);

        encoded = Py_BuildValue("(ss)",codes[0],codes[1]);
        free(codes[0]);
        free(codes[1]);

        return encoded;

    } else if (PySequence_Check(data)) {

        PyObject * list=NULL;
        int i;

        list = PyList_New(0);

        data = PySequence_Fast(data, "must be sequence");

        for (i=0; i<PyObject_Size(data);i++) {
            PyObject * encoded1, *encoded2, *item;

            item = PySequence_Fast_GET_ITEM(data,i);

            if (PyString_Check(item)) {
                char *word, *codes[2] ;

                word = PyString_AsString(item);
                DoubleMetaphone(word, codes);

                encoded1 = Py_BuildValue("s",codes[0]);
                encoded2 = Py_BuildValue("s",codes[1]);
                free(codes[0]);
                free(codes[1]);

            } else if (PyUnicode_Check(item)) {

                PyObject * pyWord;
                char * word, *codes[2];

                pyWord = PyUnicode_AsEncodedString(item,"ascii","ignore");
                word = PyString_AsString(pyWord);

                DoubleMetaphone(word, codes);
                encoded1 = Py_BuildValue("s",codes[0]);
                encoded2 = Py_BuildValue("s",codes[1]);

                Py_DECREF(pyWord);
                free(codes[0]);
                free(codes[1]);
                

            } else {
                PyErr_SetString(PyExc_TypeError, "Unsupported datatype found in list (only strings allowed)");
                return NULL;
            }


            PyList_Append(list, encoded1);
            PyList_Append(list, encoded2);
            Py_DECREF(encoded1);
            Py_DECREF(encoded2);
        }

        Py_DECREF(data);
        return list;

    } else {

        PyErr_SetString(PyExc_TypeError, "Unsupported datatype (must be string or sequence of strings)");

        return NULL;
    }
}



static PyObject *
PySoundex(PyObject *modinfo, PyObject *args)
{
    PyObject *data;

    if (! (PyArg_ParseTuple(args,"O",&data)))
        return NULL;


    if (PyString_Check(data)) {
        PyObject *encoded;
        char * res,*word;

        word = PyString_AsString(data);
        res = soundex(word);

        encoded = Py_BuildValue("s",res);
        free(res);

        return encoded;

    } else if (PyUnicode_Check(data)) {

        PyObject * pyWord, *encoded;
        char * word, *res;

        pyWord = PyUnicode_AsEncodedString(data,"ascii","ignore");
        word = PyString_AsString(pyWord);
        Py_DECREF(pyWord);

        res = soundex(word);
        encoded = Py_BuildValue("s",res);
        free(res);

        return encoded;

    } else if (PySequence_Check(data)) {

        PyObject * item=NULL,*list=NULL,*encoded=NULL;
        char *word = NULL,*res = NULL;
        int i;

        list = PyList_New(0);

        data = PySequence_Fast(data, "must be sequence");

        for (i=0; i<PyObject_Size(data);i++) {

            item = PySequence_Fast_GET_ITEM(data,i);

            if (PyString_Check(item)) {

                word = PyString_AsString(item);
                res = soundex(word);
                encoded = Py_BuildValue("s",res);
                free(res);

            } else if (PyUnicode_Check(item)) {

                PyObject * pyWord;
                char * word, *res;

                pyWord = PyUnicode_AsEncodedString(item,"ascii","ignore");
                word = PyString_AsString(pyWord);
                Py_DECREF(pyWord);

                res = soundex(word);
                encoded = Py_BuildValue("s",res);
                free(res);

            } else {
                PyErr_SetString(PyExc_TypeError, "Unsupported datatype found in list (only strings allowed)");
                return NULL;
            }

            PyList_Append(list, encoded);
            Py_DECREF(encoded);
        }

        Py_DECREF(data);
        return list;

    } else {

        PyErr_SetString(PyExc_TypeError, "Unsupported datatype (must be string or sequence of strings)");

        return NULL;
    }
}


static  PyObject *
PyLevenshtein(PyObject *modinfo, PyObject *args)
{
    PyObject * res=NULL;
    char *word1, *word2;
    int distance;

    if (! (PyArg_ParseTuple(args,"ss",&word1,&word2)))
        return NULL;

    distance = levenshtein(word1,word2);

    res = PyInt_FromLong( (long) distance);
    fflush(stdout);

    return res;
}

static struct PyMethodDef Similarity_module_methods[] =
    {
        { "availableAlgorithms", (PyCFunction)PyAvailableAlgorithms,
            METH_VARARGS,
            "availableAlgorithms() "
            "-- return list of available string Similarity algorithms"
        },
        { "metaphone", (PyCFunction)PyMetaphone,
          METH_VARARGS,
          "metaphone(word,[encoding_len=6]) "
          "-- return metaphone encoding for a word or a sequence of words"
        },
        { "double_metaphone", (PyCFunction)PyDoubleMetaphone,
          METH_VARARGS,
          "double_metaphone(word) "
          "-- return double metaphone encoding for a word or a sequence of words"
        },
        { "soundex", (PyCFunction)PySoundex,
          METH_VARARGS,
          "soundex(word) "
          "-- return soundex encoding for a word or a sequence of words"
        },
        { "levenshtein", (PyCFunction)PyLevenshtein,
          METH_VARARGS,
          "levenshtein(word1,word2)"
          "-- return computed distances between word1 and word2"
        },
        { NULL, NULL }
    };


void
initSimilarity(void)
{
    Py_InitModule3("Similarity", Similarity_module_methods,
                       "Module for string Similarity algorithms");
}
