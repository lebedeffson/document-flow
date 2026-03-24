static void debug(struct env * z, int n)
{   int i;
    printf("%d <", n);
    for (i = z->chead + HL; i < LOF(z->p, z->chead); i++) printf("%c",z->p[i]);
    printf(">\n");
}

