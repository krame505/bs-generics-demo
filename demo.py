#!/usr/bin/env python3

# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
sys.path.append("../bsc-contrib/Libraries/GenC/GenCMsg")

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
