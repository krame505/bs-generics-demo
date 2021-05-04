#!/usr/bin/env python3

from cffi import FFI

ffibuilder = FFI()
ffibuilder.cdef("\n".join(line for line in open("counter.h") if not line.startswith('#')))
ffibuilder.set_source("_counter", '#include "counter.h"', sources=["counter.c"])

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
