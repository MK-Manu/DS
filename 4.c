#include <stdio.h> 
#include <stdlib.h> 
#include <string.h> 
#include <ctype.h> 
#define MAX 100 
int precedence(char ch) { 
switch (ch) { 
    case '+': 
    case '-': 
        return 1; 
    case '*': 
    case '/': 
    case '%': 
        return 2; 
    case '^': 
        return 3; 
    } 
    return -1; 
} 
void infixToPostfix(char* infix, char* postfix) { 
    int i, j; 
    char stack[MAX]; 
    int top = -1; 
    for (i = 0, j = 0; infix[i]; ++i) { 
        if (isalnum(infix[i])) 
            postfix[j++] = infix[i]; 
        else if (infix[i] == '(') 
            stack[++top] = infix[i]; 
        else if (infix[i] == ')') { 
            while (top != -1 && stack[top] != '(') 
                postfix[j++] = stack[top--]; 
            if (top != -1) 
                top--; 
        } else { 
            while (top != -1 && precedence(infix[i]) <= precedence(stack[top])) 
                postfix[j++] = stack[top--]; 
            stack[++top] = infix[i]; 
        } 
    } 
    while (top != -1) { 
        postfix[j++] = stack[top--]; 
    } 
    postfix[j] = '\0'; 
} 
int main() { 
    char infix[MAX]; 
    char postfix[MAX]; 
    printf("Enter infix expression: "); 
    gets(infix); 
 
    infixToPostfix(infix, postfix); 
    printf("Postfix expression: %s\n", postfix); 
    return 0; 
} 
