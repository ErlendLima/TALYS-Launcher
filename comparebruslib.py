import re
import os
import argparse
import sys

pattern = re.compile("(\d{1,3})([a-zA-Z]{1,3})")
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
                symbol = match.group()
                
            sys.exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("result")
    parser.add_argument("bruslib")
    args = parser.parse_args()
    result_directory  = os.path.abspath(args.result)
    bruslib_directory = os.path.abspath(args.bruslib)
    load_bruslib(bruslib_directory)
