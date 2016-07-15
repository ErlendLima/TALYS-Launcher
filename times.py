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
import operator

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("directory", help="the directory to be searched")
	parser.add_argument("outfile", help="the file to which the timestamps will be written")
	args = parser.parse_args()

	Root = ''
	timestamps = {}
	do_run = True
	pattern = re.compile("Execution time:\s*(\d*)\s*hours\s*(\d*)\s*minutes\s*(\d*\.\d*)\s*seconds")
	for root, dirs, files in os.walk(args.directory, topdown=False):
		Root = root
		for name in files:
			if name == "output.txt":
				with open(os.path.join(root, name), "r") as output:
					match = ''
					for line in reversed(output.readlines()):
						match = re.search(pattern, line)
						if match:
							#print match.group(0)
							BREAK
					if match is not None:
						timestamps[os.path.join(root, name)] = [match.group(1), match.group(2), match.group(3)]
	if len(timestamps) == 0:
		print "Found no timestamps"
		sys.exit()
	#outfile = open(os.path.join(Root, args.outfile), "w")
	outfile = open(args.outfile, "w")
	sorted_names = sorted(timestamps.items(), key=operator.itemgetter(0))

	for name, time in sorted_names:
		outfile.write("{}:{}:{:6} {}\n".format(time[0], time[1], time[2],  name))

	totalsecs = 0
	for hour, minute, second in zip(*sorted_names)[1]:
		second = int(round(float(second)))
		hour, minute = map(int, (hour, minute))
		totalsecs += hour*3600 + minute*60 + second
	totalsecs, sec = divmod(totalsecs, 60)
	hour, minute = divmod(totalsecs, 60)
	days, hour = divmod(hour, 24)
	outfile.write("{:-^20}\n".format("TOTAL"))
	outfile.write("Days: {:3} Hours: {:3} Minutes: {:3} Seconds: {:3}\n".format(days, hour, minute, sec))
	outfile.close()
