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
from demo import Client

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        sys.exit("Expected serial port name")

    client = Client(sys.argv[1])
    client.start()

    while True:
        if (event := client.getButtonEvent()) is not None:
            print("Button", event, "pressed")
        else:
            time.sleep(0.01)
