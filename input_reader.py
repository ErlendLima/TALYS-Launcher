"""
This module contains the classes that reads
the input from the user.
"""

from tools import make_iterable
import json

class Basic_reader(object):
    """ A basic reader to build upon """
    def __init__(self, filename):
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
        # call the parent's __init__
        super(Json_reader, self).__init__(filename)

        # read the json file
        with open(filename) as rFile:
            data = json.load(rFile)

        # fill self.keywords
        for key, value in data["keywords"].iteritems():
            if key != "comment":
                self.keywords[key] = value
        self.keywords = make_iterable(self.keywords)


        # fill self.conditionals
        for value in data["conditionals"].values():
            if isinstance(value, dict):
                self.conditionals.append(value)


        # fill self.script_keywords
        for key, value in data["script_keywords"].iteritems():
            if key != "comment":
                self.script_keywords[key] = value

        self.structure = data["structure"]

class Python_reader(Basic_reader):
    """ Parses input from python file """
    def __init__(self, filename):
        # call parent's __init__
        super(Python_reader, self).__init__(filename)

        # read the python file
        options = __import__(filename)

        for key, value in talys_options.__dict__.iteritems():
            # Do not import __name__s
            if '__' not in key:
                if 'k_' not in key:
                    # TALYS keywords
                    self.keywords[key] = value
                else:
                    # script keywords
                    self.script_keywords[key[2:]] = value
