import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import LogFormatter
from matplotlib import rcParams as rcp
import scipy.optimize
import scipy.stats
try:
    from EdnaLookup import ddist
except ModuleNotFoundError:
    from .EdnaLookup import ddist
    # Messy hack to get around the problem of EdnaCalc possibly being either main or imported

class EdnaCalc:
    def __init__(self, parent=None):
        self.parent = parent
        self.data = [None, None]
        self.header = [None, None]
        self.runout = [None, None]
        self.user_slope = None      # text3             # This is configured from pyedna.OutputBox
        self.user_thick = None      # text5, ref. thick
        self.user_confidence = None # text8, conf
        self.merge = False
        self.epsilon = 0.05 # denoting 95% confidence level, TODO: configurable
                            # equivalent to "cop" in original?
        # Constants for later comparison
        self.ymin = 1e-10
        self.ymax = 1e10
        
        
    def load_data(self, file_path, data_id, **kwargs):
        '''Read a text file and determine which, if any, are runouts.
        Insert the resulting data into the appropriate place
        Matching the Python style, we use 0 and 1, rather than 1, 2, to denote 
        d_id (data id)
        
        S is accessed as data[:, 0]
        N as data[:, 1]
        runout is a 1D array giving 1 at any row of data in which the runout
        marker was detected. 
        
        TODO: There may need to be some secondary marker for keeping track of thickness in here???
        '''
        delim = kwargs.get("delimiter", ",")
        runout_marker = kwargs.get("runout", "*")
        header = kwargs.get("header_lines", 2)
        runout_markers = ("*", "^", "&")

        if runout_marker in runout_markers:
            data_str = np.genfromtxt(file_path, delimiter=delim, skip_header=header, usecols=(0,1), dtype=str)
            data = np.zeros(data_str.shape)
            runout = np.zeros(np.max(data.shape))
            for i, val in enumerate(data_str[:,0]):
                try:
                    data[i,:] = data_str[i,:].astype(np.float)
                    
                except ValueError:
                    runout[i] = 1
                    data[i,0] = np.float(data_str[i,0][1:])
                    data[i,1] = np.float(data_str[i,1])
            if (data<0).any():
                raise ValueError("A negative number was detected. Please check"\
                        " that you have set the correct runout indicator."\
                        f" PyEdna currently expects one of {runout_markers}")
            # Now get the header information that Numpy skipped
            with open(file_path) as file:
                line1 = file.readline().strip()
                line2 = file.readline().strip()
                header = (line1, line2)
        else:
            raise NotImplementedError("Currently, the only supported runout"\
              f" indicators are {runout_markers}. You requested runout indicator"\
              f" '{runout}'")
        
        self.data[data_id] = data
        self.runout[data_id] = runout.astype(bool)
        self.header[data_id] = header



    def get_data(self, data_id=0, **kwargs):
        '''A single function for handling selection of data, merging/unmerging,
        handling runouts
        
        Parameters
        ----------
        data_id : int (optional)
            Which dataset to select. If the Merge=True flag is set, this 
            parameter is ignored
        ignore_merge : Boolean
            temporarily ignore the Merge flag, and return exactly the dataset
            requested
            
        Returns
        -------
        filtered_data : numpy.ndarray
            Returns the requested data with all runouts removed
            S is accessible as filtered_data[:, 0]
            N is accessible as filtered_data[:, 1]
        data : numpy.ndarray
            Returns the requested data with all runouts included. Access
            is identical to that for filtered data
        runout : numpy.ndarray
            1D array as a mask for data. Cell is TRUE where that data point is
            a runout            
        '''
        ignore_merge = kwargs.get("ignore_merge", False)
        if type(data_id) == int:
            if self.data[data_id] is None:
                raise ValueError("A dataset matching id '%d' has not yet been loaded" % data_id)
            if self.merge and not ignore_merge:
                if self.data[0] is None or self.data[1] is None:
                    raise NotImplementedError("You have attempted to merge datasets without providing a second dataset")
        if (not self.merge) or (self.merge and ignore_merge):
            # i.e. use the specifically requested data set
            data = self.data[data_id]
            runout = self.runout[data_id]
        else:
            #i.e. merge all available datasets:
            data = np.concatenate(self.data, axis=0)
            runout = np.concatenate(self.runout, axis=0)
            
        filtered_data = data[np.invert(runout)]
        return filtered_data, data, runout
        
        
    
    def linear_regression(self, data_id, **kwargs):
        '''Perform a Stress / Lifetime analysis based on a log-normal model.
        
        Analysis is based on a SINTEF report:
            Statstical Analysis of Fatigue test data
            Marvin Rausand
            1981-07-09
            ISBN 82-595-2601-8
            Report no STF18 A81047
        
        A log-normal model is assumed, based on the following publication:
            Distrbibution functions for the prediction of fatigue life and fatigue strength
            A. M. Freudenthal and E. J Gumbel
            Proc. Int. Conf. Fatique Metals
            British Institute of Mechanical Engineers
            1956
        
        Input data set is a list of stress-ranges and associated lifetimes. One
        or more of these lifetimes may be indicated as "runouts", in which the
        testing finished without fatigue-based damage. The lifetime at a given
        stress range is assumed  to be normally diistributed around the mean.
        
        A linear regression is applied to the log10 of the input data. If the 
        'debug' flag is set, then results are printed to stdout
        
        STATUS:
            (2019-08-01): 
                Linear regression with no additional keywords correctly analyses
                all test-cases provided by Frode to the accuracy given by Edna70b
                
                Calculating parameters for condifence interval is currently incomplete
                
                Linear regression with keywords set does not work correctly, as
                it uses curve_fit with one or both parameters constrained such 
                that pcov is invalid. Need to find a better approach to this
            
        
        Parameters
        ----------
        data_id : int
            Which data set to perform a linear regression on
        kwargs
            debug : bool
                Enable or disable debugging output
            computer_slope : float
                Used by the compare() function. The user should never manually configure this value
            comptuer_intercept : float
                Used by the compare() function. The user should never manually configure this value
            ignore_merge : float
                Used by the compare() function to enforce ignoring the merge flag. The user should never manually configure this value
        
        '''
        # Handle kwargs
        debug = kwargs.get("debug", False)
        computer_slope = kwargs.get("computer_slope", None) # This is used by self.compare()
        computer_intercept = kwargs.get("computer_intercept", None) # This is used by self.compare()
        
        # Define useful constants
        log10_2e6 = np.log10(2e6) # approx 6.30103
        
        # Select the correct group of data, handling emrging as required. 
        data = self.get_data(data_id, **kwargs)[0]
        if debug:
            print(data)
        S = data[:, 0] # Stress
        N = data[:, 1] # Lifetime
        # Make a substitution to match a simple linear model
        # In this substitution, we want to find alpha = log10(intercept)
        # and beta = gradient
        # Note also: I have followed the convention in the Rausand report, 
        # mapping between  (s <> x) and (N <> y). Beware - this results in 
        # "x" being plotted on the y axis, and vice-versa. THIS IS NOT THE 
        # SAME AS IN EDNA. PAY ATTENTION TO WHICH IS WHICH WITH EXTREME CARE
        x = np.log10(S)
        y = np.log10(N)
        
        def model(x, alpha, beta):
            '''Simple linear model'''
            return alpha + (beta*x)
        
        
        # Perform a simple linear regression to find intercept and gradient
        # using scipy.optimize.curve_fit.
        # Work with any constraints provided by redefining the model to catch the correct number of constraints
        
        if self.user_slope is not None:
            # User has specified a value for the slope, therefore constrain this from changing
            raise NotImplementedError
