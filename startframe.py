from re import I
import tkinter as tk
from tkinter import (PhotoImage, Label, Menu, IntVar, Checkbutton,
                     Listbox, Scrollbar, RIGHT, END, Y, messagebox,
                     filedialog,ttk,StringVar)
from tkinter import *
from tkinter.ttk import *
import pandas as pd
import numpy as np
from pandas.core.indexes.base import Index
from pandas.core.window.rolling import Window 
import xlrd as xl
import openpyxl as ox
import os
import tabula
from datetime import datetime
from tabula import read_pdf
from tabulate import tabulate
import matplotlib.pyplot as plt
    
class Start(tk.Frame):
    """ Startframe
    """

    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        self.width = 1000
        self.height = 900
        canvas = tk.Canvas(self, height=self.height, width=self.width)
        canvas.pack()
        self.frame1 = tk.LabelFrame(self, text="Excel Data")
        self.frame1.place(height=500, width=1000)

        self.file_frame = tk.LabelFrame(self, text="Open bestand")
        self.file_frame.place(height=100, width=400, rely=0.6, relx=0)

        self.path = None
        self.current_df = None
        self.list_dataframe_undo = []
        self.current_undo_redo_index = 0
        self.deleted_columns = []
        self.added_column = None
        self.added_column_name = ""

        button1 = tk.Button(self.file_frame, text="Kies bestand", command=lambda: self.Bestand_dialog())
        button1.place(rely=0.65, relx=0.5)

        button2 = tk.Button(self.file_frame, text="Laad bestand", command=lambda: self.Laad_excel_data())
        button2.place(rely=0.65, relx=0.3)

        self.tool_frame = tk.LabelFrame(self, text="Kolommen")
        self.tool_frame.place(height=350, width=500, rely=0.6, relx=0.5)\
        
        button_exporteer = tk.Button(self, text="Exporteer bestand",command=lambda: self.save_file())
        button_exporteer.place(rely=0.9,relx=0.05)

        button_exporteer = tk.Button(self, text="Analytics",command=lambda: self.analytics_frame())
        button_exporteer.place(rely=0.85,relx=0.05)
   
        button_optionmenu_df = tk.Button(self, text="OK",command=lambda: self.execute_optionmenu_df(self.optionmenu_var.get()))
        button_optionmenu_df.place(rely=0.56, relx=0.95)

        self.optionmenu_var = StringVar(self.tool_frame)
        self.optionmenu_var.set("Verwijder record") # default value

        optionmenu_df = tk.OptionMenu(self,self.optionmenu_var, "Verwijder record", "Verwijder duplicaten","Verwijder kolommen met NaN waardes")
        optionmenu_df.place(rely=0.56, relx=0.7)

        button_reset_dataframe = tk.Button(self,text="reset",command=lambda: self.reset_dataframe())
        button_reset_dataframe.place(rely=0.56, relx=0.05)

        button_undo = tk.Button(self,text="↺",command=lambda: self.undo())
        button_undo.place(rely=0.56, relx=0.1)

        button_redo = tk.Button(self,text="↻",command=lambda: self.redo())
        button_redo.place(rely=0.56, relx=0.13)

        self.label_file = ttk.Label(self.file_frame, text="Geen bestand geselecteerd")
        self.label_file.place(rely=0, relx=0)

        self.tv1 = ttk.Treeview(self.frame1)
        self.tv1.place(relheight=1, relwidth=1)

        self.treescrolly = tk.Scrollbar(self.frame1, orient='vertical', command=self.tv1.yview)
        self.treescrollx = tk.Scrollbar(self.frame1, orient='horizontal', command=self.tv1.xview)
        self.tv1.configure(xscrollcommand=self.treescrollx.set, yscrollcommand=self.treescrolly.set)
        self.treescrollx.pack(side="bottom", fill="x")
        self.treescrolly.pack(side="right", fill="y")

        self.list_columns = Listbox(self.tool_frame)
        self.list_columns.place(relheight=0.7, relwidth=0.4)
        scrollbar = Scrollbar(self.list_columns)
        scrollbar.pack(side=RIGHT, fill=Y)

        button_remove = tk.Button(self.tool_frame, text="✖",command=lambda: self.remove_column())
        button_remove.place(rely=0.63, relx=0.4)

        button_info_column = tk.Button(self.tool_frame, text="🛈",command=lambda: self.show_column_info())
        button_info_column.place(rely=0.56, relx=0.4)

        self.variable_bewerk_data = StringVar(self.tool_frame)
        self.variable_bewerk_data.set("Verwijder spaties") # default value

        opties = tk.OptionMenu(self.tool_frame, self.variable_bewerk_data, "Verwijder spaties", "Vervang comma door punt",
                                 "Zet kolomtype om in float", "Zet datumstring om naar datumobject",
                                 "Vervang NaN door gemiddelde", "Verwijder record met NaN")
        opties.place(rely=0.7, relx=0)

        button_ok_opties = tk.Button(self.tool_frame,text="OK",command=lambda: self.opties_kolommen(self.variable_bewerk_data.get()))
        button_ok_opties.place(rely=0.9, relx=0)


        self.del_clms = Listbox(self.tool_frame)
        self.del_clms.place(relheight=0.7, relwidth=0.4, rely=0, relx=0.5)
        scrollbar = Scrollbar(self.del_clms)
        scrollbar.pack(side=RIGHT, fill=Y)      

        self.variable = StringVar(self.file_frame)
    
    def undo(self):
        if self.current_undo_redo_index != 0:
            self.current_undo_redo_index -= 1
            self.path = self.list_dataframe_undo[self.current_undo_redo_index]
            self.refresh_columns()
            self.list_columns.delete(0, END)
            self.show_colums(self.list_columns,self.path)
        else:
            return tk.messagebox.showinfo('Info', "Dit is het originele dataframe")

    def redo(self):
        try:
            self.current_undo_redo_index += 1
            self.path = self.list_dataframe_undo[self.current_undo_redo_index]
            self.refresh_columns()
            self.list_columns.delete(0, END)
            self.show_colums(self.list_columns,self.path)
        except IndexError:
            return tk.messagebox.showinfo("Info", "Dit is het laatst bewerkte dataframe")


    def reset_dataframe(self):
        self.path = pd.DataFrame(self.current_df)
        self.refresh_columns()
        self.list_columns.delete(0, END)
        self.show_colums(self.list_columns,self.path)
        self.current_undo_redo_index = 0
        self.list_dataframe_undo = []

    def execute_optionmenu_df(self,keuze):
        if keuze == "Verwijder record":
            self.remove_row()
        elif keuze == "Verwijder duplicaten":
            self.path.drop(['index'],axis=1, inplace=True)
            self.path.drop_duplicates(subset=None, keep="first", inplace=True)
            self.path.reset_index(inplace=True)
            self.path['index'] = self.path.index.tolist()
            self.refresh_columns()
        elif keuze == "Verwijder kolommen met NaN waardes":
            self.path.dropna(axis = 1, how = 'all',inplace=True)
            self.refresh_columns()

        self.list_columns.delete(0, END)
        self.show_colums(self.list_columns,self.path)

        self.current_undo_redo_index += 1
        self.list_dataframe_undo.append(pd.DataFrame(self.path))
            
    def opties_kolommen(self,keuze):
        try:
            if keuze == "Verwijder spaties":
                self.path["{}".format(self.list_columns.get(self.list_columns.curselection()))]=self.path["{}".format(self.list_columns.get(self.list_columns.curselection()))].str.replace(' ','')
            elif keuze ==  "Vervang comma door punt":
                self.path["{}".format(self.list_columns.get(self.list_columns.curselection()))]=self.path["{}".format(self.list_columns.get(self.list_columns.curselection()))].str.replace(',','.')            
            elif keuze ==  "Zet kolomtype om in float":
                self.path["{}".format(self.list_columns.get(self.list_columns.curselection()))] = self.path["{}".format(self.list_columns.get(self.list_columns.curselection()))].astype(float)           
            elif keuze == "Zet datumstring om naar datumobject":
                self.path["{}".format(self.list_columns.get(self.list_columns.curselection()))] = pd.to_datetime(self.path["{}".format(self.list_columns.get(self.list_columns.curselection()))],dayfirst=True)      
            elif keuze == "Vervang NaN door gemiddelde":
                self.path["{}".format(self.list_columns.get(self.list_columns.curselection()))].fillna(self.path["{}".format(self.list_columns.get(self.list_columns.curselection()))].mean(),inplace=True)
            self.refresh_columns()
        except ValueError as error:
            error_string = error
            return tk.messagebox.showwarning("Error","{}".format(error_string))

        self.current_undo_redo_index += 1
        self.list_dataframe_undo.append(pd.DataFrame(self.path))
    
    def show_column_info(self):
        type = self.path["{}".format(self.list_columns.get(self.list_columns.curselection()))].dtypes
        leeg = self.path["{}".format(self.list_columns.get(self.list_columns.curselection()))].isna().sum()
        return tk.messagebox.showinfo("info","Type: {}\n NaN values: {} ".format(type,leeg))
   
    def refresh_columns(self):
        self.verwijder_data()
        self.tv1["column"] = list(self.path.columns)
        self.tv1["show"] = "headings"
        for column in self.tv1["columns"]:
            self.tv1.heading(column, text=column)

        df_rows = self.path.to_numpy().tolist()
        for row in df_rows:
            self.tv1.insert("", "end", values=row)        

    def Bestand_dialog(self):
        """ Opent een venster waarbij de gebruiker een bestand kan selecteren
        """
        filename = filedialog.askopenfilename(initialdir="/",
                                              title="Selecteer een bestand",
                                              filetype=(
                                              ("xlsx files", "*xlsx"), ("csv files", "*csv"),("pdf files","*pdf"), ("All files", "*.*")))
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
        elif extension == '.pdf':
            self.master.path = tabula.read_pdf(r"{}".format(filename), pages="all")
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
            elif extension == '.csv':
                df = pd.read_csv(excel_filename)              
            else:
                df = tabula.read_pdf(r"{}".format(excel_filename), pages="all")
                output = pd.concat(df)
                df = output.dropna(axis=1, how='all')
                df.dropna(axis = 0, how = 'all', inplace = True)
            df.reset_index( inplace=True)
            df['index'] = df.index.tolist()
            self.path = df
            self.current_df = pd.DataFrame(df)
            self.list_dataframe_undo.append(pd.DataFrame(df))
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
        self.show_colums(self.list_columns,self.path)
        return None

    def verwijder_data(self):
        """ Verwijdert de huidige weergave van columns en records
        """
        self.tv1.delete(*self.tv1.get_children())

    def show_colums(self, box, dataframe):
        """ Weergeeft de column
        """
        for clm in dataframe.columns:
            box.insert(END, clm)

    def remove_column(self):
        """ Verwijdert geselecteerd variabel uit self.X
        """
        waarde = self.list_columns.get(self.list_columns.curselection())
        self.path.drop(columns=['{}'.format(waarde)],axis=1, inplace=True)
        # print(self.path.head())
        self.list_columns.delete(0, END)
        self.show_colums(self.list_columns,self.path)

        self.verwijder_data()
        self.tv1["column"] = list(self.path.columns)
        self.tv1["show"] = "headings"
        for column in self.tv1["columns"]:
            self.tv1.heading(column, text=column)

        df_rows = self.path.to_numpy().tolist()
        for row in df_rows:
            self.tv1.insert("", "end", values=row)
        
        self.current_undo_redo_index += 1
        self.list_dataframe_undo.append(pd.DataFrame(self.path))

    def remove_row(self):
        selected = self.tv1.focus()
        row = self.tv1.item(selected)
        test = row.get('values')[0]
        index_names = self.path[ self.path['index'] == test ].index

        self.path.drop(index_names, inplace = True)
        self.path.reset_index(drop=True,inplace=True)
        print(self.path.index.tolist())
        self.path['index'] = self.path.index.tolist()

        self.verwijder_data()
        self.tv1["column"] = list(self.path.columns)
        self.tv1["show"] = "headings"
        for column in self.tv1["columns"]:
            self.tv1.heading(column, text=column)

        df_rows = self.path.to_numpy().tolist()
        for row in df_rows:
            self.tv1.insert("", "end", values=row)
    
    def save_file(self):
        mylist = list(self.path.select_dtypes(include=['datetime64[ns]','timedelta64[ns]']).columns)
        if len(mylist) > 0:
            for item in mylist:
                self.path['{}'.format(item)] = self.path['{}'.format(item)].astype(str)

        savefile = filedialog.asksaveasfilename(filetypes=(("Excel files", "*.xlsx"),
                                                    ("All files", "*.*") ))               
        self.path.to_excel(savefile + ".xlsx", index=False)         
        return tk.messagebox.showinfo("Succes","Bestand opgeslagen.")

    def analytics_frame(self):
        """ Summary venster zien
        """
        try:
            window = Toplevel(self)
            resizable = window.resizable(False,False)
            window.geometry("600x500")

            list_columns = Listbox(window)
            list_columns.place(relheight=0.7, relwidth=0.4)
            scrollbar = Scrollbar(list_columns)
            scrollbar.pack(side=RIGHT, fill=Y)

            variable = StringVar(window)
            variable.set("Gemiddelde") # default value

            opties = tk.OptionMenu(window, variable, "Gemiddelde", "Cummulatief", "Interval")
            opties.pack()
            
            self.show_colums(list_columns,self.path)
            
            buttonOK = tk.Button(window,text="OK",command=lambda: self.bereken(variable.get(),list_columns.get(list_columns.curselection()),list_output))
            buttonOK.pack()

            list_output = Listbox(window)
            list_output.place(relheight=0.7, relwidth=0.4,relx=0.6)
            scrollbar = Scrollbar(list_output)
            scrollbar.pack(side=RIGHT, fill=Y)

            button_add_to_df = tk.Button(window,text="Voeg toe aan dataframe",command=lambda: self.add_to_dataframe())
            button_add_to_df.place(relx=0.6,rely=0.7)

            lijst_columns = []
            for item in list(self.path.columns):
                lijst_columns.append(item)

            variable1 = StringVar(window)
            variable1.set(list(self.path.columns)[1]) # default value

            opties_x_graph = tk.OptionMenu(window, variable1, *lijst_columns)
            opties_x_graph.place(relx=0,rely=0.7)

            variable2 = StringVar(window)
            variable2.set(list(self.path.columns)[2]) # default value

            opties_y_graph = tk.OptionMenu(window, variable2, *lijst_columns)
            opties_y_graph.place(relx=0,rely=0.77)

            constant_warning = tk.Entry(window)
            constant_warning.place(relx=0,rely=0.85)

            button_plot = tk.Button(window,text="Plot graphiek",command=lambda: self.plot_graphiek(variable1.get(),variable2.get(),(constant_warning.get())))
            button_plot.place(relx=0,rely=0.9)
        except AttributeError as error:
            error_string = error
            return tk.messagebox.showwarning("Error","{}".format(error_string))


    def plot_graphiek(self,x,y,c=None):
        y_lijst = []
        # if self.path["{}".format(y)].dtype == 'timedelta64[ns]':
        #     y_lijst.append(0)
        #     for item in self.path["{}".format(x)]:
        #         print(type(item))
        if c == "":
            x_lijst = self.path["{}".format(x)].tolist() 
            y_lijst = self.path["{}".format(y)].tolist() 
            plt.plot(x_lijst, y_lijst)
            plt.show()
        else:
            x_lijst = self.path["{}".format(x)].tolist() 
            y_lijst = self.path["{}".format(y)].tolist() 
            plt.plot(x_lijst, y_lijst)
            plt.axhline(y=float(c), color='r', linestyle='-')
            plt.show()

    def add_to_dataframe(self):
        self.path = pd.concat([self.path, self.added_column],axis=1)
        self.refresh_columns()

    def bereken(self,soort,kolom,listbox):
        try:
            if soort == "Gemiddelde":
                gemiddelde = round(self.path["{}".format(kolom)].mean(),2)  
                return tk.messagebox.showinfo('Gemiddelde',"Gemiddelde van kolom {} is: {}".format(kolom,gemiddelde))
            elif soort == "Cummulatief":
                if self.path['{}'.format(kolom)].dtypes == "datetime64[ns]":
                    cumulatieveTijd = []
                    cumulatieveTijd.append(self.path['{}'.format(kolom)][1]-self.path['{}'.format(kolom)][1])
                    current = self.path['{}'.format(kolom)][0]
                    nieuw = self.path['{}'.format(kolom)][1] - self.path['{}'.format(kolom)][0]
    
                    for t in self.path['{}'.format(kolom)][1:]:
                        verschil = t - current
                        cumulatieveTijd.append(verschil)
                        nieuw += verschil

                    for item in cumulatieveTijd:
                        listbox.insert(END, item)
                    
                    self.added_column = pd.DataFrame(cumulatieveTijd,columns=["{} {}".format(soort,kolom)])
                    
                elif self.path['{}'.format(kolom)].dtypes == "float64" or self.path['{}'.format(kolom)].dtypes == "int64":
                    self.path['{}'.format(kolom)].cumsum()
                    lijst_floats = self.path['{}'.format(kolom)].cumsum().tolist()
                    for item in lijst_floats:
                        listbox.insert(END, item)
                    self.added_column = pd.DataFrame(lijst_floats,columns=["{} {}".format(soort,kolom)])
        except TypeError as error:
            error_string = error
            return tk.messagebox.showwarning("Error","{}".format(error_string))
        except ValueError as error:
            error_string = error
            return tk.messagebox.showwarning("Error","{}".format(error_string))



        
        
            
           
    

        


   

        


        