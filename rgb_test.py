#!/usr/bin/env python3

import sys
import time
from demo import Client

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        sys.exit("Expected serial port name")

    client = Client(sys.argv[1])
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
