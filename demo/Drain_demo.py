#!/usr/bin/env python
import sys
sys.path.append('../')
from logparser import Drain

input_dir  = '../logs/HDFS/'  # The input directory of log file
output_dir = 'Drain_result/'  # The output directory of parsing results
log_file   = 'HDFS_2k.log'  # The input log file name
log_format = '<Date> <Time> <Pid> <Level> <Component>: <Content>'  # HDFS log format
# Regular expression list for optional preprocessing (default: [])
regex      = [
    (r'blk_(|-)[0-9]+' , r'<blk_id>'), # block id
    (r'(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)', r'<IP>'), # IP
    (r'(?<=[^A-Za-z0-9])(\-?\+?\d+)(?=[^A-Za-z0-9])|[0-9]+$', r'<num>') # Numbers
]
st         = 0.5  # Similarity threshold
depth      = 8  # Depth of all leaf nodes

log_file = r'../logs/HDFS/HDFS_2k.log'
with open(log_file, 'r') as f:
    msgs = f.read().splitlines()
msgs = [' '.join(msg.split()[5:]) for msg in msgs]
msgs = [(msg, hash(msg)) for msg in msgs]
parser = Drain.DrainCore(msgs, regexSubPair=regex, depth=depth, st=st)
parser.parse_all(parser.messages)

