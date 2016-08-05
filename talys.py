#! /usr/bin/python
"""
Last updated 5th of August 2016
This script is written to greatly simplify using TALYS. The main features are
- Assign ranges for the TALYS keywords
- Create a clean and customisable directory structure
- Utilise multiprocessing for running several instances of TALYS
  on multiple cores
- Use MPI on a large scale parallel-computing network, such as Abel on UiO

The script is split into logical parts:
- The file readers.py contains a few
  classes responsible for reading input given by the user in differing formats.
  Extending these should be fairly simple, see readers.py for more details.
- tools.py contain miscellaneous functions moved from this file to reduce
  clutter
- This file mainly contains the class Manager which does the largest portion of
  the work. Each of the Manager's methods should ideally only do _one_ task,
  although this is not always feasible. The actual running is done by
  Manager.run(), which in begins a chain of functions. The first functions
  simply iterate through the directory structure and creates the directories,
  while the final functions set up in TALYS input files and multiprocessing.

Use of MPI
MPI is supported, but some remarks about caution must be made. Since fork() is
called, the implementation of MPI used might not put all of the child processes
on different cores, resulting in a catastrophic increase in computing time.
The increase can be anything from 2x to 60x. To prevent this from happening,
use --nooversubscribe and supply mpirun with fewer ranks than what SLURM is
assigning. An example would be
#SBATCH --ntasks 64
mpirun -nooversubscribe -np 50 python talys.py

This script is written in Python 2.7. If the readers wish to use Python 3,
that is entirely possible, as only as few lines is necessary to be changed.

TODO: Add failsafe for multiprocessing
TODO: Check alternatives for os.system on MPI
##########################################
Imports
##########################################
"""

from __future__ import print_function    # Turns print into print()
import numpy as np                       # Linspace
import time                              # Time and date
from itertools import product            # Nested for-loops
import sys                               # Functions to access system functions
import os                                # Functions to access IO of the OS
import shutil                            # High-level file manegement
import platform                          # Information about the platform
import multiprocessing                   # Multiprocessing
import logging                           # Logging progress from the processes
import copy                              # For deepcopy
import traceback                         # To log tracebacks
import subprocess                        # More flexible os.system
from tools import *                      # Functions are put there to remove clutter
from readers import *                    # The input readers

"""
##########################################
Global Variables
##########################################
"""
Z_nr = {'H': '001',  'He': '002', 'Li': '003',  'Be': '004', 'B': '005',   'C': '006',  'N': '007',   'O': '008',  'F': '009',  'Ne': '010',
        'Na': '011', 'Mg': '012', 'Al': '013',  'Si': '014', 'P': '015',   'S': '016',  'Cl': '017',  'Ar': '018', 'K': '019',  'Ca': '020',
        'Sc': '021', 'Ti': '022', 'V': '023',   'Cr': '024', 'Mn': '025',  'Fe': '026', 'Co': '027',  'Ni': '028', 'Cu': '029', 'Zn': '030',
        'Ga': '031', 'Ge': '032', 'As': '033',  'Se': '034', 'Br': '035',  'Kr': '036', 'Rb': '037',  'Sr': '038', 'Y': '039',  'Zr': '040',
        'Nb': '041', 'Mo': '042', 'Tc': '043',  'Ru': '044', 'Rh': '045',  'Pd': '046', 'Ag': '047',  'Cd': '048', 'In': '049', 'Sn': '050',
        'Sb': '051', 'Te': '052', 'I': '053',   'Xe': '054', 'Cs': '055',  'Ba': '056', 'La': '057',  'Ce': '058', 'Pr': '059', 'Nd': '060',
        'Pm': '061', 'Sm': '062', 'Eu': '063',  'Gd': '064', 'Tb': '065',  'Dy': '066', 'Ho': '067',  'Er': '068', 'Tm': '069', 'Yb': '070',
        'Lu': '071', 'Hf': '072', 'Ta': '073',  'W': '074',  'Re': '075',  'Os': '076', 'Ir': '077',  'Pt': '078', 'Au': '079', 'Hg': '080',
        'Tl': '081', 'Pb': '082', 'Bi': '083',  'Po': '084', 'At': '085',  'Rn': '086', 'Fr': '087',  'Ra': '088', 'Ac': '089', 'Th': '090',
        'Pa': '091', 'U': '092',  'Np': '093',  'Pu': '094', 'Am': '095',  'Cm': '096', 'Bk': '097',  'Cf': '098', 'Es': '099', 'Fm': '100',
        'Md': '101', 'No': '102', 'Lr': '103',  'Rf': '104', 'Db': '105',  'Sg': '106', 'Bh': '107',  'Hs': '108', 'Mt': '109', 'Ds': '110',
        'Rg': '111', 'Cn': '112', 'Uut': '113', 'Fl': '114', 'Uup': '115', 'Lv': '116', 'Uus': '117', 'Uuo': '118'}

