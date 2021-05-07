#!/usr/bin/env python3

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
