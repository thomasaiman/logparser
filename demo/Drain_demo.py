#!/usr/bin/env python
import sys
sys.path.append('../')
from logparser import Drain

input_dir  = '../logs/HDFS/'  # The input directory of log file
output_dir = 'Drain_result/'  # The output directory of parsing results
log_file   = r'../logs/HDFS\HDFS_2k.log'  # The input log file name
# log_format = '<Date> <Time> <Pid> <Level> <Component>: <Content>'  # HDFS log format
# Regular expression list for optional preprocessing (default: [])
regex      = [
    r'blk_(|-)[0-9]+' , # block id
    r'(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)', # IP
    r'(?<=[^A-Za-z0-9])(\-?\+?\d+)(?=[^A-Za-z0-9])|[0-9]+$', # Numbers
]
st         = 0.5  # Similarity threshold
depth      = 10 # Depth of all leaf nodes

msgs = open(log_file,'r').read().splitlines()
msgs = [(msg,msg.__hash__()) for msg in msgs]
parser = Drain.DrainCore(msgs,depth=depth, st=st, rex=regex)
parser.parse_all(msgs)
parser.printTree(parser.rootNode,0)
pass