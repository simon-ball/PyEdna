import tkinter as tk

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
        self.l_slope = tk.Label(self.frame, text="Slope")
        self.l_slope.grid(row=2, column=0, sticky="nsew")
        self.t_slope = tk.Text(self.frame, width=10,height=1, wrap="none")
        self.t_slope.bind("<Return>", self.user_slope)
        self.t_slope.grid(row=2, column=1, sticky="nsew")
        self.quick_results = tk.Listbox(self.frame)
        self.quick_results.grid(row=3, column=0, columnspan=2, sticky="nsew")
        
        self.frame.grid_columnconfigure(0, weight=1, uniform="a")
        self.frame.grid_columnconfigure(1, weight=1, uniform="a")
        self.frame.grid_rowconfigure(3, weight=1)
        
    def analyse(self, **kwargs):
        d_id = self.parent.selected_data
        if d_id is not None:
            outstr = self.parent.calc.format_analysis(d_id)
            self.quick_results.delete(0,"end")
            for line in outstr:
                self.quick_results.insert("end", line)
        else:
            # TODO: some form of warning box instead of silently failing
            print("Select data first")
        
    def compare(self, **kwargs):
        d_id1 = self.parent.selected_data
        if d_id1 is not None:
            d_id2 = 1-d_id1
            outstr = self.parent.calc.format_compare(d_id1, d_id2)
            self.quick_results.delete(0,"end")
            for line in outstr:
                self.quick_results.insert("end", line)
        else:
            # TODO: some kind of warning box
            print("Select data first")
        print("Compare")
        
    def report(self, **kwargs):        
        d_id = self.parent.selected_data
        print("Report")
        
    def graph(self, **kwargs):
        d_id = self.parent.selected_data
        self.parent.calc.plot_results(d_id)
    
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
        print(self.parent.calc.user_slope)
        return "break"
            
            
        