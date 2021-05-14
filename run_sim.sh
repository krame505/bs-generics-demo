#!/bin/bash

socat -d -d PTY,raw,link=ttySimClient,mode=666 PTY,raw,link=ttySim,mode=666 &

./sysDemoSim.out
