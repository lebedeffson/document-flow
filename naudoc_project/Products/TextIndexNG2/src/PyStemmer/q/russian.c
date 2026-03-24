
/* This file was generated automatically by the Snowball to ANSI C compiler */

#include "header.h"

extern int russian_stem(struct SN_env * z);
static int r_tidy_up(struct SN_env * z);
static int r_derivational(struct SN_env * z);
static int r_noun(struct SN_env * z);
static int r_verb(struct SN_env * z);
static int r_reflexive(struct SN_env * z);
static int r_adjectival(struct SN_env * z);
static int r_adjective(struct SN_env * z);
static int r_perfective_gerund(struct SN_env * z);
static int r_R2(struct SN_env * z);
static int r_mark_regions(struct SN_env * z);

static symbol s_0_0[1] = { 1074 };
static symbol s_0_1[2] = { 1080, 1074 };
static symbol s_0_2[2] = { 1099, 1074 };
static symbol s_0_3[3] = { 1074, 1096, 1080 };
static symbol s_0_4[4] = { 1080, 1074, 1096, 1080 };
static symbol s_0_5[4] = { 1099, 1074, 1096, 1080 };
static symbol s_0_6[5] = { 1074, 1096, 1080, 1089, 1100 };
static symbol s_0_7[6] = { 1080, 1074, 1096, 1080, 1089, 1100 };
static symbol s_0_8[6] = { 1099, 1074, 1096, 1080, 1089, 1100 };

static struct among a_0[9] =
{
/*  0 */ { 1, s_0_0, -1, 1, 0},
/*  1 */ { 2, s_0_1, 0, 2, 0},
/*  2 */ { 2, s_0_2, 0, 2, 0},
/*  3 */ { 3, s_0_3, -1, 1, 0},
/*  4 */ { 4, s_0_4, 3, 2, 0},
/*  5 */ { 4, s_0_5, 3, 2, 0},
/*  6 */ { 5, s_0_6, -1, 1, 0},
/*  7 */ { 6, s_0_7, 6, 2, 0},
/*  8 */ { 6, s_0_8, 6, 2, 0}
};

static symbol s_1_0[2] = { 1077, 1077 };
static symbol s_1_1[2] = { 1080, 1077 };
static symbol s_1_2[2] = { 1086, 1077 };
static symbol s_1_3[2] = { 1099, 1077 };
static symbol s_1_4[3] = { 1080, 1084, 1080 };
static symbol s_1_5[3] = { 1099, 1084, 1080 };
static symbol s_1_6[2] = { 1077, 1081 };
static symbol s_1_7[2] = { 1080, 1081 };
static symbol s_1_8[2] = { 1086, 1081 };
static symbol s_1_9[2] = { 1099, 1081 };
static symbol s_1_10[2] = { 1077, 1084 };
static symbol s_1_11[2] = { 1080, 1084 };
static symbol s_1_12[2] = { 1086, 1084 };
static symbol s_1_13[2] = { 1099, 1084 };
static symbol s_1_14[3] = { 1077, 1075, 1086 };
static symbol s_1_15[3] = { 1086, 1075, 1086 };
static symbol s_1_16[3] = { 1077, 1084, 1091 };
static symbol s_1_17[3] = { 1086, 1084, 1091 };
static symbol s_1_18[2] = { 1080, 1093 };
static symbol s_1_19[2] = { 1099, 1093 };
static symbol s_1_20[2] = { 1077, 1102 };
static symbol s_1_21[2] = { 1086, 1102 };
static symbol s_1_22[2] = { 1091, 1102 };
static symbol s_1_23[2] = { 1102, 1102 };
static symbol s_1_24[2] = { 1072, 1103 };
static symbol s_1_25[2] = { 1103, 1103 };

