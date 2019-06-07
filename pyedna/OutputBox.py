import tkinter as tk

class OutputBox(object):
    def __init__(self, parent):
        self.parent = parent
        self.b_analysis = tk.Button(self.parent, text="Analyse", command=self.analyse)
        self.b_analysis.grid(row=0, column=0, sticky="nsew")
        self.b_compare = tk.Button(self.parent, text="Compare", command=self.compare)
        self.b_compare.grid(row=1, column=0, sticky="nsew")
        self.b_report = tk.Button(self.parent, text="Report", command=self.report)
        self.b_report.grid(row=0, column=1, sticky="nsew")
        self.b_graph = tk.Button(self.parent, text="Graph", command=self.graph)
        self.b_graph.grid(row=1, column=1, sticky="nsew")
        self.l_slope = tk.Label(self.parent, text="Slope")
        self.l_slope.grid(row=2, column=0, sticky="nsew")
        self.t_slope = tk.Text(self.parent, width=10,height=1)
        self.t_slope.grid(row=2, column=1, sticky="nsew")
        self.quick_results = tk.Listbox(self.parent).grid(row=3, column=0, columnspan=2, sticky="nsew")
        
        self.parent.grid_columnconfigure(0, weight=1, uniform="a")
        self.parent.grid_columnconfigure(1, weight=1, uniform="a")
        self.parent.grid_rowconfigure(3, weight=1)
        
    def analyse(self, **kwargs):
        print("Analyse")
    def compare(self, **kwargs):
        print("Compare")
    def report(self, **kwargs):
        print("Report")
    def graph(self, **kwargs):
        print("Graph")