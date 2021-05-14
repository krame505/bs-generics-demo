#!/bin/bash

socat -d -d PTY,link=ttySimClient,mode=666 PTY,link=ttySim,mode=666 &

./sysDemoSim.out