static struct among a_1[26] =
{
/*  0 */ { 2, s_1_0, -1, 1, 0},
/*  1 */ { 2, s_1_1, -1, 1, 0},
/*  2 */ { 2, s_1_2, -1, 1, 0},
/*  3 */ { 2, s_1_3, -1, 1, 0},
/*  4 */ { 3, s_1_4, -1, 1, 0},
/*  5 */ { 3, s_1_5, -1, 1, 0},
/*  6 */ { 2, s_1_6, -1, 1, 0},
/*  7 */ { 2, s_1_7, -1, 1, 0},
/*  8 */ { 2, s_1_8, -1, 1, 0},
/*  9 */ { 2, s_1_9, -1, 1, 0},
/* 10 */ { 2, s_1_10, -1, 1, 0},
/* 11 */ { 2, s_1_11, -1, 1, 0},
/* 12 */ { 2, s_1_12, -1, 1, 0},
/* 13 */ { 2, s_1_13, -1, 1, 0},
/* 14 */ { 3, s_1_14, -1, 1, 0},
/* 15 */ { 3, s_1_15, -1, 1, 0},
/* 16 */ { 3, s_1_16, -1, 1, 0},
/* 17 */ { 3, s_1_17, -1, 1, 0},
/* 18 */ { 2, s_1_18, -1, 1, 0},
/* 19 */ { 2, s_1_19, -1, 1, 0},
/* 20 */ { 2, s_1_20, -1, 1, 0},
/* 21 */ { 2, s_1_21, -1, 1, 0},
/* 22 */ { 2, s_1_22, -1, 1, 0},
/* 23 */ { 2, s_1_23, -1, 1, 0},
/* 24 */ { 2, s_1_24, -1, 1, 0},
/* 25 */ { 2, s_1_25, -1, 1, 0}
};

static symbol s_2_0[2] = { 1077, 1084 };
static symbol s_2_1[2] = { 1085, 1085 };
static symbol s_2_2[2] = { 1074, 1096 };
static symbol s_2_3[3] = { 1080, 1074, 1096 };
static symbol s_2_4[3] = { 1099, 1074, 1096 };
static symbol s_2_5[1] = { 1097 };
static symbol s_2_6[2] = { 1102, 1097 };
static symbol s_2_7[3] = { 1091, 1102, 1097 };

static struct among a_2[8] =
{
/*  0 */ { 2, s_2_0, -1, 1, 0},
/*  1 */ { 2, s_2_1, -1, 1, 0},
/*  2 */ { 2, s_2_2, -1, 1, 0},
/*  3 */ { 3, s_2_3, 2, 2, 0},
/*  4 */ { 3, s_2_4, 2, 2, 0},
/*  5 */ { 1, s_2_5, -1, 1, 0},
/*  6 */ { 2, s_2_6, 5, 1, 0},
/*  7 */ { 3, s_2_7, 6, 2, 0}
};

static symbol s_3_0[2] = { 1089, 1100 };
static symbol s_3_1[2] = { 1089, 1103 };

static struct among a_3[2] =
{
/*  0 */ { 2, s_3_0, -1, 1, 0},
/*  1 */ { 2, s_3_1, -1, 1, 0}
};

