import tkinter as tk
from tkinter import (PhotoImage, Label, Menu, IntVar, Checkbutton,
                     Listbox, Scrollbar, RIGHT, END, Y, messagebox,
                     filedialog,ttk)
import pandas as pd
import numpy
from tkinter import *
from tkinter.ttk import *
from startframe import Start



class Mainframe(tk.Tk):
    """ Een 'MainFrame' object dat geinstantieerd wordt met tk.TK.
        Dit dient als venster van het programma en vanuit dit venster
        kan er genavigeerd worden """

    def __init__(self):
        tk.Tk.__init__(self)
        self.frame = Start(self) # startframe
        self.frame.pack()
        self.file = None
        self.path = None
        self.resizable(False,False)

    def change(self, frame):
        """ Verandert frame o.b.v. ingevoerde frame """
        self.frame.pack_forget() # delete currrent frame
        self.frame = frame(self)
        self.frame.pack() # make new frame

    def start(self):
        """ Keert terug naar startscherm als er op start gedrukt wordt"""
        self.frame.pack_forget() # delete currrent frame
        self.frame = Start(self)
        self.frame.pack() # make new frame


if __name__ == "__main__":
    app = Mainframe()
    app.mainloop()