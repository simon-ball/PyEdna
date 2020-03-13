import tkinter as tk
import pyedna

class OutputBox(object):
    def __init__(self, parent, frame):
        self.frame = frame
        self.parent = parent
        self.b_analysis = tk.Button(self.frame, text="Analyse", command=self.analyse, state="disabled")
        self.b_analysis.grid(row=0, column=0, sticky="nsew")
        self.b_compare = tk.Button(self.frame, text="Compare", command=self.compare, state="disabled")
        self.b_compare.grid(row=1, column=0, sticky="nsew")
        self.b_report = tk.Button(self.frame, text="Report", command=self.report, state="disabled")
        self.b_report.grid(row=0, column=1, sticky="nsew")
        self.b_graph = tk.Button(self.frame, text="Graph", command=self.graph, state="disabled")
        self.b_graph.grid(row=1, column=1, sticky="nsew")
        self.l_slope = tk.Label(self.frame, text="Fix slope")
        self.l_slope.grid(row=2, column=0, sticky="nsew")
        self.t_slope = tk.Text(self.frame, width=10,height=1, wrap="none")
        self.t_slope.bind("<FocusOut>", self.user_slope)
        self.t_slope.grid(row=2, column=1, sticky="nsew")
        self.quick_results = tk.Listbox(self.frame)
        self.quick_results.grid(row=3, column=0, columnspan=2, sticky="nsew")
        
        self.frame.grid_columnconfigure(0, weight=1, uniform="a")
        self.frame.grid_columnconfigure(1, weight=1, uniform="a")
        self.frame.grid_rowconfigure(3, weight=1)
        return None
        
    def analyse(self, **kwargs):
        '''Analyse the selected (or merged) data set, and display results in 
        quick output box'''
        d_id = self.parent.selected_data
        if d_id is not None:
            outstr = self.parent.calc.format_analysis(d_id)
            self.quick_results.delete(0,"end")
            for line in outstr:
                self.quick_results.insert("end", line)
        else:
            tk.messagebox.showwarning("Select data first")
        return None
        
    def compare(self, **kwargs):
        '''Compare the two data sets and display results in quick output box'''
        d_id1 = self.parent.selected_data
        if d_id1 is not None:
            d_id2 = 1-d_id1
            outstr = self.parent.calc.format_compare(d_id1, d_id2)
            self.quick_results.delete(0,"end")
            for line in outstr:
                self.quick_results.insert("end", line)
        else:
            tk.messagebox.showwarning("Select data first")
        return None
        
    def report(self, **kwargs):
        '''Analyse the selected data and save the resulting report'''
        filename = tk.filedialog.asksaveasfile(mode="w", defaultextension=".docx", filetypes=[("Microsoft Word", ".docx")])
        if not filename:
            # The user cancelled the save file dialog
            # Do nothing
            pass
        else:
            filename = filename.name
            d_id = self.parent.selected_data
            _, data, runout = self.parent.calc.get_data(d_id)
            results = self.parent.calc.linear_regression(d_id)
            pyedna.format_report(filename, data, runout, results)
        return None

        
    def graph(self, **kwargs):
        '''Open the graph plotter window'''
        pyedna.GraphWindow(self.parent)
        return None
    
    def user_slope(self, event, **kwargs):
        '''If the text can be converted to a number, do that
        If it can't delete it to signal to the user that it's not a valid number
        The return statement is to prevent the trigger (i.e. Return buttonpress) 
        from causing a new-line'''
        string = self.t_slope.get("1.0", "end").strip()
        val = None
        try:
            if string != "":
                val = float(string)
        except:
            self.t_slope.delete('1.0','end')
        self.parent.calc.user_slope = val
        print(self.parent.calc.user_slope, type(self.parent.calc.user_slope))
        # return "break" to prevent the trigger (Return) from also causing \n
        return "break"
            
            
        