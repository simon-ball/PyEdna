# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 14:34:06 2019

@author: simoba
"""
from mailmerge import MailMerge # installed as "docx-mailmerge"
from pathlib import Path
import locale








def format_report(report_filename, data, runout, results, *args, **kwargs):
    ''' Format the results of a linear regression analysis into a prepared
    template
    
    Use docx-mailmerge to fill merge fields in the provided Microsoft Wod 2019
    file    
    
    parameters
    ----------
    filename : path-like
        The path to save the completed report to
    data : np.ndarray
        2D array of input data on which the regression was performed
        Shaped as data[0] = a row, data[:,0] is S, data[:,1] is N
    runout : np.ndarray
        1D array of runout status, True where that row was a runout
    results : dict
        Output from ednacalc.linear_regression(), the variable names are reused here
    kwargs
        locale : str
            Localisation string for number formatting. 
            Defaults to "en_GB": 
                decimal point is "."
                thousand separator is ","
            
                    
                
    
        
    Returns
    -------
    None
        
    see also
    --------
    https://pbpython.com/python-word-template.html
        Discussion of using docx-mailmerge with merge fields in Word
    '''
    template_location = Path(__file__).parent
    template = template_location / "template_report.docx"
    
    # Set localisation for number formatting
    location = kwargs.get("locale", "en_GB")
    locale.setlocale(locale.LC_ALL, location)
    
    to_write = {}
    ######### Data file header information
    to_write["header_1"] = results["header_1"]
    to_write["header_2"] = results["header_2"]
    
    ######## Input table
    # data is a 2xn Numpy array, where data[0] is [S, N], while all S is data[:,0]
    # Merging into a table is handled slightly differently to single fields
    # For this, we pass a list of dictionaries, and assign it to the first merge field in the table
    data_table = []
    for i, [S, N] in enumerate(data):
        r = int(runout[i])
        row = {"data_stress": f"{S:n}", "data_number": f"{r*'**'}{N:n}{r*'**'}"}
        data_table.append(row)
    
    ######## Output mean curve
    to_write["slope"] =             f"{-1*results['slope']:.4n}"
    to_write["intercept"] =         f"{results['intercept']:.4n}"
    to_write["log_intercept"] =     f"{results['alpha']:.4n}"
    to_write["delta_sigma"] =       f"{results['delta_sigma']:.4n}"
    to_write["stdev"] =             f"{results['stdev']:.4n}"
    to_write['mean_stress'] =       f"{results['mean_stress']:.4n}"
    to_write["r_squared"] =         f"{results['r_squared']:.4n}"
    to_write["confidence_regression"] = f"{results['regression_confidence']:.4n}"
    to_write["confidence_given_s"] =f"{results['confidence_given_s']:.4n}"
    to_write["confidence_b"] = f"{results['confidence_b']:.4n}"
    to_write["confidence_c"] = f"{results['confidence_c']:.4n}"
    to_write["s_lower"] = f"{results['s_lower']:.4n}"
    to_write["s_upper"] = f"{results['s_upper']:.4n}"
    to_write["c_lower"] = f"{results['c_lower']:.4n}"
    to_write["c_upper"] = f"{results['c_upper']:.4n}"
    
    # Confidence interval used
    to_write["epsilon"] = "{}".format(int(100*results["confidence_interval"]))
    
    # Output: Design curve
    to_write["dc_bs540_intercept"] =    f"{results['dc_bs540_intercept']:.4n}"
    to_write["dc_bs540_delta_sigma"] =  f"{results['dc_bs540_delta_sigma']:.4n}"
    to_write["dc_ec3_intercept"] =      f"{results['dc_ec3_intercept']:.4n}"
    to_write["dc_ec3_delta_sigma"] =    f"{results['dc_ec3_delta_sigma']:.4n}"
#    
    with MailMerge(template) as document:
#        fields = document.get_merge_fields()
#        for key in fields:
#            if key not in to_write.keys():
#                to_write[key] = "TODO"
        document.merge(**to_write)
        document.merge_rows("data_stress", data_table)
        document.write(report_filename)
        document.close()
    
if __name__ == "__main__":
    template = "template_report.docx"
    with MailMerge(template) as document:
        print(document.get_merge_fields())
