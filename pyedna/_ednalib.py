from math import log10, inf, sqrt
from IPython.core.display import display, HTML

import numpy
import scipy.stats

from ednaconf import *

rtab = [ 12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306, 2.262, 2.228,
          2.201, 2.179, 2.16,  2.145, 2.131, 2.12,  2.11,  2.101, 2.093, 2.086,
          2.08,  2.074, 2.069, 2.064, 2.06,  2.056, 2.052, 2.048, 2.045, 2.042, 2.021 ]

#RT90 = [  6.31,  2.92,  2.35,  2.13,  2.02,  1.94,  1.89,  1.86,  1.83,  1.81,
#          1.8,   1.78,  1.77,  1.76,  1.75,  1.75,  1.74,  1.73,  1.73,  1.72,
#          1.72,  1.72,  1.71,  1.71,  1.71,  1.71,  1.7,   1.7,   1.7,   1.7,   1.68 ]
#
#RT80 = [  1.08,  1.89,  1.64,  1.53,  1.48,  1.44,  1.41,  1.4,   1.38,  1.37, 
#          1.36,  1.36,  1.35,  1.35,  1.34,  1.34,  1.33,  1.33,  1.33,  1.33,
#          1.32,  1.32,  1.32,  1.32,  1.32,  1.31,  1.31,  1.31,  1.31,  1.31,  1.3 ]


ddist = [ 10.1, 4.58, 3.63, 3.16, 2.85, 2.7,  2.59, 2.51, 2.45, 2.39,
         2.35, 2.31, 2.26, 2.24, 2.22, 2.2,  2.18, 2.16, 2.15, 2.14,
         2.13, 2.12, 2.1,  2.09, 2.08, 2.06, 2.05, 2.03, 2.02, 2.01,
         2.00, 1.99, 1.99, 1.99, 1.98, 1.98, 1.98, 1.97, 1.97, 1.96,
         1.96, 1.95, 1.95, 1.94, 1.94, 1.93, 1.93, 1.93, 1.93, 1.93,
         1.92, 1.92, 1.92, 1.91, 1.91, 1.91, 1.91, 1.91, 1.91, 1.9,
         1.9,  1.9,  1.9,  1.9,  1.89, 1.89, 1.89, 1.89, 1.89, 1.88,
         1.88, 1.88, 1.88, 1.88, 1.87, 1.87, 1.87, 1.87, 1.87, 1.87,
         1.86, 1.86, 1.86, 1.86, 1.86, 1.86, 1.86, 1.85, 1.85, 1.85,
         1.85, 1.85, 1.85, 1.85, 1.85, 1.85, 1.85, 1.84, 1.84, 1.84 ]
         
def Alog(verdi):
    return log10(verdi)
    
def analysis1(Slog, Nlog, tkk, npkt):
#   init()
    global B 
    global C 
    global des3
    global xmax 
    global xmin 
    global r 
    global s2 
#    global s9Xs
    global s9x
    global pre
#   s95 = 0
    outstr = ''
    tknavn = "<<tknavn>>"
    vbCrLf = "\n"
    textx = "<<textx>>"
    
    #        stati(B, C, xmax, xmin, r, S2, s9x, pre, npkt, s95)
    (B, C, xmax, xmin, r, S2, s9x, pre, s95) = stati(Slog, Nlog, tkk, npkt) 
    # input: npkt (Slog, Nlog, tkk)
    #output: B C r S2 s95 s9x, pre
    
    if join:
        outstr = tknavn + vbCrLf
        outstr = outstr + textx + vbCrLf
        if r == 100:
            #Spør: her må noe være mulig å fjerne? 
            outstr = outstr + "Goodnes of Fit:  " + ("%f.3" % (r**2)) + vbCrLf
        else:
            outstr = outstr + "Goodnes of Fit:  " + ("%f.3" % (r**2)) + vbCrLf
        #End If
        f95d = 2 * f95
        pred = 2 * pre
        #           Dim s2e6 As String
        s2e6 = ("%.4f" %(10 ** ((C - 6.30103) / -B))) 
        outstr = outstr + "Standard Deviation: " + ("%.3f" % (s * 1)) + vbCrLf
        outstr = outstr + "Slope b:  " + ("%.3f" % (B * 1)) + vbCrLf
        outstr = outstr + "Intercept C: " + ("%.2f" % (10 ** C)) + vbCrLf
        outstr = outstr + "Delta Sigma(2E6):  " + s2e6 + vbCrLf
        outstr = outstr + vbCrLf + "Design curve:" + vbCrLf
        outstr = outstr + "Intercept C: " + ("%.2f" % (10 ** (C - s95 * sqrt(npkt + 1))))
        outstr = outstr + vbCrLf
        outstr = outstr + "Delta Sigma(2E6):  " + ("%.4f" % (10 ** ((C - 6.30103 - s95 * sqrt(npkt + 1)) / -B))) + vbCrLf
        outstr = outstr + "Intercept C: " + ("%.2f" % (10 ** (C - des3)))
        outstr = outstr + vbCrLf
        outstr = outstr + "Delta Sigma(2E6):  " + ("%.4f" % (10 ** ((C - 6.30103 - des3) / -B))) + vbCrLf
        outstr = outstr + sntdat
         
        #End If
    return outstr
