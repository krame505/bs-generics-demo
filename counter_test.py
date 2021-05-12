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
import time
import threading
from demo import Client

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        sys.exit("Expected serial port name")

    client = Client(sys.argv[1])
    client.start()

    def handler():
        expectedSums = {i for i in range(500)}
        expectedSquareSums = {i for i in range(500)}
        while expectedSums or expectedSquareSums:
            if res := client.getSum():
                expectedSums -= {res.id}
                print("Sum", res.id, res.val)
            elif res := client.getSquareSum():
                expectedSquareSums -= {res.id}
                print("Squares", res.id, res.val)
            else:
                if expectedSums:
                   print("Waiting on sums", expectedSums)
                if expectedSquareSums:
                   print("Waiting on squares", expectedSquareSums)
            time.sleep(0.005)

    handlerThread = threading.Thread(target=handler)
    handlerThread.start()

    k = 0
    for i in range(5):
        print("Reset", i)
        client.resetSum(i)
        client.resetSquareSum(i)
        for j in range(1, 101):
            print("Send", k, j)
            client.sendNum(k, j)
            k += 1

    handlerThread.join()
