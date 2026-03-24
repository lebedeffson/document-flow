/*
  Levenshtein.c v2003-04-10
  Python extension computing Levenshtein distances, string similarities,
  median strings and other goodies.

  Copyright (C) 2002-2003 David Necas (Yeti) <yeti@physics.muni.cz>.

  This program is free software; you can redistribute it and/or modify it
  under the terms of the GNU General Public License as published by the Free
  Software Foundation; either version 2 of the License, or (at your option)
  any later version.

  This program is distributed in the hope that it will be useful, but WITHOUT
  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
  more details.

  You should have received a copy of the GNU General Public License along
  with this program; if not, write to the Free Software Foundation, Inc.,
  59 Temple Place, Suite 330, Boston, MA 02111-1307 USA.
*/

/**
 * TODO:
 *
 * - Implement weighted string averaging, see:
 *   H. Bunke et. al.: On the Weighted Mean of a Pair of Strings,
 *         Pattern Analysis and Applications 2002, 5(1): 23-30.
 *   X. Jiang et. al.: Dynamic Computations of Generalized Median Strings,
 *         Pattern Analysis and Applications 2002, ???.
 *   The latter also contains an interesting median-search algorithm.
 *
 * - A `hierarchical greedy' generalized median algorithm with bound
 *   competitive ratio:
 *   R. Mettu, C. Plaxton: The Online Median Problem,
 *         IEEE Symposium on Foundations of Computer Science 2000, 339-348.
 *
 * - A linear approximate set median algorithm:
 *   P. Indyk: Sublinear time algorithms for metric space problems,
 *         STOC 1999, http://citeseer.nj.nec.com/indyk00sublinear.html.
 *
 **/
#ifdef NO_PYTHON
#define _GNU_SOURCE
#include <string.h>
#include <math.h>
#else /* NO_PYTHON */
#define LEV_STATIC_PY static
#define lev_wchar Py_UNICODE
#include <Python.h>
#endif /* NO_PYTHON */
#include <assert.h>
#include <stdio.h>
#include "Levenshtein.h"

#ifndef NO_PYTHON
/* python interface and wrappers */
static PyObject* distance_py(PyObject *self, PyObject *args);
static PyObject* ratio_py(PyObject *self, PyObject *args);

#define Levenshtein_DESC \
  "A C extension module for fast computation of:\n" \
  "- Levenshtein (edit) distance and edit sequence manipluation\n" \
  "- string similarity\n" \
  "- approximate median strings, and generally string averaging\n" \
  "- string sequence and set similarity\n" \
  "\n" \
  "Levenshtein has a large overlap with difflib (SequenceMatcher).  It\n" \
  "supports only strings, not arbitrary sequence types, but on the\n" \
  "other hand it's much faster.\n" \
  "\n" \
  "It supports both normal and Unicode strings, but can't mix them, all\n" \
  "arguments to a function (method) have to be of the same type (or its\n" \
  "subclasses).\n"

#define distance_DESC \
  "Compute absolute Levenshtein distance of two strings.\n" \
  "\n" \
  "Examples (it's hard to spell Levenshtein correctly):\n" \
  ">>> distance('Levenshtein', 'Lenvinsten')\n" \
  "4\n" \
  ">>> distance('Levenshtein', 'Levensthein')\n" \
  "2\n" \
  ">>> distance('Levenshtein', 'Levenshten')\n" \
  "1\n" \
  ">>> distance('Levenshtein', 'Levenshtein')\n" \
  "0\n" \
  "\n" \
  "Yeah, we've managed it at last.\n"

#define ratio_DESC \
  "Compute similarity of two strings.\n" \
  "\n" \
  "The similarity is a number between 0 and 1, it's usually equal or\n" \
  "somewhat higher than difflib.SequenceMatcher.ratio(), becuase it's\n" \
  "based on real minimal edit distance.\n" \
  "\n" \
  "Examples:\n" \
  ">>> ratio('Hello world!', 'Holly grail!')\n" \
  "0.58333333333333337\n" \
  ">>> ratio('Brian', 'Jesus')\n" \
  "0.0\n" \
  "\n" \
  "Really?  I thought there was some smiliarity.\n"



#define METHODS_ITEM(x) { #x, x##_py, METH_VARARGS, x##_DESC }
PyMethodDef methods[] = {
  METHODS_ITEM(distance),
  METHODS_ITEM(ratio),
  { NULL, NULL, 0, NULL },
};


static long int
levenshtein_common(PyObject *args,
                   char *name,
                   size_t xcost,
                   size_t *lensum);

/****************************************************************************
 *
 * Python interface and subroutines
 *
 ****************************************************************************/

static long int
levenshtein_common(PyObject *args, char *name, size_t xcost,
                   size_t *lensum)
{
  PyObject *arg1, *arg2;
  size_t len1, len2;

  if (!PyArg_ParseTuple(args, "OO", &arg1, &arg2))
    return -1;

  if (PyUnicode_Check(arg1)
      && PyUnicode_Check(arg2)) {
    Py_UNICODE *string1, *string2;

    len1 = PyUnicode_GET_SIZE(arg1);
    len2 = PyUnicode_GET_SIZE(arg2);
    *lensum = len1 + len2;
    string1 = PyUnicode_AS_UNICODE(arg1);
    string2 = PyUnicode_AS_UNICODE(arg2);
    return lev_u_edit_distance(len1, string1, len2, string2, xcost);
  }
  else {
    PyErr_Format(PyExc_ValueError,
                 "%s expected two Strings or two Unicodes", name);
    return -1;
  }
}

