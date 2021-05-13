
BSCFLAGS=-p ../bsc-contrib/Libraries/GenCRepr/:../bsc-contrib/Libraries/GenCMsg/:../bsc-contrib/Libraries/UART/:../bsc-contrib/Libraries/COBS/:+

all: rtl ffi

rtl:
	bsc -u $(BSCFLAGS) -verilog Demo.bs

ffi: | rtl
	./build_demo_ffi.py

clean:
	rm -rf *~ *.o *.c *.h *.cxx *.v *.bo *.ba *.so *.out __pycache__/
