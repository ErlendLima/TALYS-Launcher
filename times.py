#! /usr/bin/python
"""
This script recursively searches through the directory structure, finds all
output files and writes the time stamps into the output file.
Syntax:
python times.py directory outfile
"""

import argparse
import os
import re
import sys

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("directory", help="the directory to be searched")
	parser.add_argument("outfile", help="the file to which the timestamps will be written")
	args = parser.parse_args()

	timestamps = {}
	pattern = re.compile("Execution time:\s*(\d*)\s*hours\s*(\d*)\s*minutes\s*(\d*\.\d*)\s*seconds")
	for root, dirs, files in os.walk(args.directory, topdown=False):
		for name in files:
			if name == "output.txt":
				with open(os.path.join(root, name), "r") as output:
					match = ''
					for line in reversed(output.readlines()):
						match = re.search(pattern, line)
						if match:
							print match.group(0)
							break
					if match is not None:
						timestamps[os.path.join(root, name)] = [match.group(1), match.group(2), match.group(3)]
	if len(timestamps) == 0:
		print "Found no timestamps"
		sys.exit()
	root, _, _ = os.walk(args.directory, topdown=False)
	outfile = open(os.path.join(root, args.outfile), "w")
	for name, time in timestamps.iteritems():
		outfile.write("{}:{}:{} {}\n".format(time[0], time[1], time[2],  name))
	outfile.close()