static PyObject*
distance_py(PyObject *self, PyObject *args)
{
  size_t lensum;
  long int ldist;

  if ((ldist = levenshtein_common(args, "distance", 0, &lensum)) < 0)
    return NULL;

  return Py_BuildValue("l", ldist);
}

static PyObject*
ratio_py(PyObject *self, PyObject *args)
{
  size_t lensum;
  long int ldist;

  if ((ldist = levenshtein_common(args, "ratio", 1, &lensum)) < 0)
    return NULL;

  if (lensum == 0)
    return Py_BuildValue("d", 1.0);

  return Py_BuildValue("d", (double)(lensum - ldist)/(lensum));
}



void
initLevenshtein(void)
{
  PyObject *module;
  module = Py_InitModule3("Levenshtein", methods, Levenshtein_DESC);
}
#endif /* not NO_PYTHON */


/****************************************************************************
 *
 * Basic stuff, Levenshtein distance
 *
 ****************************************************************************/

#define EPSILON 1e-14


/*
 * Levenshtein distance between string1 and string2 (Unicode).
 *
 * Replace cost is normally 1, and 2 with nonzero xcost.
 */
LEV_STATIC_PY size_t
lev_u_edit_distance(size_t len1, const lev_wchar *string1,
                    size_t len2, const lev_wchar *string2,
                    size_t xcost)
{
  size_t i;
  size_t *row;  /* we only need to keep one row of costs */
  size_t *end;
  size_t half;

  /* strip common prefix */
  while (len1 > 0 && len2 > 0 && *string1 == *string2) {
    len1--;
    len2--;
    string1++;
    string2++;
  }

  /* strip common suffix */
  while (len1 > 0 && len2 > 0 && string1[len1-1] == string2[len2-1]) {
    len1--;
    len2--;
  }

  /* catch trivial cases */
  if (len1 == 0)
    return len2;
  if (len2 == 0)
    return len1;

  /* make the inner cycle (i.e. string2) the longer one */
  if (len1 > len2) {
    size_t nx = len1;
    const lev_wchar *sx = string1;
    len1 = len2;
    len2 = nx;
    string1 = string2;
    string2 = sx;
  }
  /* check len1 == 1 separately */
  if (len1 == 1) {
    lev_wchar z = *string1;
    const lev_wchar *p = string2;
    for (i = len2; i; i--) {
      if (*(p++) == z)
        return len2 - 1;
    }
    return len2 + (xcost != 0);
  }
  len1++;
  len2++;
  half = len1 >> 1;

  /* initalize first row */
  row = (size_t*)malloc(len2*sizeof(size_t));
  end = row + len2 - 1;
  for (i = 0; i < len2 - (xcost ? 0 : half); i++)
    row[i] = i;

  /* go through the matrix and compute the costs.  yes, this is an extremely
   * obfuscated version, but also extremely memory-conservative and relatively
   * fast.  */
  if (xcost) {
    for (i = 1; i < len1; i++) {
      size_t *p = row + 1;
      const lev_wchar char1 = string1[i - 1];
      const lev_wchar *char2p = string2;
      size_t D = i - 1;
      size_t x = i;
      while (p <= end) {
        if (char1 == *(char2p++))
          x = D;
        else
          x++;
        D = *p;
        if (x > D + 1)
          x = D + 1;
        *(p++) = x;
      }
    }
  }
  else {
    /* in this case we don't have to scan two corner triangles (of size len1/2)
     * in the matrix because no best path can go throught them. note this
     * breaks when len1 == len2 == 2 so the memchr() special case above is
     * necessary */
    row[0] = len1 - half - 1;
    for (i = 1; i < len1; i++) {
      size_t *p;
      const lev_wchar char1 = string1[i - 1];
      const lev_wchar *char2p;
      size_t D, x;
      /* skip the upper triangle */
      if (i >= len1 - half) {
        size_t offset = i - (len1 - half);
        size_t c3;

        char2p = string2 + offset;
        p = row + offset;
        c3 = *(p++) + (char1 != *(char2p++));
        x = *p;
        x++;
        D = x;
        if (x > c3)
          x = c3;
        *(p++) = x;
      }
      else {
        p = row + 1;
        char2p = string2;
        D = x = i;
      }
      /* skip the lower triangle */
      if (i <= half + 1)
        end = row + len2 + i - half - 2;
      /* main */
      while (p <= end) {
        size_t c3 = --D + (char1 != *(char2p++));
        x++;
        if (x > c3)
          x = c3;
        D = *p;
        D++;
        if (x > D)
          x = D;
        *(p++) = x;
      }
      /* lower triangle sentinel */
      if (i <= half) {
        size_t c3 = --D + (char1 != *char2p);
        x++;
        if (x > c3)
          x = c3;
        *p = x;
      }
    }
  }

  i = *end;
  free(row);
  return i;
}

