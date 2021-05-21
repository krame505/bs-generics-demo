BSCCONTRIB ?=../bsc-contrib
BSCFLAGS=-p $(BSCCONTRIB)/inst/lib/Libraries/GenC/GenCRepr:$(BSCCONTRIB)/inst/lib/Libraries/GenC/GenCMsg:$(BSCCONTRIB)/inst/lib/Libraries/FPGA/Misc:$(BSCCONTRIB)/inst/lib/Libraries/COBS:+

all: rtl sim ffi

contrib:
	make -C $(BSCCONTRIB)/Libraries/GenC install

rtl: | contrib
	bsc $(BSCFLAGS) -u -verilog Demo.bs

ffi: | rtl
	python3 $(BSCCONTRIB)/Libraries/GenC/build_ffi.py "demo"

sim: | contrib
	bsc $(BSCFLAGS) -u -sim DemoSim.bs
	bsc $(BSCFLAGS) -sim -e sysDemoSim -o sysDemoSim.out pty.c
	python3 $(BSCCONTRIB)/Libraries/GenC/build_ffi.py "demo_sim"

clean:
	rm -rf *~ *.o *demo.c *demo_sim.c *.h *.cxx *.v *.bo *.ba *.so *.out __pycache__/

.PHONY: all contrib rtl sim ffi clean
