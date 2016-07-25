"""
This module contains helper functions.
The main purpose is to remove clutter in the main
file
"""

import argparse
import sys
import os
import logging
import copy
from string import Formatter


class KeyFormatter(Formatter):
    def get_value(self, field_name, args, kwargs):
        return kwargs.get(field_name, '')

    def get_field(self, field_name, args, kwargs):
        first, rest = field_name._formatter_field_name_split()
        obj = self.get_value(first, args, kwargs)

        print(first, rest)
        print(obj)
        for is_attr, i in rest:
            print(is_attr, i)
            if is_attr:
                print(getattr(obj, i))
                obj = getattr(obj, i)
            else:
                obj = obj.get(i, '')
        return obj, first


def correct(input_argument):
    """ Function to check syntax of input arguments given by user """

    if input_argument in('n', 'no'):
        return 'no'

    elif input_argument in('y', 'yes'):
        return 'yes'

    # if input argument is given incorrectly, function returns 'error'
    else:
        error_message = " please make sure these input arguments are gives as: \n input = 'no' or input = 'yes' \n input = 'n'  or input = 'y' \n input = ['no', 'yes'] or input = ['n', 'y'] \n"
        sys.exit(error_message)


def mkdir(directory):
    """ Check if directory exists. If not, create it """
    if not os.path.exists(directory):
        os.makedirs(directory)


def make_iterable(dictionary):
    """ Makes every entry in the dictionary iterable and returns the result """
    new_dict = copy.deepcopy(dictionary)

    for key in dictionary:
        if not isinstance(dictionary[key], (tuple, list)):
            new_dict[key] = [new_dict[key]]

    # check if every item in user given list is unique
    for key, value in new_dict.iteritems():

        try:
            # if variable tuple or list => new list with value only once
            if len(set(value)) != len(value):
                newlist = []
                for val in value:
                    if val not in newlist:
                        newlist.append(val)
                        new_dict[key] = newlist

        except TypeError:
            # if variable == dict => new dict with value only once inside
            # user_input[key]
            for keys, values in value[0].iteritems():
                if len(set(values)) != len(values):
                    newlist = []
                    for val in values:
                        if val not in newlist:
                            newlist.append(val)
                            value[0][keys] = newlist

                new_dict[key] = value[0]
    return new_dict


def get_args():
    """
    Manages the argparse module.
    Any changes to the arguments from terminal are done here
    Parameters: none
    Returns: class instance of 'argparse.Namespace'
    Algorithm: Add arguments to argparse.ArgumentParser(), fix some arguments
               regarding logging, and return the parsed arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug",
                        help="Show debugging information. Overrules log and verbosity",
                        action="store_true")
    parser.add_argument("-l", "--log",
                        help="Set the log level",
                        choices=["DEBUG", "INFO",
                                 "WARNING", "ERROR", "CRITICAL"],
                        type=str.upper, default="INFO")
    parser.add_argument("-v", "--verbosity",
                        help="Set the verbosity level",
                        choices=["DEBUG", "INFO",
                                 "WARNING", "ERROR", "CRITICAL"],
                        type=str.upper, default="INFO")
    parser.add_argument("--lfilename",
                        help="Filename of the log file",
                        type=str, default="talys.log")
    parser.add_argument("--efilename",
                        help="Filename of the error file",
                        type=str, default="error.log")
    parser.add_argument("--input_filename",
                        help="The filename for where the options are stored",
                        type=str, default="structure.json")
    parser.add_argument("-p", "--processes",
                        help="Set the number of processes the script will use. Should be less than or equal to number of CPU cores",
                        type=int, default=0)

    args = parser.parse_args()
    # Convert the input strings to the corresponding logging type
    args.log = getattr(logging, args.log)
    args.verbosity = getattr(logging, args.verbosity)

    # --debug overrules --log and --verbosity
    if args.debug:
        args.log = logging.DEBUG
        args.verbosity = logging.DEBUG

    return args


class Cd:
    """ Simplifies directory mangement """

    def __init__(self, newPath):
        """ When an object of cd is created, the given path is expanded all the way back to $HOME"""
        self.newPath = os.path.expanduser(newPath)

    """ In order for an cd object to be used with the with-statement, __enter__ and __exit__ are needed """

    def __enter__(self):
        """ Changes directory to the one given in __init__ while saving the current when entering
        the with-statement """
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        """ Returns to the original path when exiting the with-statement """
        os.chdir(self.savedPath)