#End Sub
         
def datainn( tkfil, disp, disp2, disp3 ):
    Slog = [] ;
    Nlog = [] ;
    tkk = [] ;
    tykk = 0 
    for i in tkfil:
        if numpy.isnan(i[1]):
            tykk = i[0]
            print('tykkelsen er', tykk)
        else:
            Slog.append(i[0])
            Nlog.append(i[1])
            tkk.append(tykk)
    return( Slog, Nlog, tkk )
         
         
         #def stati(bs, Cs, xmaxs, xmins, r, S2s, s9Xs, pres, nant, s95s):
def stati(Slog, Nlog, tkk, nant):
         
#    Static npk2 As Integer, npk1  As Integer, npkt3 As Integer
#    Dim sn As Double
    global text3
    global des3
#    global text8
#    global f95
    global s
    global d1, d0
    global YMID
    global f9x
    ant = nant
    sumx = 0
    sumy = 0
    sumx2 = 0
    sumy2 = 0
    sumxy = 0
    ST = 0
    ST2 = 0
    SST = 0
    SNT = 0
    SS = 0
    sn = 0
    SSN = 0
    SS2 = 0
    SN2 = 0
    pkt = 0
    ymin = inf
    ymax = -inf
    # Spør om det er greit å bruke inf her i stedet for 10 mrd? 
    Q = 0
    
    #    val_text5 = str2val(Text5)
    
    for i in range(0,nant):
        XLO = Alog(Nlog[i + j])
        YLO = Alog(Slog[i + j])
        # spør: hvor kommer variabelen j fra? 
        sumx = sumx + XLO
        sumy = sumy + YLO
        sumx2 = sumx2 + XLO * XLO
        sumy2 = sumy2 + YLO * YLO
        sumxy = sumxy + YLO * XLO
        print(sumxy)
        if text5 != 0 and tkk[i] != 0:
            SS = SS + YLO
            sn = sn + XLO
            SSN = SSN + YLO * XLO
            SS2 = SS2 + YLO * YLO
            SN2 = SN2 + XLO * XLO
            pkt = pkt + 1
            t = Alog(tkk[i] / text5)
            if tkk[i] == text5:
                t = 0
                
            ST = ST + t
            ST2 = ST2 + t * t
            SST = SST + YLO * t
            SNT = SNT + XLO * t
        print(SS)
        #       finner st�rste og minste verdier av lg(x) og lg(y) i datasett n
        if YLO < ymin:
            ymin = YLO
        if YLO > ymax:
            ymax = YLO
    ##   Next i
         
    if text5 != 0 and tkk[0] != 0:
        sntreg(sn, SSN, SN2, SST, ST2, SS2, SS, SNT, ST, pkt)
    # End If
    XMID = sumx / ant
    YMID = sumy / ant
         
    #       b er m og C er lgC
         
    Valhel = False
    # Spør: dette må sjekkes
    if text3 != 0:
        if text3 > 0 :
            text3 = -text3
        bs = text3  
        #    if Text3.text != "":
        #    for i in range(1,Len(Text3.text))
        #     If Mid(Text3.text, i, 1) = "," Then
        #      Text3.text = Left(Text3, i - 1) & "." & Right(Text3, (Len(Text3) - i))
        #     End If
        #     Next i
        #     If Val(Text3.text) > 0 Then Text3.text = "-" & Text3.text
        #     bs = Val(Text3.text)    
        Valhel = True
    else:
        bs = (sumxy * ant - sumx * sumy) / (sumy2 * ant - sumy * sumy)
    #End If
         
    Cs = XMID - bs * YMID
    xmins = bs * ymax + Cs
    xmaxs = bs * ymin + Cs
    if nant >= 3:
        sumxx = 0
        sumyy = 0
        rss = 0
        for i in range(0,nant):
            XLO = Alog(Nlog[i + j])
            YLO = Alog(Slog[i + j])
            sumxx = (XLO - XMID) * (XLO - XMID) + sumxx
            sumyy = (YLO - YMID) * (YLO - YMID) + sumyy
            rss = (XLO - bs * YLO - Cs) * (XLO - bs * YLO - Cs) + rss
        #Next i
    #End If
         
    #finner variansen s2
    if Valhel:
        S2s = rss / (ant - 1)
        if 1 - rss / sumxx < 0:
            r = 0
        else:
            r = sqrt(1 - rss / sumxx)
        #End If
    elif ant > 2:
        S2s = rss / (ant - 2)
        if ant * sumy2 - sumy * sumy >= 0:
            r = (ant * sumxy - sumx * sumy) / sqrt((ant * sumy2 - sumy * sumy) * (ant * sumx2 - sumx * sumx))
        else:
            r = 0 #for sikkerhetsskyld Spør om det heller skal være 1
        #End If
    else:
        S2s = 0
        r = 1
    #End If
         
    s = sqrt(S2s)
    YM = ymax
    conf = text8
    cop = (100 - text8) / 100
    npk2 = nant - 2
    npk1 = nant - 1

    # NB: Excel's TINV uses a two-sided tail probability, thus div-by-2
    #    rp = Excel.WorksheetFunction.TInv(0.05, npk2)
    rp = scipy.stats.t.isf(0.05/2, npk2)
         
    #    rp1 = Excel.WorksheetFunction.TInv(0.05, npk1)
    #rp2 = scipy.stats.t.ppf(cop, npk2)
    rp1 = scipy.stats.t.isf(0.05/2, npk1)
    #    rp1 = Excel.WorksheetFunction.TInv(0.05, npk1)
    #rp2 = scipy.stats.t.ppf(cop, npk2)
    rp2 = scipy.stats.t.isf(cop/2, npk2)
    #   rf = Excel.WorksheetFunction.FInv(0.05, 2, npk2)
    rf = scipy.stats.f.isf(0.05, 2, npk2)    
    #    rf1 = Excel.WorksheetFunction.FInv(0.05, 1, npk1)
    rf1 = scipy.stats.f.isf(0.05, 1, npk1)
    
    s95s = rp * s / sqrt(nant)
    s9Xs = rp2 * s / sqrt(nant)
    pres = s9Xs * sqrt(nant + 2)
    if npk2 > 100:
        des3 = s * 1.8
    else:
        des3 = s * ddist[npk2-1]
    #End If
    if Valhel:
        d1 = 0
        d0 = 2 * s * sqrt(2 * rf1 / nant)
        f95 = s * rp1 * sqrt(1 / nant)
        pred = 2 * pres / rp * rp1
    elif ant > 2:
        pred = 2 * pres
        f95 = s * sqrt(2 * rf / nant)
        
        d1 = 2 * s * sqrt(2 * rf / sumyy)
        d0 = 2 * f95
         
         
    else:
        d1 = 0
        d0 = 0
        f95 = 0
        pred = 0
        xlo1 = Alog(Nlog[0])
        ylo1 = Alog(Slog[0])
        xlo2 = Alog(Nlog[1])
        ylo2 = Alog(Slog[1])
        bs = (xlo2 - xlo1) / (ylo2 - ylo1)
        Cs = XMID - bs * YMID
    #End If
    return (bs, Cs, xmaxs, xmins, r, S2s, s9Xs, pres, s95s) 
