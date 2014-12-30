#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

char CODE_BOOK[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890";
int CODE_BOOK_LENGTH;

int randomlySelect(int len){
	double randomValue;
	do{
		randomValue = (double)rand() / RAND_MAX;
	}while(randomValue == 1.0);
	return (int)(randomValue * len);
}

void generate(char *str, int len){
	for(int i = 0; i < len; i ++){
		str[i] = CODE_BOOK[randomlySelect(CODE_BOOK_LENGTH)];
	}
	str[len] = 0;
}

int main(){
	srand(time(NULL));
	CODE_BOOK_LENGTH = strlen(CODE_BOOK);
	char code[100];
	generate(code, 10);
	puts(code);
	return 0;
}
