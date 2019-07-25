# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 14:48:10 2019

@author: simoba
"""

import tkinter as tk


#import pyedna

class GraphWindow(object):
    '''
    General plan:
        * one frame of _what to plot_ (points, regression line, design curves, etc)
        * One frame of _how to plot_ (symbols, lines, limits, grid)
        * misc (e.g. make plot button)
    '''
    ##########################################################################
    ###############     USER INTERFACE INITIALISATION
    ##########################################################################
    def __init__(self, parent):
        self.parent = parent
        self.root = tk.Tk()
        self.root.title("PyEdna")
        self.init_values()
        self.init_frames()
        self.init_what()
        self.init_how()
        self.init_misc()
        self.root.mainloop()
        pass
    
    def init_values(self):
        '''Initialise the values that the various buttoms will rely on'''
        self.plot_points = tk.BooleanVar()
        self.plot_regression = tk.BooleanVar()
        self.plot_conf_pt = tk.BooleanVar()
        self.plot_conf_reg = tk.BooleanVar()
        self.plot_dc_bs540 = tk.BooleanVar()
        self.plot_dc_ec3 = tk.BooleanVar()
        
        self.grid = tk.BooleanVar()
        
        self.symbol = tk.StringVar()
        self.symbol.set("o")
        
        self.line = tk.StringVar()
        self.line.set("-")
        
        self.axis_limit = tk.IntVar()
        self.axis_limit.set(0)
    
    def init_frames(self):
        '''Initialise the frames that hold the various UI elements'''
        self.frame_what = tk.Frame(self.root, height=250)
        self.frame_how  = tk.Frame(self.root, height=250)
        self.frame_misc = tk.Frame(self.root, height=50)
        self.frame_what.grid(row=1, column=0, sticky="nsew", pady=5, padx=5)
        self.frame_what.grid_columnconfigure(0, weight=1) # allow to grow width-wise
        self.frame_how.grid(row=2, column=0, sticky="nsew", pady=5, padx=5)
        self.frame_how.grid_columnconfigure(0, weight=1, uniform="how")
        self.frame_how.grid_columnconfigure(1, weight=1, uniform="how")
        self.frame_how.grid_columnconfigure(2, weight=1, uniform="how")
        self.frame_misc.grid(row=3, column=0, sticky="nsew", pady=5, padx=5)
        self.frame_misc.grid_columnconfigure(0, weight=1)
        pass
        
    def init_what(self):
        '''Initialise the actual UI elements in the "what" frame
        In this sense, "what" refers to user decisions on what data will be plotted on the graph:
            * Data points entered into the program
            * Regression analysis
            * Confidence interval of one or both
            
            * Design curves given by the various standards'''
        self.what_title = tk.Label(self.frame_what, text="Plotting Features")  
        self.what_subtitle = tk.Label(self.frame_what, text="Design Curves")  
        
        self.bt_plot_points = tk.Checkbutton(self.frame_what, text="Data points", variable=self.plot_points)
        self.bt_plot_regres = tk.Checkbutton(self.frame_what, text="Regression line", variable=self.plot_regression)
        self.bt_plot_points_conf = tk.Checkbutton(self.frame_what, text="Conf. for reg. line", variable=self.plot_conf_pt)
        self.bt_plot_regres_conf = tk.Checkbutton(self.frame_what, text="Conf. for given value S", variable=self.plot_conf_reg)
        self.bt_dc_bs540 = tk.Checkbutton(self.frame_what, text="95% Surv, 97.5% Conf (BS540, NS3472)", variable=self.plot_dc_bs540)
        self.bt_dc_ec3   = tk.Checkbutton(self.frame_what, text="95% Surv, 75% Conf (EC3)", variable=self.plot_dc_ec3)
        
        self.what_title.grid(row=0, sticky="nsew")
        
        self.bt_plot_points.grid(row=1, sticky="nsw")
        self.bt_plot_regres.grid(row=2, sticky="nsw")
        self.bt_plot_points_conf.grid(row=3, sticky="nsw")
        self.bt_plot_regres_conf.grid(row=4, sticky="nsw")
        
        self.what_subtitle.grid(row=5, sticky="nsew")
        
        self.bt_dc_bs540.grid(row=6, sticky="nsw")
        self.bt_dc_ec3.grid(row=7, sticky="nsw")
        pass
    
    def init_how(self):
        '''Initialise the actual UI elements relating to "how"
        In this sense, "how" refers to how the plotted data will be presented:
            * Axis limits
            * Fitted line limits
            * Symbols and line style
            * Grid
        '''
        self.how_title = tk.Label(self.frame_how, text = "Plotting style")
        self.how_title.grid(row=0, column=0, columnspan=4)
        
        # Data point symbols - here the variable is directly the Matplotlib marker command
        self.how_subtitle_symbol = tk.Label(self.frame_how, text="Symbol style")
        self.bt_symbols = (tk.Radiobutton(self.frame_how, text="Circle", variable=self.symbol, value="o"),
                        tk.Radiobutton(self.frame_how, text="Square", variable=self.symbol, value="s",),
                        tk.Radiobutton(self.frame_how, text="Triangle", variable=self.symbol, value="^",),
                        tk.Radiobutton(self.frame_how, text="Cross", variable=self.symbol, value="x",),
                        tk.Radiobutton(self.frame_how, text="Star", variable=self.symbol, value="*",),
                        tk.Radiobutton(self.frame_how, text="Diamond", variable=self.symbol, value="d",), )
        self.how_subtitle_symbol.grid(row=1, column=0, sticky="nsew")
        for i, sym in enumerate(self.bt_symbols):
            sym.grid(row=i+2, column=0, sticky="nsw")
        
        # Line styles - here the variable is directly the Matplotlib marker command
        self.how_subtitle_line = tk.Label(self.frame_how, text="Line style")
        self.bt_lines = (tk.Radiobutton(self.frame_how, text="Solid", variable=self.line, value="-"),
                        tk.Radiobutton(self.frame_how, text="Dashed", variable=self.line, value="--",),
                        tk.Radiobutton(self.frame_how, text="Dotted", variable=self.line, value=":",),
                        tk.Radiobutton(self.frame_how, text="Dash-dot", variable=self.line, value="-.",))
        self.how_subtitle_line.grid(row=1, column=1, sticky="nsew")
        for i, lin in enumerate(self.bt_lines):
            lin.grid(row=i+2, column=1, sticky="nsw")
        
        # Axis limits
        self.how_subtitle_axis_limits = tk.Label(self.frame_how, text="Axis Limits")
        self.bt_axis_limits = (tk.Radiobutton(self.frame_how, text="Steel", variable=self.axis_limit, value=0),
                               tk.Radiobutton(self.frame_how, text="Aluminium", variable=self.axis_limit, value=1),
                               tk.Radiobutton(self.frame_how, text="N-limits", variable=self.axis_limit, value=2),
                               tk.Radiobutton(self.frame_how, text="S-limits", variable=self.axis_limit, value=3),
                               tk.Radiobutton(self.frame_how, text="Auto-limits", variable=self.axis_limit, value=4),)
        self.how_subtitle_axis_limits.grid(row=1, column=2, sticky="nsew")
        for i, axl in enumerate(self.bt_axis_limits):
            axl.grid(row=i+2, column=2, sticky="nsw")
            
        # Grid - be careful of distinction between _tkinter grid_ and _grid to be plotted in graph_
        self.how_subtitle_grid = tk.Label(self.frame_how, text="Grid")
        self.how_subtitle_grid.grid(row=1, column=3, sticky="nsew")
        self.bt_grid = tk.Checkbutton(self.frame_how, text="Grid", variable=self.grid)
        self.bt_grid.grid(row=2, column=3, sticky="nsw")
            
    
    def init_misc(self):
        '''Initialise everything else'''
        self.bt_plot = tk.Button(self.frame_misc, text="Plot SN Curve", command=self.plot_curve)
        self.bt_plot.grid(row=0, sticky="nsew")
        
        pass
    
    
    ##########################################################################
    ###############     FUNCTIONAL CODE HERE
    ##########################################################################
    
    def plot_curve(self):
        '''Triggered by "Plot SN curve" button'''
        kwargs = {"marker" : self.symbol,
                  "line_style" : self.line,
                  "axis_limit" : self.axis_limit,
                  "grid" : self.grid, }
        print("Plot! \n" + str(kwargs))
            
            
if __name__ == "__main__":
    gui = GraphWindow(None)
    gui
        
        