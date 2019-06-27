import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import LogFormatter
from matplotlib import rcParams as rcp
import scipy.optimize
import scipy.stats

class EdnaCalc:
    def __init__(self, parent=None):
        self.parent = parent
        self.data = [None, None]
        self.runout = [None, None]
        self.user_slope = None      # text3
        self.user_thick = None      # text5, ref. thick
        self.user_confidence = None # text8
        # Constants for later comparison
        self.ymin = 1e-10
        self.ymax = 1e10
        
        
    def read_data_file(self, file_path, d_id, **kwargs):
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
        

        if runout_marker in ("*", "^"):
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
                raise ValueError("A negative number was detected. Please check that you have set the correct runout indicator. PyEdna currently expects '*' or '^'")
        else:
            raise NotImplementedError("Currently, the only supported runout \
              indicators are ('^', '*'). You requested runout indicator\
              '%s'" % runout)
        
        self.data[d_id] = data
        self.runout[d_id] = runout


        
    def linear_regression(self, data_id, **kwargs):
        '''Perform a Stress / Lifetime analysis based on a log-normal model.
        
        # TODO: Account for the user entering a defined slope, and decide on appropriate scope (method or class)
        # TODO: Account for runouts
        # TODO: Account for calculating with epsilon properly
        
        Analysis is based on a SINTEF report:
            Statstical ANalysis of Fatigue test data
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
        
        Parameters
        ----------
        data_id : int
            Which data set to perform a linear regression on
        '''
        # Handle kwargs
        debug = kwargs.get("debug", False)
        user_slope = kwargs.get("user_slope", None)
        epsilon = kwargs.get("epsilon", 0.05)
        
        # Test that the requested data_id exists:
        if self.data[data_id] is None:
            raise ValueError("A dataset matching id '%d' has not yet been loaded" % data_id)
        
        
        # Define useful constants
        # Don't know *why* they're useful right now, but they are used repeatedly throughout Edna's code
        edna_value = 6.30103
        
        # Extract data
        S = self.data[data_id][:, 0] # Stress
        N = self.data[data_id][:, 1] # Lifetime
        
        # Make a substitution to match a simple linear model
        # In this substitution, we want to find alpha = log10(intercept)
        # and beta = gradient
        x = np.log10(S)
        y = np.log10(N)
        def model(x, alpha, beta):
            return alpha + (beta*x)
        
        # TODO! The model is only valid for non-runout, so filter those out first
        
        # Perform a simple linear regression to find intercept and gradient
        # using scipy.optimize.curve_fit.
        initial_guess = [1, 1]
        params, cov = scipy.optimize.curve_fit(model, x, y, initial_guess)
        # params: [alpha, beta], the values which minimise least-squares
        # cov: covariance matrix, the variance of [params] is the diagonal
        # np.diag(cov)
        
        # (section 3.3)
        # Estimate the variance of the observations y_i around the model
        residuals = model(x, *params) - y
        num_points = y.size
        dof = len(params)
        residual_sum_of_squares = np.sum(np.square(residuals))
        total_sum_of_squares = np.sum(np.square(y - np.mean(y)))
        variance = residual_sum_of_squares / (num_points - dof)
        stdev = np.sqrt(variance)
        
        r_squared = 1 - ( residual_sum_of_squares / total_sum_of_squares )
        
        # Section 3.4
        # Confidence intervals for alpha, beta
        alpha, beta = params
        sigma_alpha, sigma_beta = np.sqrt(np.diag(cov))
        s95_alpha, s95_beta = 2*np.sqrt(np.diag(cov))
        # Two standard deviations is (approximately) the 95% boundary (actually 95.45%)
        # TODO - section 3.4 uses a student-t distribution, does scipy?
        # TODO: convert from sigma-based to percentile based
        
        results = {"r_squared": r_squared, "stdev":stdev, "slope": beta,
                   "intercept":10**alpha, "delta_sigma": 10**((alpha - edna_value)/-beta),
                   "variance":variance, "points":num_points, "dof":dof}
        # It's unclear what this delta_sigma represents, but Edna calculates it
        
        
        #Test code
        if debug:
            print("Quick results")
            print("Goodness of fit: %.4f" % r_squared)
            print("Stdev: %.4f" % np.sqrt(variance))
            print("Slope b: %.4f" % (beta))
            print("Intercept c: %.4f" % (10**alpha))
            print("Delta Sigma (2e6): %.4f" % 10**((alpha - edna_value)/-beta))
        
        return results
    
        
    def Q(self, alpha, beta):
        '''Equation 3.32 in Rausand 1981'''
        val = 0
        for k in range(2):
            y = np.log10(self.data[k])[:,0]
            x = np.log10(self.data[k])[:,1]
            val += np.sum(np.square(y - alpha[k] - (beta[k]*x)))
        return val
    def compare(self, d_id_1, d_id_2, **kwargs):
        '''
        Compare two different data sets for compatibility, to give a yes/no 
        answer to whether they can be merged
        
        # TODO: Validate that the various statistical tests are implemented correctly. 
        
        '''
        # Handle kwargs
        debug = kwargs.get("debug", False)
        
        for idx in [d_id_1, d_id_2]:
            if self.data[idx] is None:
                raise ValueError("Cannot compare two datasets because dataset (%s) are not yet loaded" % idx)
        
        results1 = self.linear_regression(d_id_1)
        results2 = self.linear_regression(d_id_2)
        
        # Step 1: test whether the variances can be assumed different or not
        var1 = results1["variance"]
        var2 = results2["variance"]
        m_dof1 = results1['points'] - results1['dof']
        m_dof2 = results2['points'] - results2['dof']
        
        variances_different = var1/var2 < 1 / scipy.stats.f.isf(0.05/2, m_dof1, m_dof2)
        
        # Step 2: test whether SN curves are parallel
        
    
        
        RSS_H1 = self.Q((results1['intercept'], results2['intercept']), (results1['slope'], results2['slope']))
        RSS = self.Q((results1['intercept'], results2['intercept']), (results1['slope'], results1['slope'])) # note, slope2=slope1
        curves_parallel = ((RSS_H1 - RSS)/RSS) * (m_dof1 + m_dof2) > scipy.stats.f.isf(0.05, 1, m_dof1 + m_dof2)
        
        if debug:
            print(variances_different)
            print(curves_parallel)
        # TODO!
        
        
    def format_analysis(self, d_id, **kwargs):
        results = self.linear_regression(d_id, **kwargs)
        rsq = results["r_squared"]
        stdev = results["stdev"]
        slope = results["slope"]
        intercept = results["intercept"]
        ds = results["delta_sigma"]
        outstr = (f"R squared:  {rsq:3g}",
                f"Std. Dev:  {stdev:3g}", 
                f"Slope:  {slope:3g}",
                f"Intercept:  {intercept:3g}",
                f"Delta Sigma (2e6):  {ds:3g}")
        return outstr
    
    def plot_results(self, d_id, **kwargs):
        results = self.linear_regression(d_id)
        N = self.data[d_id][:,0]
        S = self.data[d_id][:,1]
        
        fig, ax = plt.subplots(figsize=(12,9))
        
        ax.set_xlim(1e2, 1e7)
        ax.set_ylim(1e1, 1e3)
        ax.set_yscale('log')
        ax.set_xscale('log')
        ax.set_xlabel('Number of cycles')
        ax.set_ylabel('Load')
        ax.set_title('Fatigue Lifecycle')
        ax.yaxis.label.set_fontsize(25)
        ax.xaxis.label.set_fontsize(25)
        ax.title.set_fontsize(35)
        rcp['axes.titlepad'] = 10
        ax.tick_params(which='major', width=0.00, length=25, labelsize=25)
        ax.tick_params(which='major', pad=0, axis="y", width=0.00, length=5, labelsize=18)
        ax.tick_params(which='minor', pad=5, direction="in", width=1.00, length=5, labelsize=12)
        ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:6.0f}'))
        ax.yaxis.set_minor_formatter(ticker.StrMethodFormatter('{x:6.0f}'))
        ax.xaxis.set_minor_formatter(ticker.FuncFormatter(lambda x, pos: '%s' % (str(x)[0] if int(str(x)[0]) < 6 else '')))
        ax.grid(True, which="minor",ls=":")
        ax.grid(True, which="major", axis="x", ls="-", color="black")
        
        ax.scatter(S, N, marker="x", color="black")
        
        plt.show()
        
        
if __name__ == '__main__':
    filepath1 = r"C:\Users\simoba\Documents\_work\NTNUIT\2019-03-29 - Edna\Round 2\Files from Frode\Test Data\test1.sn"
    filepath2 = r"C:\Users\simoba\Documents\_work\NTNUIT\2019-03-29 - Edna\Round 2\Files from Frode\Test Data\test1.sn"
    import ednalib as edna
    ec = EdnaCalc()
    ec.read_data_file(filepath1, 0, runout='*',debug=True)
    ec.read_data_file(filepath2, 1, runout='*',debug=True)
    print(ec.format_analysis(0))
    ec.plot_results(0)
    
#    # Cardinal
#    print("\n---- Cardinal----\n")
#    sn1 = np.genfromtxt( filepath1, delimiter=',', skip_header=2)
#    (Slog, Nlog, tkk) = edna.datainn(sn1, 0, 0, 0 )
#    print(tkk)
#    npkt = len(Slog)
#    foo = edna.analysis1(Slog, Nlog, tkk, npkt)
#    print(foo)