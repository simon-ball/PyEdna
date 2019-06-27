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
        self.data.bind("<<ListboxSelect>>", self.select)
        self.data.grid(row=2, sticky="nesw")
    
        
        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid(row=0, column=0, sticky="nsew")
    
    
    def select(self, event, **kwargs):
        # Indicate to PyEdna that this listbox is selected
        self.parent.selected_data = self.id
        self.parent.chkst_button()