
#include "header.h"

extern int stem(struct SN_env * z);
static int r_Step_5b(struct SN_env * z);
static int r_Step_5a(struct SN_env * z);
static int r_Step_4(struct SN_env * z);
static int r_Step_3(struct SN_env * z);
static int r_Step_2(struct SN_env * z);
static int r_Step_1c(struct SN_env * z);
static int r_Step_1b(struct SN_env * z);
static int r_Step_1a(struct SN_env * z);
static int r_R2(struct SN_env * z);
static int r_R1(struct SN_env * z);
static int r_shortv(struct SN_env * z);

static struct among a_0[4] =
{
/*  0 */ { 1, (byte *)"s", -1, 3},
/*  1 */ { 3, (byte *)"ies", 0, 2},
/*  2 */ { 4, (byte *)"sses", 0, 1},
/*  3 */ { 2, (byte *)"ss", 0, -1}
};

static struct among a_1[13] =
{
/*  0 */ { 0, (byte *)"", -1, 3},
/*  1 */ { 2, (byte *)"bb", 0, 2},
/*  2 */ { 2, (byte *)"dd", 0, 2},
/*  3 */ { 2, (byte *)"ff", 0, 2},
/*  4 */ { 2, (byte *)"gg", 0, 2},
/*  5 */ { 2, (byte *)"bl", 0, 1},
/*  6 */ { 2, (byte *)"mm", 0, 2},
/*  7 */ { 2, (byte *)"nn", 0, 2},
/*  8 */ { 2, (byte *)"pp", 0, 2},
/*  9 */ { 2, (byte *)"rr", 0, 2},
/* 10 */ { 2, (byte *)"at", 0, 1},
/* 11 */ { 2, (byte *)"tt", 0, 2},
/* 12 */ { 2, (byte *)"iz", 0, 1}
};

static struct among a_2[3] =
{
/*  0 */ { 2, (byte *)"ed", -1, 2},
/*  1 */ { 3, (byte *)"eed", 0, 1},
/*  2 */ { 3, (byte *)"ing", -1, 2}
};

static struct among a_3[20] =
{
/*  0 */ { 4, (byte *)"anci", -1, 3},
/*  1 */ { 4, (byte *)"enci", -1, 2},
/*  2 */ { 4, (byte *)"abli", -1, 4},
/*  3 */ { 3, (byte *)"eli", -1, 6},
/*  4 */ { 4, (byte *)"alli", -1, 9},
/*  5 */ { 5, (byte *)"ousli", -1, 12},
/*  6 */ { 5, (byte *)"entli", -1, 5},
/*  7 */ { 5, (byte *)"aliti", -1, 10},
/*  8 */ { 6, (byte *)"biliti", -1, 14},
/*  9 */ { 5, (byte *)"iviti", -1, 13},
/* 10 */ { 6, (byte *)"tional", -1, 1},
/* 11 */ { 7, (byte *)"ational", 10, 8},
/* 12 */ { 5, (byte *)"alism", -1, 10},
/* 13 */ { 5, (byte *)"ation", -1, 8},
/* 14 */ { 7, (byte *)"ization", 13, 7},
/* 15 */ { 4, (byte *)"izer", -1, 7},
/* 16 */ { 4, (byte *)"ator", -1, 8},
/* 17 */ { 7, (byte *)"iveness", -1, 13},
/* 18 */ { 7, (byte *)"fulness", -1, 11},
/* 19 */ { 7, (byte *)"ousness", -1, 12}
};

static struct among a_4[7] =
{
/*  0 */ { 5, (byte *)"icate", -1, 2},
/*  1 */ { 5, (byte *)"ative", -1, 3},
/*  2 */ { 5, (byte *)"alize", -1, 1},
/*  3 */ { 5, (byte *)"iciti", -1, 2},
/*  4 */ { 4, (byte *)"ical", -1, 2},
/*  5 */ { 3, (byte *)"ful", -1, 3},
/*  6 */ { 4, (byte *)"ness", -1, 3}
};

static struct among a_5[19] =
{
/*  0 */ { 2, (byte *)"ic", -1, 1},
/*  1 */ { 4, (byte *)"ance", -1, 1},
/*  2 */ { 4, (byte *)"ence", -1, 1},
/*  3 */ { 4, (byte *)"able", -1, 1},
/*  4 */ { 4, (byte *)"ible", -1, 1},
/*  5 */ { 3, (byte *)"ate", -1, 1},
/*  6 */ { 3, (byte *)"ive", -1, 1},
/*  7 */ { 3, (byte *)"ize", -1, 1},
/*  8 */ { 3, (byte *)"iti", -1, 1},
/*  9 */ { 2, (byte *)"al", -1, 1},
/* 10 */ { 3, (byte *)"ism", -1, 1},
/* 11 */ { 3, (byte *)"ion", -1, 2},
/* 12 */ { 2, (byte *)"er", -1, 1},
/* 13 */ { 3, (byte *)"ous", -1, 1},
/* 14 */ { 3, (byte *)"ant", -1, 1},
/* 15 */ { 3, (byte *)"ent", -1, 1},
/* 16 */ { 4, (byte *)"ment", 15, 1},
/* 17 */ { 5, (byte *)"ement", 16, 1},
/* 18 */ { 2, (byte *)"ou", -1, 1}
};


