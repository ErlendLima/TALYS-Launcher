from __future__ import print_function    # Changes print to Python 3's print. Fixes  a few bugs
import numpy as np                       # Linspace
import time                              # Time and date
from itertools import product            # Nested for-loops
import sys                               # Functions to access system functions
import os                                # Functions to access IO of the OS
import shutil                            # High-level file manegement
import platform                          # Information about the platform
import logging                           # Logging progress from the processes
import argparse                          # Parsing arguments given in terminal
import copy                              # For deepcopy
import traceback                         # To log tracebacks
from mpi4py import MPI                   # For multiprocessing and Abel
import json                              # 
from talys import make_iterable
import operator


class Input:

    def __init__(self):
        with open("structure.json") as wFile:
            data = json.load(wFile)

        self.keywords = {}
        for key, value in data["keywords"].iteritems():
            if key != "comment":
                self.keywords[key] = value

        self.keywords = make_iterable(self.keywords)
        self.conditionals = []
        for _, value in data["conditionals"].iteritems():
            if isinstance(value, dict):
                self.conditionals.append(value)

        self.script_keywords = {}
        for key, value in data["script_keywords"].iteritems():
            if key != "comment":
                self.script_keywords[key] = value

        self.structure = data["structure"]

    def __getitem__(self, index):
        return self.keywords[index]

    def get_condition_val(self, key):
        for c in self.conditionals:
            if key in c.keys():
                return c[key]


class Directory:
    """ Simplifies directory management"""
    def __init__(self, structure):
        self.structure = structure
        self.root = self.structure["root"]
        self.wd = self.root

    def cd(self, path):
        if isinstance(dict, path):
            self.wd=path

    def next(self):
        recursively_find_key("next")


def recursively_find_key(dictionary, key):
    """ Returns a reverse list of the keys leading to the wanted key"""
    if key in dictionary:
        return [key]
    for _key, _val in dictionary.iteritems():
        if isinstance(_val, dict):
            match = recursively_find_key(_val, key)
            if match is not None:
                match.append(_key)
                return match


class Dict():
    def __init__(self):
        self._dict = {}

    def __call__(self, key, path):
        if not os.path.exists(path):
            print("Making dir ", path)
        self._dict[key] = path

    def __getitem__(self, key):
        return self._dict[key]

class Manager():
    def __init__(self, input):
        self.input = input
        self.directories = Dict()
        self.currOrig = ''
        self.currRes  = ''

    def run(self):
        if MPI.COMM_WORLD.Get_rank() == 0:
            # If root process
            pass
        else:
            # All other processes
            pass

    def run_element(self, element):
        self.currDir = os.path.join(self.currOrig, element)
        self.directories("element", self.currOrig)
        for isotope in self.input["mass"]:
            

    def run_rest(self, user, path):
        path = os.path.join(path)
        pathh = os.path.join(path, user.keywords["mass"])
    
        keywords = []
        values = []
        # have the keys in alphabetical order
        sorted_keys = user.keywords.keys()
        sorted_keys.sort()
        for sorted_key in sorted_keys:
            # only use keywords that vary
            if len(user.keywords[sorted_key]) > 1 and sorted_key != "element" and sorted_key != "mass":
                # both lists are in "alphabetical order" and corresponding
                # key-value pair have the same index
                keywords.append(sorted_key)
                values.append(user[sorted_key])
    
        # 1) append the conditional names to the keywords, since they
        # are the one to be chosen from. This is undone at 2)
        for condition in user.conditionals:
            values.append(condition.keys())
    
        for vals in product(*values):
            # 2) splits the result back into keywords and conditions
            keywordvals = vals[:len(keywords)]
            conditionkeys = vals[len(keywords):]
    
            # name the directory according to the alphabetical order and value
            # of the keyword
            name = ''
            for s in keywordvals:
                name = "{}-{}".format(name, s)
                # remove the unecessary -
            name = name[1:]
    
            # name the directory according to the chosen condition
            for key in conditionkeys:
                name = "{}-{}-{}".format(name, key, user.get_condition_val(key))
    
                pathhh = os.path.join(pathh, name)
                print pathhh
def mkdir(path):
    if not os.path.exists(path):
        print "Making dir", path
        #os.makedirs(path)


def search(user, dir, path):
    for key, value in dir.iteritems():
        print(key, value)
        if key == "{rest}":
            print "In", key
            path = os.path.join(path, key)
            run_rest(user, path)
        elif isinstance(value, dict):
            print "Next"
            path = os.path.join(path, key)
            search(user, value, path)


if __name__ == "__main__":
    
    user = Input()

    date = time.strftime('%y')
    timestamp = time.strftime('%H')
    root = "{date}{time}".format(date=date, time=timestamp)
    original_path = os.path.join(root, "work")
    for key, val in user.structure.iteritems():
        if isinstance(val , dict):
            search(user, val, original_path)
    # for element in user["element"]:
    #    path = os.path.join(original_path, element)
    #    for mass in user["mass"][element]:
    #        run_rest(user, path)
