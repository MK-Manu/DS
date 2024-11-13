#include <stdio.h> 
#include <stdlib.h> 
#include <string.h> 
typedef struct { 
char *name;        
int date;          
char *description; 
} Day; 
void create(Day *week, int size) { 
for (int i = 0; i < size; i++) { 

week[i].name = (char *)malloc(20 * sizeof(char));  

week[i].description = (char *)malloc(100 * sizeof(char));  
} 
} 
void read(Day *week, int size) { 
for (int i = 0; i < size; i++) { 
        printf("Enter name of day %d: ", i + 1); 
        scanf("%s", week[i].name); 
        printf("Enter date: "); 
        scanf("%d", &week[i].date); 
        printf("Enter description: "); 
        scanf(" %[^\n]", week[i].description); 
    } 
} 
 
void display(Day *week, int size) { 
    printf("\nWeek's Activity Details:\n"); 
    for (int i = 0; i < size; i++) { 
        printf("Day: %s, Date: %d, Activity: %s\n", week[i].name, 
week[i].date, week[i].description); 
    } 
} 
 
int main() { 
    int size = 7; 
    Day *week = (Day *)malloc(size * sizeof(Day)); 
 
    create(week, size); 
    read(week, size);  
    display(week, size); 
 
    for (int i = 0; i < size; i++) { 
        free(week[i].name); 
        free(week[i].description); 
    } 
    free(week); 
    return 0; 
}
