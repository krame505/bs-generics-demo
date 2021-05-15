#!/usr/bin/env python3

import sys
import tkinter as tk
from tkinter import colorchooser
from tkinter import messagebox
import msgclient
import serial
from _demo_sim import ffi, lib

class DemoSimClient(msgclient.Client):
    def __init__(self, port):
        super().__init__("DemoSimMsgs", ffi, lib, serial.Serial(port, 115200))

    def getRGBCommand(self):
        return self.get("rgbCommands")

    def putButtonEvent(self, i):
        self.put("buttonEvents", i)

class Application(tk.Frame):
    def __init__(self, client, master=None):
        super().__init__(master)
        self.client = client
        self.master = master
        self.pack()

        self.leds = []
        for i in range(4):
            led = tk.Label(self, text="LED " + str(i), fg='white', bg='black')
            led.grid(row=0, column=i)
            self.leds.append(led)
        
        for i in range(4):
            tk.Button(self, text="Button " + str(i), command=lambda i=i: self.client.putButtonEvent(i)).grid(row=1, column=i)

        self.pollLEDs()

    def pollLEDs(self):
        while (command := self.client.getRGBCommand()) is not None:
            self.leds[command.addr].config(bg="#{:02x}{:02x}{:02x}".format(command.state.red, command.state.green, command.state.blue))
        self.after(100, self.pollLEDs)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        sys.exit("Expected serial port name")

    client = DemoSimClient(sys.argv[1])
    root = tk.Tk()
    root.title("Message Demo Simulated FPGA")
    app = Application(client, root)
    client.start()
    app.mainloop()