#End Sub
         
         


def format2(tall, typ ):
#Dim Tekst As String, tp As String, Form As String
    if typ == 1:
        Form = ("%6.2f" % (tall))
    if typ == 2:
        Form = ("%.3e" % (tall))
    if typ == 3:
        Form = ("%5.3f" % (tall))
    if typ == 4:
        Form = ("%5.1f" % (tall))
    return Form 
#End Function



#Private Sub lagre3(B, C, xmax, xmin, r, S2, s95, pre, s9x)
#def lagre3(B, C, xmax, xmin, r, S2, s95, pre, s9x):
def lagre3(filname,npkt, Slog, Nlog):
    global B
    global C
    global xmax
    global xmin
    global r
    global S2
    global bt
    global s95
    global pre
    global f9x
    global YMID
    global s9x
    global Text8
    global text5
    global d1, d0
    global bt, sbt, vtk, stk, ctex, sct, sdev
##    f9x = 0 ## Spør hva er denne, var udefinert
    vbCrLf = "\n"
    taba = "\t"
    textx = "<<textx>>" ; 
    
# Dim taba As String
# taba = Chr(9)
#    filname = "analysis-report.rtf"
# CommonDialog1.InitDir = CurDir
# CommonDialog1.Filter = "Result Files (*.rtf)|*.rtf"
# ' Specify default filter
# CommonDialog1.FilterIndex = 2
# ' display the File Open dialog
# CommonDialog1.ShowSave
# filname = CommonDialog1.filename
# If filname <> "" Then
# If Right(filname, 3) <> "rtf" Then filname = filename & ".rtf"
# TODO: fikse dette med filtype. 
#     RTB1.TextRTF = ""
    display(HTML("<h3>Statistical Analysis of Fatigue data.</h3>"))


    RTB1_text = ""
    tabb = "&nbsp; &nbsp; &nbsp; " 

