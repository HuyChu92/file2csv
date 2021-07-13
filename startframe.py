import tkinter as tk
from tkinter import (PhotoImage, Label, Menu, IntVar, Checkbutton,
                     Listbox, Scrollbar, RIGHT, END, Y, messagebox,
                     filedialog, ttk, StringVar)
from tkinter import *
from tkinter.ttk import *
import pandas as pd
import numpy
import os


class Start(tk.Frame):
    """ Startframe
    """

    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        self.width = 1000
        self.height = 1000
        canvas = tk.Canvas(self, height=self.height, width=self.width)
        canvas.pack()
        self.frame1 = tk.LabelFrame(self, text="Excel Data")
        self.frame1.place(height=500, width=1000)

        self.file_frame = tk.LabelFrame(self, text="Open bestand")
        self.file_frame.place(height=100, width=400, rely=0.5, relx=0)

        self.path = None

        button1 = tk.Button(self.file_frame, text="Kies bestand", command=lambda: self.Bestand_dialog())
        button1.place(rely=0.65, relx=0.5)

        button2 = tk.Button(self.file_frame, text="Laad bestand", command=lambda: self.Laad_excel_data())
        button2.place(rely=0.65, relx=0.3)

        self.tool_frame = tk.LabelFrame(self, text="Selecteer wat u wilt doen")
        self.tool_frame.place(height=400, width=500, rely=0.5, relx=0.5)

        button_knn = tk.Button(self.tool_frame, text="Classification",
                               command=lambda: messagebox.showerror("Waarschuwing", "Open eerst een bestand!") if len(
                                   self.master.path) == None
                               else self.master.change(Classification))
        button_knn.place(rely=0.1, relx=0.1)

        button_regression = tk.Button(self.tool_frame, text="Regression",
                                      command=lambda: messagebox.showerror("Waarschuwing",
                                                                           "Open eerst een bestand!") if len(
                                          self.master.path) == None
                                      else self.master.change(Regression))
        button_regression.place(rely=0.2, relx=0.1)

        button_tree = tk.Button(self.tool_frame, text="Classification Trees",
                                command=lambda: messagebox.showwarning('Waarschuwing',
                                                                       'Deze functie is nog niet beschikbaar'))
        button_tree.place(rely=0.3, relx=0.1)

        self.label_file = ttk.Label(self.file_frame, text="Geen bestand geselecteerd")
        self.label_file.place(rely=0, relx=0)

        self.tv1 = ttk.Treeview(self.frame1)
        self.tv1.place(relheight=1, relwidth=1)

        self.treescrolly = tk.Scrollbar(self.frame1, orient='vertical', command=self.tv1.yview)
        self.treescrollx = tk.Scrollbar(self.frame1, orient='horizontal', command=self.tv1.xview)
        self.tv1.configure(xscrollcommand=self.treescrollx.set, yscrollcommand=self.treescrolly.set)
        self.treescrollx.pack(side="bottom", fill="x")
        self.treescrolly.pack(side="right", fill="y")

        self.variable = StringVar(self.file_frame)

    def Bestand_dialog(self):
        """ Opent een venster waarbij de gebruiker een bestand kan selecteren
        """
        filename = filedialog.askopenfilename(initialdir="/",
                                              title="Selecteer een bestand",
                                              filetype=(
                                              ("xlsx files", "*xlsx"), ("csv files", "*csv"), ("All files", "*.*")))
        self.master.file = filename
        name, extension = os.path.splitext(filename)
        if extension == '.xlsx':
            self.master.path = pd.read_excel(filename)
            workbook = xl.open_workbook(filename)
            # print(workbook)
            # print(workbook.sheet_names())

            w = OptionMenu(self.file_frame, self.variable, *workbook.sheet_names())
            w.place(rely=0.65, relx=0)
            self.sheet = self.variable.get()
        else:
            self.master.path = pd.read_csv(filename)
        self.label_file["text"] = filename
        # print(self.master.path)

    def Laad_excel_data(self):
        """ Laad het geselecteerde bestand en weergeeft de columns en records
        """
        file_path = self.label_file["text"]
        name, extension = os.path.splitext(file_path)
        try:
            excel_filename = r"{}".format(file_path)
            if extension == '.xlsx':
                df = pd.read_excel(excel_filename, self.variable.get())
            else:
                df = pd.read_csv(excel_filename)
            self.path = df
            # print(excel_filename)
            # print(self.variable.get())
            # print(self.master.file)
            self.master.path = df
            # print(self.master.path)
        except ValueError:
            tk.messagebox.showerror("Informatie", "Het geselecteerde bestand is ongeldig")
            return None
        except FileNotFoundError:
            tk.messagebox.showerror("Informatie", f"Bestand {file_path} bestaat niet")
            return None

        self.verwijder_data()
        self.tv1["column"] = list(df.columns)
        self.tv1["show"] = "headings"
        for column in self.tv1["columns"]:
            self.tv1.heading(column, text=column)

        df_rows = df.to_numpy().tolist()
        for row in df_rows:
            self.tv1.insert("", "end", values=row)
        return None

    def verwijder_data(self):
        """ Verwijdert de huidige weergave van columns en records
        """
        self.tv1.delete(*self.tv1.get_children())