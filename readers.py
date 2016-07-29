"""
This module contains the classes that reads
the input from the user.
"""

from tools import make_iterable
import json

class Basic_reader(object):
    """ A basic reader to build upon """
    def __init__(self):
        """ Make the variables
            Parameters: None
            Returns:    None
            Algorithm   Simply set the variables
        """
        # contains the keywords
        self.keywords = {}
        # contains those keywords that depend on another keyword
        self.conditionals = []
        # contains the keywords related to the script
        self.script_keywords = {}

    def __getitem__(self, index, s=False):
        """ Reader[index] first tries to return Reader.keywords[index]
        and if it fails, returns Reader.script_keywords[index]
        """
        if s:
            return self.script_keywords[index]
        else:
            try:
                return self.keywords[index]
            except KeyError:
                return self.script_keywords[index]

    def convert(self, var):
        try:
            return float(var)
        except Exception as e:
            return var

    def get_condition_val(self, key):
        """ Return the value for a given key in conditionals
        Example:
        >>> A = [{"sheep":2, "cow":1}, {"cat":4}, {"dog":0}]
        >>> print get_condition_val(A, cat)
        4
        """
        for c in self.conditionals:
            if key in c.keys():
                return c[key]


class Json_reader(Basic_reader):
    """ Parses input from json file """
    def __init__(self, filename):
        """ Reads the json file and puts the result into the correct variables

            Parameters: filename: the name of the json file
            Returns:    None
            Algorithm:  Call super's init, read the json file, put the
                        variables into the correct containers
        """
        # Call the parent's __init__
        super(Json_reader, self).__init__()

        # Read the json file
        with open(filename) as rFile:
            data = json.load(rFile)

        # fill self.keywords
        for key, value in data["keywords"].items():
            if key != "comment":
                self.keywords[key] = self.convert(value)
        self.keywords = make_iterable(self.keywords)


        # fill self.conditionals
        for value in data["conditionals"].values():
            if isinstance(value, dict):
                self.conditionals.append(value)


        # fill self.script_keywords
        for key, value in data["script_keywords"].items():
            if key != "comment":
                self.script_keywords[key] = self.convert(value)

        #self.structure = data["structure"]


class Python_reader(Basic_reader):
    """ Parses input from python file. NB: DOESN'T WORK """
    def __init__(self, filename):
        """ Reads the python file and puts the result into the correct
            variables
        
            Parameters: filename: the name of the python file
            Returns:    None
            Algorithm:  Call super's init, read the python file, put the
                        variables into the correct containers
        """
        # Call parent's __init__
        super(Python_reader, self).__init__()

        # Read the python file
        options = __import__(filename)

        for key, value in talys_options.__dict__.iteritems():
            # Do not import __name__s
            if '__' not in key:
                if 'k_' not in key:
                    # TALYS keywords
                    self.keywords[key] = value
                else:
                    # Script keywords
                    self.script_keywords[key[2:]] = value


class BRUSLIB_reader(Basic_reader):
    """ Parses input for files in a BRUSLIB format """
    def __init__(self, filename):
        """ Reads the file and puts the result into the correct
            variables

            Parameters: filename: the name of the file
            Returns:    None
            Algorithm:
        """
        import re

        # Call parent's __init__
        super(BRUSLIB_reader, self).__init__()

        elements = []
        mass = {}
        # Match 63eu96 103 or 26fe41, ect
        pattern = re.compile("(\d{1,3})(\w\w?)(\d{1,3})\s?(\d{1,3})?")
        # Match E1 2.5E-6 or E2 5673.23, etc
        energy_pattern = re.compile("(E[1,2])\s+((?:0|[1-9]\d*)(?:\.\d*)?(?:[eE][+\-]?\d+))")
        with open(filename, 'r') as rFile:
            for line in rFile:
                line = line.rstrip()
                match = re.match(pattern, line)
                energy_match = re.match(energy_pattern, line)
                if not line:
                    continue
                elif match is not None:
                    # Iterate over the range, if given
                    start = int(match.group(3))
                    end = int(match.group(4))+1 if match.group(4) is not None else start+1
                    element = match.group(2)
                    elements.append(element)
                    mass[element] = []
                    for neutrons in range(start, end):
                        # mass = neutrons + protons
                        mass[element].append(neutrons+int(match.group(1)))
                elif energy_match is not None:
                    self.keywords[energy_match.group(1)] = float(energy_match.group(2))
                else:
                    print("{} is of invalid format".format(line))
        self.keywords["element"] = elements
        self.keywords["mass"] = mass
