'''
This is an arbitrary lookup table implemented in old Edna
No-one has been able to offer an explanation for how the values are calculated,
and so the full lookup table is recreated here in full
'''
import numpy as np
lookup_table_ddist = np.zeros(101)
lookup_table_ddist[1] = 10.1
lookup_table_ddist[2] = 4.58
lookup_table_ddist[3] = 3.63
lookup_table_ddist[4] = 3.16
lookup_table_ddist[5] = 2.85
lookup_table_ddist[6] = 2.7
lookup_table_ddist[7] = 2.59
lookup_table_ddist[8] = 2.51
lookup_table_ddist[9] = 2.45
lookup_table_ddist[10] = 2.39
lookup_table_ddist[11] = 2.35
lookup_table_ddist[12] = 2.31
lookup_table_ddist[13] = 2.26
lookup_table_ddist[14] = 2.24
lookup_table_ddist[15] = 2.22
lookup_table_ddist[16] = 2.2
lookup_table_ddist[17] = 2.18
lookup_table_ddist[18] = 2.16
lookup_table_ddist[19] = 2.15
lookup_table_ddist[20] = 2.14
lookup_table_ddist[21] = 2.13
lookup_table_ddist[22] = 2.12
lookup_table_ddist[23] = 2.1
lookup_table_ddist[24] = 2.09
lookup_table_ddist[25] = 2.08
lookup_table_ddist[26] = 2.06
lookup_table_ddist[27] = 2.05
lookup_table_ddist[28] = 2.03
lookup_table_ddist[29] = 2.02
lookup_table_ddist[30] = 2.01
lookup_table_ddist[31] = 2
lookup_table_ddist[32] = 1.99
lookup_table_ddist[33] = 1.99
lookup_table_ddist[34] = 1.99
lookup_table_ddist[35] = 1.98
lookup_table_ddist[35] = 1.98
lookup_table_ddist[36] = 1.98
lookup_table_ddist[37] = 1.98
lookup_table_ddist[38] = 1.97
lookup_table_ddist[39] = 1.97
lookup_table_ddist[40] = 1.96
lookup_table_ddist[41] = 1.96
lookup_table_ddist[42] = 1.95
lookup_table_ddist[43] = 1.95
lookup_table_ddist[44] = 1.94
lookup_table_ddist[45] = 1.94
lookup_table_ddist[46] = 1.93
lookup_table_ddist[47] = 1.93
lookup_table_ddist[48] = 1.93
lookup_table_ddist[49] = 1.93
lookup_table_ddist[50] = 1.93
lookup_table_ddist[51] = 1.92
lookup_table_ddist[52] = 1.92
lookup_table_ddist[53] = 1.92
lookup_table_ddist[54] = 1.91
lookup_table_ddist[55] = 1.91
lookup_table_ddist[56] = 1.91
lookup_table_ddist[57] = 1.91
lookup_table_ddist[58] = 1.91
lookup_table_ddist[59] = 1.91
lookup_table_ddist[60] = 1.9
lookup_table_ddist[61] = 1.9
lookup_table_ddist[62] = 1.9
lookup_table_ddist[63] = 1.9
lookup_table_ddist[64] = 1.9
lookup_table_ddist[65] = 1.89
lookup_table_ddist[66] = 1.89
lookup_table_ddist[67] = 1.89
lookup_table_ddist[68] = 1.89
lookup_table_ddist[69] = 1.89
lookup_table_ddist[70] = 1.88
lookup_table_ddist[71] = 1.88
lookup_table_ddist[72] = 1.88
lookup_table_ddist[73] = 1.88
lookup_table_ddist[74] = 1.88
lookup_table_ddist[75] = 1.87
lookup_table_ddist[76] = 1.87
lookup_table_ddist[77] = 1.87
lookup_table_ddist[78] = 1.87
lookup_table_ddist[79] = 1.87
lookup_table_ddist[80] = 1.87
lookup_table_ddist[81] = 1.86
lookup_table_ddist[82] = 1.86
lookup_table_ddist[83] = 1.86
lookup_table_ddist[84] = 1.86
lookup_table_ddist[85] = 1.86
lookup_table_ddist[86] = 1.86
lookup_table_ddist[87] = 1.86
lookup_table_ddist[88] = 1.85
lookup_table_ddist[89] = 1.85
lookup_table_ddist[90] = 1.85
lookup_table_ddist[91] = 1.85
lookup_table_ddist[92] = 1.85
lookup_table_ddist[93] = 1.85
lookup_table_ddist[94] = 1.85
lookup_table_ddist[95] = 1.85
lookup_table_ddist[96] = 1.85
lookup_table_ddist[97] = 1.85
lookup_table_ddist[98] = 1.84
lookup_table_ddist[99] = 1.84
lookup_table_ddist[100] = 1.84
lookup_table_ddist = lookup_table_ddist[1:]
# This was easier than modifying every single numebr by 1 when duplicating out
# of the original Edna, because VB is 1-indexed, and python is 0-indexed. 
# The end result is an array with a length of 100 (i.e. 0-99)

def ddist(n):
    if n > lookup_table_ddist.size:
        result = 1.8
    else:
        result = lookup_table_ddist[n-1]
    return result