static symbol s_4_0[2] = { 1083, 1072 };
static symbol s_4_1[3] = { 1080, 1083, 1072 };
static symbol s_4_2[3] = { 1099, 1083, 1072 };
static symbol s_4_3[2] = { 1085, 1072 };
static symbol s_4_4[3] = { 1077, 1085, 1072 };
static symbol s_4_5[3] = { 1077, 1090, 1077 };
static symbol s_4_6[3] = { 1080, 1090, 1077 };
static symbol s_4_7[3] = { 1081, 1090, 1077 };
static symbol s_4_8[4] = { 1077, 1081, 1090, 1077 };
static symbol s_4_9[4] = { 1091, 1081, 1090, 1077 };
static symbol s_4_10[2] = { 1083, 1080 };
static symbol s_4_11[3] = { 1080, 1083, 1080 };
static symbol s_4_12[3] = { 1099, 1083, 1080 };
static symbol s_4_13[1] = { 1081 };
static symbol s_4_14[2] = { 1077, 1081 };
static symbol s_4_15[2] = { 1091, 1081 };
static symbol s_4_16[1] = { 1083 };
static symbol s_4_17[2] = { 1080, 1083 };
static symbol s_4_18[2] = { 1099, 1083 };
static symbol s_4_19[2] = { 1077, 1084 };
static symbol s_4_20[2] = { 1080, 1084 };
static symbol s_4_21[2] = { 1099, 1084 };
static symbol s_4_22[1] = { 1085 };
static symbol s_4_23[2] = { 1077, 1085 };
static symbol s_4_24[2] = { 1083, 1086 };
static symbol s_4_25[3] = { 1080, 1083, 1086 };
static symbol s_4_26[3] = { 1099, 1083, 1086 };
static symbol s_4_27[2] = { 1085, 1086 };
static symbol s_4_28[3] = { 1077, 1085, 1086 };
static symbol s_4_29[3] = { 1085, 1085, 1086 };
static symbol s_4_30[2] = { 1077, 1090 };
static symbol s_4_31[3] = { 1091, 1077, 1090 };
static symbol s_4_32[2] = { 1080, 1090 };
static symbol s_4_33[2] = { 1099, 1090 };
static symbol s_4_34[2] = { 1102, 1090 };
static symbol s_4_35[3] = { 1091, 1102, 1090 };
static symbol s_4_36[2] = { 1103, 1090 };
static symbol s_4_37[2] = { 1085, 1099 };
static symbol s_4_38[3] = { 1077, 1085, 1099 };
static symbol s_4_39[2] = { 1090, 1100 };
static symbol s_4_40[3] = { 1080, 1090, 1100 };
static symbol s_4_41[3] = { 1099, 1090, 1100 };
static symbol s_4_42[3] = { 1077, 1096, 1100 };
static symbol s_4_43[3] = { 1080, 1096, 1100 };
static symbol s_4_44[1] = { 1102 };
static symbol s_4_45[2] = { 1091, 1102 };

static struct among a_4[46] =
{
/*  0 */ { 2, s_4_0, -1, 1, 0},
/*  1 */ { 3, s_4_1, 0, 2, 0},
/*  2 */ { 3, s_4_2, 0, 2, 0},
/*  3 */ { 2, s_4_3, -1, 1, 0},
/*  4 */ { 3, s_4_4, 3, 2, 0},
/*  5 */ { 3, s_4_5, -1, 1, 0},
/*  6 */ { 3, s_4_6, -1, 2, 0},
/*  7 */ { 3, s_4_7, -1, 1, 0},
/*  8 */ { 4, s_4_8, 7, 2, 0},
/*  9 */ { 4, s_4_9, 7, 2, 0},
/* 10 */ { 2, s_4_10, -1, 1, 0},
/* 11 */ { 3, s_4_11, 10, 2, 0},
/* 12 */ { 3, s_4_12, 10, 2, 0},
/* 13 */ { 1, s_4_13, -1, 1, 0},
/* 14 */ { 2, s_4_14, 13, 2, 0},
/* 15 */ { 2, s_4_15, 13, 2, 0},
/* 16 */ { 1, s_4_16, -1, 1, 0},
/* 17 */ { 2, s_4_17, 16, 2, 0},
/* 18 */ { 2, s_4_18, 16, 2, 0},
/* 19 */ { 2, s_4_19, -1, 1, 0},
/* 20 */ { 2, s_4_20, -1, 2, 0},
/* 21 */ { 2, s_4_21, -1, 2, 0},
/* 22 */ { 1, s_4_22, -1, 1, 0},
/* 23 */ { 2, s_4_23, 22, 2, 0},
/* 24 */ { 2, s_4_24, -1, 1, 0},
/* 25 */ { 3, s_4_25, 24, 2, 0},
/* 26 */ { 3, s_4_26, 24, 2, 0},
/* 27 */ { 2, s_4_27, -1, 1, 0},
/* 28 */ { 3, s_4_28, 27, 2, 0},
/* 29 */ { 3, s_4_29, 27, 1, 0},
/* 30 */ { 2, s_4_30, -1, 1, 0},
/* 31 */ { 3, s_4_31, 30, 2, 0},
/* 32 */ { 2, s_4_32, -1, 2, 0},
/* 33 */ { 2, s_4_33, -1, 2, 0},
/* 34 */ { 2, s_4_34, -1, 1, 0},
/* 35 */ { 3, s_4_35, 34, 2, 0},
/* 36 */ { 2, s_4_36, -1, 2, 0},
/* 37 */ { 2, s_4_37, -1, 1, 0},
/* 38 */ { 3, s_4_38, 37, 2, 0},
/* 39 */ { 2, s_4_39, -1, 1, 0},
/* 40 */ { 3, s_4_40, 39, 2, 0},
/* 41 */ { 3, s_4_41, 39, 2, 0},
/* 42 */ { 3, s_4_42, -1, 1, 0},
/* 43 */ { 3, s_4_43, -1, 2, 0},
/* 44 */ { 1, s_4_44, -1, 2, 0},
/* 45 */ { 2, s_4_45, 44, 2, 0}
};

