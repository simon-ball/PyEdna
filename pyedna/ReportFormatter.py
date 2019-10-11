# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 14:34:06 2019

@author: simoba
"""
from mailmerge import MailMerge # installed as "docx-mailmerge"
from pathlib import Path






def format_report(report_filename, results, *args, **kwargs):
    ''' Format the results of a linear regression analysis into a prepared
    template
    
    Use docx-mailmerge to fill merge fields in the provided Microsoft Wod 2019
    file    
    
    parameters
    ----------
    filename : path-like
        The path to save the completed report to
    results : dict
        Output from ednacalc.linear_regression(), the variable names are reused here
    other: dict
        Other values required for the report
        TODO: Mostly still TBD
        
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
    
    
    to_write = {}
    ######### Data file header information
    to_write["header_1"] = results["header_1"]
    to_write["header_2"] = results["header_2"]
    
    ######## Input table
    # TODO
    
    ######## Output mean curve
    to_write["slope"] =             f"{results['slope']:3g}"
    to_write["intercept"] =         f"{results['intercept']:3g}"
    to_write["log_intercept"] =     f"{results['alpha']:3g}"
    to_write["delta_sigma"] =       f"{results['delta_sigma']:3g}"
    to_write["stdev"] =             f"{results['stdev']:3g}"
    to_write['mean_stress'] =       f"{results['mean_stress']:3g}"
    to_write["r_squared"] =         f"{results['r_squared']:3g}"
    to_write["confidence_regression"] = f"{results['regression_confidence']:3g}"
    to_write["confidence_given_s"] =f"{results['confidence_given_s']:3g}"
    to_write["confidence_b"] = f"{results['confidence_b']:3g}"
    to_write["confidence_c"] = f"{results['confidence_c']:3g}"
    to_write["s_lower"] = f"{results['s_lower']:3g}"
    to_write["s_upper"] = f"{results['s_upper']:3g}"
    to_write["c_lower"] = f"{results['c_lower']:3g}"
    to_write["c_upper"] = f"{results['c_upper']:3g}"
    
    # Confidence interval used
    to_write["epsilon"] = "{}".format(int(100*results["confidence_interval"]))
    
    # Output: Design curve
    to_write["dc_bs540_intercept"] =    f"{results['dc_bs540_intercept']:3g}"
    to_write["dc_bs540_delta_sigma"] =  f"{results['dc_bs540_delta_sigma']:3g}"
    to_write["dc_ec3_intercept"] =      f"{results['dc_ec3_intercept']:3g}"
    to_write["dc_ec3_delta_sigma"] =    f"{results['dc_ec3_delta_sigma']:3g}"
#    
    with MailMerge(template) as document:
        fields = document.get_merge_fields()
        for key in fields:
            if key not in to_write.keys():
                to_write[key] = "TODO"
        document.merge(**to_write)
        document.write(report_filename)
        document.close()
    
if __name__ == "__main__":
    template = "template_report.docx"
    with MailMerge(template) as document:
        print(document.get_merge_fields())
