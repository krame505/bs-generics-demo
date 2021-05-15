#!/usr/bin/env python3

import sys
import time
from demo import DemoClient

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        sys.exit("Expected serial port name")

    client = DemoClient(sys.argv[1])
    client.start()

    while True:
        if (event := client.getButtonEvent()) is not None:
            print("Button", event, "pressed")
        else:
            time.sleep(0.01)
