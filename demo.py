#!/usr/bin/env python3

import msgclient
import serial
from _demo import ffi, lib

class DemoClient(msgclient.Client):
    def __init__(self, port):
        super().__init__("DemoMsgs", ffi, lib, serial.Serial(port, 115200))

    def putCounterRequest(self, request):
        self.put("ctrRequests", request)

    def getSum(self):
        return self.get("sums")

    def getSquareSum(self):
        return self.get("squareSums")

    def putRGBCommand(self, command):
        self.put("rgbCommands", command)

    def getButtonEvent(self):
        return self.get("buttonEvents")

    def sendNum(self, id, val):
        self.putCounterRequest(ffi.new("CounterRequest *", {'id': id, 'command': {'tag': lib.CounterCommand_Num, 'contents': {'Num': val}}})[0])

    def resetSum(self, id):
        self.putCounterRequest(ffi.new("CounterRequest *", {'id': id, 'command': {'tag': lib.CounterCommand_ResetSum}})[0])

    def resetSquareSum(self, id):
        self.putCounterRequest(ffi.new("CounterRequest *", {'id': id, 'command': {'tag': lib.CounterCommand_ResetSquareSum}})[0])

    def rgb(self, a, r, g, b):
        self.putRGBCommand(ffi.new("RGBCommand_4 *", {'addr': a, 'state': {'red': r, 'green': g, 'blue': b}})[0])
