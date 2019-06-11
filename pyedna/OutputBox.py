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
        self.t_slope = tk.Text(self.frame, width=10,height=1)
        self.t_slope.grid(row=2, column=1, sticky="nsew")
        self.quick_results = tk.Listbox(self.frame).grid(row=3, column=0, columnspan=2, sticky="nsew")
        
        self.frame.grid_columnconfigure(0, weight=1, uniform="a")
        self.frame.grid_columnconfigure(1, weight=1, uniform="a")
        self.frame.grid_rowconfigure(3, weight=1)
        
    def analyse(self, **kwargs):
        print("Analyse")
    def compare(self, **kwargs):
        print("Compare")
    def report(self, **kwargs):
        print("Report")
    def graph(self, **kwargs):
        print("Graph")