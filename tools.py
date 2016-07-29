"""
This module contains helper functions.
The main purpose is to remove clutter in the main
file
"""

from __future__ import print_function
import argparse
import sys
import os
import logging
import copy
from string import Formatter


class StyleFormatter(Formatter):
    """ Custom formatter that handles nested field of two levels
        such as '{mass[element]}'. Don't know how it works
    """
    def get_value(self, field_name, args, kwargs):
        # Return kwargs[field_name], else return ''
        return kwargs.get(field_name, '')

    def get_field(self, field_name, args, kwargs):
        # To illustrate, the example '{mass[element]}' is used with
        # the kwargs {"element":"Pr", "mass":{"Pr":128}}

        # Split the field_name into the field and an iterator
        # ex. mass <fieldnameiterator object at 0x105308840>
        first, rest = field_name._formatter_field_name_split()
        #print("First:", first)
        #print("Kwargs:", kwargs)
        # obj = kwargs[field_name] or obj = '' if KeyError
        # ex. obj = {"Pr":128}
        obj = self.get_value(first, args, kwargs)

        # Often, "rest" is only one deep
        # is_attr is a bool. I think it is true if something.keyword exists
        # keyword is just a keyword, like something[keyword] or something.keyword
        for is_attr, keyword in rest:
            # This is the juciy stuff. If the keyword is in kwargs, return the
            # value in obj
            # ex. obj = {"Pr":128}["Pr"] = 128
            if keyword in kwargs:
                #print(obj)
                obj = obj[kwargs.get(keyword)]
        # ex. 128
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
    """ Check if directory exists. If not, create it
    Parameters: directory: the name of the directory
    Returns:    None
    Algorithm:  Check if the direcctory exists, if not, create it
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def make_iterable(dictionary):
    """ Makes every entry in the dictionary iterable and returns the result
    Parameters: dictionary: the dict to be made iterable
    Output:     The iterable dictionary
    Algorithm:  Make every key in the list iterable and make the results
                entries unique"""
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
    parser.add_argument("--enable_pausing",
                        help="Enable pausing by running a process that checks for input",
                        action="store_true")

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


def getkey():
    # Magic
    import termios
    TERMIOS = termios
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    new = termios.tcgetattr(fd)
    new[3] = new[3] & ~TERMIOS.ICANON & ~TERMIOS.ECHO
    new[6][TERMIOS.VMIN] = 1
    new[6][TERMIOS.VTIME] = 0
    termios.tcsetattr(fd, TERMIOS.TCSANOW, new)
    c = None
    try:
        c = os.read(fd, 1)
    finally:
        termios.tcsetattr(fd, TERMIOS.TCSAFLUSH, old)
    return c
