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


import demo
import sys
import tkinter as tk
from tkinter import colorchooser
from tkinter import messagebox

class Application(tk.Frame):
    def __init__(self, client, master=None):
        super().__init__(master)
        self.client = client
        self.master = master
        self.pack()

        counterFrame = tk.Frame(self)
        counterFrame.grid(column=0)
        tk.Label(counterFrame, text="Request id").grid(row=0, column=0)
        self.idOut = tk.Label(counterFrame, text="0", width=15)
        self.idOut.grid(row=0, column=1)
        tk.Label(counterFrame, text="Sum").grid(row=1, column=0)
        self.sumOut = tk.Label(counterFrame, text="0", width=15)
        self.sumOut.grid(row=1, column=1)
        tk.Label(counterFrame, text="Sum of squares").grid(row=2, column=0)
        self.squaresOut = tk.Label(counterFrame, text="0", width=15)
        self.squaresOut.grid(row=2, column=1)
        self.counterId = 0
        self.value = tk.StringVar(value="0")
        valueEntry = tk.Entry(counterFrame, width=10, textvariable=self.value)
        valueEntry.grid(row=3, column=0)
        valueEntry.bind('<Return>', self.sendValue)
        tk.Button(counterFrame, text="Send value", command=self.sendValue).grid(row=3, column=1)
        tk.Button(counterFrame, text="Reset sum", command=self.resetSum).grid(row=4, column=0)
        tk.Button(counterFrame, text="Reset squares", command=self.resetSquareSum).grid(row=4, column=1)
        
        self.pollCounter()

        buttons = tk.Frame(self)
        buttons.grid(row=0, column=1)
        for i in range(4):
            tk.Button(buttons, text="LED " + str(i) + " color", command=lambda i=i: self.setLED(i)).pack()

        self.pollButtons()

    def setLED(self, i):
        rgb, h = colorchooser.askcolor(title="Choose LED" + str(i) + " color")
        if rgb is not None:
            r, g, b = rgb
            self.client.rgb(i, int(r), int(g), int(b))

    def pollCounter(self):
        while (res := self.client.getSum()) is not None:
            self.idOut['text'] = str(res.id)
            self.sumOut['text'] = str(res.val)
        while (res := self.client.getSquareSum()) is not None:
            self.idOut['text'] = res.id
            self.squaresOut['text'] = res.val
        self.after(100, self.pollCounter)

    def sendValue(self, event=None):
        try:
            self.client.sendNum(self.counterId, int(self.value.get()))
        except (ValueError, OverflowError) as e:
            messagebox.showerror("Value error", str(e))
        self.counterId += 1

    def resetSum(self, event=None):
        try:
            self.client.resetSum(self.counterId)
        except (ValueError, OverflowError) as e:
            messagebox.showerror("Value error", str(e))
        self.counterId += 1

    def resetSquareSum(self, event=None):
        try:
            self.client.resetSquareSum(self.counterId)
        except (ValueError, OverflowError) as e:
            messagebox.showerror("Value error", str(e))
        self.counterId += 1

    def pollButtons(self):
        while (event := self.client.getButtonEvent()) is not None:
            messagebox.showinfo("Button pressed", "Button " + str(event) + " pressed!")
        self.after(100, self.pollButtons)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        sys.exit("Expected serial port name")

    client = demo.DemoClient(sys.argv[1])
    root = tk.Tk()
    root.title("FPGA Message Demo")
    app = Application(client, root)
    client.start()
    app.mainloop()

