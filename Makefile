
all:
	bsc -u -verilog -p +:../bsc-contrib/Libraries/GenCRepr/ Demo.bs
	./build_demo_ffi.py

clean:
	rm -rf *~ *.o *.c *.h *.cxx *.v *.bo *.ba *.so *.out __pycache__/
