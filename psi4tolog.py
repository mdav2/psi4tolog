#!/usr/bin/env python
import re
import sedre

header = """ Entering Gaussian System, Link 0=g09
 Input=C-3-f.gjf
 Output=C-3-f.log
 Initial command:
 /opt/g09/l1.exe "/scratch/gaussian/Gau-113407.inp" -scrdir="/scratch/gaussian/"
 Entering Link 1 = /opt/g09/l1.exe PID=    113408.

 Copyright (c) 1988,1990,1992,1993,1995,1998,2003,2009,2013,
            Gaussian, Inc.  All Rights Reserved.
"""

compline = """ ---------------------------------------------------------------------
 #N
 ---------------------------------------------------------------------
"""

input_orientation = """                          Input orientation:
 ---------------------------------------------------------------------
 Center     Atomic      Atomic             Coordinates (Angstroms)
 Number     Number       Type             X           Y           Z
 ---------------------------------------------------------------------
"""

std_orient = """                         Standard orientation:
 ---------------------------------------------------------------------
 Center     Atomic      Atomic             Coordinates (Angstroms)
 Number     Number       Type             X           Y           Z
 ---------------------------------------------------------------------
"""

sep = "---------------------------------------------------------------------\n"
nmode_head = "  Atom  AN    X      Y      Z        X      Y      Z        X      Y      Z"
freqline = " Frequencies --  {} {} {}\n"
rmass_line = " Red. masses --  {} {} {}\n"
frc_line = " Frc consts  --  {} {} {}\n"
intens_line = " IR Inten    --  {} {} {}\n"
dline = "{} "*11 + "\n"
gline = "{} {} {} {} {} {}\n"
anynum = "[-.0-9i]+"
canynum = "([-.0-9i]+)"
space = "\s+"
atlookup = {"h":1,"he":2,"li":3,"be":4,"b":5,"c":6,"n":7,"o":8,
            "f":9,"ne":10}

freq_rstr  = "Freq \[cm\^-1\]"+space+canynum+space+canynum+space+canynum
rmass_rstr = "Reduced mass \[u\]"+space+canynum+space+canynum+space+canynum
frc_rstr   = "Force const \[mDyne/A\]"+space+canynum+space+canynum+space+canynum
int_rstr   = "IR activ \[km/mol\]"+space+canynum+space+canynum+space+canynum
disp_rstr  = "\s+[0-9]   "+"([A-Za-z]+)"+(space+canynum+space+canynum+space+canynum)*3
geom_rstr  = "([A-Z]|[A-Z][A-Z])"+(space+canynum)*3

with open('output.dat','r') as f: cont = f.read()
myp = sedre.Parser(program="psi4")
geom = myp.data['properties']['GEOM']['cart']['vals'][-1]
freq = re.findall(freq_rstr,cont)
rmass = re.findall(rmass_rstr,cont)
frc = re.findall(frc_rstr,cont)
intens = re.findall(int_rstr,cont)
disps = re.findall(disp_rstr,cont)
natom = len(geom)
ostr = ""
ostr += header
ostr += compline
ostr += input_orientation
for idx,atom in enumerate(geom):
    num = atlookup[atom[0].strip().lower()]
    ostr += gline.format(idx+1,num,0,*atom[1:])
ostr += sep
ostr += std_orient
for idx,atom in enumerate(geom):
    num = atlookup[atom[0].strip().lower()]
    ostr += gline.format(idx+1,num,0,*atom[1:])
ostr += sep
freq = list(map(list,freq))
for idx,line in enumerate(freq):
    for idx2,indiv in enumerate(line):
        if 'i' in indiv:
            line[idx2] = line[idx2].replace("i","")
            line[idx2] = "-" + line[idx2]
    ostr += freqline.format(*line)
    ostr += rmass_line.format(*rmass[idx])
    ostr += frc_line.format(*frc[idx])
    if len(intens) != 0:
        ostr += intens_line.format(*intens[idx])
    else:
        ostr += intens_line.format("0.0","0.0","0.0")
    for i in range(natom):
        n = idx*natom+i
        ostr += dline.format(i+1,atlookup[disps[n][0].lower()],*disps[n][1:])
    ostr += "\n"
print(ostr)