static byte g_v[] = { 17, 65, 16, 1 };

static byte g_v_WXY[] = { 1, 17, 65, 208, 1 };

static int r_shortv(struct SN_env * z) {
    if (!(out_grouping_b(z, g_v_WXY, 89, 121))) return 0;
    if (!(in_grouping_b(z, g_v, 97, 121))) return 0;
    if (!(out_grouping_b(z, g_v, 97, 121))) return 0;
    return 1;
}

static int r_R1(struct SN_env * z) {
    if (!(z->I[0] <= z->c)) return 0;
    return 1;
}

static int r_R2(struct SN_env * z) {
    if (!(z->I[1] <= z->c)) return 0;
    return 1;
}

static int r_Step_1a(struct SN_env * z) {
    z->ket = z->c; /* [, line 25 */
    z->a = find_among_b(z, a_0, 4); /* substring, line 25 */
    z->bra = z->c; /* ], line 25 */
    switch(z->a) {
        case 0: return 0;
        case 1:
            slice_from_s(z, 2, "ss"); /* <-, line 26 */
            break;
        case 2:
            slice_from_s(z, 1, "i"); /* <-, line 27 */
            break;
        case 3:
            slice_del(z); /* delete, line 29 */
            break;
    }
    return 1;
}

static int r_Step_1b(struct SN_env * z) {
    z->ket = z->c; /* [, line 34 */
    z->a = find_among_b(z, a_2, 3); /* substring, line 34 */
    z->bra = z->c; /* ], line 34 */
    switch(z->a) {
        case 0: return 0;
        case 1:
            if (!r_R1(z)) return 0; /* call R1, line 35 */
            slice_from_s(z, 2, "ee"); /* <-, line 35 */
            break;
        case 2:
            {   int m_test = z->l - z->c; /* test, line 38 */
                while(1) { /* gopast, line 38 */
                    if (!(in_grouping_b(z, g_v, 97, 121))) goto lab0;
                    break;
                lab0:
                    if (z->c <= z->lb) return 0;
                    z->c--;
                }
                z->c = z->l - m_test;
            }
            slice_del(z); /* delete, line 38 */
            {   int m_test = z->l - z->c; /* test, line 39 */
                z->a = find_among_b(z, a_1, 13); /* substring, line 39 */
                z->c = z->l - m_test;
            }
            switch(z->a) {
                case 0: return 0;
                case 1:
                    {   int c = z->c;
                        insert_s(z, z->c, z->c, 1, "e"); /* <+, line 41 */
                        z->c = c;
                    }
                    break;
                case 2:
                    z->ket = z->c; /* [, line 44 */
                    if (z->c <= z->lb) return 0;
                    z->c--; /* next, line 44 */
                    z->bra = z->c; /* ], line 44 */
                    slice_del(z); /* delete, line 44 */
                    break;
                case 3:
                    if (z->c != z->I[0]) return 0; /* atmark, line 45 */
                    {   int m_test = z->l - z->c; /* test, line 45 */
                        if (!r_shortv(z)) return 0; /* call shortv, line 45 */
                        z->c = z->l - m_test;
                    }
                    {   int c = z->c;
                        insert_s(z, z->c, z->c, 1, "e"); /* <+, line 45 */
                        z->c = c;
                    }
                    break;
            }
            break;
    }
    return 1;
}

static int r_Step_1c(struct SN_env * z) {
    z->ket = z->c; /* [, line 52 */
    {   int m = z->l - z->c; /* or, line 52 */
        if (!(eq_s_b(z, 1, "y"))) goto lab1;
        goto lab0;
    lab1:
        z->c = z->l - m;
        if (!(eq_s_b(z, 1, "Y"))) return 0;
    }
lab0:
    z->bra = z->c; /* ], line 52 */
    while(1) { /* gopast, line 53 */
        if (!(in_grouping_b(z, g_v, 97, 121))) goto lab2;
        break;
    lab2:
        if (z->c <= z->lb) return 0;
        z->c--;
    }
    slice_from_s(z, 1, "i"); /* <-, line 54 */
    return 1;
}

