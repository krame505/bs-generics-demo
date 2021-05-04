#!/usr/bin/env python3

import sys
import serial
import threading
import select
import eventfd
import time
from cobs import cobs
from _counter import ffi, lib

class CounterClient:
    def __init__(self, port):
        self._state = ffi.new("CounterMsgs_state *")
        lib.init_CounterMsgs(self._state)
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
                    lib.decode_CounterMsgs(self._state, cobs.decode(bytes(rxData)))
                    rxData.clear()
                else:
                    rxData.append(byte)

            txArray = ffi.new("uint8_t[]", lib.size_tx_CounterMsgs)
            txSize = lib.encode_CounterMsgs(self._state, txArray)
            if txSize:
                while txSize:
                    txData = bytes(txArray)[0:txSize]
                    #print("Tx", txSize, txData)
                    self._ser.write(cobs.encode(txData) + b'\0')
                    self._txDone.set()
                    txSize = lib.encode_CounterMsgs(self._state, txArray)
            else:
                self._stateMutex.release()
                select.select([self._ser, self._txReady], [], [])
                self._stateMutex.acquire()
                self._txReady.clear()

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def putCommand(self, command):
        self._stateMutex.acquire()
        while not lib.enqueue_CounterMsgs_commands(self._state, command):
            self._stateMutex.release()
            self._txDone.wait()
            self._stateMutex.acquire()
            self._txDone.clear()

        self._txReady.set()
        self._stateMutex.release()

    def getSum(self):
        res = ffi.new("Result_int16 *")
        self._stateMutex.acquire()
        hasRes = lib.dequeue_CounterMsgs_sums(self._state, res)
        self._txReady.set()
        self._stateMutex.release()
        if hasRes:
            return res

    def getProduct(self):
        res = ffi.new("Result_int64 *")
        self._stateMutex.acquire()
        hasRes = lib.dequeue_CounterMsgs_products(self._state, res)
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

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        sys.exit("Expected serial port name")

    client = CounterClient(sys.argv[1])
    client.start()

    def handler():
        expectedSums = {i for i in range(500)}
        expectedProducts = {i for i in range(500)}
        while expectedSums or expectedProducts:
            if res := client.getSum():
                expectedSums -= {res.id}
                print("Sum", res.id, res.val)
            elif res := client.getProduct():
                expectedProducts -= {res.id}
                print("Product", res.id, res.val)
            else:
                if expectedSums:
                   print("Waiting on sums", expectedSums)
                if expectedProducts:
                   print("Waiting on products", expectedProducts)
            time.sleep(0.005)

    handlerThread = threading.Thread(target=handler)
    handlerThread.start()

    k = 0
    for i in range(5):
        print("Reset", i)
        client.resetSum(i)
        client.resetProduct(i)
        for j in range(1, 101):
            print("Send", k, j)
            client.sendNum(k, j)
            k += 1

    handlerThread.join()
