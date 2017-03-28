all: test1 test2
test1: checksum.o rdt.o test.o test1.o
	gcc -g checksum.o rdt.o test.o test1.o -o test1
test2: checksum.o rdt.o test.o test2.o
	gcc -g checksum.o rdt.o test.o test2.o -o test2
checksum.o: packet.h checksum.h checksum.cpp
	gcc -g -c checksum.cpp
rdt.o: packet.h rdt.h checksum.h rdt.cpp
	gcc -g -c rdt.cpp
test.o: test.h test.cpp
	gcc -g -c test.cpp
test1.o: test.h rdt.h test1.cpp
	gcc -g -c test1.cpp
test2.o: test.h rdt.h test2.cpp
	gcc -g -c test2.cpp
clean:
	rm checksum.o rdt.o test.o test1.o test2.o