static int r_Step_2(struct SN_env * z) {
    z->ket = z->c; /* [, line 58 */
    z->a = find_among_b(z, a_3, 20); /* substring, line 58 */
    z->bra = z->c; /* ], line 58 */
    if (!r_R1(z)) return 0; /* call R1, line 58 */
    switch(z->a) {
        case 0: return 0;
        case 1:
            slice_from_s(z, 4, "tion"); /* <-, line 59 */
            break;
        case 2:
            slice_from_s(z, 4, "ence"); /* <-, line 60 */
            break;
        case 3:
            slice_from_s(z, 4, "ance"); /* <-, line 61 */
            break;
        case 4:
            slice_from_s(z, 4, "able"); /* <-, line 62 */
            break;
        case 5:
            slice_from_s(z, 3, "ent"); /* <-, line 63 */
            break;
        case 6:
            slice_from_s(z, 1, "e"); /* <-, line 64 */
            break;
        case 7:
            slice_from_s(z, 3, "ize"); /* <-, line 66 */
            break;
        case 8:
            slice_from_s(z, 3, "ate"); /* <-, line 68 */
            break;
        case 9:
            slice_from_s(z, 2, "al"); /* <-, line 69 */
            break;
        case 10:
            slice_from_s(z, 2, "al"); /* <-, line 71 */
            break;
        case 11:
            slice_from_s(z, 3, "ful"); /* <-, line 72 */
            break;
        case 12:
            slice_from_s(z, 3, "ous"); /* <-, line 74 */
            break;
        case 13:
            slice_from_s(z, 3, "ive"); /* <-, line 76 */
            break;
        case 14:
            slice_from_s(z, 3, "ble"); /* <-, line 77 */
            break;
    }
    return 1;
}

static int r_Step_3(struct SN_env * z) {
    z->ket = z->c; /* [, line 82 */
    z->a = find_among_b(z, a_4, 7); /* substring, line 82 */
    z->bra = z->c; /* ], line 82 */
    if (!r_R1(z)) return 0; /* call R1, line 82 */
    switch(z->a) {
        case 0: return 0;
        case 1:
            slice_from_s(z, 2, "al"); /* <-, line 83 */
            break;
        case 2:
            slice_from_s(z, 2, "ic"); /* <-, line 85 */
            break;
        case 3:
            slice_del(z); /* delete, line 87 */
            break;
    }
    return 1;
}

static int r_Step_4(struct SN_env * z) {
    z->ket = z->c; /* [, line 92 */
    z->a = find_among_b(z, a_5, 19); /* substring, line 92 */
    z->bra = z->c; /* ], line 92 */
    if (!r_R2(z)) return 0; /* call R2, line 92 */
    switch(z->a) {
        case 0: return 0;
        case 1:
            slice_del(z); /* delete, line 95 */
            break;
        case 2:
            {   int m = z->l - z->c; /* or, line 96 */
                if (!(eq_s_b(z, 1, "s"))) goto lab1;
                goto lab0;
            lab1:
                z->c = z->l - m;
                if (!(eq_s_b(z, 1, "t"))) return 0;
            }
        lab0:
            slice_del(z); /* delete, line 96 */
            break;
    }
    return 1;
}

static int r_Step_5a(struct SN_env * z) {
    z->ket = z->c; /* [, line 101 */
    if (!(eq_s_b(z, 1, "e"))) return 0;
    z->bra = z->c; /* ], line 101 */
    {   int m = z->l - z->c; /* or, line 102 */
        if (!r_R2(z)) goto lab1; /* call R2, line 102 */
        goto lab0;
    lab1:
        z->c = z->l - m;
        if (!r_R1(z)) return 0; /* call R1, line 102 */
        {   int m = z->l - z->c; /* not, line 102 */
            if (!r_shortv(z)) goto lab2; /* call shortv, line 102 */
            return 0;
        lab2:
            z->c = z->l - m;
        }
    }
lab0:
    slice_del(z); /* delete, line 103 */
    return 1;
}

static int r_Step_5b(struct SN_env * z) {
    z->ket = z->c; /* [, line 107 */
    if (!(eq_s_b(z, 1, "l"))) return 0;
    z->bra = z->c; /* ], line 107 */
    if (!r_R2(z)) return 0; /* call R2, line 108 */
    if (!(eq_s_b(z, 1, "l"))) return 0;
    slice_del(z); /* delete, line 109 */
    return 1;
}