static symbol s_5_0[1] = { 1072 };
static symbol s_5_1[2] = { 1077, 1074 };
static symbol s_5_2[2] = { 1086, 1074 };
static symbol s_5_3[1] = { 1077 };
static symbol s_5_4[2] = { 1080, 1077 };
static symbol s_5_5[2] = { 1100, 1077 };
static symbol s_5_6[1] = { 1080 };
static symbol s_5_7[2] = { 1077, 1080 };
static symbol s_5_8[2] = { 1080, 1080 };
static symbol s_5_9[3] = { 1072, 1084, 1080 };
static symbol s_5_10[3] = { 1103, 1084, 1080 };
static symbol s_5_11[4] = { 1080, 1103, 1084, 1080 };
static symbol s_5_12[1] = { 1081 };
static symbol s_5_13[2] = { 1077, 1081 };
static symbol s_5_14[3] = { 1080, 1077, 1081 };
static symbol s_5_15[2] = { 1080, 1081 };
static symbol s_5_16[2] = { 1086, 1081 };
static symbol s_5_17[2] = { 1072, 1084 };
static symbol s_5_18[2] = { 1077, 1084 };
static symbol s_5_19[3] = { 1080, 1077, 1084 };
static symbol s_5_20[2] = { 1086, 1084 };
static symbol s_5_21[2] = { 1103, 1084 };
static symbol s_5_22[3] = { 1080, 1103, 1084 };
static symbol s_5_23[1] = { 1086 };
static symbol s_5_24[1] = { 1091 };
static symbol s_5_25[2] = { 1072, 1093 };
static symbol s_5_26[2] = { 1103, 1093 };
static symbol s_5_27[3] = { 1080, 1103, 1093 };
static symbol s_5_28[1] = { 1099 };
static symbol s_5_29[1] = { 1100 };
static symbol s_5_30[1] = { 1102 };
static symbol s_5_31[2] = { 1080, 1102 };
static symbol s_5_32[2] = { 1100, 1102 };
static symbol s_5_33[1] = { 1103 };
static symbol s_5_34[2] = { 1080, 1103 };
static symbol s_5_35[2] = { 1100, 1103 };