#            limits = ([-np.inf, self.user_slope-2*np.spacing(1)], [np.inf, self.user_slope+2*np.spacing(1)])
#            initial_guess = [1, self.user_slope]
        elif computer_slope is not None and computer_intercept is not None:
            # Slope and intercept both specified for self.compare()
            raise NotImplementedError
            # TODO TODO: This is a special case, because there are NO degrees of freedom, so curve_fit will throw a hissy fit
#            initial_guess = (computer_intercept, computer_slope)
#            limits = ([computer_intercept*0.999, computer_slope-2*np.spacing(1)], [computer_intercept*1.001, computer_slope+2*np.spacing(1)])
#            dof = 0

        elif computer_slope is not None:
            # Mechanical specified slope parameter, used by self.compare()
            raise NotImplementedError
#            initial_guess = [1, computer_slope]
#            limits = ([-np.inf, computer_slope-2*np.spacing(1)], [np.inf, computer_slope+np.spacing(1)])
#            dof = 1
        elif self.user_thick is not None:
            raise NotImplementedError
        else:
            initial_guess = [1, 1]
            limits = (-np.inf, np.inf)
            dof = 2
        try:
            params, cov = scipy.optimize.curve_fit(model, x, y, initial_guess, bounds=limits)
        except ValueError as e:
            print(e)
            print(initial_guess)
            print(limits)
            print(self.user_slope)
            print(computer_slope)
            print(computer_intercept)
            return
        # params: [alpha, beta], the values which minimise least-squares
        # cov: covariance matrix, the variance of [params] is the diagonal
        # np.diag(cov)
        
        # (section 3.3)
        # Estimate the variance of the observations y_i around the model
        residuals = model(x, *params) - y
        num_points = y.size
        residual_sum_of_squares = np.sum(np.square(residuals))
        total_sum_of_squares = np.sum(np.square(y - np.mean(y)))
        variance = residual_sum_of_squares / (num_points - dof)
        stdev = np.sqrt(variance)
        
        r_squared = 1 - ( residual_sum_of_squares / total_sum_of_squares )
        
        # Section 3.4
        # Confidence intervals for alpha, beta
        # We get the uncertainty of the params from the diag of the covariance matrix. This is given as sigma
        alpha, beta = params
        sigma_alpha, sigma_beta = np.sqrt(np.diag(cov))
        # We want percentile confidence, not sigma - use the ppf to convert. 
        s95_alpha, s95_beta = scipy.stats.norm.ppf(1-self.epsilon, 0, 1)*np.sqrt(np.diag(cov))
        
        
        results = {"r_squared": r_squared, "stdev": stdev, "slope": beta,
                   "intercept":10**alpha, "delta_sigma": 10**((alpha - log10_2e6)/-beta),
                   "variance": variance, "points":num_points, "dof": dof, "alpha": alpha,
                   "intercept_conf": s95_alpha, "slope_conf": s95_beta}
        # Delta-sigma is in units [Mpa]
        
        # Also write some information about the input data to the results
        results["header_1"] = self.header[data_id][0]
        results["header_2"] = self.header[data_id][1]
        
        
        ####################### Report statistics
        # No-one has been able to provide me with a specification for the following statistics.
        # Therefore, they are cobbled together as best I can from reverse engineering the original code
        # In particular, the reversal of x and y relative to mathematical convention (and relative to Edna) 
        # renders interpretation considerably more difficult and error prone
        # When, or if, I am able to get a clearer explanation from the users what it all means and why,
        # it will be tided up
        #
        # Until such time, abandon hope all ye who enter, for here be dragons
        # Simon Ball, Sept 2019
        
        
        #Handled around line 1750 in frmhoved.frm
        
        # confidence interval for regression line in Analysis Report
        mean_logS = np.sum(x)/num_points # YMID
        mean_logN = np.sum(y)/num_points # XMID
        sumx = np.sum(x)
        sumy = np.sum(y)
        sumx2 = np.sum(x**2)
        sumy2 = np.sum(y**2)
        sumxy = np.sum(x*y)
        sumxx = np.sum( (x-mean_logS)**2 ) # sumyy in frmHoved, around line 1735
        sumyy = np.sum( (y-mean_logN)**2 )
        if self.user_slope is not None: # user_slope: text3, Valhel, line 1744
            S2s = residual_sum_of_squares / (num_points - dof)
            temp = 1-(residual_sum_of_squares/sumxx) 
            r = max(0, temp) # not lower than zero.
        elif self.user_slope is None and num_points > 2: # line 1752
            S2s = residual_sum_of_squares / (num_points - dof)
            temp_numerator = (num_points*sumxy) - (sumx*sumy)
            temp_denominator = np.sqrt( ((num_points * sumy2) - sumy**2) * ((num_points*sumx2) - sumx**2) )
            temp = temp_numerator / temp_denominator
            r = max(0, temp)
        else: # line 1757
            S2s = 0
            r = 1
        s = np.sqrt(S2s)
        rp = scipy.stats.t.isf(0.05/2, num_points-dof) # Only distinction here seems to be that s95 uses hardcoded confidence, s9xs allows user choice
        rp2 = scipy.stats.t.isf(self.epsilon/2, num_points-dof) # DivBy2 - original Excel functions are double-sided; scipy are single tailed
        s9Xs = rp2 * s / np.sqrt(num_points) # I think that in Edna, this is a placeholder for (future) user-defined epsilon
        s95s = rp * s / np.sqrt(num_points)
        des3 = s * ddist(num_points-dof) # Used for EC3 design curve
        rf = scipy.stats.f.isf(self.epsilon, dof, num_points-dof)
        d0 = 2 * s * np.sqrt(2*rf/num_points) # Used for the confidence interval at the mean value of b/beta
        d1 = 2 * s * np.sqrt(2*rf / sumxx) # Used for the confidence interval at a mean value of c/alpha
        pre = 2 * s9Xs * np.sqrt(num_points + 2) ## NOTE the +: this is used in the original code. No idea why. 
        results["mean_stress"] = 10**mean_logS # In units [MPa]
        results["regression_confidence"] = 2* s9Xs  # "% confidence interval for Regression Line"
        results["confidence_given_s"] = pre   # "% confidence interval for given value of S"
        results["confidence_b"] = d1 # "% confidence interval (for mean value of C)"
        results["confidence_c"] = d0 # "% confidence interval (for mean value of b)"
        results["s_lower"] = -beta - (d1*0.5)
        results["s_upper"] = -beta + (d1*0.5)
        results["c_lower"] = 10**(alpha-(0.5*d0))
        results["c_upper"] = 10**(alpha+(0.5*d0))
        results["dc_bs540_intercept"] = 10**(alpha-(s95s*np.sqrt(num_points+1))) # frmhoved line 426
        results["dc_bs540_delta_sigma"] = 10**((alpha - log10_2e6 - (s95s*np.sqrt(num_points+1)) )/-beta)
        results["dc_ec3_intercept"] = 10**(alpha-des3) # frmhoved line 429
        results["dc_ec3_delta_sigma"] = 10**((alpha - log10_2e6 - des3)/-beta)
        
        # Include the confidence interval used
        results["confidence_interval"] = 1-self.epsilon # recall that epsilon is, e.g., 0.05 for 95%
        #debugging code
        if debug:
            print("Quick results")
            for key in results.keys():
                print(f"{key}: {results[key]}")
        return results
    
    
    
    def compare(self, d_id_1, d_id_2, **kwargs):
        
        '''
        Compare two different data sets for compatibility, to give a yes/no 
        answer to whether they can be merged
        
        # TODO: Validate that the various statistical tests are implemented correctly. 
        '''
        raise NotImplementedError # TODO
        # Handle kwargs
        debug = kwargs.get("debug", False)
        
        for idx in [d_id_1, d_id_2]:
            if self.data[idx] is None:
                raise ValueError("Cannot compare two datasets because dataset (%s) are not yet loaded" % idx)
        
        results1 = self.linear_regression(d_id_1, ignore_merge=True)
        results2 = self.linear_regression(d_id_2, ignore_merge=True)
        
        # Step 1: test whether the variances can be assumed different or not
        # Section 3.8.1, page 18
        var1 = results1["variance"]
        var2 = results2["variance"]
        m_dof1 = results1['points'] - results1['dof']
        m_dof2 = results2['points'] - results2['dof']
        
        # Null hypothesis: variances are equal
        # We REJECT the null hypothesis if either statement is True
        # Therefore, we ACCEPT hypothesis if NOT (either statement is True)
        variances_equal = not (var1/var2 > scipy.stats.f.isf(self.epsilon/2, m_dof1, m_dof2)) or \
                                (var1/var2 < 1/scipy.stats.f.isf(self.epsilon/2, m_dof2, m_dof1))

        # Step 2: test whether SN curves are parallel
        # Section 3.8.2, page 20
        temp_results = self.linear_regression(d_id_2, computer_slope=results1['slope'], ignore_merge=True)
        m_dof2 = temp_results['points'] - temp_results['dof']
        RSS = self.Q((results1['intercept'], results2['intercept']), (results1['slope'], results2['slope']))
        RSS_H1 = self.Q((results1['intercept'], temp_results['intercept']), (results1['slope'], temp_results['slope']))
        #I don't think this is quite right, I think we have to recalculate results where the two slopes are forced to be equal - that requires changes to self.linear_regression
        
        # Null hypothesis (1): curves are parallel
        # We REJECT the null hypothesis (1) if the conditional statement is TRUE
        # Therefore, we ACCEPT the null hypothesis (1) if NOT(statement is True)
        curves_parallel = not (((RSS_H1 - RSS)/RSS) * (m_dof1 + m_dof2) > scipy.stats.f.isf(self.epsilon, 1, m_dof1 + m_dof2))
        
        
        # Step 3: test whether the two curves are _equal_
        # Section 3.8.4, page 22
        # Note: this is not the same as curves_parallel AND variances_equal, because
        # that does not respect the confidence interval of the combined test.
        temp_results = self.linear_regression(d_id_2, computer_slope=results1['slope'], computer_intercept = results1['intercept'], ignore_merge=True)
        m_dof2 = temp_results['points'] - temp_results['dof']
        RSS_H5 = self.Q((results1['intercept'], temp_results['intercept']), (results1['slope'], temp_results['slope']))
        
        # Null hypothesis (5): slope and intercepts are equal
        # We REJECT the null hypothesis (5) if the conditional statement is True
        # We ACCEPT the null hypothesis (5) if NOT(statement is True)
        curves_equal = not ( ((RSS_H5 - RSS)/RSS) * ((m_dof1 + m_dof2)/2) > scipy.stats.f.isf(self.epsilon, 2, m_dof1+m_dof2))
        
        
        if debug:
            print(f"Variances equal: {variances_equal}")
            print(f"Curves parallel: {curves_parallel}")
            print(f"Curves equal: {curves_equal}")
        return variances_equal, curves_parallel, curves_equal
    
        
    
    def Q(self, alpha, beta):
        '''Equation 3.32 in Rausand 1981, Used for comparison
        
        Parameters
        ----------
        alpha : tuple
            The intercepts of data set 0 and dataset 1, respectively, calculated from self.linear_regression()
        beta : tuple
            The slopes of data set 0 and 1 respectively, calculated from self.linear_regression()
        '''
        val = 0
        for k in range(2):
            y = np.log10(self.data[k])[:,0]
            x = np.log10(self.data[k])[:,1]
            val += np.sum(np.square(y - alpha[k] - (beta[k]*x)))
        return val
      
        
        
    def format_analysis(self, d_id, **kwargs):
        '''Produce a formatted string representation of a linear regression
        of the data set d_id'''
        results = self.linear_regression(d_id, **kwargs)
        rsq = results["r_squared"]
        stdev = results["stdev"]
        slope = results["slope"]
        intercept = results["intercept"]
        ds = results["delta_sigma"]
        if self.merge:
            d_id = "merged"
        else:
            d_id +=1
        outstr = (f"=== Data {d_id} ===" ,
                f"R squared:  {rsq:3g}",
                f"Std. Dev:  {stdev:3g}", 
                f"Slope:  {slope:3g}",
                f"Intercept:  {intercept:3g}",
                f"Delta Sigma (2e6):  {ds:3g}",
                "",
                f"Design Curve",
                f"Intercept C: {results['dc_bs540_intercept']:3g}",
                f"Delta Sigma (2E6): {results['dc_bs540_delta_sigma']:3g}",
                f"Intercept C: {results['dc_ec3_intercept']:3g}",
                f"Delta Sigma (2E6): {results['dc_ec3_delta_sigma']:3g}",)
        return outstr
    
    
    
    def format_compare(self, d_id1, d_id2, **kwargs):
        '''Produce a formatter string representation of a comparison'''
        var_equal, curv_para, curv_equal = self.compare(d_id1, d_id2, **kwargs)
        outstr = (f"=== Comparing data {d_id1+1} to {d_id2+1} ===",
                  f"Variances equal : {var_equal}",
                  f"Curves parallel: {curv_para}",
                  f"Curves equal: {curv_equal}")
        return outstr


    
    def plot_results(self, data_id=0, **kwargs):
        '''Handle plotting of the S-N curve. 
        
        This function is written to match the options available in the VB6 
        version of Edna. If you require additional customisation, this function 
        can be modified to accomplish pretty much anything
        
        Paramters
        ---------
        data_id : int
            Which data set to plot? If Merge=True, then this parameter can be 
            ignored
        marker : str
            Matplotlib marker codes. Typical values are "o", ".", "x" etc
            Default is "o"
        line_style : str
            Matplotlib line style codes. Valid values are "-", "--", "-.", ":"
            Default is "-"
        axis_limits : list
            (min n, max n, min s, max s)  
        log_y : boolean
            Plot the Y axis (s) as a log or not
        grid_major : boolean
            Show major grid lines or not. Default False
        grid_minor : boolean
            Show minor grid lines or not. Default False
        plot_points : boolean
            Plot S-N data points. Default True
        plot_regression : boolean
            Plot the regression line or not. Default True
        plot_points_conf : boolean
            Plot the confidence interval of the S-N points or not. Default False
        plot_regression_conf : boolean
            Plot the confidence interval of the regression line or not. Default False
        plot_dc_bs540 : boolean
            Plot the BS540 / NS3472 design curves or not. Default False
        plot_dc_ec3 : boolean
            Plot the EC3 design curve or not. Default False
        font : int
            Font size in pt
        
        fig : matplotlib.figure.Figure
            OPTIONAL: if provided, then the data will be plotted into the
            provided canvas. If not provided, then a new canvas will be created.
            Included to allow the plotting logic to be handled here, but the
            graph be contained within the GraphPlotter class
        ax : matplotlib.axes._subplots.AxesSubplot
            OPTIONAL: if provided, then the data will be plotted into the
            provided canvas. If not provided, then a new canvas will be created.
            Included to allow the plotting logic to be handled here, but the
            graph be contained within the GraphPlotter class
            
        Returns
        -------
        None
        '''
        ##########################################################
        ############    Handle args and kwargs
        
        marker = kwargs.get("marker", "o")
        line_style = kwargs.get("line_style", "-")
        axis_limits = kwargs.get("axis_limits", None)
        log_y = kwargs.get("axis_style", True)
        grid_major = kwargs.get("grid_major", False)
        grid_minor = kwargs.get("grid_minor", False)
        plot_points = kwargs.get("plot_points", True)
        plot_regression = kwargs.get("plot_regression", True)
        plot_points_conf = kwargs.get("plot_points_conf", False)
        plot_regression_conf = kwargs.get("plot_points_regression", False)
        plot_dc_bs540 = kwargs.get("plot_dc_bs540", False)
        plot_dc_ec3 = kwargs.get("plot_dc_ec3", False)
        plot_legend=kwargs.get("plot_legend", True)
        font = kwargs.get("font", 12)
        fig = kwargs.get("fig", None)
        ax = kwargs.get("ax", None)
        

        # Get the data, and the meaning of kwargs
        filtered_data, data, runout = self.get_data(data_id, ignore_merge=False)
        results = self.linear_regression(data_id, ignore_merge=False)
        S = data[:, 0] # Stress : Y axis
        N = data[:, 1] # Lifetime : X axis
        
        
        if fig is None:
            figsize = (12, 9) # in inches
            fig, ax = plt.subplots(figsize=figsize)
        else:
            figsize = fig.get_size_inches()
            ax.clear()
        
        
        ##########################################################
        ############    Format the graph
        
        # Set labels
        ax.set_xlabel("N [cycles]")
        ax.set_ylabel("S [MPa]")
        ax.set_title('Fatigue Lifecycle')
        
        # Set the axis behaviour
        ax.set_xscale('log')
        ax.xaxis.set_minor_formatter(ticker.FuncFormatter(lambda x, pos: '%s' % (str(x)[0] if int(str(x)[0]) < 6 else '')))
        if log_y:
            ax.set_yscale("log")
            ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:6.0f}'))
            ax.yaxis.set_minor_formatter(ticker.FuncFormatter(lambda x, pos: '%s' % (str(x)[0] if int(str(x)[0]) < 6 else '')))
        else:
            ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:6.0f}'))

            
        
        # Set the axis limits, if any:
        if axis_limits is not None:
            ax.set_xlim(axis_limits[0], axis_limits[1])
            ax.set_ylim(axis_limits[2], axis_limits[3])
        
        # Set font size
        ax.yaxis.label.set_fontsize(font)
        ax.xaxis.label.set_fontsize(font)
        ax.title.set_fontsize(font + 4)
        ax.tick_params(which='major', axis="x", direction="in", length=5, labelsize=font-2)
        ax.tick_params(which='major', pad=0, axis="y", direction="in", length=3, labelsize=font-2)
        ax.tick_params(which='minor', pad=5, direction="in", width=1.00, length=3, labelsize=font-4)
        rcp['axes.titlepad'] = 10
        
        # set grid
        if grid_major:
            ax.grid(which="major", ls=":", color="black")
        if grid_minor:
            ax.grid(which="minor", ls=":", color="black")

        def curve(intercept, gradient, s, label):
            alpha = np.log10(intercept)
            log_s = np.log10(s)
            log_n = alpha + (gradient * log_s)
            n = 10**log_n
            ax.plot(n, s, linestyle=line_style, label=label)
        
        ##########################################################
        ############    plot the graph
        
        if plot_points:
            ax.scatter(N, S, marker=marker, label="Data")
            rl = None
            for i, is_runout in enumerate(runout):
                if is_runout:
                    # handle any runout points by plotting an arrow from the marker 
                    # pointing to top right
                    # Want these arrows to appear the same regardless of where on the graph they are
                    # And regardless of whether using a log or linear scale
                    start_x, start_y = N[i], S[i]                    
                    len_x = start_x * 0.5
                    if log_y:
                        len_y = start_y * 0.1
                    else:
                        if rl is None:
                            rl = axis_limits[2] * 0.2
                        len_y = rl
                    
                    ax.annotate("", xy=(start_x+len_x, start_y+len_y), xytext=(start_x, start_y), arrowprops=dict(arrowstyle="->"))
                    
        curve_s = np.array([1*np.min(S), 1*np.max(S)])
        if plot_regression:
            curve(results["intercept"], results["slope"], curve_s, label="Regression")

            
        if plot_points_conf:
            # 95%% conf. for given value of S
            raise NotImplementedError
        
        if plot_regression_conf:
            # 95%% conf. for reg. line            
            raise NotImplementedError
        
        if plot_dc_bs540:
            # Plot design curves for BS540, NS3472
            curve(results["dc_bs540_intercept"], results["slope"], curve_s, label="BS540, NS3472")
        
        if plot_dc_ec3:
            # Plot design curves for EC3
            curve(results["dc_ec3_intercept"], results["slope"], curve_s, label="EC3")
        if plot_legend:
            ax.legend(fontsize=font)
        
        