"""
###########################################
Functions
###########################################
"""


def support_multiprocessing(check_list=False):
    """ A decorator running functions with multiprocessing

    Parameters: check_list: Boolean variable indicating if the given function
                contains a keyword "name". If it does, the keyword "name"
                will be compared with entires in args.multi_list. If
                there is a match, multiprocessing will be used, if not
                the function will be called as normal;
    Returns:    Next level decorator.
    Algorithm:  Create a standard decorator and return it
    Note:       The target function must put the terminating child's PID
                on self.queue.
    """
    def decorator(func):
        def inner(*args, **kwargs):
            """ Lowest level of the decorator
            Parameters: args: The args to the function to be called
                        kwargs: The kwargs to the function to be called
            Algorithm:  If check_list is True, check if the keyword "name
                        is in args.multi_list. If it is, use multiprocessing.
                        If check_list is False, use multiprocessing.
                        Check if the number of active children is under
                        the limit set by --processes. If it is, increment
                        the running_children counter. This is done first to
                        make it less likely that the number of processes
                        exeeds the limit. Run the function and store the
                        PID in a multiprocessing.Manager
                        If the limit is reached, wait at the
                        multiprocessing.Queue for a PID. This PID is then
                        removed from the list over running children and the
                        counter is decremented":"""
            if check_list:
                if kwargs["name"] in args[0].multi_list:
                    do_run = True
                else:
                    do_run = False
            else:
                do_run = True
            if args[0].use_multiprocessing and do_run:
                # Only pause if the limit set by --processes is reached
                if args[0].running_children.value >= args[0].args.processes:
                    args[0].logger.debug("Waiting for available process")
                    pid = args[0].queue.get()
                    # Wait a second to let the process be terminated
                    time.sleep(1)
                    for process in args[0].mps_list:
                        if process == pid:
                            # If it did not terminate, wait till it does
                            #process.join()
                            args[0].logger.debug("Removing %s from list", pid)
                            # Finally, remove it
                            args[0].mps_list.remove(process)
                            args[0].running_children.value -= 1
                            break
                    if args[0].running_children.value >= args[0].args.processes:
                        args[0].logger.exception("PID not on list")
                        raise Exception
                args[0].running_children.value += 1
                job = multiprocessing.Process(
                    target=func,
                    args=args, kwargs=kwargs)
                # Keep a reference to shut them down
                # Start it
                job.start()
                args[0].mps_list.append(job.pid)
            else:
                func(*args, **kwargs)
    
        return inner
    return decorator

"""
###########################################
Classes
###########################################
"""