static struct among a_5[36] =
{
/*  0 */ { 1, s_5_0, -1, 1, 0},
/*  1 */ { 2, s_5_1, -1, 1, 0},
/*  2 */ { 2, s_5_2, -1, 1, 0},
/*  3 */ { 1, s_5_3, -1, 1, 0},
/*  4 */ { 2, s_5_4, 3, 1, 0},
/*  5 */ { 2, s_5_5, 3, 1, 0},
/*  6 */ { 1, s_5_6, -1, 1, 0},
/*  7 */ { 2, s_5_7, 6, 1, 0},
/*  8 */ { 2, s_5_8, 6, 1, 0},
/*  9 */ { 3, s_5_9, 6, 1, 0},
/* 10 */ { 3, s_5_10, 6, 1, 0},
/* 11 */ { 4, s_5_11, 10, 1, 0},
/* 12 */ { 1, s_5_12, -1, 1, 0},
/* 13 */ { 2, s_5_13, 12, 1, 0},
/* 14 */ { 3, s_5_14, 13, 1, 0},
/* 15 */ { 2, s_5_15, 12, 1, 0},
/* 16 */ { 2, s_5_16, 12, 1, 0},
/* 17 */ { 2, s_5_17, -1, 1, 0},
/* 18 */ { 2, s_5_18, -1, 1, 0},
/* 19 */ { 3, s_5_19, 18, 1, 0},
/* 20 */ { 2, s_5_20, -1, 1, 0},
/* 21 */ { 2, s_5_21, -1, 1, 0},
/* 22 */ { 3, s_5_22, 21, 1, 0},
/* 23 */ { 1, s_5_23, -1, 1, 0},
/* 24 */ { 1, s_5_24, -1, 1, 0},
/* 25 */ { 2, s_5_25, -1, 1, 0},
/* 26 */ { 2, s_5_26, -1, 1, 0},
/* 27 */ { 3, s_5_27, 26, 1, 0},
/* 28 */ { 1, s_5_28, -1, 1, 0},
/* 29 */ { 1, s_5_29, -1, 1, 0},
/* 30 */ { 1, s_5_30, -1, 1, 0},
/* 31 */ { 2, s_5_31, 30, 1, 0},
/* 32 */ { 2, s_5_32, 30, 1, 0},
/* 33 */ { 1, s_5_33, -1, 1, 0},
/* 34 */ { 2, s_5_34, 33, 1, 0},
/* 35 */ { 2, s_5_35, 33, 1, 0}
};

static symbol s_6_0[3] = { 1086, 1089, 1090 };
static symbol s_6_1[4] = { 1086, 1089, 1090, 1100 };

static struct among a_6[2] =
{
/*  0 */ { 3, s_6_0, -1, 1, 0},
/*  1 */ { 4, s_6_1, -1, 1, 0}
};

static symbol s_7_0[4] = { 1077, 1081, 1096, 1077 };
static symbol s_7_1[1] = { 1085 };
static symbol s_7_2[3] = { 1077, 1081, 1096 };
static symbol s_7_3[1] = { 1100 };

static struct among a_7[4] =
{
/*  0 */ { 4, s_7_0, -1, 1, 0},
/*  1 */ { 1, s_7_1, -1, 2, 0},
/*  2 */ { 3, s_7_2, -1, 1, 0},
/*  3 */ { 1, s_7_3, -1, 3, 0}
};

static unsigned char g_v[] = { 33, 65, 8, 232 };

static symbol s_0[] = { 1072 };
static symbol s_1[] = { 1103 };
static symbol s_2[] = { 1072 };
static symbol s_3[] = { 1103 };
static symbol s_4[] = { 1072 };
static symbol s_5[] = { 1103 };
static symbol s_6[] = { 1085 };
static symbol s_7[] = { 1085 };
static symbol s_8[] = { 1085 };
static symbol s_9[] = { 1080 };

static int r_mark_regions(struct SN_env * z) {
    z->I[0] = z->l;
    z->I[1] = z->l;
    {   int c = z->c; /* do, line 65 */
        while(1) { /* gopast, line 66 */
            if (!(in_grouping(z, g_v, 1072, 1103))) goto lab1;
            break;
        lab1:
            if (z->c >= z->l) goto lab0;
            z->c++;
        }
        z->I[0] = z->c; /* setmark pV, line 66 */
        while(1) { /* gopast, line 66 */
            if (!(out_grouping(z, g_v, 1072, 1103))) goto lab2;
            break;
        lab2:
            if (z->c >= z->l) goto lab0;
            z->c++;
        }
        while(1) { /* gopast, line 67 */
            if (!(in_grouping(z, g_v, 1072, 1103))) goto lab3;
            break;
        lab3:
            if (z->c >= z->l) goto lab0;
            z->c++;
        }
        while(1) { /* gopast, line 67 */
            if (!(out_grouping(z, g_v, 1072, 1103))) goto lab4;
            break;
        lab4:
            if (z->c >= z->l) goto lab0;
            z->c++;
        }
        z->I[1] = z->c; /* setmark p2, line 67 */
    lab0:
        z->c = c;
    }
    return 1;
}

