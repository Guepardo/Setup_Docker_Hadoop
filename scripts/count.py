import sys
import os
import subprocess

HADOOP_PATH = os.environ['HADOOP_PREFIX'] + '/bin/'

filepath = sys.argv[1]

print(filepath)
cat = subprocess.Popen(["%(HADOOP_PATH)shadoop" % locals(), "fs", "-cat", filepath], stdout = subprocess.PIPE)

for line in cat.stdout: 
	print(line.upper())