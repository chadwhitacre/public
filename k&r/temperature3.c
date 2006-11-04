#include <stdio.h>

/* Excercise 1.4 */

/* print Celsius-Fahrenheit table
    for celsius = 0, 20, ..., 300; floating-point version */
main()
{
    float celsius, fahr;
    int lower, upper, step;

    lower = -20;      /* lower limit of temperature table */
    upper = 150;    /* upper limit */
    step = 10;      /* step size */

    celsius = lower;

    printf("celsius fahr\n");
    while (celsius <= upper) {
        fahr = ((9.0 * celsius) / 5.0) + 32;
        printf("%6.1f %4.0f\n", celsius, fahr);
        celsius = celsius + step;
    }
}
