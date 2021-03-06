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
    '''
    A calculation library for vrious materials-engineering calculations, specifically
    relating to stress-cycling.
    
    This library is stand-alone, and can be used at the command-line without
    requirement for the GUI. The GUI is provided for the convenience of less
    experienced users
    
    This library was developed by reverse engineering and source-code analysis 
    of Edna70b, as supplied by Frode Saether to the author. No comprehensive
    specification has been made available, and consequently this library is provided
    SOLELY on a "best-effort" basis. No guarantee is provided for the formal or
    mathematical correctness of this library. By using this library, users
    accept all responsibility for verifying the correctness of outputs, and all
    liability arising from its use
    '''
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
        
        Parameters
        ----------
        file_path : path
            Path to a data file. 
            Format (unless overruled in kwargs):
                2 lines of header
                Comma separated
                column 0 is stress
                column 1 is cycles
                Runouts are denominated with a *
        data_id : int
            ID for the data set. Valid values are 0 or 1. 
        kwargs
            delim: str
                Data delimiter. Default "," (i.e. comma-separated variable)
            runout_marker : str
                Marker used to denote a row as a Runout. Default "*". Use of a
                marker that is a valid character in a floating point number 
                (i.e. -, +, . etc) is not valid
            header : int
                Number of lines of header information. Default 2.
        
        Returns
        -------
        None
        
        Raises
        ------
        ValueError
        '''
        delim = kwargs.get("delimiter", ",")
        runout_marker = kwargs.get("runout", "*")
        header_lines = kwargs.get("header_lines", 2)
        
        if runout_marker in ("-", "+", "=", ".", ","):
            raise ValueError(f"A runout marker of '{runout_marker}' is not"\
                             " valid. Use a character that is not a valid"\
                             " component of a number.")

        data_str = np.genfromtxt(file_path, delimiter=delim, skip_header=header_lines, usecols=(0,1), dtype=str)
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
                    f" PyEdna currently expects {runout_marker}")
        # Now get the header information that Numpy skipped
        with open(file_path) as file:
            header = []
            for i in range(header_lines):
                line_n = file.readline().strip()
                header.append(line_n)
        
        self.data[data_id] = data
        self.runout[data_id] = runout.astype(bool)
        self.header[data_id] = header
        return None



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
        
        Returns
        -------
        results : dict
            Dictionary of results and associated statistics
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
        

        ###########################
        #
        # Provide 3 separate methods for the three cases of Linear Regression
        #   a) 2 DOF (i.e. fit both slope and intercept)
        #   b) 1 DOF (i.e. fit intercept, given a defined slope)
        #   c) 0 DOF (i.e. given defined slope and intercept, calculate how good the fit is)
        # Edna does not implement any situation requiring 1DOF but with a defined intercept
        # 
        
        def linear_2dof():
            '''Implement a linear regression on 2 DOF'''
            def model(x, alpha, beta):
                '''Simple linear model'''
                return alpha + (beta*x)
            dof = 2
            (alpha, beta), cov = scipy.optimize.curve_fit(model, x, y)
            residuals = model(x, alpha, beta) - y
            
            # (section 3.3)
            # Estimate the variance of the observations y_i around the model
            num_points = y.size
            residual_sum_of_squares = np.sum(np.square(residuals))
            total_sum_of_squares = np.sum(np.square(y - np.mean(y)))
            variance = residual_sum_of_squares / (num_points - dof)
            stdev = np.sqrt(variance)
            
            # Section 3.4
            # Confidence intervals for alpha, beta
            r_squared = 1 - ( residual_sum_of_squares / total_sum_of_squares )
            s95_alpha, s95_beta = scipy.stats.norm.ppf(1-self.epsilon, 0, 1)*np.sqrt(np.diag(cov))
            return alpha, beta, num_points, dof, r_squared, stdev, variance, s95_alpha, s95_beta, residual_sum_of_squares


        def linear_1dof(fixed_slope):
            '''Implement a linear regression on 1DOF, where the curve slope is fixed
            In this case, alpha is returned as a 1-element numpy array, so need to extract from it'''
            def model(x, alpha):
                '''Simple linear model'''
                return alpha + (fixed_slope*x)
            dof = 1
            beta = fixed_slope
            alpha, cov = scipy.optimize.curve_fit(model, x, y)
            assert(alpha.size == 1)
            alpha = alpha[0]
            residuals = model(x, alpha) - y
            
            num_points = y.size
            residual_sum_of_squares = np.sum(np.square(residuals))
            total_sum_of_squares = np.sum(np.square(y - np.mean(y)))
            variance = residual_sum_of_squares / (num_points - dof)
            stdev = np.sqrt(variance)
            
            r_squared = 1 - ( residual_sum_of_squares / total_sum_of_squares )
            s95_alpha = scipy.stats.norm.ppf(1-self.epsilon, 0, 1)*np.sqrt(cov)
            s95_beta = 0
            return alpha, beta, num_points, dof, r_squared, stdev, variance, s95_alpha, s95_beta, residual_sum_of_squares

        def linear_0dof(fixed_slope, fixed_intercept):
            '''Implement a placeholder for a linear regression, where there are
            no degrees of freedom. This is NOT a linear regression, but provides
            an equivalent interface for getting the same values out'''
            def model(x):
                return fixed_intercept + (fixed_slope*x)
            dof = 0
            alpha = fixed_intercept
            beta = fixed_slope
            residuals = model(x) - y
            
            num_points = y.size
            residual_sum_of_squares = np.sum(np.square(residuals))
            total_sum_of_squares = np.sum(np.square(y - np.mean(y)))
            variance = residual_sum_of_squares / (num_points - dof)
            stdev = np.sqrt(variance)
            
            r_squared = 1 - ( residual_sum_of_squares / total_sum_of_squares )
            s95_alpha = s95_beta = 0
            return alpha, beta, num_points, dof, r_squared, stdev, variance, s95_alpha, s95_beta, residual_sum_of_squares

        # Perform a simple linear regression to find intercept and gradient
        # using scipy.optimize.curve_fit.
        # Work with any constraints provided by redefining the model to catch the correct number of constraints
        
        if self.user_slope is not None:
            # User has specified a value for the slope, therefore constrain this from changing
            alpha, beta, num_points, dof, r_squared, stdev, variance, s95_alpha, s95_beta, residual_sum_of_squares = linear_1dof(self.user_slope)
        elif computer_slope is not None and computer_intercept is None:
            # Mechanical specified slope parameter, used by self.compare()
            alpha, beta, num_points, dof, r_squared, stdev, variance, s95_alpha, s95_beta, residual_sum_of_squares = linear_1dof(computer_slope)
        elif computer_slope is not None and computer_intercept is not None:
            # Slope and intercept both specified for self.compare()
            alpha, beta, num_points, dof, r_squared, stdev, variance, s95_alpha, s95_beta, residual_sum_of_squares = linear_0dof(computer_slope, computer_intercept)
        elif self.user_thick is not None:
            # The user has specified a thickness of some sort. 
            # No idea what this means or how it influences things
            raise NotImplementedError
        else:
            # No special parameters defined -> DEFAULT CASE
            alpha, beta, num_points, dof, r_squared, stdev, variance, s95_alpha, s95_beta, residual_sum_of_squares = linear_2dof()


        results = {"r_squared": r_squared, "stdev": stdev, "slope": beta,
                   "intercept":10**alpha, "delta_sigma": 10**((alpha - log10_2e6)/-beta),
                   "variance": variance, "points":num_points, "dof": dof, "alpha": alpha,
                   "intercept_conf": s95_alpha, "slope_conf": s95_beta}
        # Delta-sigma is in units [Mpa]
        
        # Also write some information about the input data to the results
        # TODO: Update to account for merged reports. 
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
            r = max(0, temp) # Must be positive. 
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
        
        Parameters
        ----------
        d_id_1 : int
        d_id_2 : int
            Which datasets to compare. Datasets must have already been loaded.
        
        Returns
        -------
        variances_equal : bool
            Is it correct to accept the hypothesis that the variances of the
            two datasets are equal?
        curves_parallel : bool
            Is it correct to accept the hypothesis that the two datasets are
            parallel?
        curves_equal : bool
            Is it correct to accept the hypothesis that the two datasets are
            simultaneously parallel and have consistent variances?
        '''
        # Handle kwargs
        debug = kwargs.get("debug", False)
        
        for idx in [d_id_1, d_id_2]:
            if self.data[idx] is None:
                raise ValueError("Cannot compare two datasets because dataset (%s) are not yet loaded" % idx)
        
        results1 = self.linear_regression(d_id_1, ignore_merge=True)
        results2 = self.linear_regression(d_id_2, ignore_merge=True)
        
        previous_state = self.merge
        self.merge = True
        joint_results = self.linear_regression(-1, ignore_merge=False)
        self.merge = previous_state
        
        # TEST 1: test whether the variances can be assumed different or not
        # Section 3.8.1, page 18
        var1 = results1["variance"]
        var2 = results2["variance"]
        m_dof1 = results1['points'] - results1['dof']
        m_dof2 = results2['points'] - results2['dof']
        
        # Null hypothesis: variances are equal
        # We REJECT the null hypothesis if either statement is True
        # Therefore, we ACCEPT hypothesis if NOT (either statement is True)
        value_1 = var1/var2
        test_1_criteria_1 = scipy.stats.f.isf(self.epsilon/2, m_dof1, m_dof2)
        test_1_criteria_2 = 1/scipy.stats.f.isf(self.epsilon/2, m_dof2, m_dof1)
        variances_equal = not ((value_1 > test_1_criteria_1) or \
                                (value_1 < test_1_criteria_2))
        if debug:
            print(f"======  Hypothesis 0: Variances are Equal (**{variances_equal}**)  ======")
            print(f" Value: {value_1}")
            print(f" test 1 value: {test_1_criteria_1}")
            print(f" test 2 value: {test_1_criteria_2}")
            print(f" Hypothesis ACCEPTED if NOT:")
            print(f" ( (value_1 > test_1 [{value_1 > test_1_criteria_1}]) OR (value_1 < test_2 [{value_1<test_1_criteria_1}]) )")
            print(f" i.e. if both FALSE, then Hypothesis ACCEPTED")
            print("")
            
            
            
        # TEST 2: test whether SN curves are parallel
        # Section 3.8.2, page 20
        # Compare the individual cases to the joint case, i.e. the slope is the same for both 
        RSS = self.Q((results1['intercept'], results2['intercept']), (results1['slope'], results2['slope']))
        RSS_H1 = self.Q((results1['intercept'], results2['intercept']), (joint_results['slope'], joint_results['slope']))
        
        # Null hypothesis (1): curves are parallel
        # We REJECT the null hypothesis (1) if the conditional statement is TRUE
        # Therefore, we ACCEPT the null hypothesis (1) if NOT(statement is True)
        value_2 = ((RSS_H1 - RSS)/RSS) * (m_dof1 + m_dof2)
        test_2_criteria = scipy.stats.f.isf(self.epsilon/2, 1, m_dof1 + m_dof2 -1) 
        curves_parallel = not ( value_2 > test_2_criteria )
        
        if debug:
            print(f"======  Hypothesis 1: Curves are Parallel (**{curves_parallel}**)  ======")
            print(f" Value: {value_2}")
            print(f" test 3 value: {test_2_criteria}")
            print(f" Hypothesis ACCEPTED if NOT (value_2 > test_2_criteria [{value_2 > test_2_criteria}])")
            print(f" i.e. if test is FALSE, then Hypothesis ACCEPTED")
            print("")
        
        
        # Step 3: test whether the two curves are _equal_
        # Section 3.8.4, page 22
        # Note: this is not the same as curves_parallel AND variances_equal, because
        # that does not respect the confidence interval of the combined test.
        # Recalculate the "linear regression" for *2*, where both the *slope* and *intercept* are set equal to *1*
        # This is not actually a linear regression, because there are no free parameters. 
        temp_results = self.linear_regression(d_id_2, computer_slope=results1['slope'], computer_intercept = np.log10(results1['intercept']), ignore_merge=True)
        m_dof2 = results2['points'] - results2['dof']
        RSS_H5 = self.Q((results1['intercept'], temp_results['intercept']), (results1['slope'], temp_results['slope']))
        
        # Null hypothesis (5): slope and intercepts are equal
        # We REJECT the null hypothesis (5) if the conditional statement is True
        # We ACCEPT the null hypothesis (5) if NOT(statement is True)
        value_4 = ((RSS_H5 - RSS)/RSS) * ((m_dof1 + m_dof2)/2)
        test_4_criteria = scipy.stats.f.isf(self.epsilon/2, 2, m_dof1+m_dof2)
        curves_equal = not ( value_4 > test_4_criteria)
        
        if debug:
            print(f"======  Hypothesis 5: Curves are _Coincident_ (**{curves_equal}**)  ======")
            print(f" Value: {value_4}")
            print(f" test 3 value: {test_4_criteria}")
            print(f" Hypothesis ACCEPTED if NOT (value_4 > test_4_criteria [{value_4 > test_4_criteria}])")
            print(f" i.e. if test is FALSE, then Hypothesis ACCEPTED")
            print("")
            
        
        
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
            y = np.log10(self.data[k])[:,1]
            x = np.log10(self.data[k])[:,0]
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
                f"Model Std. Dev:  {stdev:3g}", 
                f"Slope:  {slope:3g}",
                f"Log(10) Intercept:  {np.log10(intercept):3g}",
                f"Stress Range at N=2e6 (MPa):  {ds:3g}",
                "",
                f"Design Curve (BS540)",
                f"Log(10) Intercept: {np.log10(results['dc_bs540_intercept']):3g}",
                f"Stress Range at N=2e6 (MPa): {results['dc_bs540_delta_sigma']:3g}",
                f"Design Curve (EC3)",
                f"log(10) Intercept: {np.log10(results['dc_ec3_intercept']):3g}",
                f"Stress Range at N=2e6 (MPa): {results['dc_ec3_delta_sigma']:3g}",)
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
            ((min n, max n), (min s, max s))  
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
        list
            Actual axis limits, in the form ((x_min, x_max), (y_min, y_max))
        '''
        ##########################################################
        ############    Handle args and kwargs
        
        marker = kwargs.get("marker", "o")
        line_style = kwargs.get("line_style", "-")
        x_axis_limits, y_axis_limits = kwargs.get("axis_limits", (None, None))
        log_y = kwargs.get("axis_style", True)
        grid_major = kwargs.get("grid_major", False)
        grid_minor = kwargs.get("grid_minor", False)
        plot_points = kwargs.get("plot_points", True)
        plot_regression = kwargs.get("plot_regression", True)
        plot_points_conf = kwargs.get("plot_points_conf", False)
        plot_regression_conf = kwargs.get("plot_regression_conf", False)
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
        else:
            ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:6.0f}'))

            
        
        # Set the axis limits, if any:
        if x_axis_limits is not None:
            ax.set_xlim(*x_axis_limits)
        if y_axis_limits is not None:
            ax.set_ylim(*y_axis_limits)
        else:
            ax.set_ylim(10, 1000)
        
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

        def calculate_curve_by_s(intercept, gradient, s):
            '''Calculate N, S values to plot the requested curve'''
            alpha = np.log10(intercept)
            log_s = np.log10(s)
            log_n = alpha + (gradient * log_s)
            n = 10**log_n
            return n, s
        
        def calculate_curve_by_n(intercept, gradient, n):
            alpha = np.log10(intercept)
            log_n = np.log10(n)
            log_s = (log_n - alpha)/gradient
            s = 10**log_s
            return n, s
        
        ##########################################################
        ############    plot the graph
        # Plotting the base points is deliberately done LAST, because that has a dependence on
        # the automatic limits of the plot. 
                    
        #curve_s = np.array([1*np.min(S), 1*np.max(S)])
        #curve_n, _ = calculate_curve_by_s(results["intercept"], results["slope"], curve_s)
        curve_n = np.array([1*np.min(N), 1*np.max(N)])
        _, curve_s = calculate_curve_by_n(results["intercept"], results["slope"], curve_n)
        if plot_regression:
            ax.plot(curve_n, curve_s, linestyle=line_style, label="Regression")

        if plot_points_conf:
            # 95% confidence interval for given value of S
            raise NotImplementedError            
        
        if plot_regression_conf:
            # 95%% conf. for given value of S
            # Modify the intercept argument given to curve()
            # Second curve is not labelled to avoid duplicating labels in legend
            label = f"{results['confidence_interval']*100:n}% for regression"
            n1, s1 = calculate_curve_by_n(results["c_upper"], results["slope"], curve_n)
            n2, s2 = calculate_curve_by_n(results["c_lower"], results["slope"], curve_n)
            ax.plot(n1, s1, linestyle="--", label=label, color="C4")
            ax.plot(n2, s2, linestyle="--", color="C4")
        
        if plot_dc_bs540:
            # Plot design curves for BS540, NS3472
            n, s = calculate_curve_by_n(results["dc_bs540_intercept"], results["slope"], curve_n)
            ax.plot(n, s, linestyle=line_style, label="BS540, NS3472")
        
        if plot_dc_ec3:
            # Plot design curves for EC3
            n, s = calculate_curve_by_n(results["dc_ec3_intercept"], results["slope"], curve_n)
            ax.plot(n, s, linestyle=line_style, label="EC3")
            
        if plot_points:
            # Main data points
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
                            rl = ax.get_ylim()[0] * 0.2
                        len_y = rl
                    ax.annotate("", xy=(start_x+len_x, start_y+len_y), xytext=(start_x, start_y), arrowprops=dict(arrowstyle="->"))
            
        if plot_legend:
            ax.legend(fontsize=font)
        
        # For display of the automatic axis limit values:
        # After drawing all relevant lines, get the limits, 
        # and return them to the calling program (probably GraphPlotter)
        actual_limits = *ax.get_xlim(), *ax.get_ylim()
        return actual_limits