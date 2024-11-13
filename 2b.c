#include <stdio.h>
#include <conio.h>

char s[100], p[50], r[50], a[100];
int j, i, k, c, m, flag = 0;

// Function to read strings for main, pattern, and replace strings
void readString(char *str) {
    int index = 0;
    char ch;
    while ((ch = getchar()) != '\n' && ch != EOF && index < 99) {
        str[index++] = ch;
    }
    str[index] = '\0';  // Null-terminate the string
}

// Function to find the pattern in the main string
int findPattern() {
    i = m = c = j = 0;
    while (s[c] != '\0') {
        if (s[m] == p[i]) {
            i++; m++;
            if (p[i] == '\0') {
                flag = 1;
                return 1;  // Pattern found
            }
        } else {
            c++;
            m = c;
            i = 0;
        }
    }
    return 0;  // Pattern not found
}

// Function to replace pattern occurrences in the main string
void replacePattern() {
    i = m = c = j = 0;
    while (s[c] != '\0') {
        if (s[m] == p[i]) {
            i++; m++;
            if (p[i] == '\0') {
                for (k = 0; r[k] != '\0'; k++, j++) {
                    a[j] = r[k];
                }
                i = 0;
                c = m;
            }
        } else {
            a[j++] = s[c++];
            m = c;
            i = 0;
        }
    }
    a[j] = '\0';  // Null-terminate the resultant string
}

int main() {
    printf("\nEnter the main string:\n");
    readString(s);

    printf("\nEnter the pattern string:\n");
    readString(p);

    printf("\nEnter the replace string:\n");
    readString(r);

    if (findPattern()) {
        replacePattern();
        printf("\nThe resultant string is:\n%s\n", a);
    } else {
        printf("\nPattern string is not found\n");
    }

    return 0;
}
