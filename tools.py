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
import subprocess
from operator import attrgetter
from string import Formatter

try:
    # Python 3
    import _string
except ImportError:
    # Python 2
    pass


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
        
        try:
            # Python 2.7
            first, rest = field_name._formatter_field_name_split()
        except:
            # Python 3 (Only tested on 3.5)
            first, rest = _string.formatter_field_name_split(field_name)
        # print("First:", first)
        # print("Kwargs:", kwargs)
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
    for key, value in new_dict.items():

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
            for keys, values in value[0].items():
                print(keys, values)
                if len(set(values)) != len(values):
                    newlist = []
                    for val in values:
                        if val not in newlist:
                            newlist.append(val)
                            value[0][keys] = newlist

                new_dict[key] = value[0]
    return new_dict


def which(program):
    """ Find path of binary

    Paramteres: program: name of binary
    Returns:    Path to binary if found, else none
    Algorithm:  Mimic the UNIX 'which' command
    """
    import os

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def talys_version(local=False):
    """ Get the version of TALYS being used

    Parameters: local: Wether to use a binary talys file in the current
                       directory or the system-wide talys
    Returns:    String of the format #.#
    Algorithm:  Call shell command "strings" and greps the result
    """
    # Find the path of TALYS
    if local:
        talys_path = os.path.join(os.getcwd(), "talys")
    else:
        talys_path = which("talys")
    if "talys" not in talys_path:
        raise RuntimeError("Could not find talys")

    # Use the UNIX command 'strings' to extract all strings from
    # the binary

    talys18string = "pshiftadjust"
    talys16string = "fisbaradjust"
    talys14string = "deuteronomp"
    talys12string = "gamgamadjust"
    last_resort_string = "massmodel"

    strings = subprocess.check_output(["strings", talys_path]).decode("utf8")
    if talys18string in strings:
        return "1.8"
    elif talys16string in strings:
        return "1.6"
    elif talys14string in strings:
        return "1.4"
    elif talys12string in strings:
        return "1.2"
    elif last_resort_string in strings:
        return "1.0"
    else:
        return "unknown"


class SortingHelpFormatter(argparse.RawTextHelpFormatter):
    """ Custom formatter for argparse help """
    def add_arguments(self, actions):
        actions = sorted(actions, key=attrgetter('option_strings'))
        super(SortingHelpFormatter, self).add_arguments(actions)

def get_args():
    """
    Manages the argparse module.
    Any changes to the arguments from terminal are done here
    Parameters: none
    Returns: class instance of 'argparse.Namespace'
    Algorithm: Add arguments to argparse.ArgumentParser(), fix some arguments
               regarding logging, and return the parsed arguments.
    """
    parser = argparse.ArgumentParser(description=("Automates the process of "
                   "creating and running thousands of simulations with TALYS"),
                                     formatter_class=SortingHelpFormatter)
    parser.add_argument("-d", "--debug",
                        help="show debugging information. Overrules log and verbosity",
                        action="store_true")
    parser.add_argument("-l", "--log",
                        help="set the verbosity for the log file",
                        choices=["DEBUG", "INFO",
                                 "WARNING", "ERROR", "CRITICAL"],
                        type=str.upper, default="INFO")
    parser.add_argument("-v", "--verbosity",
                        help="set the verbosity level",
                        choices=["DEBUG", "INFO",
                                 "WARNING", "ERROR", "CRITICAL"],
                        type=str.upper, default="INFO")
    parser.add_argument("--lfile",
                        help="filename of the log file",
                        type=str, default="talys.log",
                        metavar='LOG_FILENAME',
                        dest="log_filename")
    parser.add_argument("--efile",
                        help="filename of the error file",
                        type=str, default="error.log",
                        metavar='ERROR_FILENAME',
                        dest="error_filename")
    parser.add_argument("--ifile",
                        help=("the filename for where the options are stored"
                              "\nDefault is input.json"),
                        type=str, default="structure.json",
                        metavar='INPUT_FILENAME',
                        dest="input_filename")
    parser.add_argument("-p", "--processes",
                        help=("set the number of processes the script will use."
                        "\nShould be less than or equal to number of CPU cores."
                        "\nIf no N is specified, all available cores are used"),
                        type=int, nargs="?",
                        metavar='N', const=0)
    parser.add_argument("--enable-pausing",
                        help="enable pausing by running a process that checks for input",
                        action="store_true",
                        dest="enable_pausing")
    parser.add_argument("--multi",
                        help=("the name of the level at which multiprocessing will be run."
                              "\nThis should only be used if _only_ mass and elements vary"),
                        nargs='+', type=str, default=[])
    parser.add_argument("--default-excepthook",
                        help="use the default excepthook",
                        action="store_true",
                        dest="default_excepthook")
    parser.add_argument("--disable-filters",
                        help="do not filter log messages",
                        action="store_true",
                        dest="disable_filters")
    parser.add_argument("-r", "--resume",
                        help=("resume from previous checkpoint. If there are"
                              "\nmore than one TALYS-directory, it will choose"
                              "\nthe last directory"),
                        action="store_true")
    parser.add_argument("--dummy",
                        help="for not run TALYS, only create the directories",
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