extern int stem(struct SN_env * z) {
    z->B[0] = 0; /* unset Y_found, line 115 */
    {   int c = z->c; /* do, line 116 */
        z->bra = z->c; /* [, line 116 */
        if (!(eq_s(z, 1, "y"))) goto lab0;
        z->ket = z->c; /* ], line 116 */
        slice_from_s(z, 1, "Y"); /* <-, line 116 */
        z->B[0] = 1; /* set Y_found, line 116 */
    lab0:
        z->c = c;
    }
    {   int c = z->c; /* do, line 117 */
        while(1) { /* repeat, line 117 */
            int c = z->c;
            while(1) { /* goto, line 117 */
                int c = z->c;
                if (!(in_grouping(z, g_v, 97, 121))) goto lab3;
                z->bra = z->c; /* [, line 117 */
                if (!(eq_s(z, 1, "y"))) goto lab3;
                z->ket = z->c; /* ], line 117 */
                z->c = c;
                break;
            lab3:
                z->c = c;
                if (z->c >= z->l) goto lab2;
                z->c++;
            }
            slice_from_s(z, 1, "Y"); /* <-, line 117 */
            z->B[0] = 1; /* set Y_found, line 117 */
            continue;
        lab2:
            z->c = c;
            break;
        }
    lab1:
        z->c = c;
    }
    z->I[0] = z->l;
    z->I[1] = z->l;
    {   int c = z->c; /* do, line 121 */
        while(1) { /* gopast, line 122 */
            if (!(in_grouping(z, g_v, 97, 121))) goto lab5;
            break;
        lab5:
            if (z->c >= z->l) goto lab4;
            z->c++;
        }
        while(1) { /* gopast, line 122 */
            if (!(out_grouping(z, g_v, 97, 121))) goto lab6;
            break;
        lab6:
            if (z->c >= z->l) goto lab4;
            z->c++;
        }
        z->I[0] = z->c; /* setmark p1, line 122 */
        while(1) { /* gopast, line 123 */
            if (!(in_grouping(z, g_v, 97, 121))) goto lab7;
            break;
        lab7:
            if (z->c >= z->l) goto lab4;
            z->c++;
        }
        while(1) { /* gopast, line 123 */
            if (!(out_grouping(z, g_v, 97, 121))) goto lab8;
            break;
        lab8:
            if (z->c >= z->l) goto lab4;
            z->c++;
        }
        z->I[1] = z->c; /* setmark p2, line 123 */
    lab4:
        z->c = c;
    }
    z->lb = z->c; z->c = z->l; /* backwards, line 126 */

    {   int m = z->l - z->c; /* do, line 127 */
        if (!r_Step_1a(z)) goto lab9; /* call Step_1a, line 127 */
    lab9:
        z->c = z->l - m;
    }
    {   int m = z->l - z->c; /* do, line 128 */
        if (!r_Step_1b(z)) goto lab10; /* call Step_1b, line 128 */
    lab10:
        z->c = z->l - m;
    }
    {   int m = z->l - z->c; /* do, line 129 */
        if (!r_Step_1c(z)) goto lab11; /* call Step_1c, line 129 */
    lab11:
        z->c = z->l - m;
    }
    {   int m = z->l - z->c; /* do, line 130 */
        if (!r_Step_2(z)) goto lab12; /* call Step_2, line 130 */
    lab12:
        z->c = z->l - m;
    }
    {   int m = z->l - z->c; /* do, line 131 */
        if (!r_Step_3(z)) goto lab13; /* call Step_3, line 131 */
    lab13:
        z->c = z->l - m;
    }
    {   int m = z->l - z->c; /* do, line 132 */
        if (!r_Step_4(z)) goto lab14; /* call Step_4, line 132 */
    lab14:
        z->c = z->l - m;
    }
    {   int m = z->l - z->c; /* do, line 133 */
        if (!r_Step_5a(z)) goto lab15; /* call Step_5a, line 133 */
    lab15:
        z->c = z->l - m;
    }
    {   int m = z->l - z->c; /* do, line 134 */
        if (!r_Step_5b(z)) goto lab16; /* call Step_5b, line 134 */
    lab16:
        z->c = z->l - m;
    }
    z->c = z->lb;    {   int c = z->c; /* do, line 137 */
        if (!(z->B[0])) goto lab17; /* Boolean test Y_found, line 137 */
        while(1) { /* repeat, line 137 */
            int c = z->c;
            while(1) { /* goto, line 137 */
                int c = z->c;
                z->bra = z->c; /* [, line 137 */
                if (!(eq_s(z, 1, "Y"))) goto lab19;
                z->ket = z->c; /* ], line 137 */
                z->c = c;
                break;
            lab19:
                z->c = c;
                if (z->c >= z->l) goto lab18;
                z->c++;
            }
            slice_from_s(z, 1, "y"); /* <-, line 137 */
            continue;
        lab18:
            z->c = c;
            break;
        }
    lab17:
        z->c = c;
    }
    return 1;
}

extern struct SN_env * create_env(void) { return SN_create_env(0, 2, 1); }

extern void close_env(struct SN_env * z) { SN_close_env(z); }

