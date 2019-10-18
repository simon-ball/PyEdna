# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 14:48:10 2019

@author: simoba
"""
import numpy as np
import tkinter as tk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


'''
Plans:
    * Remove the figure size control, it's just awkward, and the user can get 
    coarse control by jsut resizing the window
    
    * Add back in the Plot button -> rather than real-time adjustment, I think 
    it's better to have the user set things up how they like and then press go
    
    * better handling of the initial default state :
        * Define a default dictionary at the start?
        * Plot the default curves on opening?
        * Results should probably already be calculated, once, unless Frode 
            confirms a maximum size on datasets
    
    * Tight layout (as part of plot?)
'''


import pyedna

# Define the font style used for titles
FONT = "-size 12"
PAD = 5
INCH2CM = 2.54

# define aliases for the axis limit types here
STEEL = "steel"
AL = "aluminium"
NN = "n"
SS = "s"
AUTO = "auto"
MANUAL = "manual"

# Define the limits for arbitrary material types
# limits are (n_min, n_max, s_min, s_max)
STEEL_lim = (1e4, 1e7, 50, 600)
AL_lim = (1e4, 1e7, 20, 300)
# NN, SS use one user-defined, one auto
# AUTO uses both auto

# Starting state



class GraphWindow(tk.Toplevel):
    '''
    General plan:
        * one frame of _what to plot_ (points, regression line, design curves, etc)
        * One frame of _how to plot_ (symbols, lines, limits, grid)
        * misc (e.g. make plot button)
    This class does not do ANY plotting directly: it is just an interface to 
    choose parameters for the plotting performed in EdnaCalc
    '''
    ##########################################################################
    ###############     USER INTERFACE INITIALISATION
    ##########################################################################
    def __init__(self, parent):
        self.parent = parent
        self.root = tk.Toplevel()
        self.root.title("PyEdna")
        self.init_values()
        self.init_frames()
        self.init_what()
        self.init_how()
        self.init_misc()
        self.init_graph()
        self.busy_starting = False
        #Initialise limit_vars values

        
        
        pass
 
    def init_values(self):
        '''Initialise the values that the various buttoms will rely on'''
        self.busy_starting = True # Used to prevent callbacks until everything is initialised
        
        self.plot_points = tk.BooleanVar()
        self.plot_points.set(True)
        self.plot_regression = tk.BooleanVar()
        self.plot_regression.set(True)
        self.plot_conf_pt = tk.BooleanVar()
        self.plot_conf_reg = tk.BooleanVar()
        self.plot_dc_bs540 = tk.BooleanVar()
        self.plot_dc_ec3 = tk.BooleanVar()
        
        self.grid_major = tk.BooleanVar()
        self.grid_minor = tk.BooleanVar()
        
        self.symbol = tk.StringVar()
        self.symbol.set("o")
        
        self.line = tk.StringVar()
        self.line.set("-")
        
        self.axis_limit = tk.StringVar()
        self.axis_limit.set(STEEL)
        self.axis_limit.trace("w", self.btn_axis_limits_changed)
        
        # Keeping track of graph size in cm
        self.x_size = tk.DoubleVar()
        self.y_size = tk.DoubleVar()
        self.x_size.trace("w", self.set_graph_size)
        self.y_size.trace("w", self.set_graph_size)
        
        # Axis limits
        self.n_min = tk.IntVar()
        self.n_max = tk.IntVar()
        self.s_min = tk.IntVar()
        self.s_max = tk.IntVar()
        self.limit_vars = (self.n_min, self.n_max, self.s_min, self.s_max)
        for i, var in enumerate(self.limit_vars):
            var.set(STEEL_lim[i])
        
        self.font_size = tk.IntVar()
        self.font_size.set(12)
        
        
    
    def init_frames(self):
        '''Initialise the frames that hold the various UI elements
        self.root has a Left and Right frame
        Left is divded into the various controls (what, how, limits, misc)
        Right holds the actual graph'''
        self.frame_left = tk.Frame(self.root)
        self.frame_right = tk.Frame(self.root)
        self.frame_left.grid(row=0, column=0, sticky="nsew")
        self.frame_right.grid(row=0, column=1, sticky="nsew")
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        self.frame_what = tk.Frame(self.frame_left, height=250)
        self.frame_how  = tk.Frame(self.frame_left, height=250)
        self.frame_misc = tk.Frame(self.frame_left, height=50)
        self.frame_what.grid(row=1, column=0, sticky="nsew", pady=PAD, padx=PAD)
        self.frame_what.grid_columnconfigure(0, weight=1) # allow to grow width-wise
        self.frame_how.grid(row=2, column=0, sticky="nsew", pady=PAD, padx=PAD)
        self.frame_how.grid_columnconfigure(0, weight=1, uniform="how")
        self.frame_how.grid_columnconfigure(1, weight=1, uniform="how")
        self.frame_how.grid_columnconfigure(2, weight=1, uniform="how")
        self.frame_misc.grid(row=3, column=0, sticky="nsew", pady=PAD, padx=PAD)
        self.frame_misc.grid_columnconfigure(0, weight=1)
        
        
        pass
        
    def init_what(self):
        '''Initialise the actual UI elements in the "what" frame
        In this sense, "what" refers to user decisions on what data will be plotted on the graph:
            * Data points entered into the program
            * Regression analysis
            * Confidence interval of one or both
            
            * Design curves given by the various standards'''
        self.what_title = tk.Label(self.frame_what, text="Plotting Features", font=FONT)
        self.what_subtitle = tk.Label(self.frame_what, text="Design Curves", font=FONT)
        
        self.bt_plot_points = tk.Checkbutton(self.frame_what, text="Data points", variable=self.plot_points)
        self.bt_plot_regres = tk.Checkbutton(self.frame_what, text="Regression line", variable=self.plot_regression)
        self.bt_plot_points_conf = tk.Checkbutton(self.frame_what, text="95% conf. for reg. line", variable=self.plot_conf_reg)
        self.bt_plot_regres_conf = tk.Checkbutton(self.frame_what, text="95% conf. for given value of S", variable=self.plot_conf_pt)
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
        self.how_title = tk.Label(self.frame_how, text = "Plotting style", font=FONT)
        self.how_title.grid(row=0, column=0, columnspan=4, sticky="nsew")
        
        # Data point symbols - here the variable is directly the Matplotlib marker command
        self.how_subtitle_symbol = tk.Label(self.frame_how, text="Symbol style", font=FONT)
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
        self.how_subtitle_line = tk.Label(self.frame_how, text="Line style", font=FONT)
        self.bt_lines = (tk.Radiobutton(self.frame_how, text="Solid", variable=self.line, value="-"),
                        tk.Radiobutton(self.frame_how, text="Dashed", variable=self.line, value="--",),
                        tk.Radiobutton(self.frame_how, text="Dotted", variable=self.line, value=":",),
                        tk.Radiobutton(self.frame_how, text="Dash-dot", variable=self.line, value="-.",))
        self.how_subtitle_line.grid(row=1, column=1, sticky="nsew")
        for i, lin in enumerate(self.bt_lines):
            lin.grid(row=i+2, column=1, sticky="nsw")
        
        # Axis limits
        self.how_subtitle_axis_limits = tk.Label(self.frame_how, text="Axis Limits", font=FONT)
        self.bt_axis_limits = (tk.Radiobutton(self.frame_how, text="Steel", variable=self.axis_limit, value=STEEL),
                               tk.Radiobutton(self.frame_how, text="Aluminium", variable=self.axis_limit, value=AL),
                               tk.Radiobutton(self.frame_how, text="N-limits", variable=self.axis_limit, value=NN),
                               tk.Radiobutton(self.frame_how, text="S-limits", variable=self.axis_limit, value=SS),
                               tk.Radiobutton(self.frame_how, text="Auto limits", variable=self.axis_limit, value=AUTO),
                               tk.Radiobutton(self.frame_how, text="Manual limits", variable=self.axis_limit, value=MANUAL),
                               )
        self.how_subtitle_axis_limits.grid(row=1, column=2, sticky="nsew")
        for i, axl in enumerate(self.bt_axis_limits):
            axl.grid(row=i+2, column=2, sticky="nsw")
            
        # Grid - be careful of distinction between _tkinter grid_ and _grid to be plotted in graph_
        self.how_subtitle_grid = tk.Label(self.frame_how, text="Grid", font=FONT)
        self.how_subtitle_grid.grid(row=1, column=3, sticky="nsew")
        self.bt_grid_major = tk.Checkbutton(self.frame_how, text="Major", variable=self.grid_major)
        self.bt_grid_major.grid(row=2, column=3, sticky="nsw")
        self.bt_grid_minor = tk.Checkbutton(self.frame_how, text="Minor", variable=self.grid_minor)
        self.bt_grid_minor.grid(row=3, column=3, sticky="nsw")
    
    
    

    
    def init_misc(self):
        '''Initialise figure style handling'''
        # Everything in here is referred to by linekd variables, therefore nothing needs to be added to self
        figstyle_title = tk.Label(self.frame_misc, text="Figure Style", font=FONT)
        figstyle_title.grid(row=0, column=0, columnspan=4, sticky="nsew")
        
        # Figure size
        # This feature has been deprecated
#        fig_size_x_label = tk.Label(self.frame_misc, text="N (cm)")
#        fig_size_y_label = tk.Label(self.frame_misc, text="S (cm)")
#        fig_size_x = tk.Entry(self.frame_misc, textvariable=self.x_size)#, validate="focusout", validatecommand=self.set_graph_size)
#        fig_size_y = tk.Entry(self.frame_misc, textvariable=self.y_size)#, validate="focusout", validatecommand=self.set_graph_size)
#        fig_size_x_label.grid(row=2, column=0, sticky="nsw")
#        fig_size_x.grid(row=2, column=1, sticky="nsw")
#        fig_size_y_label.grid(row=2, column=2, sticky="nsw")
#        fig_size_y.grid(row=2, column=3, sticky="nsw")
        
        lim_xmin_label = tk.Label(self.frame_misc, text="N (min)")
        lim_xmax_label = tk.Label(self.frame_misc, text="N (max)")
        lim_ymin_label = tk.Label(self.frame_misc, text="S (min)")
        lim_ymax_label = tk.Label(self.frame_misc, text="S (max)")
        
        lim_xmin = tk.Entry(self.frame_misc, textvariable=self.n_min, state="disabled")
        lim_xmax = tk.Entry(self.frame_misc, textvariable=self.n_max, state="disabled")
        lim_ymin = tk.Entry(self.frame_misc, textvariable=self.s_min, state="disabled")
        lim_ymax = tk.Entry(self.frame_misc, textvariable=self.s_max, state="disabled")
        self.limit_entries = (lim_xmin, lim_xmax, lim_ymin, lim_ymax)
        
        lim_xmin_label.grid(row=4, column=0, sticky="nsw")
        lim_xmax_label.grid(row=5, column=0, sticky="nsw")
        lim_ymin_label.grid(row=4, column=2, sticky="nsw")
        lim_ymax_label.grid(row=5, column=2, sticky="nsw")
        
        lim_xmin.grid(row=4, column=1, sticky="nsew")
        lim_xmax.grid(row=5, column=1, sticky="nsew")
        lim_ymin.grid(row=4, column=3, sticky="nsew")
        lim_ymax.grid(row=5, column=3, sticky="nsew")
        
        font_size_label = tk.Label(self.frame_misc, text="Font (pt)")
        font_size = tk.Entry(self.frame_misc, textvariable=self.font_size, state="normal")
        
        font_size_label.grid(row=6, column=0, sticky="nsw")
        font_size.grid(row=6, column=1, sticky="nsew")
        
        self.btn_plot = tk.Button(self.frame_left, text="Plot SN curve", font=FONT, command=self.plot_curve, state="normal")
        self.btn_plot.grid(row=4, column=0, sticky="nsew", pady=PAD, padx=PAD)
        
        # 
        pass
    
    def init_graph(self):
        '''based on https://matplotlib.org/3.1.0/gallery/user_interfaces/embedding_in_tk_sgskip.html'''
        self.fig = Figure()
        self.ax  = self.fig.add_subplot(111)
        self.graph = FigureCanvasTkAgg(self.fig, master=self.frame_right)
        self.graph.draw()
        self.graph.get_tk_widget().pack(side="top", fill="both", expand=1)
        self.graph_toolbar = NavigationToolbar2Tk(self.graph, self.frame_right)
        self.graph_toolbar.update()
        self.graph.get_tk_widget().pack(side="top", fill="both", expand=1)
        
        self.frame_right.bind("<Configure>", self.graph_resized)
        
        self.ax.set_xlabel("N [cycles]")
        self.ax.set_ylabel("S [MPa]")
        self.ax.set_title('Fatigue Lifecycle')
        # TODO: Also set some other style information here even prior to plotting?
    
    def btn_axis_limits_changed(self, *args, **kwargs):
        '''Possible values are: "steel", "aluminium", "n", "s", "auto", "manual".
        Limits are grouped in a list like so: (n_min, n_max, s_min, s_max)
        Where auto ranges are required, we have to get the range of data that will be plotted'''
        # TODO: SHould this happen over in EdnaCalc? The thing is that it is also UI related, including the numbers that should appear
        if self.parent:
            data = self.parent.calc.data[self.parent.selected_data] # TODO This will currently ignore merging, probably want a method in ednacalc to provide the relevant data
        else: #DEBUGGING PURPOSES ONLY
            data = np.arange(10).reshape(5,2)
        actual_data_range_limit = np.array(( np.min(data[:,1]), np.max(data[:,1]), np.min(data[:,0]), np.max(data[:,0]) ))
        actual_data_range_limit *= np.array((0.8, 1.2, 0.8, 1.2)) # give a 20% buffer around
        limit_type = self.axis_limit.get()
        if limit_type == STEEL:
            lims = STEEL_lim
            states = ["disabled"]*4
        elif limit_type == AL:
            lims = AL_lim
            states = ["disabled"]*4
        elif limit_type == NN:
            states = ("normal", "normal", "disabled", "disabled")
            lims = (self.n_min.get(), self.n_max.get(), actual_data_range_limit[2], actual_data_range_limit[3])
        elif limit_type == SS:
            states = ("disabled", "disabled", "normal", "normal")
            lims = (actual_data_range_limit[0], actual_data_range_limit[1], self.s_min.get(), self.s_max.get())
        elif limit_type == AUTO:
            states = ["disabled"]*4
            lims = actual_data_range_limit
        elif limit_type == MANUAL:
            states = ["normal"]*4
            lims = (self.n_min.get(), self.n_max.get(), self.s_min.get(), self.s_max.get())
        for i in range(4):
            self.limit_entries[i].config(state=states[i])
            self.limit_vars[i].set(lims[i])
        

        
        
    def graph_resized(self, event, **kwargs):
        '''Callback when graph size changes'''
        (x, y) = self.fig.get_size_inches()
        self.x_size.set(x * INCH2CM)
        self.y_size.set(y * INCH2CM)
    
    def set_graph_size(self, *args, **kwargs):
        '''callback when graph size setting changed'''
        # TODO: THis bit doesn't actually work!
        
        if self.busy_starting:
            #print("Callback (pass)")
            pass
        else:
            #print("Callback (change)")
            x = self.x_size.get() / INCH2CM
            y = self.y_size.get() / INCH2CM
            self.fig.set_size_inches(x, y)
    
    ##########################################################################
    ###############     FUNCTIONAL CODE HERE
    ##########################################################################
    
    def plot_curve(self):
        '''Triggered by "Plot SN curve" button
        Pass the resulting values on to EdnaCalc as a dictionary. The idea is 
        that the actual plotting is handled in EdnaCalc, so it can be run
        standalone if desired'''
        kwargs = {"marker" : self.symbol.get(),
                  "line_style" : self.line.get(),
                  "axis_limits" : [var.get() for var in self.limit_vars],
                  "grid_major" : self.grid_major.get(),
                  "grid_minor" : self.grid_minor.get(),
                  "plot_points" : self.plot_points.get(),
                  "plot_regression" : self.plot_regression.get(),
                  "plot_points_conf" : self.plot_conf_pt.get(),
                  "plot_regression_conf": self.plot_conf_reg.get(),
                  "plot_dc_bs540" : self.plot_dc_bs540.get(),
                  "plot_dc_ec3" : self.plot_dc_ec3.get(),
                  "font": self.font_size.get(),
                  "fig" : self.fig,
                  "ax" : self.ax,
                  }
        if self.parent is not None:
            self.parent.calc.plot_results(self.parent.selected_data, **kwargs)
            self.refresh_graph()
        else:
            print("Plot! \n" + str(kwargs)) 
    
    def refresh_graph(self, *args, **kwargs):
        self.fig.tight_layout()
        self.graph.draw()
            
            
if __name__ == "__main__":
    gui = GraphWindow(None)
    gui.root.mainloop()
        
        