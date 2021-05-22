# Demo of Bluespec Generic Messaging Library

This project is a demonstration of how to use a composable, cross-language
messaging library (written using Bluespec generics) to connect a simple
host application to an FPGA.

This code was written as part of a 2020 Google internship.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for details.

## License

Apache 2.0; see [`LICENSE`](LICENSE) for details.

## Disclaimer

This project is not an official Google project. It is not supported by
Google and Google specifically disclaims all warranties as to its quality,
merchantability, or fitness for a particular purpose.

## Setup instructions
1. Install [bsc](https://github.com/b-lang-org/bsc)
2. Clone the [bsc-contrib](https://github.com/b-lang-org/bsc-contrib) repository in the same top-level directory as this one
```
$ git clone https://github.com/b-lang-org/bsc-contrib
```
3. Install required python libraries
```
$ python3 -m pip install pyserial cffi eventfd cobs
```
On some systems you may need to manually install tkinter as well
```
$ sudo apt install python3-tk
```
4. Build everything by running `make`.  This will
   * Compile the Bluespec source files and libraries
   * Generate Verilog for the top-level `mkTop` module specified in `Demo.bs`
   * Generate demo message library C source and header files `demo.c` and `demo.h`
   * Build a Python FFI wrapper module `_demo` for the C message library
   * Generate a Bluesim simulator for the top-level `sysDemoSim` module specified in `DemoSim.bs`
   * Generate C source and header files for an additional message library used by the simulator interface, `demo_sim.c` and `demo_sim.h`
   * Build a corresponding Python FFI wrapper module `_demo_sim`


## Running the simulator
1. Run `./sysDemoSim.out` to start the simulator; this will print the name of the simulated serial device and launch a graphical interface with mock LEDs and buttons.
```
$ ./sysDemoSim.out
Initialized simulated serial device at /dev/pts/44
```
2. Launch the host application with the specified device
```
./app.py /dev/pts/44
```
3. Try
  * Enter numbers in the host application to change the counter values
  * Select colors in the host application to change the LED colors in the simulator interface
  * Click the buttons in the simulator interface to trigger a popup in the host application
4. When finished, closing the host application should also cause the simulator to exit.
5. Alternatively, the `counter_test.py`, `rgb_test.py` and `button_test.py` scripts can be run to exercise each feature of the design.


## Running on an FPGA
The design can also be run in hardware on an Arty A7 FPGA board.
1. Install [Vivado and the Digilent board files](https://reference.digilentinc.com/vivado/installing-vivado/start).  Note that there are multiple versions available; ensure that the installed version supports Xilinx FPGAs.
2. Open the `bs-generics-demo.xpr` project file in Vivado
3. Generate a bitstream file and program the device.  A serial device corresponding to the FPGA board should appear, e.g. `/dev/ttyUSB1`
4. Run any of the host application scripts using the serial device
```
./app.py /dev/ttyUSB1
```