#    display(HTML("Data set ID: " + textx + "\nFirst line " + tekst2 + "\nSecond line " + tekst2))
    
    RTB1_text = RTB1_text + vbCrLf + "Data set ID: " + taba + textx + vbCrLf
    RTB1_text = RTB1_text + "             " + taba + tekst2 + vbCrLf + vbCrLf
    RTB1_text = RTB1_text + "Estimates of Coefficients b and C in S/N-Curve N*S^b=C" + vbCrLf
    RTB1_text = RTB1_text + "Regression Model: log(N)=log(C)-b*log(S)" + vbCrLf
    RTB1_text = RTB1_text + "Input:" + vbCrLf
    
    RTB1_text = RTB1_text + "  Stress Range     Number of Cycles" + vbCrLf
 
    for i in range(0, npkt):
        RTB1_text = RTB1_text + taba + ("%.0f" % (Slog[i])) + taba + taba + ("%.0f" % (Nlog[i])) + vbCrLf
        #Next i
#    for i in range(0, ii):
#        RTB1_text = RTB1_text + taba + Srun[i] + taba + taba + Nrun[i] + taba + "Run out" + vbCrLf
#        #Next i
#    for i in range(0,iii):
#        RTB1_text = RTB1_text + taba + Spun[i] + taba + taba + Npun[i] + taba + "Rotfeil" + vbCrLf
#        #Next i
      
    RTB1_text = RTB1_text + vbCrLf + "Output:" + vbCrLf
    display(HTML("<p>Mean SN Curve.  (( $\SI{2.34e-30}$ <br>"))
    RTB1_text = RTB1_text + vbCrLf + "Mean SN Curve." + vbCrLf

    display(HTML(tabb + "$NS^{"+format2(-B,1)+"}="+format2(10**C,2) + "$;     $log(C) = "+format2(C*1,3)+"$<br>\n" )) 
    
    RTB1_text = RTB1_text + "N*S^"
    RTB1_text = RTB1_text + format2(-B, 1) + "=" + format2(10 ** C, 2)
    RTB1_text = RTB1_text + "   log(C) = " + format2(C * 1, 3) + vbCrLf
    
    g2e7 = 10 ** ((C - 6.30103) / -B)
    display(HTML(tabb + "Stress range at $2*10^6$ cycles: " + format2(10 ** ((C - 6.30103) / -B), 4) + " MPa<br>"))
    RTB1_text = RTB1_text + "Stress range at 2E6 cycles :        " + format2(10 ** ((C - 6.30103) / -B), 4) + " MPa" + vbCrLf
    RTB1_text = RTB1_text + "Standard Deviation Sigma from Input data: " + format2(s * 1, 3) + vbCrLf
    RTB1_text = RTB1_text + "Mean Stress : " + format2(10 ** YMID, 4) + " MPa" + vbCrLf
    RTB1_text = RTB1_text + "Goodnes of Fit  r^2 :   " + format2(r ** 2, 3) + vbCrLf
    print(RTB1_text)

    ##'RTB1.Font.Underline = False

    f95d = 2 * f9x
    pred = 2 * pre
    RTB1_text = RTB1_text + "95% Confidence limits for the coefficients (at mean values):" + vbCrLf
    RTB1_text = RTB1_text + "log(N):" + taba + " " + Text8 + "% Confidence interval for Regression Line:     " + taba + format2(2 * f9x, 3) + vbCrLf
    RTB1_text = RTB1_text + "log(N):" + taba + " " + Text8 + "% Confidence interval for given value of S:    " + taba + format2(2 * pre, 3) + vbCrLf
    RTB1_text = RTB1_text + "b:" + taba + " " + Text8 + "% Confidence interval (for mean value of C):   " + taba + format2(d1 * 1, 3) + vbCrLf
    RTB1_text = RTB1_text + "log(C):" + taba + " " + Text8 + "% Confidence interval (for mean value of b):   " + taba + format2(d0 * 1, 3) + vbCrLf

    RTB1_text = RTB1_text + format2(-B - 0.5 * d1, 1) + " < b < " + format2(-B + 0.5 * d1, 1) + vbCrLf
    RTB1_text = RTB1_text + format2(10 ** (C - 0.5 * d0), 2) + " < C < " + format2(10 ** (C + 0.5 * d0), 2) + vbCrLf
    ##'RTB1_text = RTB1_text  + vbCrLf
    ##'RTB1_text = RTB1_text + "-----------------------------------------------------------------------------------" + vbCrLf
    for i in range(0,52):
        RTB1_text = RTB1_text + "_"
        #Next i
    ##'If design Or design3 Then
    RTB1_text = RTB1_text + vbCrLf + "Design SN Curve:" + vbCrLf
      

    ##'If (design) Then
    RTB1_text = RTB1_text + "N*S^"
    RTB1_text = RTB1_text + format2(-B, 1) + "=" + format2(10 ** (C - s95 * sqrt(npkt + 1)), 2)
    RTB1_text = RTB1_text + taba + " (95% Surv.,97.5% conf.(BS540, NS3472))" + vbCrLf
    RTB1_text = RTB1_text + "Stress range at 2E6 cycles for design curve: " + format2(10 ** ((C - 6.30103 - s95 * sqrt(npkt + 1)) / -B), 4) + " MPa" + vbCrLf
    ##'End If
    ## 'If design3 Then
    RTB1_text = RTB1_text + "N*S^"
    RTB1_text = RTB1_text + format2(-B, 1) + "=" + format2(10 ** (C - des3), 2)
    RTB1_text = RTB1_text + taba + " (95% Surv.,75% conf.(EC3))" + vbCrLf
    RTB1_text = RTB1_text + "Stress range at 2E6 cycles for design curve: " + format2(10 ** ((C - 6.30103 - des3) / -B), 4) + " MPa" + vbCrLf
    ##'End If
    if text5 != 0:
        sntText1_text = vbCrLf + vbCrLf + "SNt-Regression" + vbCrLf + "Regression coefficients bt,n(=v/bt), and ct for the equation:" + vbCrLf
        sntText1_text = sntText1_text + "log(N)=log(ct)+bt*log(S)+v*log(t)" + vbCrLf
        sntText1_text = sntText1_text + "bt=" + format2(-bt, 3) + "�" + format2(sbt, 3) + vbCrLf
        sntText1_text = sntText1_text + "n=" + format2(vtk, 3) + "�" + format2(-stk, 3) + vbCrLf
        sntText1_text = sntText1_text + "Ct=" + format2(ctex, 2) + "x/" + format2(sct, 3) + vbCrLf
        sntText1_text = sntText1_text + "Std=" + format2(sdev, 3) + vbCrLf
        sntText1_text = sntText1_text + "Total number of points" + ("%f" % (pkt)) + vbCrLf
     
        RTB1_text = RTB1_text + sntText1_text
        ##End If
