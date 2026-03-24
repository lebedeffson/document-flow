/*

 TextIndexNG                The next generation TextIndex for Zope

 This software is governed by a license. See
 LICENSE.txt for the terms of this license.

*/


#include <stdlib.h>
#include <string.h>

#define LEVENSHTEIN_MAX_LENTH 255


int levenshtein(const char *s1,  const char *s2)

{

    int *p1, *p2, *tmp;
    int i1, i2, c0, c1, c2;

    int l1,l2, cost_ins, cost_rep, cost_del;

    l1 = strlen(s1);
    l2 = strlen(s2);

    cost_ins  = 1;
    cost_rep  = 1;
    cost_del  = 1;


    if(l1==0)
        return l2*cost_ins;
    if(l2==0)
        return l1*cost_del;

    if((l1>LEVENSHTEIN_MAX_LENTH)||(l2>LEVENSHTEIN_MAX_LENTH))
        return -1;

    if(!(p1=malloc(l2*sizeof(int)))) {
        return -2;
    }
    if(!(p2=malloc(l2*sizeof(int)))) {
        free(p1);
        return -2;
    }

    p1[0]=(s1[0]==s2[0])?0:cost_rep;

    for(i2=1;i2<l2;i2++)
        p1[i2]=i2*cost_ins;

    for(i1=1;i1<l1;i1++) {
        p2[0]=i1*cost_del;
        for(i2=1;i2<l2;i2++) {
            c0=p1[i2-1]+((s1[i1]==s2[i2])?0:cost_rep);
            c1=p1[i2]+cost_del;
            if(c1<c0)
                c0=c1;
            c2=p2[i2-1]+cost_ins;
            if(c2<c0)
                c0=c2;
            p2[i2]=c0;
        }
        tmp=p1;
        p1=p2;
        p2=tmp;
    }

    c0=p1[l2-1];

    free(p1);
    free(p2);

    return c0;
}
/* }}} */
