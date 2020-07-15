SHELL := /bin/bash

# Set compiler
CC = g++ -std=c++17
FLAGS = -g -O2
LIBS = -I/usr/include/hdf5/serial
LIBS += -Wdate-time
LIBS += -D_FORTIFY_SOURCE=2
LIBS += -fdebug-prefix-map=/build/hdf5-X9JKIg/hdf5-1.10.0-patch1+docs=.
LIBS += -fstack-protector-strong
LIBS += -Wformat
LIBS += -Werror=format-security 
LIBS += -L/usr/lib/x86_64-linux-gnu/hdf5/serial /usr/lib/x86_64-linux-gnu/hdf5/serial/libhdf5_hl_cpp.a 
LIBS += /usr/lib/x86_64-linux-gnu/hdf5/serial/libhdf5_cpp.a 
LIBS += /usr/lib/x86_64-linux-gnu/hdf5/serial/libhdf5_hl.a 
LIBS += /usr/lib/x86_64-linux-gnu/hdf5/serial/libhdf5.a 
LIBS += -Wl,-Bsymbolic-functions 
LIBS += -Wl,-z,relro 
LIBS += -lpthread 
LIBS += -lsz -lz -ldl -lm -Wl,-rpath 
LIBS += -Wl,/usr/lib/x86_64-linux-gnu/hdf5/serial
LIBS += -llapack -lblas -larmadillo


MAINPROG = testh5read.out

all: $(MAINPROG)

${MAINPROG}:	testh5read.cpp 
	${CC} testh5read.cpp ${LIBS} ${FLAGS} -o ${MAINPROG}

run_mapedit:
	./testh5read.out
   