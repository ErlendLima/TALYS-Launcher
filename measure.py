#! /usr/bin/python
"""
This script recursively searches through the directory structure, finds all
output files and writes the time stamps into the output file.
Syntax:
python measure.py directory outfile slurmfile/logfile
"""
from __future__ import print_function
import argparse
import os
import re
import sys
import operator
import copy


def get_talys_stamps(directory):
    do_run = True
    timestamps = {}
    pattern = re.compile(
        "Execution time:\s*(\d*)\s*hours\s*(\d*)\s*minutes\s*(\d*\.\d*)\s*seconds")
    for root, dirs, files in os.walk(directory, topdown=False):
        Root = root
        for name in files:
            if name == "output.txt":
                with open(os.path.join(root, name), "r") as output:
                    match = ''
                    for line in reversed(output.readlines()):
                        match = re.search(pattern, line)
                        if match:
                            # print match.group(0)
                            break
                    if match is not None:
                        timestamps[os.path.join(root, name)] = [
                            match.group(1), match.group(2), match.group(3)]
    return timestamps


def get_slurm_stamps(slurmfile, sorted_stamps):
    pattern = re.compile("Execution time:\s*(\d\d):(\d\d)")
    sorted_stamps = copy.deepcopy(sorted_stamps)
    stamps = []
    with open(slurmfile, "r") as input:
        for line in input:
            #print(line)
            for name, time in sorted_stamps:
                #print(key.split('/')[-2])
                s = name.split('/')
                search_s = '-'.join([s[-3],s[-2]])
                if search_s in line:
                    match = re.search(pattern, line)
                    stamps.append([name, time, [0, str(int(match.group(1))), match.group(2)]])
                    sorted_stamps.remove((name, time))
                    break
    print("Missed ", len(sorted_stamps))
    return stamps


def total_time(times):
    totalsecs = 0
    for hour, minute, second in times:
        second = int(round(float(second)))
        hour, minute = map(int, (hour, minute))
        totalsecs += hour * 3600 + minute * 60 + second
    totalsecs, sec = divmod(totalsecs, 60)
    hour, minute = divmod(totalsecs, 60)
    days, hour = divmod(hour, 24)
    return days, hour, minute, sec


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="the directory to be searched")
    parser.add_argument("outfile",
                        help="the file to which the timestamps will be written",
                        nargs='?',
                        default="timestamps.txt")
    parser.add_argument("slurmfile",
                        help="A slurmfile containing timestamps",
                        nargs='?')
    args = parser.parse_args()
    Root = ''
    
    timestamps = get_talys_stamps(args.directory)
    if len(timestamps) == 0:
        print("Found no timestamps")
        sys.exit()

    #outfile = open(os.path.join(Root, args.outfile), "w")
    outfile = open(args.outfile, "w")
    sorted_names = sorted(timestamps.items(), key=operator.itemgetter(0))
    if args.slurmfile is not None:
        slurmstamps = get_slurm_stamps(args.slurmfile, sorted_names)
        for name, time, ttime in slurmstamps:
            outfile.write("{}:{}:{}/{}:{}:{} {:>30}\n".format(
                time[0], time[1], time[2], ttime[0], ttime[1], ttime[2], name
            ))
    else:
        for name, time in sorted_names:
            outfile.write("{}:{}:{} {:>30}\n".format(
                time[0], time[1], time[2],  name))

    days, hours, minutes, seconds = total_time(zip(*sorted_names)[1])
    outfile.write("{:-^20}\n".format("TOTAL"))
    outfile.write("Days: {:<3} Hours: {:<3} Minutes: {:<3} Seconds: {:<3}\n".format(
        days, hours, minutes, seconds))
    if args.slurmfile is not None:
        days, hours, minutes, seconds = total_time(zip(*slurmstamps)[2])
        outfile.write("{:-^20}\n".format("SLURM"))
        outfile.write("Days: {:<3} Hours: {:<3} Minutes: {:<3} Seconds: {:<3}\n".format(
            days, hours, minutes, seconds))       

    outfile.close()