#    RTB1.SelStart = 0
#    RTB1.SelLength = 37
#    RTB1.SelUnderline = True
#    i = InStr(RTB1_text, "Input")
#    RTB1.SelStart = i - 1
#    RTB1.SelLength = 8
#    RTB1.SelUnderline = True
#    i = InStr(RTB1_text, "Stress")
#    RTB1.SelStart = i - 1
#    RTB1.SelLength = 33
#    RTB1.SelUnderline = True
#    i = InStr(RTB1_text, "Output")
#    RTB1.SelStart = i - 1
#    RTB1.SelLength = 7
#    RTB1.SelUnderline = True
#    i = InStr(RTB1_text, "^")
#    RTB1.SelStart = i - 1
#    RTB1.SelLength = 2
#    RTB1.SelFontSize = 8
#    RTB1.SelCharOffset = 100
    
#    RTB1.SelText = Right(RTB1.SelText, 1)
#    i = InStr(i + 12, RTB1_text, "^")
#    RTB1.SelStart = i - 1
#    RTB1.SelLength = 5
#    RTB1.SelFontSize = 8
#    RTB1.SelCharOffset = 100
#    RTB1.SelText = Right(RTB1.SelText, 4)
#    i = InStr(i + 12, RTB1_text, "^")
#    RTB1.SelStart = i - 1
#    RTB1.SelLength = 2
#    RTB1.SelFontSize = 8
#    RTB1.SelCharOffset = 100
#    RTB1.SelText = Right(RTB1.SelText, 1)
#    i = 1
#    for ii in range(1,6):
#        i = InStr(i, RTB1_text, "E+")
    
