
all:
	bsc -u -verilog -p ../bsc-contrib/Libraries/GenCRepr/:../bsc-contrib/Libraries/GenCMsg/:../bsc-contrib/Libraries/UART/:../bsc-contrib/Libraries/COBS/:+ Demo.bs
	./build_demo_ffi.py

clean:
	rm -rf *~ *.o *.c *.h *.cxx *.v *.bo *.ba *.so *.out __pycache__/
