TARGETS?=cepces
MODULES?=${TARGETS:=.pp}

all: ${TARGETS:=.pp}

%.pp: %.te %.fc %.if
	make -f /usr/share/selinux/devel/Makefile $@

clean:
	rm -f *~ *.tc *.pp
	rm -rf tmp
