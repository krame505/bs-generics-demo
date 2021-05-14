
BSCFLAGS=-p ../bsc-contrib/Libraries/GenCRepr/:../bsc-contrib/Libraries/GenCMsg/:../bsc-contrib/Libraries/UART/:../bsc-contrib/Libraries/COBS/:+

all: rtl sim ffi

rtl:
	bsc $(BSCFLAGS) -u -verilog Demo.bs

sim:
	bsc $(BSCFLAGS) -u -sim DemoSim.bs
	bsc $(BSCFLAGS) -sim -e sysDemoSim -o sysDemoSim.out

ffi: | rtl
	./build_demo_ffi.py

clean:
	rm -rf *~ *.o *.c *.h *.cxx *.v *.bo *.ba *.so *.out __pycache__/

.PHONY: all rtl sim ffi clean
