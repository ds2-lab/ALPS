# FIX ME
TREE=/linux

BPFTOOL=$(TREE)/tools/bpf/bpftool/bpftool
LIBBPF=$(TREE)/tools/lib/bpf/libbpf.a
INCLUDES := -I$(TREE)/sample/bpf -I/usr/include/python3.8 -I$(TREE)/tools/include/uapi -I$(TREE)/tools/lib/ -I$(TREE)/tools/bpf/bpftool/ -I.
ARCH := $(shell uname -m | sed 's/x86_64/x86/')

all: alps

alps: alps.c alps_skel.h
	gcc -Wall -g  $(INCLUDES) $< -o alps.o $(LIBBPF) -lelf -lz

bpf: alps_bpf.c
	clang -g -O2 -target bpf -D__TARGET_ARCH_$(ARCH) $(INCLUDES) -o alps_bpf.o -c $^
	llvm-strip -g alps_bpf.o

alps_bpf.o: alps_bpf.c
	clang -g -O2 -target bpf -D__TARGET_ARCH_$(ARCH) $(INCLUDES) -o alps_bpf.o -c $^
	llvm-strip -g alps_bpf.o

alps_skel.h: alps_bpf.o
	$(BPFTOOL) gen skeleton $< > alps_skel.h

clean:
	rm -f *.o alps *_skel.h