#        if i == 0:
#            leave
#        RTB1.SelStart = i + 1
#        RTB1.SelLength = 2
#        RTB1.SelFontSize = 8
#        RTB1.SelCharOffset = 100
#        RTB1.SelStart = i - 1
#        RTB1.SelLength = 2
#        RTB1.SelText = "*10"
        
#        ##Next ii
#
#    i = 1
#    i = InStr(i, RTB1_text, "E-")

#    If i <> 0:
#        RTB1.SelStart = i
#        RTB1.SelLength = 3
#        
#        RTB1.SelFontSize = 8
#        RTB1.SelCharOffset = 100
#        RTB1.SelStart = i - 1
#        RTB1.SelLength = 1
#        RTB1.SelText = "*10"
#        ##End If
#i = 1
#For ii = 1 To 3
#i = InStr(i, RTB1_text, "2E6")
#If i = 0 Then Exit For
#RTB1.SelStart = i - 1
#RTB1.SelLength = 3
#RTB1.SelFontSize = 12
#
#RTB1.SelText = "2*106"
#Next ii

#i = 1
#For ii = 1 To 14
#i = InStr(i, RTB1_text, "*")
#If i = 0 Then Exit For
#RTB1.SelStart = i - 1
#RTB1.SelLength = 1
#RTB1.SelFontSize = 12
#RTB1.SelCharOffset = 60
#RTB1.SelText = "."
#Next ii
#i = 1
#For ii = 1 To 3
#i = InStr(i + 5, RTB1_text, ".106")
#If i = 0 Then Exit For
#RTB1.SelStart = i + 2
#RTB1.SelLength = 1
#RTB1.SelFontSize = 8
#RTB1.SelCharOffset = 100
#RTB1.SelText = "6"
#Next ii
#i = 100

#i = InStr(i + 12, RTB1_text, "^")
#RTB1.SelStart = i - 1
#RTB1.SelLength = 5
#RTB1.SelFontSize = 8
#RTB1.SelCharOffset = 100
#RTB1.SelText = Right(RTB1.SelText, 4)

#i = InStr(i + 12, RTB1_text, "^")
#RTB1.SelStart = i - 1
#RTB1.SelLength = 5
#RTB1.SelFontSize = 8
#RTB1.SelCharOffset = 100
#RTB1.SelText = Right(RTB1.SelText, 4)

    print(RTB1_text) 
#     RTB1.SaveFile filname
#Dim exetekst As String, liten As String
#liten = CurDir + "\SNTREG.rtf"
#exetekst = "copy " + filname + " + " + CurDir + "\SNTREG.rtf"

