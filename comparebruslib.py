import re
import os
import argparse
import sys
import pprint

def load_bruslib(directory):
    data = {}
    # Iterate through the directories
    for root, subdirs, files in os.walk(directory):
        for file in files:
            # Read all files
            path = os.path.join(root, file)
            try:
                with open(path, "r") as inputfile:
                    lines = inputfile.readlines()
            except Exception as E:
                print(E)
                continue
            # The reaction rates from each isotope is stored in chunks
            chunks = []
            while lines:
                # A block of results is 33 lines long
                chunks.append(lines[:33])
                lines = lines[33:]
            for chunk in chunks:
                # Find the mass+Symbol on the second line
                match = re.search(pattern, chunk[1])
                # If not, skip it
                if match is None:
                    continue
                
                massSymbol = match.group(1)
                data[massSymbol] = []
                for line in chunk[4:]:
                    # Remove newline and leading space
                    line = line.lstrip()
                    splot = line.split(' ')
                    # Split the data into columns, so to speak
                    try:
                        # Some of the files contain random newlines and stuff
                        # Only use data that is real data, not newlines
                        if len(splot) > 1:
                            data[name].append([float(splot[0]),
                                                 float(splot[1])])
                    except:
                        # The file pfLI serves to purpose
                        if file != "pfLI":
                            print(file)

    return data


def load_results(directory):
    data = {}
    # Iterate through the directories and sub-directories
    for root, subdirs, files in os.walk(os.path.join(directory, "results_data")):
        for file in files:
            # Only look at astrorate.g
            if not file == "astrorate.g":
                continue
            # Find the path and read the file
            path = os.path.join(root, file)
            with open(path, "r") as inputfile:
                lines = inputfile.readlines()
            # Extract the mass+symbol from the first line
            match = re.search(pattern, lines[0])
            # Line might be empty, so skip if no mass+symbol is found
            if match is None:
                continue

            massSymbol = match.group(1)
            data[massSymbol] = []
            for line in lines[4:]:
                line = line.lstrip()
                splot = line.split(' ')
                data[massSymbol].append([float(splot[0]),
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
    parser.add_argument("talysdirectory")
    parser.add_argument("bruslib")
    args = parser.parse_args()
    # Regex to extract mass+symbol of element
    pattern = re.compile("(\d{1,3}[a-zA-Z]{1,3})")
    # Make the paths absolute (technical detail)
    talys_directory  = os.path.abspath(args.talysdirectory)
    bruslib_directory = os.path.abspath(args.bruslib)
    # Get the data
    resdata  = load_results(talys_directory)
    brusdata = load_bruslib(bruslib_directory)
    # resdata and brusdata are dicts of the form
    # {MassElement:[Temperature,ReactionRate]}
    # for example:
    # {151Sm:[[0,0.1],[0.1,2.1E-8]...], 152S:[...]}

    # For illustration:
    compare(brusdata, resdata)