static int r_R2(struct SN_env * z) {
    if (!(z->I[1] <= z->c)) return 0;
    return 1;
}

static int r_perfective_gerund(struct SN_env * z) {
    int among_var;
    z->ket = z->c; /* [, line 76 */
    among_var = find_among_b(z, a_0, 9); /* substring, line 76 */
    if (!(among_var)) return 0;
    z->bra = z->c; /* ], line 76 */
    switch(among_var) {
        case 0: return 0;
        case 1:
            {   int m = z->l - z->c; /* or, line 80 */
                if (!(eq_s_b(z, 1, s_0))) goto lab1;
                goto lab0;
            lab1:
                z->c = z->l - m;
                if (!(eq_s_b(z, 1, s_1))) return 0;
            }
        lab0:
            slice_del(z); /* delete, line 80 */
            break;
        case 2:
            slice_del(z); /* delete, line 87 */
            break;
    }
    return 1;
}

static int r_adjective(struct SN_env * z) {
    int among_var;
    z->ket = z->c; /* [, line 92 */
    among_var = find_among_b(z, a_1, 26); /* substring, line 92 */
    if (!(among_var)) return 0;
    z->bra = z->c; /* ], line 92 */
    switch(among_var) {
        case 0: return 0;
        case 1:
            slice_del(z); /* delete, line 101 */
            break;
    }
    return 1;
}

static int r_adjectival(struct SN_env * z) {
    int among_var;
    if (!r_adjective(z)) return 0; /* call adjective, line 106 */
    {   int m = z->l - z->c; /* try, line 113 */
        z->ket = z->c; /* [, line 114 */
        among_var = find_among_b(z, a_2, 8); /* substring, line 114 */
        if (!(among_var)) { z->c = z->l - m; goto lab0; }
        z->bra = z->c; /* ], line 114 */
        switch(among_var) {
            case 0: { z->c = z->l - m; goto lab0; }
            case 1:
                {   int m = z->l - z->c; /* or, line 119 */
                    if (!(eq_s_b(z, 1, s_2))) goto lab2;
                    goto lab1;
                lab2:
                    z->c = z->l - m;
                    if (!(eq_s_b(z, 1, s_3))) { z->c = z->l - m; goto lab0; }
                }
            lab1:
                slice_del(z); /* delete, line 119 */
                break;
            case 2:
                slice_del(z); /* delete, line 126 */
                break;
        }
    lab0:
        ;
    }
    return 1;
}

static int r_reflexive(struct SN_env * z) {
    int among_var;
    z->ket = z->c; /* [, line 133 */
    among_var = find_among_b(z, a_3, 2); /* substring, line 133 */
    if (!(among_var)) return 0;
    z->bra = z->c; /* ], line 133 */
    switch(among_var) {
        case 0: return 0;
        case 1:
            slice_del(z); /* delete, line 136 */
            break;
    }
    return 1;
}

static int r_verb(struct SN_env * z) {
    int among_var;
    z->ket = z->c; /* [, line 141 */
    among_var = find_among_b(z, a_4, 46); /* substring, line 141 */
    if (!(among_var)) return 0;
    z->bra = z->c; /* ], line 141 */
    switch(among_var) {
        case 0: return 0;
        case 1:
            {   int m = z->l - z->c; /* or, line 147 */
                if (!(eq_s_b(z, 1, s_4))) goto lab1;
                goto lab0;
            lab1:
                z->c = z->l - m;
                if (!(eq_s_b(z, 1, s_5))) return 0;
            }
        lab0:
            slice_del(z); /* delete, line 147 */
            break;
        case 2:
            slice_del(z); /* delete, line 155 */
            break;
    }
    return 1;
}

static int r_noun(struct SN_env * z) {
    int among_var;
    z->ket = z->c; /* [, line 164 */
    among_var = find_among_b(z, a_5, 36); /* substring, line 164 */
    if (!(among_var)) return 0;
    z->bra = z->c; /* ], line 164 */
    switch(among_var) {
        case 0: return 0;
        case 1:
            slice_del(z); /* delete, line 171 */
            break;
    }
    return 1;
}

