#include <stdio.h>

/* Exercise 1-13: Write a program to print a histogram of the lengths of words
   in its input. It is easy to draw the histogram with the bars horizontal; a
   vertical orientation is more challenging. */

/* At this point we haven't learned how to dynamically resize an array, and we
   haven't learned how to buffer input, so that we could loop through it twice.
   Therefore, I'm going to make an assumption that no word in the input will be
   longer than 45 characters (per Wikipedia). */


#define MAX_WORD_LENGTH     45      /* maximum word length we will support */

main()
{
    int i, j;                     /* counters */
    int c;                        /* current character in input */
    int length;                   /* length of the current word */
    int lengths[MAX_WORD_LENGTH]; /* one for each possible histogram bar */
    int overlong_words;           /* number of words that were too long */

    for (i = 0; i < MAX_WORD_LENGTH; ++i)
        lengths[i] = 0;
    overlong_words = 0;

    while((c = getchar()) != EOF)
        if (c == ' ' || c == '\t' || c == '\n')
            while ((c = getchar()) && c == ' ' || c == '\t' || c == '\n')
                ;
        else {
            length = 1;
            while ((c = getchar()) && c != ' ' && c != '\t' && c != '\n')
                ++length;
            if (length < MAX_WORD_LENGTH)
                ++lengths[length];
            else
                ++overlong_words;

        }

    printf("Histogram by Word Lengths\n");
    printf("=========================\n");
    for (i = 0; i < MAX_WORD_LENGTH; ++i) {
        if (lengths[i] != 0) {
            printf("%2d ", i);
            for (j = 0; j < lengths[i]; ++j)
                putchar('#');
            putchar('\n');
        }
    }
}
