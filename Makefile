all:
	gcc -c -Wall -fpic wave.c
	gcc -shared -o libwave.so wave.o
