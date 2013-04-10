#!/usr/bin/env python

import re

symbol_regex = re.compile("=(.*)\W\(")

handle = open("bmw32.ini", "r")

lines = handle.readlines()

bmw_symbols = []

for line in lines:
    match = symbol_regex.search(line)
    if match:
        bmw_symbols.append(match.group(1))


bmw_file_format = """Bagpipe Music Writer Gold:1.0
MIDINoteMappings,(54,56,58,59,61,63,64,66,68,56,58,60,61,63,65,66,68,70,55,57,59,60,62,64,65,67,69)
FrequencyMappings,(370,415,466,494,554,622,659,740,831,415,466,523,554,622,699,740,831,932,392,440,494,523,587,659,699,784,880)
InstrumentMappings,(71,71,45,33,1000,60,70)
GracenoteDurations,(20,40,30,50,100,200,800,1200,250,250,250,500,200)
FontSizes,(90,100,88,80,250)
TuneFormat,(1,0,M,L,500,500,500,500,P,0,0)
TuneTempo,84
"BMW Symbols",(T,L,0,0,Times New Roman,16,700,0,0,18,0,0,0)
"",(Y,C,0,0,Times New Roman,14,400,0,0,18,0,0,0)
"Graham MacMaster",(M,R,0,0,Times New Roman,14,400,0,0,18,0,0,0)
"",(F,R,0,0,Times New Roman,12,400,0,0,18,0,0,0)
%s
""" % " ".join(bmw_symbols)

print bmw_file_format