static int r_derivational(struct SN_env * z) {
    int among_var;
    z->ket = z->c; /* [, line 180 */
    among_var = find_among_b(z, a_6, 2); /* substring, line 180 */
    if (!(among_var)) return 0;
    z->bra = z->c; /* ], line 180 */
    if (!r_R2(z)) return 0; /* call R2, line 180 */
    switch(among_var) {
        case 0: return 0;
        case 1:
            slice_del(z); /* delete, line 183 */
            break;
    }
    return 1;
}

static int r_tidy_up(struct SN_env * z) {
    int among_var;
    z->ket = z->c; /* [, line 188 */
    among_var = find_among_b(z, a_7, 4); /* substring, line 188 */
    if (!(among_var)) return 0;
    z->bra = z->c; /* ], line 188 */
    switch(among_var) {
        case 0: return 0;
        case 1:
            slice_del(z); /* delete, line 192 */
            z->ket = z->c; /* [, line 193 */
            if (!(eq_s_b(z, 1, s_6))) return 0;
            z->bra = z->c; /* ], line 193 */
            if (!(eq_s_b(z, 1, s_7))) return 0;
            slice_del(z); /* delete, line 193 */
            break;
        case 2:
            if (!(eq_s_b(z, 1, s_8))) return 0;
            slice_del(z); /* delete, line 196 */
            break;
        case 3:
            slice_del(z); /* delete, line 198 */
            break;
    }
    return 1;
}

extern int russian_stem(struct SN_env * z) {
    {   int c = z->c; /* do, line 205 */
        if (!r_mark_regions(z)) goto lab0; /* call mark_regions, line 205 */
    lab0:
        z->c = c;
    }
    z->lb = z->c; z->c = z->l; /* backwards, line 206 */

    {   int m = z->l - z->c; /* setlimit, line 206 */
        int m3;
        if (z->c < z->I[0]) return 0;
        z->c = z->I[0]; /* tomark, line 206 */
        m3 = z->lb; z->lb = z->c;
        z->c = z->l - m;
        {   int m = z->l - z->c; /* do, line 207 */
            {   int m = z->l - z->c; /* or, line 208 */
                if (!r_perfective_gerund(z)) goto lab3; /* call perfective_gerund, line 208 */
                goto lab2;
            lab3:
                z->c = z->l - m;
                {   int m = z->l - z->c; /* try, line 209 */
                    if (!r_reflexive(z)) { z->c = z->l - m; goto lab4; } /* call reflexive, line 209 */
                lab4:
                    ;
                }
                {   int m = z->l - z->c; /* or, line 210 */
                    if (!r_adjectival(z)) goto lab6; /* call adjectival, line 210 */
                    goto lab5;
                lab6:
                    z->c = z->l - m;
                    if (!r_verb(z)) goto lab7; /* call verb, line 210 */
                    goto lab5;
                lab7:
                    z->c = z->l - m;
                    if (!r_noun(z)) goto lab1; /* call noun, line 210 */
                }
            lab5:
                ;
            }
        lab2:
        lab1:
            z->c = z->l - m;
        }
        {   int m = z->l - z->c; /* try, line 213 */
            z->ket = z->c; /* [, line 213 */
            if (!(eq_s_b(z, 1, s_9))) { z->c = z->l - m; goto lab8; }
            z->bra = z->c; /* ], line 213 */
            slice_del(z); /* delete, line 213 */
        lab8:
            ;
        }
        {   int m = z->l - z->c; /* do, line 216 */
            if (!r_derivational(z)) goto lab9; /* call derivational, line 216 */
        lab9:
            z->c = z->l - m;
        }
        {   int m = z->l - z->c; /* do, line 217 */
            if (!r_tidy_up(z)) goto lab10; /* call tidy_up, line 217 */
        lab10:
            z->c = z->l - m;
        }
        z->lb = m3;
    }
    z->c = z->lb;
    return 1;
}

extern struct SN_env * russian_create_env(void) { return SN_create_env(0, 2, 0); }

extern void russian_close_env(struct SN_env * z) { SN_close_env(z); }