class Manager:
    """ Creates the directories, manages logging and runs talys """
    def __init__(self, options, args):
        """ Runs when an instance of Manager is created

        Parameters: options: the input options read from file
                    args: the parsed arguments from the terminal
        Returns:    None
        Algorithm:  set the parameters as self, check if using MPI or
                    multiprocessing and set the corresponding flags. Replace
                    the default excepthook and send options to any MPI children
        """
        self.reader = options  # Arguments read from file
        self.args = args       # Arguments read from terminal

        # Check the size given by MPI.COMM to determine if the
        # script is being run by MPI
        self.use_MPI = size > 1
        # Set a multiprocessing flag if running several processes
        if args.processes == 0:
            try:
                self.args.processes = multiprocessing.cpu_count()
            except NotImplementedError:
                sys.exit("Could not find cpu count. Specify -p N") 
        self.use_multiprocessing = self.args.processes > 0
        # Multiprocessing and MPI may not be used in conjunction
        if self.use_MPI and self.use_multiprocessing:
            print("Multiprocessing can not be used with MPI")
            comm.Abort()
        # The number of MPI nodes
        self.mpisize = size
        # Counter to store the total number of TALYS-executions
        self.counter_max = 0
        # Keeps the queues for multiprocessing
        self.queue = multiprocessing.Queue()
        # Counter showing how many child processing are running around
        self.running_children = multiprocessing.Value('i', 0)
        # List containing references to all running children
        self.mps_list = multiprocessing.Manager().list()
        # Names for where multiprocessing will be run
        self.multi_list = args.multi
        # Shared memory resource for keeping track of how many
        # TALYS-executions has been done
        self.counter = multiprocessing.Value('i', 0)
        # Keeps track of the number of running MPI ranks
        self.used_ranks = 1
        # The current MPI rank to send to
        self.send_to_rank = 1

        # Create the root directory named by the current date and time
        self.root_directory = 'TALYS-calculations-{}-{}'.format(
            time.strftime('%y%m%d'), time.strftime('%H%M%S'))
        mkdir(self.root_directory)

        # Initialize and start the logging
        self.init_logger()

        # sys.excepthook is what deals with an unhandled exception
        if not self.args.default_excepthook:
            sys.excepthook = self.excepthook

        # send the input options to the mpichildren
        for n in range(1, self.mpisize):
            self.logger.debug("Sending reader to %s", n)
            comm.send(self.reader, dest=n, tag=1)

    def __enter__(self):
        """ In order to be used with the with-statement """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ Shut down the children when exiting """
        for rank in range(1, self.mpisize):
            print("Sending stop to", rank)
            comm.send(("stop", "stop"), dest=rank)

    def count(self, values):
        """ Find the total number of TALYS runs

        Parameters: values: a list over the keywords
        Returns:    None
        Algorithm:  Iterates through the elements, masses and product, each
                    time increasing the self.counter_max
        """
        elements = self.reader["element"]
        masses = self.reader["mass"]
        for e in elements:
            for m in masses[e]:
                for p in product(*values):
                    self.counter_max += 1

    def init_logger(self):
        """ Set up logging

        This is the best tool to handle information that should either be
        printed to the terminal or written to a file. All of the information
        from both normal and abnormal execution is written to both the terminal
        and to the log file (default name is talys.log), but debugging
        information is also written to the log file. To ease troubleshooting,
        error messages is also written to the error file (default name is
        error.log).
        Parameters: None
        Returns:    None
        Algorithm:  Pick correct multiprocessing logger, add filters to prevent
                    spamming, create file handles and terminal handle and add
                    the handles and filters tot the logger.
        """

        # Use a multiprocessing-safe logger if --processes is set
        if self.use_multiprocessing > 0:
            self.logger = multiprocessing.get_logger()
        else:
            self.logger = logging.getLogger()

        # Create and add a filter to suppress multiprocessing information
        class NoMultiProcessingFilter(logging.Filter):
            def filter(self, record):
                return not "process" in record.getMessage()

        # Create and add a filter to suppress additional multiprocessing info
        class NoMmapFilter(logging.Filter):
            def filter(self, record):
                return not "mmap" in record.getMessage()

        if not self.args.disable_filters:
            self.logger.addFilter(NoMultiProcessingFilter())
            self.logger.addFilter(NoMmapFilter())

        # File Handler - writes log messages to log file
        log_handle = logging.FileHandler(
            os.path.join(self.root_directory, self.args.log_filename))
        log_handle.setLevel(self.args.log)

        # File Handler - writes error messages to error file
        error_handle = logging.FileHandler(
            os.path.join(self.root_directory, self.args.error_filename))
        error_handle.setLevel(logging.ERROR)

        # Console handler - writes log messages to the console
        console_handle = logging.StreamHandler()
        console_handle.setLevel(self.args.verbosity)

        # Formatter - formates the input
        # Something is really buggy here, but by a miracle, it got fixed
        # Do not touch this
        if self.args.debug:
            formatter = logging.Formatter('%(asctime)s - %(processName)-12s - %(levelname)-8s - %(message)s')
        else:
            formatter = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)s')
        log_handle.setFormatter(formatter)
        console_handle.setFormatter(formatter)
        error_handle.setFormatter(formatter)

        # Connect the handlers to the actual logging
        self.logger.addHandler(log_handle)
        self.logger.addHandler(console_handle)
        self.logger.addHandler(error_handle)

        # For debugging purposes
        if self.args.processes > 0:
            self.logger.debug(multiprocessing.current_process().pid)
        if self.use_MPI:
            self.logger.warning("Only rank 0 can use logging")

    def excepthook(self, ex_cls, ex, tb):
        """ Replace the default excepthook

        The excepthook is called when the script experiences an exception.
        In order to log the traceback and ensure termination of the child
        processes, this excepthook replaces the default one
        Parameters: ex_cls: exception class
                    ex: exception instance
                    tb: the traceback
        Returns:    None
        Algorithm: Log the traceback, terminate any active children and exit
                   the program
        """
        # Log the traceback in a readable format
        self.logger.critical(''.join(traceback.format_tb(tb)))
        # Log a short summary of the exception
        self.logger.critical('{0}: {1}'.format(ex_cls.__name__, ex))
        # Kill the kids
        for p in multiprocessing.active_children():
            p.terminate()
        sys.exit()

    def make_info_file(self):
        """ Create the info file and energy file

        Parameters: None
        Returns:    None
        Algorithm:  Write system information and the input options to a file,
                    as well as create the energy file
        """
        padding_size = 20
        # Create file

        outfile = open(os.path.join(self.root_directory, "information.txt"), 'w')
        input = self.reader

        # Write date, time and input  to file
        outfile.write('TALYS-calculations')

        outfile.write('\n{:<{}s} {}'.format(
            "Date:", padding_size, time.strftime('%d %B %Y')))
        outfile.write('\n{:<{}s} {}'.format(
            "Time:", padding_size, time.strftime('%H:%M:%S-%Z')))

        # Write system information
        outfile.write('\n{:<{}s} {}'.format(
            "Platform:", padding_size, platform.platform()))
        outfile.write('\n{:<{}s} {}'.format(
            "Python version:", padding_size, platform.python_version()))

        # Write energy information
        outfile.write('\n\n{:<{}s} {}'.format(
            "name of energy file:", padding_size, input['energy'][0]))
        outfile.write('\n{:<{}s} {}'.format(
            "energy min:", padding_size, input['E1']))
        outfile.write('\n{:<{}s} {}'.format(
            "energy max:", padding_size, input['E2']))
        outfile.write('\n{:<{}s} {}'.format(
            "number of energies:", padding_size, input['N']))

        outfile.write('\n\n{:<{}s} {}'.format(
            "name of input file:", padding_size, input['input_file']))
        outfile.write('\n{:<{}s} {}'.format(
            "name of output file:", padding_size, input['output_file']))
        outfile.write('\n\nVariable input:')

        # Write the rest of the keywords
        for value, key in input.keywords.items():
            if len(key) == 1:
                key = key[0]
            elif isinstance(key, (list)):
                key = json.dumps(key, sort_keys=True)
            elif isinstance(key, (dict)):
                key = json.dumps(key, sort_keys=True)
                #key = json.dumps(key, sort_keys=True, indent=4)
            outfile.write('\n{:<{}s} {}' .format(
                value + ':',  padding_size, key))

        outfile.write('\n\nEnergies: \n')

        if "n" in input["astro"] or "no" in input["astro"]:
            self.astro_yes = False
            # Create energy input
            energies = np.linspace(float(self.reader['E1']),
                                   float(self.reader['E2']),
                                   float(self.reader['N']))
            # Outfile named energy_file
            outfile_energy = open(os.path.join(self.root_directory, self.reader['energy'][0]), 'w')
            # Write energies to energy_file and file in one column
            for Ei in energies:
                # Write energies to file in column
                outfile_energy.write('%.2E \n' % Ei)
                # Write energies to  file in one column
                outfile.write('%.2E \n' % Ei)
            outfile_energy.close()
        else:
            self.astro_yes = True    

        outfile.close()

    def make_input_file(self, keywords, directories):
        """ Creates the inputfile for TALYS

        Parameters: keywords: the input options
                    directories: a dictionary to store the directory names
        Returns:    None
        Alogrithm:  Write a few lines of comment to explain the reaction and
                    write all of the TALYS keywords given in the input
        """
        keywords = copy.deepcopy(keywords)

        # Pop out the keywords that shouldn't be written twice
        projectile = keywords.pop('projectile')
        mass = keywords.pop('mass')
        element = keywords.pop("element")
        energy = keywords.pop('energy')

        # Open the file and begin writing
        outfile_input = open(os.path.join(
            directories["rest_directory"],
            self.reader["input_file"]), 'w')
        # This shows the reaction taking place, e.g 159Eu(n,g)160Eu
        reaction_line = '{}{}({},g){}{}'.format(mass, element, projectile,
                                                int(mass)+1, element)
        outfile_input.write('########################## \n')
        outfile_input.write('##   TALYS input file   ## \n')
        outfile_input.write('##{:^{}}## \n'.format(reaction_line, 22))
        outfile_input.write('########################## \n \n')
        outfile_input.write('# All keywords are explained in README. \n \n')

        outfile_input.write('element {} \n'.format(element))
        outfile_input.write('projectile {} \n'.format(projectile))
        outfile_input.write('mass {} \n'.format(mass))
        if not self.astro_yes:
            outfile_input.write('energy {} \n \n'.format(energy))
        else:
            outfile_input.write('energy 1\n')

        # Write the keyword and corresponding value
        for key, value in keywords.items():
            outfile_input.write('{} {} \n'.format(key, str(value)))

        # Bad things happen if the file isn't closed
        outfile_input.close()

        if not self.astro_yes:
            # Copy energy file  to isotope directory
            src_energy_new = os.path.join(
                self.root_directory, energy)
            dst_energy_input = directories["rest_directory"]
            shutil.copy(src_energy_new, dst_energy_input)

    def run(self):
        """ Simple wrapper for self._run()

        Parameters: None
        Returns:    None
        Algortihm:  If --enable_pausing is not enabled, just call self._run()
                    Otherwise, start self._run() as a subprocess and wait for
                    keystrokes
        """

        if self.args.enable_pausing:
            self.pausing_queue = multiprocessing.Queue()
            self.do_pause = multiprocessing.Value('i', 0)
            running_manager = multiprocessing.Process(target=self._run)
            running_manager.start()
            print("manager is running")
            while True:
                if getkey() == "p":
                    if self.do_pause.value == 0:
                        self.logger.info("PAUSING")
                        self.do_pause.value = 1
                    else:
                        self.logger.info("STARTING")
                        self.do_pause.value = 0
                        self.pausing_queue.empty()
                        self.pausing_queue.put_nowait("pause")
        else:
            self._run()
            

    def _run(self):
        """ Sets up the logging, and creates the root directory

        Parameters: None
        Returns:    None
        Algorithm:  Create the root directory, make the info file and the
                    original and result directories, then run self.run_deeper
                    which creates the nested directories and runs TALYS
                    appropriatley
        """
        start = time.time()
        # Do a deepcopy to prevent multiprocessing mixing
        keywords = copy.deepcopy(self.reader.keywords)

        # directories keep the values of each file path and directory path
        # to 1) make it possible to add to it 2) prevent subprocesses from
        # adding and removing from eachothers directories 3) make it easier
        # to send names and paths through functions
        directories = {}

        directories["root_directory"] = self.root_directory

        # Make the info file.
        self.make_info_file()

        # In the root directory, create a new directory to store the computations
        directories["original_data"] = os.path.join(
            directories["root_directory"], "original_data")
        mkdir(directories["original_data"])

        # In the root directory, create a new direcotry to store the results
        directories["results_data"] = os.path.join(
            directories["root_directory"], "results_data")
        mkdir(directories["results_data"])

        # Change the "current" directories. The working directory doesnt
        # actually change
        directories["current_orig"] = directories["original_data"]
        directories["current_res"] = directories["results_data"]

        keywords["Z_nr"] = Z_nr
        structure = [
            {"element": "{Z_nr[element]}{element}"},
            {"mass": "{mass}{element}"},
            {"rest": ""},
        ]
        # Run the rest
        self.run_deeper(keywords, directories, structure)

        # When the script has completed, log the total time
        elapsed = time.strftime("%H:%M:%S", time.localtime(time.time() - start))
        self.logger.info("Total elapsed time: %s", elapsed)

    def run_deeper(self, keywords, directories, structure):
        """ A recursive function that creates the directory structure

        Parameters: keywords: the input keywords
                    directories: a dictionary to store the directory names
                    structure: a list of {name:style} describing the directory
                    names. Index 0 is the top of the directory, with each
                    subsequent directory having some knowledge of the previous,
                    ex. [{"element":"{element}"}, {"rest":""}]
        Returns:    None
        Algorithm:  Iterate through structure, running talys if name=
                    "rest" else create directories and call itself
        """
        # Deepcopy the mutable variables to prevent processing mixup
        structure = copy.deepcopy(structure)
        keywords = copy.deepcopy(keywords)
        directories = copy.deepcopy(directories)

        # Create an instance of the custom formatter
        fmt = StyleFormatter()

        # Iterate through the list consiting of [{name:style}, {name:style} ...]
        for name, style in structure[0].items():
            # The for loop is needed to keep the iteration going, but in
            # reality it is only iterating through 1 element. Instead
            # the list is shrunk by deleting the newly used element
            del structure[0]

            # If the name is "rest", talys will be run
            if name == "rest":
                self.run_rest(keywords, directories)
            else:
                # If not, create the directories and go to the next level
                # tmp_keywords is used if the keyword is a dict in order to
                # store the resulting list
                tmp_keywords = copy.deepcopy(keywords)
                if isinstance(keywords[name], (dict)):
                    # ex. keywords["prev_keyword"] = "Pr"
                    #     keywords["mass"] = {"Pr":[128, 129], "Sm":[158, 159, 160]}
                    #     tmp_keywords["mass"] = [128, 129]
                    tmp_keywords[name] = keywords[name][keywords["prev_keyword"]]

                # new_keywords is to overwrite the keywords[name] without
                # interfeering with the next iteration of the loop
                new_keywords = copy.deepcopy(tmp_keywords)
                current_orig = directories["current_orig"]
                current_res = directories["current_res"]
                for keyword in tmp_keywords[name]:
                    # ex. tmp_keywords["element"] = ["Pm", "Sm", "Tb"]
                    #     keyword = "Pm"
                    #     new_keywords["element"] = "Pm"
                    new_keywords[name] = keyword
                    self.run_deeper_useless_function(keywords=new_keywords,
                                                     directories=directories,
                                                     keyword=keyword,
                                                     current_orig=current_orig,
                                                     current_res=current_res,
                                                     name=name,
                                                     style=style,
                                                     structure=structure)

    @support_multiprocessing(check_list=True)
    def run_deeper_useless_function(self, keywords, directories, keyword,
                                    current_orig, current_res, name,
                                    style, structure):
        """ Split from run_deeper to support multiprocessing """
        fmt = StyleFormatter()
        # Create the directories with names according to the style
        directories["current_orig"] = os.path.join(
            current_orig, fmt.format(style, **keywords))
        directories["current_res"] = os.path.join(
            current_res, fmt.format(style, **keywords))
        mkdir(directories["current_orig"])
        mkdir(directories["current_res"])
        # This is an ugly piece of code. Since the "mass" keyword
        # is dependent on the current element, the current element
        # must be stored for this function to work
        keywords["prev_keyword"] = keyword
        self.run_deeper(keywords, directories, structure)
        if self.use_multiprocessing and False:
            self.logger.debug("%s is terminating",
                              multiprocessing.current_process().pid)
            self.queue.put(multiprocessing.current_process().pid)


    def run_rest(self, keywords, directories):
        """ Creates the name of the final directory and calls self.run_talys()

        The format is keyword1value-keyword2value-...-conditional1name -
        conditional1value-conditional2name-conditional2value-...
        in alphabetical order
        Parameters: keywords: the input options
                    directories: a dictionary over the directory names
        Returns:    None
        Algorithm:  Sort the keywords, combine and iterate over the keywords
                    and conditionals, set up and handle the multiprocessing,
                    create the final directory and run self.run_talys()
        """

        # deepcopy the mutable variables to prevent processing mixup
        keywords = copy.deepcopy(keywords)
        directories = copy.deepcopy(directories)

        # Z_nr and prev_keyword were added in the previous loop. Remove them
        del keywords["Z_nr"]
        del keywords["prev_keyword"]

        keys = []
        values = []
        talys_keywords = {}

        # Put the keys in alphabetical order
        sorted_keys = keywords.keys()
        sorted_keys.sort()
        for key in sorted_keys:
            # Only use keywords that vary, and astro
            if (len(self.reader[key]) > 1
                and key != "element"
                and key != "mass"):
                #)   or key == "astro":
                # the next two lists are in alphabetical order, and
                # corresponding key-value pair have the same index
                keys.append(key)
                values.append(keywords[key])
            else:
                talys_keywords[key] = keywords[key]
        # 1) append the conditional names to the keywords, since they
        # are the one to be chosen from. This is undone in 2)
        for condition in self.reader.conditionals:
            values.append(condition.keys())

        # Deal with epr, gpr, spr
        if len(self.reader.nesteds.keys()) > 0:
            for key, value in self.reader.nesteds[keywords["element"]][str(keywords["mass"])].items():
                talys_keywords[key] = "{} {} {} M1".format(int(Z_nr[keywords["element"]]),
                                                       int(keywords["mass"])+1,
                                                       value)

        # The queue is used to track the completed subprocesses.
        # A queue is used since it is multiprocessing-safe
        self.talys_queue = multiprocessing.Queue()
        # talys_jobs contains the subprocesses
        talys_jobs = []
        # Set the counter to inform the user on the progress
        # It is at this stage that the script knows how many iterations it
        # must do, so the counter_max is set only once - during the first run
        if self.counter_max == 0:
            self.count(values)
        # current_rank keeps track of how many available ranks there are
        # send_to_rank stores the rank to which information will be sent
        for value in product(*values):
            # If --enable_pausing is set, check if execution shall pause
            if self.args.enable_pausing:
                if self.do_pause.value == 1:
                    self.logger.debug("Waiting to be restarted...")
                    self.pausing_queue.get()
                    self.logger.debug("Restarting")
            # 2) splits the result back into keywords and conditions
            keywordvals = value[:len(keys)]
            conditionkeys = value[len(keys):]
            # Name the directory according to the alphabetical order
            # of the keywords
            name = ''
            for i in range(len(keywordvals)):
                # Add to the name
                name = "{}-{}".format(name, keywordvals[i])
                # add the now one-option keyword to talys_keywords
                talys_keywords[keys[i]] = keywordvals[i]

            # Remove the unecessary -
            name = name[1:]

            # Furthermore, name the directory accoring to the chosen condition
            for key in conditionkeys:
                value = self.reader.get_condition_val(key)
                name = "{}-{}-{}".format(name, key, value)
                talys_keywords[key] = value

            keywords["name"] = name

            # Make all values to non-lists
            for key, val in talys_keywords.items():
                if isinstance(val, (list, tuple)):
                    talys_keywords[key] = val[0]

            # Make the directories
            if name:
                directories["rest_directory"] = os.path.join(
                    directories["current_orig"], name)
                mkdir(directories["rest_directory"])
            else:
                # If nothing varies, name the directories by a counter
                directories["rest_directory"] = directories["current_orig"]

            # Make input file
            try:
                self.make_input_file(talys_keywords, directories)
            except Exception as exc:
                # No biggie. Just print an error and move on
                self.logger.error("An error occured with %s: %s", name, exc)
                continue

            # Run TALYS
            if self.use_MPI:
                if self.used_ranks >= self.mpisize:
                    self.logger.debug("Waiting for available rank")
                    try:
                        self.send_to_rank, execution_time = comm.recv(source=MPI.ANY_SOURCE)
                        self.logger.info('(%s/%s) %s',self.counter.value,
                                         self.counter_max,
                                         execution_time)
                        self.counter.value += 1
                    finally:
                        self.logger.debug("Sending to %s", self.send_to_rank)
                    self.used_ranks -= 1
                comm.send((keywords, directories), dest=self.send_to_rank)
                self.used_ranks += 1
                self.send_to_rank = self.used_ranks
            else:
                # No kind of multiprocessing
                self.run_talys(keywords=keywords, directories=directories)

    @support_multiprocessing()
    def run_talys(self, keywords, directories):
        """ Runs TALYS

        Parameters: keywords: the input options
                    directories: a dictionary over the names of the directories
        Algorithm:  call system.fork() to run TALYS, and redirect the system
                    signals and standard outputs to this python script. Log
                    any errors and execution time
        """
        # Deepcopy the directories list to prevent multiprocessing mixup
        directories = copy.deepcopy(directories)
        directories["current_orig"] = directories["rest_directory"]

        # Actually run TALYS and time its execution
        start = time.time()
        with Cd(directories["current_orig"]):
            process = subprocess.Popen('talys <{}> {}'.format(
                self.reader["input_file"],
                self.reader["output_file"]),
                # Do not send signals to the subprocess
                preexec_fn=os.setpgrp,
                # Spawn a shell
                shell=True,
                # Send both stdout and stderr to pipe.stdout
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                # Don't know
                close_fds=True)
        # Get STDOUT and STDERR and see if they are non-empty
        # (Both are sent to STDOUT)
        stdout, _ = process.communicate()
        if stdout:
            self.logger.critical("TALYS could not be run: %s", stdout.rstrip())
            return

        elapsed = time.strftime("%M:%S", time.localtime(time.time() - start))
        info = "{mass}{element}-{name}".format(**keywords) if keywords["name"] else "{mass}{element}".format(**keywords)
        self.counter.value += 1
        self.logger.info("(%s/%s) Execution time: %s by %s", self.counter.value,
                         self.counter_max, elapsed, info)

        # Move result file to
        # TALYS-calculations-date-time/result_files/element/isotope
        try:
            for filename in self.reader["result_files"]:
                name = "{}-{}".format(keywords["name"], filename) if keywords["name"] else filename
                shutil.copy(os.path.join(directories["current_orig"], filename),
                            os.path.join(directories["current_res"],
                                         name))
        except Exception as exc:
            # Give TALYS some time to write the output.txt
            time.sleep(1)

            self.logger.error(exc)
            # The filesize of output_file is an indicator of whether the
            # execution was successful or not
            path = os.path.join(directories["current_orig"],
                                self.reader["output_file"])
            if os.path.getsize(path) < 600:
                # execution failed. Open the file and log the output
                with open(path, "r") as output_file:
                    msg = ''.join(output_file.readlines()).rstrip()
                self.logger.error(msg[1:])

        # Tell the parent process that the child has finnished
        # The purpose of this is to let the next process begin
        self.logger.debug("%s is terminating",
                          multiprocessing.current_process().pid)
        self.queue.put(multiprocessing.current_process().pid)


# For MPI
class ChildRunner(Manager):
    # Remove Manager's init
    def __init__(self, rank):
        self.rank = rank
        self.use_MPI = True
        self.reader = comm.recv(source=0, tag=1)
        self.wait_for_root()

    def wait_for_root(self):
        """ Waits for commands from the script running as rank 0
        Parameters: None
        Returns:    None
        Algorithm:  For eternity, get commands from rank 0, break execution if
                    commanded to do so, and run talys if commanded to do so
        """
        while True:
            try:
                keywords, directories = comm.recv(source=0)
                if "stop" in directories:
                    break
                self.run_talys(keywords, directories)
                comm.send((self.rank, self.execution_time), dest=0)
            except Exception as e:
                print("An error occured: ", e)

    def run_talys(self, keywords, directories):
        """ Runs TALYS

        Parameters: keywords: the input options
                    directories: a dictionary over the names of the directories
        Algorithm:  call system.fork() to run TALYS, and redirect the system
                    signals and standard outputs to this python script. Log
                    any errors and execution time
        """
        directories["current_orig"] = directories["rest_directory"]

        shutil.copy("talys", directories["current_orig"])

        # Actually run TALYS and time its execution
        start = time.time()
        with Cd(directories["current_orig"]):
            os.system("./talys <{}> {}".format(
                self.reader["input_file"],
                self.reader["output_file"]))
            os.remove("talys")

        elapsed = time.strftime("%M:%S", time.localtime(time.time() - start))
        info = "{mass}{element}-{name}".format(**keywords) if keywords["name"] else "{mass}{element}".format(**keywords)
        # When running MPI, the scripts has no knowlegde of neither the
        # logger nor the counters
        self.execution_time = "Execution time: {} by {}".format(elapsed, info)
        # Move result file to
        # TALYS-calculations-date-time/result_files/element/isotope
        try:
            for filename in self.reader["result_files"]:
                name = "{}-{}".format(keywords["name"], filename) if keywords["name"] else filename
                shutil.copy(os.path.join(directories["current_orig"], filename),
                            os.path.join(directories["current_res"],
                                         name))
        except Exception as exc:
            print("Error: ", exc)

# Keep the script from running if imported as a module
if __name__ == "__main__":
    try:
        # Set up MPI. This must always be first
        from mpi4py import MPI
        # The almighty communicator. Communicates messages between the nodes
        # in a supercomputing cluster
        comm = MPI.COMM_WORLD
        # The rank is the current process' ID
        rank = comm.Get_rank()
        # Size is the number of processes
        size = comm.Get_size()
    except ImportError:
        rank = 0
        size = 1

    # Only the root process, 0, shall create the directories
    if rank == 0:
        # Handle the arguments from terminal
        args = get_args()

        # Set up  logging
        try:  # Python 2.7+
            from logging import NullHandler
        except ImportError:
            class NullHandler(logging.Handler):
                def emit(self, record):
                    pass

        # Had a bug, this fixed it. It should't have, but it did. Leave it be
        if args.debug:
            logging.basicConfig(level=logging.DEBUG, filename=args.log_filename,
                                filemode="w", format="%(asctime)s - %(processName)-12s -  %(levelname)-8s - %(message)s")
        else:
            logging.basicConfig(level=logging.DEBUG, filename=args.log_filename,
                                filemode="w", format="%(asctime)s - %(levelname)-8s - %(message)s")
        logging.getLogger("__name__").addHandler(NullHandler())

        # Get the options
        options = Json_reader(args.input_filename)
        print("Loaded ", args.input_filename)

        # Create an instance of Manager to run the simulations
        with Manager(options=options, args=args) as simulations:
            simulations.run()
    else:
        # The other processes run TALYS, but must wait for root
        ChildRunner(rank)

