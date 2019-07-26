# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 14:34:06 2019

@author: simoba
"""

from mailmerge import MailMerge # installed as "docx-mailmerge"






def format_report(report_filename, results, other, **kwargs):
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
    template = "template_report.docx"
    
    
    to_write = {}
    # Data file header information
    to_write["header_1"] = other["header_1"]
    to_write["header_2"] = other["header_2"]
    
    #Input table
    # TODO
    
    # Output mean curve
    to_write = {**to_write, **results}
    to_write['mean_stress'] = other['mean_stress']
    to_write["confidence_regression"]
    to_write["confidence_given"]
    to_write["confidence_b"]
    to_write["confidence_c"]
    to_write["s_lower"]
    to_write["s_lupper"]
    to_write["c_lower"]
    to_write["c_lupper"]
    
    # Output: Design curve
    to_write["d_intercept_bs540"]
    to_write["d_delta2e6_bs540"]
    to_write["d_intercept_ec3"]
    to_write["d_delta2e6_ec3"]
    
    document = MailMerge(template)
    document.merge(**to_write)
    document.write(report_filename)
    document.close()
    
if __name__ == "__main__":
    template = "template_report.docx"
    with MailMerge(template) as document:
        print(document.get_merge_fields())