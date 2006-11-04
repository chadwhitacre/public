#include <stdio.h>

/* Exercise 1-8: "Write a program to count blanks, tabs, and newlines." */

main()
{
    int c;
    int blanks, tabs, newlines;

    blanks = 0;
    tabs = 0;
    newlines = 0;

    while((c = getchar()) != EOF) {
        if (c == ' ')
            ++blanks;
        if (c == '\t')
            ++tabs;
        if (c == '\n')
            ++newlines;
    }
    printf("  blanks: %2d\n", blanks);
    printf("    tabs: %2d\n", tabs);
    printf("newlines: %2d\n", newlines);
}

    /* Mistakes:

        1. didn't include newlines in printf
        2. didn't declare variables
        3. didn't initialize variables, with wacko results:

            whit537@josemaria$ gcc exercise.1-8.c && ./a.out
              ^D
              blanks: 18
                tabs: 672297437
            newlines: -1077941623
            whit537@josemaria$

    */
