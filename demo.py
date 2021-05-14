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
        seenStart = False
        rxData = []
        self._stateMutex.acquire()
        while True:
            for byte in self._ser.read(self._ser.in_waiting):
                if not seenStart:
                    print("Discard", bytes([byte]))
                    seenStart = byte == 0
                elif byte == 0:
                    print("Rx raw", bytes(rxData))
                    print("Rx", cobs.decode(bytes(rxData)))
                    lib.decode_DemoMsgs(self._state, cobs.decode(bytes(rxData)))
                    rxData.clear()
                else:
                    rxData.append(byte)

            txArray = ffi.new("uint8_t[]", lib.size_tx_DemoMsgs)
            txSize = lib.encode_DemoMsgs(self._state, txArray)
            if txSize:
                while txSize:
                    txData = bytes(txArray)[0:txSize]
                    print("Tx", txSize, txData)
                    print("Tx raw", cobs.encode(txData) + b'\0')
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

    def putCounterRequest(self, request):
        self._stateMutex.acquire()
        while not lib.enqueue_DemoMsgs_ctrRequests(self._state, request):
            self._stateMutex.release()
            self._txDone.wait()
            self._stateMutex.acquire()
            self._txDone.clear()

        self._txReady.set()
        self._stateMutex.release()

    def getSum(self):
        res = ffi.new("CounterResponse_int32 *")
        self._stateMutex.acquire()
        hasRes = lib.dequeue_DemoMsgs_sums(self._state, res)
        self._txReady.set()
        self._stateMutex.release()
        if hasRes:
            return res

    def getSquareSum(self):
        res = ffi.new("CounterResponse_int64 *")
        self._stateMutex.acquire()
        hasRes = lib.dequeue_DemoMsgs_squareSums(self._state, res)
        self._txReady.set()
        self._stateMutex.release()
        if hasRes:
            return res

    def putRGBCommand(self, command):
        self._stateMutex.acquire()
        while not lib.enqueue_DemoMsgs_rgbCommands(self._state, command):
            self._stateMutex.release()
            self._txDone.wait()
            self._stateMutex.acquire()
            self._txDone.clear()

        self._txReady.set()
        self._stateMutex.release()

    def getButtonEvent(self):
        res = ffi.new("uint8_t *")
        self._stateMutex.acquire()
        hasRes = lib.dequeue_DemoMsgs_buttonEvents(self._state, res)
        self._txReady.set()
        self._stateMutex.release()
        if hasRes:
            return res[0]

    def sendNum(self, id, val):
        self.putCounterRequest(ffi.new("CounterRequest *", {'id': id, 'command': {'tag': lib.CounterCommand_Num, 'contents': {'Num': val}}})[0])

    def resetSum(self, id):
        self.putCounterRequest(ffi.new("CounterRequest *", {'id': id, 'command': {'tag': lib.CounterCommand_ResetSum}})[0])

    def resetSquareSum(self, id):
        self.putCounterRequest(ffi.new("CounterRequest *", {'id': id, 'command': {'tag': lib.CounterCommand_ResetSquareSum}})[0])

    def rgb(self, a, r, g, b):
        self.putRGBCommand(ffi.new("RGBCommand_4 *", {'addr': a, 'state': {'red': r, 'green': g, 'blue': b}})[0])
