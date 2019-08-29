'''Raw data display'''

import tkinter as tk

class InputDisplay(object):
    def __init__(self, parent, frame, title_text, d_id):
        self.id = d_id
        self.frame = frame
        self.parent = parent
        self.title = tk.Label(self.frame, text=title_text)
        self.title.grid(row=0, sticky="nesw")
        
        self.path = tk.Text(self.frame, wrap="none", height=1, width=45, state="disabled")
        self.path.grid(row=1, sticky="nsew")
        
        self.data = tk.Listbox(self.frame)
        self.data.bind("<FocusIn>", self.select)
        self.data.grid(row=2, sticky="nesw")
    
        
        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid(row=0, column=0, sticky="nsew")
    
    
    def select(self, event, **kwargs):
        '''Select this data as the primary focus in PyEdna
        ONly do so if some data has already been loaded into this listbox 
        (== data has been loaded into EdnaCalc too)'''
        if self.data.size() != 0:
            self.parent.selected_data = self.id
            self.parent.chkst_button()
            