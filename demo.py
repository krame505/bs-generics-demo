#!/usr/bin/env python3

import serial
import threading
import select
import eventfd
import time
from cobs import cobs
from _demo import ffi, lib

class Client:
    def __init__(self, port):
        self._state = ffi.new("DemoMsgs_state *")
        lib.init_DemoMsgs(self._state)
        self._stateMutex = threading.Lock()
        self._txReady = eventfd.EventFD()
        self._txDone = eventfd.EventFD()
        self._ser = serial.Serial(port, 115200)

    def _run(self):
        rxData = []
        self._stateMutex.acquire()
        while True:
            for byte in self._ser.read(self._ser.in_waiting):
                if byte == 0:
                    #print("Rx", cobs.decode(bytes(rxData)))
                    lib.decode_DemoMsgs(self._state, cobs.decode(bytes(rxData)))
                    rxData.clear()
                else:
                    rxData.append(byte)

            txArray = ffi.new("uint8_t[]", lib.size_tx_DemoMsgs)
            txSize = lib.encode_DemoMsgs(self._state, txArray)
            if txSize:
                while txSize:
                    txData = bytes(txArray)[0:txSize]
                    #print("Tx", txSize, txData)
                    self._ser.write(cobs.encode(txData) + b'\0')
                    self._txDone.set()
                    txSize = lib.encode_DemoMsgs(self._state, txArray)
            else:
                self._stateMutex.release()
                select.select([self._ser, self._txReady], [], [])
                self._stateMutex.acquire()
                self._txReady.clear()

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def putCommand(self, command):
        self._stateMutex.acquire()
        while not lib.enqueue_DemoMsgs_commands(self._state, command):
            self._stateMutex.release()
            self._txDone.wait()
            self._stateMutex.acquire()
            self._txDone.clear()

        self._txReady.set()
        self._stateMutex.release()

    def getSum(self):
        res = ffi.new("Result_int16 *")
        self._stateMutex.acquire()
        hasRes = lib.dequeue_DemoMsgs_sums(self._state, res)
        self._txReady.set()
        self._stateMutex.release()
        if hasRes:
            return res

    def getProduct(self):
        res = ffi.new("Result_int64 *")
        self._stateMutex.acquire()
        hasRes = lib.dequeue_DemoMsgs_products(self._state, res)
        self._txReady.set()
        self._stateMutex.release()
        if hasRes:
            return res

    def sendNum(self, id, val):
        self.putCommand(ffi.new("Command *", {'tag': lib.Command_Num, 'contents': {'Num': {'id': id, 'val': val}}})[0])

    def resetSum(self, val):
        self.putCommand(ffi.new("Command *", {'tag': lib.Command_ResetSum, 'contents': {'ResetSum': val}})[0])

    def resetProduct(self, val):
        self.putCommand(ffi.new("Command *", {'tag': lib.Command_ResetProduct, 'contents': {'ResetProduct': val}})[0])
