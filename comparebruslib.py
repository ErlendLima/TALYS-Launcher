import re
import os
import argparse
import sys
import pprint

def load_bruslib(directory):
    data = {}
    for root, subdirs, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            with open(path, "r") as inputfile:
                lines = inputfile.readlines()
            chunks = []
            while lines:
                chunks.append(lines[:33])
                lines = lines[33:]
            for chunk in chunks:
                match = re.search(pattern, chunk[1])
                if match is None:
                    continue
                name = match.group(1)
                data[name] = []
                for line in chunk[4:-2]:
                    line = line.lstrip()
                    splot = line.split(' ')
                    try:
                        if len(splot) > 1:
                            data[name].append([float(splot[0]),
                                                 float(splot[1])])
                    except:
                        print(file)

    return data

def load_results(directory):
    data = {}
    for root, subdirs, files in os.walk(directory):
        for file in files:
            if not file == "astrorate.g":
                continue
            path = os.path.join(root, file)
            with open(path, "r") as inputfile:
                lines = inputfile.readlines()
            match = re.search(pattern, lines[0])
            if match is None:
                continue
            name = match.group(1)
            data[name] = []
            for line in lines[4:]:
                line = line.lstrip()
                splot = line.split(' ')
                data[name].append([float(splot[0]),
                                   float(splot[1])])
    return data


def compare(dict1, dict2):
    for key in dict1.keys():
        zips = zip(dict1[key], dict2[key])
        print(key)
        for temp, rate in zips:
            print(temp, rate)
        input()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("result")
    parser.add_argument("bruslib")
    args = parser.parse_args()
    pattern = re.compile("(\d{1,3}[a-zA-Z]{1,3})")
    result_directory  = os.path.abspath(args.result)
    bruslib_directory = os.path.abspath(args.bruslib)
    brusdata = load_bruslib(bruslib_directory)
    resdata  = load_results(result_directory)
    compare(brusdata, resdata)