#RTB1_text = exetekst

#  End If
#End Sub




#      Private Sub sntreg(sn As Double, SSN, SN2, SST, ST2, SS2, SS, SNT, ST, pkt As Integer)
def sntreg(sn, SSN, SN2, SST, ST2, SS2, SS, SNT, ST, pkt):
#Static npkt3 As Integer
    global bt, sbt, vtk, stk, ctex, sct, sdev
    npkt3 = 0     
    SSNSS = SSN / SS
    if ST != 0:
        ST2ST = ST2 / ST
        SSTST = SST / ST
        SNTST = SNT / ST
    else:
        ST2ST = 0
        SSTST = 0
        SNTST = 0
    #End If
    SS2SS = SS2 / SS
    SSTSS = SST / SS
    SNPKT = sn / pkt
    STPKT = ST / pkt
    SSPKT = SS / pkt

    SNST1 = SSNSS - SNPKT
    SNST2 = SSTSS - STPKT
    SNST3 = SSTST - SSPKT
    SNST4 = SS2SS - SSPKT
    SNST5 = ST2ST - STPKT
    SNST6 = SNTST - SNPKT
    Btt = SNST2 * SNST6 - SNST1 * SNST5
    Vtt = SNST1 * SNST3 - SNST4 * SNST6
    Tn = SNST2 * SNST3 - SNST4 * SNST5
    if Tn != 0:
        bt = Btt / Tn
        vt = Vtt / Tn
    #End If

    print('foobar')
    if bt != 0 and Btt != 0:
        vtk = Vtt / Btt
    Ct = (sn - bt * SS - vt * ST) / pkt
    ctex = 10 ** Ct
    RSSM = 0
    for i in range(0, npkt-1):
        if Text5 != 0 and tkk[i] != 0:
            t = Alog(tkk[i] / Text5)
            if tkk[i] == Text5:
                t = 0
            Yv = Ct + bt * Alog(Slog(i)) + vt * t
            RSSM = RSSM + (Alog(Nlog(i)) - Yv) * (Alog(Nlog(i)) - Yv)
        #End If
    #Next i
    npkt3 = pkt - 3
    sdev2 = RSSM / npkt3
    sdev = sqrt(sdev2)
    ##'TreSdev = 3 * sdev2 * RPOT(npkt3, F953())
    ##TreSdev = 3 * sdev2 * Excel.WorksheetFunction.FInv(0.05, 3, npkt3)
    TreSdev = 3 * sdev2 * scipy.stats.f.isf(0.05, 3, npkt3)
    sbt = sqrt(TreSdev / SS2)
    if bt != 0:
        stk = sqrt(TreSdev / ST2) / bt
        #End If
    sct = 10 ** sqrt(TreSdev / pkt)

    sntdat = vbCrLf & "Snt Regression:" & vbCrLf
    sntdat = sntdat & "Regression coefficients bt,n(=v/bt), and ct for the equation:" & vbCrLf
    sntdat = sntdat & "log(N)=log(ct)+bt*log(S)+v*log(t)" & vbCrLf
    sntdat = sntdat & "bt=" & format2(-bt, 3) & "�" & format2(sbt, 3) & vbCrLf
    sntdat = sntdat & "n=" & format2(vtk, 3) & "�" & format2(-stk, 3) & vbCrLf
    sntdat = sntdat & "Ct=" & format2(ctex, 2) & "x/" & format2(sct, 3) & vbCrLf
    sntdat = sntdat & "Std=" & format2(sdev, 3) & vbCrLf
#End Sub


def nvarrow(x1,y1,ax,plt):
    inv = ax.transData.inverted() 
    foo = ax.transData.transform(ax.axis())
    arrowSide = (foo[1]-foo[0]+foo[3]-foo[2])/150
    (abs_x1,abs_y1) = ax.transData.transform((x1,y1))
    abs_x2 = abs_x1 + arrowSide
    abs_y2 = abs_y1 + arrowSide
    (x2,y2) = inv.transform((abs_x2,abs_y2))
    plt.annotate('', xy=(x2,y2), xytext=(x1,y1), arrowprops=dict(facecolor='black',width=1.0,shrink=0.0) , zorder=2)

    
