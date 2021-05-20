
BSCFLAGS=-p ../bsc-contrib/Libraries/GenCRepr:../bsc-contrib/Libraries/GenCMsg:../bsc-contrib/Libraries/FPGA/Misc:../bsc-contrib/Libraries/COBS:+

all: rtl sim ffi

rtl:
	bsc $(BSCFLAGS) -u -verilog Demo.bs

ffi: | rtl
	python3 build_ffi.py "demo"

sim:
	bsc $(BSCFLAGS) -u -sim DemoSim.bs
	bsc $(BSCFLAGS) -sim -e sysDemoSim -o sysDemoSim.out pty.c
	python3 build_ffi.py "demo_sim"

clean:
	rm -rf *~ *.o *demo.c *demo_sim.c *.h *.cxx *.v *.bo *.ba *.so *.out __pycache__/

.PHONY: all rtl sim ffi clean
