# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 09:58:26 2019

@author: simoba
"""

import tkinter as tk
import tkinter.filedialog as filedialog
import os

import pyedna

PAD_X = 5
PAD_Y = 5
SUFFIX = '.sn'
TITLE = "PyEdna"


class MainWindow(object):
    def __init__(self):      
        self.init_values()
        self.init_ui_elements()
        self.chkst_button()
        self.root.mainloop()
        
    def init_values(self):
        # Working folder: start in the user folder. This should be OS agnostic
        self.folder = os.environ["USERPROFILE"] or os.path.join(os.environ['HOMEDRIVE'], os.environ['HOMEPATH'])
        self.have_data1 = False
        self.have_data2 = False
        self.calc = pyedna.EdnaCalc(self)
        self.selected_data = None
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
        self.lower_1 = tk.Frame(self.lower, padx=PAD_X)
        self.lower_2 = tk.Frame(self.lower, padx=PAD_X)

        # Go through each defined frame in turn, and insert the actual UI elements (widgets)
        # First, the three upper frame
        # Two more complicated elements are defined in separate classes
        self.main_title = tk.Label(self.upper_1, text="Stress-Life Test", font="-size 18")
        self.main_title.grid(row=0, column=0, sticky="n")
        self.upper_tree = pyedna.TTKTree(self, self.upper_1) # define more complicated element in a separate class
        self.b_directory = tk.Button(self.upper_1, text="Find Directory", command=self.button_load_directory)
        self.b_directory.grid(row=3,column=0,sticky="nsew")
        
        self.upper_files_title = tk.Label(self.upper_2, text="Data files")
        self.upper_files_title.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.b_merge = tk.Button(self.upper_2, text="Merge", command=self.button_merge, state="disabled")
        self.b_merge.grid(row=1,column=0,columnspan=2, sticky="nsew")
        self.b_load1 = tk.Button(self.upper_2, text="Set 1", command=self.button_load1, state="disabled")
        self.b_load1.grid(row=2, column=0, sticky="nsew")
        self.b_load2 = tk.Button(self.upper_2, text="Set 2", command=self.button_load2, state="disabled")
        self.b_load2.grid(row=2, column=1, sticky="nsew")
        self.upper_files = tk.Listbox(self.upper_2, selectmode="single")
        self.upper_files.grid(row=3, column=0, columnspan=2, sticky="nsew")  
        self.upper_2.grid_rowconfigure(3, weight=1) # allow this element to grow heightwise
        self.upper_2.grid_columnconfigure(0, weight=1)
        self.upper_2.grid_columnconfigure(1, weight=1)
        
        self.upper_results = pyedna.OutputBox(self, self.upper_3)
        
        # Now that the widgets are in the 3 upper frames, arrrange the 3 upper frames within the "outer" upper frame
        self.upper_1.grid(row=0, column=0, sticky="nsew")
        self.upper_2.grid(row=0, column=1, sticky="nsew")        
        self.upper_3.grid(row=0, column=2, sticky="nsew")

        # Now insert widgets into the lower "inner" frames
        self.lower_data1 = pyedna.InputDisplay(self, self.lower_1, "Data 1", 0)
        self.lower_data2 = pyedna.InputDisplay(self, self.lower_2, "Data 2", 1)
        
        # Arrange the two lower inner frames into the outer lower frame
        self.lower_1.grid(row=0, column=0, sticky="nsew")
        self.lower_2.grid(row=0, column=1, sticky="nsew")
        
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
        
    ###########################################################################
    #####################           Button-called functions
    ###########################################################################

    def button_load_directory(self, **kwargs):
        # This should open a directory search box, and both expand the tree to 
        # that location and load that directory same as choosing a directory in
        # the tree
        # TODO: expanding tree to desired location
        self.folder = filedialog.askdirectory()
        self.load_directory()
        self.upper_tree.go_to_selected_folder(self.folder)
        self.chkst_button()
        pass
    
    def button_merge(self, **kwargs):
        pass
    
    def button_load1(self, **kwargs):
        self.read_test_file(self.lower_data1, 0)
        self.have_data1 = True
        self.chkst_button()
        pass
    
    def button_load2(self, **kwargs):
        self.read_test_file(self.lower_data2, 1)
        self.have_data2 = True
        self.chkst_button()
        pass
    
    ###########################################################################
    #####################           Helper functions
    ###########################################################################
    
    def load_directory(self, **kwargs):
        self.upper_files.delete(0,"end") # Remove previous contents
        items = os.listdir(self.folder)
        test_files = [f for f in items if "."+f.split(".")[-1] in SUFFIX]
        for f in test_files:
            self.upper_files.insert("end", f)
        pass

    
    def chkst_button(self):
        '''Control the state of UI buttons based on what actions are available for them to take
        * Available at all times:
            * Find Directory
        * Available when a directory is selected:
            * Load Set 1
            * Load set 2
        * Available when 1 or 2 sets have been loaded:
            * Analyse
            * Report
            * Graph
        * Available when both sets have been loaded:
            * Merge
            * Compare
        '''
        # Directory has been found: self.folder is not none
        condition = self.folder is not None
        self.set_button_state(self.b_load1, condition)
        self.set_button_state(self.b_load2, condition)
        
        # 1 or more data sets have been loaded and 1 has been selected
        condition = (self.have_data1 or self.have_data2) and (self.selected_data is not None)
        self.set_button_state(self.upper_results.b_analysis, condition)
        self.set_button_state(self.upper_results.b_report, condition)
        self.set_button_state(self.upper_results.b_graph, condition)
        
        # Both data sets have been loaded
        condition = self.have_data1 and self.have_data2
        self.set_button_state(self.upper_results.b_compare, condition)
        self.set_button_state(self.b_merge, condition)
        pass
    
    def set_button_state(self, button, state):
        '''brief wrapper function to allow calling buttons by True/False instead of strings'''
        if state:
            button['state'] = 'normal'
        else:
            button['state'] = 'disabled'
        pass
   

    def read_test_file(self, destination, data_id):
        '''Based on a selected entry in self.upper_files, load and insert into the requested data box'''
        # TODO - this should have some kind of validation of the file, in addition to just reading out the pure text
        # construct the full filepath
        index = self.upper_files.curselection()[0]
        file_name = self.upper_files.get(index)
        full_file_name = os.path.join(self.folder, file_name)
        
        # Read the data file into the calculator: this extracts the actual data as numbers
        self.calc.read_data_file(full_file_name, data_id)
        
        # Read the data file into the GUI - note this is ONLY for display, 
        # the text in the GUI is never used for calculations        
        destination.data.delete(0,"end") # Remove previous contents
        
        # Store the full file path as a copiable string for the user
        destination.path.config(state="normal")
        destination.path.delete('1.0','end') # wierdly, Text widgets first index is '1.0', not 0
        destination.path.insert("end", full_file_name)
        destination.path.config(state="disabled")
        with open(full_file_name, "r") as f:
            for line in f.readlines():
                line = line.strip()
                destination.data.insert("end", line)
        pass
        
        

        


