/*

 TextIndexNG                The next generation TextIndex for Zope

 This software is governed by a license. See
 LICENSE.txt for the terms of this license.

*/


#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <ctype.h>

/* 
    Simple soundex algorithm as described by Knuth in TAOCP, vol 3
    implementation details borrowed from PHP's ext/standard/soundex.c
    (See www.php.net for more info)
*/



char * soundex(char *somestring)
{
    int	i, _small, len, code, last;
    char	 * soundex;

    static char soundex_table[26] =
        {0,							/* A */
         '1',						/* B */
         '2',						/* C */
         '3',						/* D */
         0,							/* E */
         '1',						/* F */
         '2',						/* G */
         0,							/* H */
         0,							/* I */
         '2',						/* J */
         '2',						/* K */
         '4',						/* L */
         '5',						/* M */
         '5',						/* N */
         0,							/* O */
         '1',						/* P */
         '2',						/* Q */
         '6',						/* R */
         '2',						/* S */
         '3',						/* T */
         0,							/* U */
         '1',						/* V */
         0,							/* W */
         '2',						/* X */
         0,							/* Y */
         '2'};						/* Z */

    len = strlen(somestring);
    soundex = (char *) malloc(10);

    /* build soundex string */
    last = -1;
    for (i = 0, _small = 0; i < len && _small < 4; i++) {

        /* convert chars to upper case and strip non-letter chars */
        /* BUG: should also map here accented letters used in non */
        /* English words or names (also found in English text!): */
        /* esstsett, thorn, n-tilde, c-cedilla, s-caron, ... */

        code = toupper(somestring[i]);
        if (code >= 'A' && code <= 'Z') {
            if (_small == 0) {
                /* remember first valid char */
                soundex[_small++] = code;
                last = soundex_table[code - 'A'];
            } else {
                /* ignore sequences of consonants with same soundex */
                /* code in trail, and vowels unless they separate */
                /* consonant letters */
                code = soundex_table[code - 'A'];
                if (code != last) {
                    if (code != 0) {
                        soundex[_small++] = code;
                    }
                    last = code;
                }
            }
        }
    }

    /* pad with '0' and terminate with 0 ;-) */

    while (_small < 4) {
        soundex[_small++] = '0';
    }
    soundex[_small] = '\0';

    return soundex;
}
