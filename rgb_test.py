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
from demo import DemoClient

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        sys.exit("Expected serial port name")

    client = DemoClient(sys.argv[1])
    client.start()

    for b in range(0, 100, 10):
        for a in range(4):
            for r in range(0, 100, 10):
                for g in range(0, 100, 10):
                    print(a, r, g, b)
                    client.rgb(a, r, g, b)
                    time.sleep(0.001)
    for a in range(4):
        client.rgb(a, 255, 0, 0)
        time.sleep(1)
    for a in range(4):
        client.rgb(a, 0, 255, 0)
        time.sleep(1)
    for a in range(4):
        client.rgb(a, 0, 0, 255)
        time.sleep(1)
    for a in range(4):
        client.rgb(a, 0, 0, 0)
        time.sleep(1)
