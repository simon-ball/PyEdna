# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 09:58:26 2019

@author: simoba
"""

import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk
import psutil
import os
import sys

from pyedna import OutputBox, TTKTree

PAD_X = 5
PAD_Y = 5
SUFFIX = '.sn'
TITLE = "PyEdna"


class Gui(object):
    def __init__(self):      
        self.init_values()
        self.init_ui_elements()
        self.root.mainloop()
        
    def init_values(self):
        # Working folder: start in the user folder. This should be OS agnostic
        self.folder = os.environ["USERPROFILE"] or os.path.join(os.environ['HOMEDRIVE'], os.environ['HOMEPATH'])
        pass
    
    def init_ui_elements(self):
        self.root = tk.Tk()
        self.root.title(TITLE)
        # Layout based on guide at 
        # https://stackoverflow.com/questions/36506152/tkinter-grid-or-pack-inside-a-grid
        # Define the main areas of the UI here as frames
        # Actual UI elements will be inserted into those frames in the next sections
        self.upper = tk.Frame(self.root, height=150)
        self.upper_1 = tk.Frame(self.upper, padx=PAD_X)
        self.upper_2 = tk.Frame(self.upper, padx=PAD_X)
        self.upper_3 = tk.Frame(self.upper, padx=PAD_X)
        self.lower = tk.Frame(self.root, height=150, pady=PAD_Y)
        self.lower_data1 = tk.Frame(self.lower, padx=PAD_X)
        self.lower_data2 = tk.Frame(self.lower, padx=PAD_X)
        
        # Go through each defined frame in turn, and insert the actual UI elements (widgets)
        # First, the three upper frame
        # Two more complicated elements are defined in separate classes
        self.main_title = tk.Label(self.upper_1, text="Stress-Life Test", font="-size 18")
        self.main_title.grid(row=0, column=0, sticky="n")
        self.upper_tree = TTKTree(self.upper_1) # define more complicated element in a separate class
        self.b_directory = tk.Button(self.upper_1, text="Find Directory", command=self.button_load_directory)
        self.b_directory.grid(row=3,column=0,sticky="nsew")
        
        self.upper_files_title = tk.Label(self.upper_2, text="Data files")
        self.upper_files_title.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.b_merge = tk.Button(self.upper_2, text="Merge", command=self.button_merge)
        self.b_merge.grid(row=1,column=0,columnspan=2, sticky="nsew")
        self.b_load1 = tk.Button(self.upper_2, text="Set 1", command=self.button_load1)
        self.b_load1.grid(row=2, column=0, sticky="nsew")
        self.b_load2 = tk.Button(self.upper_2, text="Set 2", command=self.button_load2)
        self.b_load2.grid(row=2, column=1, sticky="nsew")
        self.upper_files = tk.Listbox(self.upper_2, selectmode="single")
        self.upper_files.grid(row=3, column=0, columnspan=2, sticky="nsew")  
        self.upper_2.grid_rowconfigure(3, weight=1) # allow this element to grow heightwise
        self.upper_2.grid_columnconfigure(0, weight=1)
        self.upper_2.grid_columnconfigure(1, weight=1)
        
        self.upper_results = OutputBox(self.upper_3)
        
        # Now that the widgets are in the 3 upper frames, arrrange the 3 upper frames within the "outer" upper frame
        self.upper_1.grid(row=0, column=0, sticky="nsew")
        self.upper_2.grid(row=0, column=1, sticky="nsew")        
        self.upper_3.grid(row=0, column=2, sticky="nsew")
        
        # Now insert widgets into the lower "inner" frames
        self.lower_data1_title = tk.Label(self.lower_data1, text="Data 1")
        self.lower_data1_title.grid(row=0, sticky="nesw")
        self.lower_data1_data = tk.Listbox(self.lower_data1)
        self.lower_data1_data.grid(row=1, sticky="nesw")
        self.lower_data1.grid_rowconfigure(1, weight=1)
        self.lower_data1.grid_columnconfigure(0, weight=1)
        self.lower_data2_title = tk.Label(self.lower_data2, text="Data 2")
        self.lower_data2_title.grid(row=0, sticky="nesw")
        self.lower_data2_data = tk.Listbox(self.lower_data2)
        self.lower_data2_data.grid(row=1, sticky="nesw")
        self.lower_data2.grid_rowconfigure(1, weight=1) # this causes the listbox to grow heightwise
        self.lower_data2.grid_columnconfigure(0, weight=1) # this causes the listbox to grow widthwise
        
        # Arrange the two lower inner frames into the outer lower frame
        self.lower_data1.grid(row=0, column=0, sticky="nsew")
        self.lower_data2.grid(row=0, column=1, sticky="nsew")
        
        
        #Define how the outer frames  are aligned into the root frame
        self.upper.grid(row=0, column=0, rowspan=1, sticky="nsew")
        self.upper.grid_rowconfigure(0, weight=1)
        self.upper.grid_columnconfigure(0, weight=1)
        self.upper.grid_columnconfigure(1, weight=1)
        self.upper.grid_columnconfigure(2, weight=1)
        self.lower.grid(row=1, column=0, rowspan=1, sticky="nsew")
        self.lower.grid_rowconfigure(0, weight=1)
        self.lower.grid_columnconfigure(0, weight=1)
        self.lower.grid_columnconfigure(1, weight=1)
        
        # Ensure that the root frame grid weights correctly
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Prevent the window from being shrunk such that widgets become covered
        self.root.update()
        self.root.minsize(self.root.winfo_width(), self.root.winfo_height())
        pass
        
    def button_load_directory(self, **kwargs):
        # This should open a directory search box, and both expand the tree to that location
        # and load that directory same as choosing a directory in the tree
        self.folder = filedialog.askdirectory()
        self.upper_files.delete(0,"end") # Remove previous contents
        items = os.listdir(self.folder)
        test_files = [f for f in items if "."+f.split(".")[-1] in SUFFIX]
        for f in test_files:
            self.upper_files.insert("end", f)
        pass
    
    def button_merge(self, **kwargs):
        print("Merge")
        pass
    
    def button_load1(self, **kwargs):
        self.read_test_file(self.lower_data1_data)
        pass
    
    def button_load2(self, **kwargs):
        self.read_test_file(self.lower_data2_data)
        pass

    def read_test_file(self, destination):
        '''Based on a selected entry in self.upper_files, load and insert into the requested data box'''
        destination.delete(0,"end") # Remove previous contents
        index = self.upper_files.curselection()[0]
        file_name = self.upper_files.get(index)
        full_file_name = os.path.join(self.folder, file_name)
        with open(full_file_name, "r") as f:
            for line in f.readlines():
                line = line.strip()
                destination.insert("end", line)
        pass
        
        
        

        
        


    

        
                                                    
if __name__ == '__main__':
    
    g = Gui()
    g.folder = r"C:\Users\simoba\Documents\_work\NTNUIT\2019-03-29 - Edna\Round 2\Files from Frode\Test Data"
    g.load_directory()
        


