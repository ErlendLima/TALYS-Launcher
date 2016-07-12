#! /usr/bin/python
"""
##########################################
Imports
##########################################
"""

from __future__ import print_function  # To write to stderr
import numpy as np
import time                                              # Time and date
from itertools import product                  # Nested for-loops
import sys                                              # Functions to access system functions
import os                                                # Functions to access IO of the OS
import shutil                                           # High-level file manegement
import platform                                      # Information about the platform
import multiprocessing                         # Multiprocessing
import logging                                       # Logging progress from the processes
import argparse                                    # Parsing arguments given in terminal
import copy                                          # For deepcopy
#from enum import Enum                      # Enumeration for levels of verbosity and logging
import logging                                      # Manages logging
import traceback
import datetime

"""
##########################################
Global Variables
##########################################
"""
Z_nr = {'H':'001',  'He':'002', 'Li':'003',  'Be':'004', 'B':'005',   'C':'006',  'N':'007',   'O':'008',  'F':'009',  'Ne':'010', 
		'Na':'011', 'Mg':'012', 'Al':'013',  'Si':'014', 'P':'015',   'S':'016',  'Cl':'017',  'Ar':'018', 'K':'019',  'Ca':'020', 
		'Sc':'021', 'Ti':'022', 'V':'023',   'Cr':'024', 'Mn':'025',  'Fe':'026', 'Co':'027',  'Ni':'028', 'Cu':'029', 'Zn':'030', 
		'Ga':'031', 'Ge':'032', 'As':'033',  'Se':'034', 'Br':'035',  'Kr':'036', 'Rb':'037',  'Sr':'038', 'Y':'039',  'Zr':'040', 
		'Nb':'041', 'Mo':'042', 'Tc':'043',  'Ru':'044', 'Rh':'045',  'Pd':'046', 'Ag':'047',  'Cd':'048', 'In':'049', 'Sn':'050', 
		'Sb':'051', 'Te':'052', 'I':'053',   'Xe':'054', 'Cs':'055',  'Ba':'056', 'La':'057',  'Ce':'058', 'Pr':'059', 'Nd':'060', 
		'Pm':'061', 'Sm':'062', 'Eu':'063',  'Gd':'064', 'Tb':'065',  'Dy':'066', 'Ho':'067',  'Er':'068', 'Tm':'069', 'Yb':'070', 
		'Lu':'071', 'Hf':'072', 'Ta':'073',  'W':'074',  'Re':'075',  'Os':'076', 'Ir':'077',  'Pt':'078', 'Au':'079', 'Hg':'080', 
		'Tl':'081', 'Pb':'082', 'Bi':'083',  'Po':'084', 'At':'085',  'Rn':'086', 'Fr':'087',  'Ra':'088', 'Ac':'089', 'Th':'090', 
		'Pa':'091', 'U':'092',  'Np':'093',  'Pu':'094', 'Am':'095',  'Cm':'096', 'Bk':'097',  'Cf':'098', 'Es':'099', 'Fm':'100', 
		'Md':'101', 'No':'102', 'Lr':'103',  'Rf':'104', 'Db':'105',  'Sg':'106', 'Bh':'107',  'Hs':'108', 'Mt':'109', 'Ds':'110', 
		'Rg':'111', 'Cn':'112', 'Uut':'113', 'Fl':'114', 'Uup':'115', 'Lv':'116', 'Uus':'117', 'Uuo':'118'}

"""
###########################################
Functions
###########################################
"""



def import_options():
        """ Import the the options. Returns the options in a dict """

        import talys_options

        user_input_keys    = []
        user_input_values = []
        for key, value in talys_options.__dict__.iteritems():
                if '__' not in key:
                        user_input_keys.append(key)
                        user_input_values.append(value)

        user_input_dict = dict(zip(user_input_keys, user_input_values))
        return user_input_dict

def count_combinations(options):
        """ Returns the combinations of the options to be run """
        elements = len(options["element"])
        masses = 0
        for e in options["element"]:
                masses += len(options["mass"][e])
        astro = len(options["astro"])
        rest = 0
        options = make_iterable(options)
        for mm, lm, s, o  in product(options['massmodel'], options['ldmodel'], options['strength'], options['optical']):
                rest += 1
        return astro, elements, masses, rest, astro*masses*rest

def correct(input_argument):
	""" Function to check syntax of input arguments given by user """

	if input_argument in('n', 'no'):
		return 'no'
	
	elif input_argument in('y', 'yes'):
		return 'yes'
	
	## if input argument is given incorrectly, function returns 'error'
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
			# ## put single input noe iterable into talys_input
			# talys_input[key] = user_input[key]
			# ## put single entries into list if iterable variable
			# user_input[key] = [user_input[key]]

	## #check if every item in user given list is unique
	for key, value in new_dict.iteritems():

		try:
			## if variable tuple or list => new list with value only once
			if len(set(value)) != len(value):
				newlist = []
				for val in value:
					if val not in newlist:
						newlist.append(val)
				                new_dict[key] = newlist
		                                
		except TypeError:
			## if variable == dict => new dict with value only once inside user_input[key]
			for keys, values in value[0].iteritems():
				if len(set(values)) != len(values):
					newlist = []
					for val in values:
						if val not in newlist:
							newlist.append(val)
					                value[0][keys] = newlist

				new_dict[key] = value[0]
        return new_dict


"""
##########################################
Classes
##########################################
"""
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

# class Log:
# 	""" Simplifies logging """
# 	def __init__(self, log_level=Log_level.INFO, verbosity=Verbosity_level.NOTHING, log_filename="log.txt", output_channel=sys.stdout):
# 		self.log_level = log_level
# 		self.verbosity = verbosity
# 		self.filename = log_filename
# 		self.output_channel = output_channel
# 		if self.verbosity >= Verbosity_level.DEBUG:
# 			self.write(stamp("Log level: {}".format(self.log_level)))
# 			self.write(stamp("Verbosity: {}".format(self.verbosity)))
# 			self.write(stamp("Writing to {}".format(self.filename)))

# 	def __call__(self, msg, vThreshold=Verbosity_level.NOTHING, lThreshold=Log_level.NOTHING, **kwargs):
# 		""" Writes to log and to stdout/stderr depending on levels """
# 		if self.verbosity > vThreshold:
# 			self.write(stamp(msg), **kwargs)
# 		if self.log_level > lThreshold:
# 			self.queue.put(stamp(msg))
		
# 	def start(self, top_directory):
# 		""" Set up the logging server """
# 		if self.log_level > Log_level.NOTHING:
# 			if self.verbosity > Verbosity_level.NOTHING:
# 				self.write(stamp("Starting server"))
# 			self.queue = mutliprocessing.Queue()
# 			self.server = multiprocessing.Process(target=self.run_server, args=(top_directory,))
# 			self.server.start()

# 	def run_server(self, top_directory):
# 		""" Reads from queue and writes to file """
# 		self.server_is_running = True
# 		with open(os.paths.join(top_directory, self.log_filename), "a") as log:
# 			while self.server_is_running:
# 				msg = self.queue.get()
# 				log.write("{}\n".format(msg))

# 	def write(self, *args, **kwargs):
# 		""" Prints to the specified channel """
# 		output_channel = self.output_channel if "file" not in kwargs else kwargs["file"]
# 		print(*args, file=output_channel, **kwargs)

class Manager:
        """ Runs the simulations """
        def __init__(self, user_input, args):
                self.user_input = user_input            # Arguments read from file
                self.args = args                               # Arguments read from terminal

        def init_logger(self):
	        """ Set up logging"""
                self.logger = multiprocessing.get_logger()

                # File Handler
                self.file_handle = logging.FileHandler(os.path.join(self.top_directory, self.args.lfilename))
                self.file_handle.setLevel(self.args.log)
                # Console handler
                self.console_handle = logging.StreamHandler()
                self.console_handle.setLevel(self.args.verbosity)
                # Formatter
                formatter = logging.Formatter('%(asctime)s - %(processName)s -  %(levelname)s - %(message)s')
                self.file_handle.setFormatter(formatter)
                self.console_handle.setFormatter(formatter)
                
                self.logger.addHandler(self.file_handle)
                self.logger.addHandler(self.console_handle)
                
                sys.excepthook = self.excepthook
                
        def excepthook(self, ex_cls, ex, tb):
                """ Kill all children when script crashes """
                self.logger.critical(''.join(traceback.format_tb(tb)))
                self.logger.critical('{0}: {1}'.format(ex_cls, ex))
                for p in multiprocessing.active_children():
                        p.terminate()
                sys.exit()

        def make_info_file(self):
                """ Create the  file and energy file """
                padding_size = 20
                ## create file
                file = '%s-.txt' %self.top_directory
                date_file = time.strftime('%d %B %Y')
                time_file = time.strftime('%H:%M:%S-%Z')

                outfile = open(file, 'w')
                input = dict(self.user_input)

                ## write date, time and input  to file
                outfile.write('TALYS-calculations')

                outfile.write('\n{:<{}s} {}'.format("Date:", padding_size, date_file))
                outfile.write('\n{:<{}s} {}'.format("Time:", padding_size, time_file))

                # write system information
                outfile.write('\n{:<{}s} {}'.format("Platform:", padding_size, platform.platform()))
                outfile.write('\n{:<{}s} {}'.format("Python version:", padding_size, platform.python_version()))

                # write energy information
                outfile.write('\n\n{:<{}s} {}'.format("name of energy file:", padding_size, input['energy_file']))
                outfile.write('\n{:<{}s} {}'.format("energy min:", padding_size, input['E1']))
                outfile.write('\n{:<{}s} {}'.format("energy max:", padding_size, input['E2']))
                outfile.write('\n{:<{}s} {}'.format("energy step:", padding_size, input['step']))

                outfile.write('\n\n{:<{}s} {}'.format("name of input file:", padding_size, input['input_file']))
                outfile.write('\n{:<{}s} {}'.format("name of output file:", padding_size, input['output_file']))
                outfile.write('\n\nVariable input:') 

                for value, key in input.iteritems():
                        outfile.write('\n{:<{}s} {}' .format(value+':',  padding_size, key))

                outfile.write('\n\nEnergies: \n')

                ## create energy input 
                energies = np.linspace(float(self.user_input['E1'][0]), float(self.user_input['E2'][0]), float(self.user_input['step'][0]))
                ## outfile named energy_file 
                outfile_energy = open(self.user_input['energy_file'][0], 'w')
                ## write energies to energy_file and file in one column
                for Ei in energies:
                        outfile_energy.write('%.2E \n' %Ei) # write energies to file in column
                        outfile.write('%.2E \n' %Ei) # write energies to  file in one column

                outfile_energy.close()
                outfile.close()

                ## move energy_file and info_file to:
                ## > TALYS-calculations-date-time
                src_energy = self.user_input['energy_file'][0]
                src = file
                dst_energy = self.top_directory
                shutil.move(src_energy, dst_energy)
                shutil.move(src, dst_energy)

        def make_header(self, talys_input, variable_directory, optical):
                talys_input2 = copy.deepcopy(talys_input)
                ## copy of input_dictionary => able to delete items and iterate over the rest
                m, e, o = talys_input2['mass'], talys_input2['element'], optical
                ## need projectile, input_file, output_file twice
                projectile = talys_input2.pop(['projectile'][0])
                input_file = talys_input2.pop('input_file')

                outfile_input = open(os.path.join(variable_directory, self.user_input["input_file"][0]), 'w')
                outfile_input.write('###################### \n')
                outfile_input.write('## TALYS input file ## \n')
                outfile_input.write('##  {}{}({},g){}{}   ## \n'.format(m, e, projectile, m+1, e))
                outfile_input.write('###################### \n \n')
                outfile_input.write('# All keywords are explained in README. \n \n')

                outfile_input.write('element {} \n'.format(e))
                outfile_input.write('projectile {} \n'.format(projectile))
                outfile_input.write('mass {} \n'.format(m))
                outfile_input.write('energy {} \n \n'.format(talys_input2.pop('energy_file')))
                outfile_input.write('{}\n'.format(o))

                talys_input2.pop('element')
                talys_input2.pop('mass')
                talys_input2.pop('E1')
                talys_input2.pop('E2')
                talys_input2.pop('step')
                talys_input2.pop('output_file')
                talys_input2.pop('optical')

                for key, value in talys_input2.iteritems():
                        outfile_input.write('{} {} \n'.format(key, str(value)))

                outfile_input.close()

                ## Copy energy file  to isotope directory
                ## new src energy file
                src_energy = self.user_input['energy_file'][0]
                src_energy_new = '{}/{}'.format(self.top_directory, src_energy)
                ## dst input file > variable directory
                dst_energy_input = variable_directory

                ## copy energy file to variable directory
                shutil.copy(src_energy_new, dst_energy_input)

        def run_element(self, element, talys_input, directories):
                """ Manages the element-option """
                talys_input = copy.deepcopy(talys_input)
                directories = copy.deepcopy(directories)
                talys_input['element'] = element
                a = talys_input['astro']

                ## mkdir: > TALYS-calculations-date-time/original_data/astro-a/ZZ-X
                element_original = '%s/Z%s-%s' %(directories["astro_original"], Z_nr[element], element)
                directories["element_original"] = element_original
                mkdir(element_original)

                ## mkdir: > TALYS-calculations-date-time/result_data/astro-a/ZZ-X
                element_results = '%s/Z%s-%s' %(directories["astro_results"], Z_nr[element], element)
                directories["element_results"] = element_results
                mkdir(element_results)
                mass_jobs = []
                for mass in self.user_input['mass'][element]:
                        if self.args.multi_mass:
                                """ Use multiprocessing for each mass """
                                mass_job = multiprocessing.Process(target=self.run_mass,
                                                                   args=(mass, talys_input, directories, ))
                                mass_jobs.append(mass_job)
                                mass_job.start()
                        else:
                                self.run_mass(mass, talys_input, directories)

                # Wait for the mass_jobs to complete
                for mass_job in mass_jobs:
                        mass_job.join()
                        

        def run_mass(self, mass, talys_input, directories):
                """ Manages the mass-option """
                talys_input = copy.deepcopy(talys_input)
                directories = copy.deepcopy(directories)
                talys_input['mass'] = mass
                m = mass
                e = talys_input['element']
                a = talys_input['astro']

                ## mkdir: > TALYS-calculations-date-time/original_data/astro-a/ZZ-X/isotope
                isotope_original = '%s/%g%s' %(directories["element_original"], m, e)
                directories["isotope_original"] = isotope_original
                mkdir(isotope_original)

                ## mkdir: > TALYS-calculations-date-time/result_data/astro-a/ZZ-X/isotope
                isotope_results = '%s/%g%s' %(directories["element_results"], m, e)
                directories["isotope_results"] = isotope_results
                mkdir(isotope_results)

                # Reset talys job list
                talys_jobs = []
                self.talys_queue = multiprocessing.Queue()
                for mm, lm, s, o in product(self.user_input['massmodel'], self.user_input['ldmodel'], self.user_input['strength'], self.user_input['optical']):

                        ### split optical input into TALYS variable and value
                        optical_name = o.split(' ')[0]
                        optical_value = o.split(' ')[1]

                        #self.talys_input['massmodel'], self.talys_input['ldmodel'], self.talys_input['strength'], self.talys_input[optical_name] = mm, lm, s, optical_value
                        talys_input['massmodel'], talys_input['ldmodel'], talys_input['strength'] = mm, lm, s

                        ### mkdir: > TALYS-calculations-date-time/original_data/astro-a/ZZ-X/isotope/isotope-massmodel-ldmodel-strength-localomp-jlmomp
                        variable_directory = '%s/%g%s-0%g-0%g-0%g-%s-%s' %(isotope_original, m, e, mm, lm, s, optical_name, optical_value)
                        directories["variable_directory"] = variable_directory
                        mkdir(variable_directory)

                        ### make input file
                        ## make header
                        try:
                                self.make_header(talys_input, variable_directory, o)
                        except Exception as exc:
                                self.logger.error( "An error occured while writing header for a={} e={} mm={} lm={} s={} o={}:\n{}".format(a, e, mm, lm, s, o, exc))
                                continue
                        
                        # Prepare all of the directory names so multiprocessing won't interfer
                        #src_result_file = '%s/rp%s%s.tot' %(variable_directory, Z_nr[e], m+1)
                        src_result_file = "{}/astrorate.tot".format(variable_directory)
                        dst_result_file = "{}/{}{}{}{}-{}-{}-{}-{}-{}-astrorate.tot".format(isotope_results, m, e, Z_nr[e], m+1, mm, lm, s, optical_name, optical_value)
                        #dst_result_file = '%s/%s%s-rp%s%s-0%g-0%g-0%g-%s-%s.tot' %(isotope_results, m, e, Z_nr[e], m+1, mm, lm, s, optical_name, optical_value)
                        error_directory = '%s/error' %self.top_directory
                        error_file = '%s/%s-error.txt' %(self.top_directory, Z_nr[e])
                        src_error = '%s/output.txt' %variable_directory

                        directories["src_result_file"] = src_result_file
                        directories["dst_result_file"] = dst_result_file
                        directories["error_directory"] = error_directory
                        directories["error_file"] = error_file
                        directories["src_error"] = src_error

                        ## run TALYS
                        if self.args.multi_talys:
	                        """ Use multiprocessing on each run of talys"""
	                        if self.args.processes > 0:
		                        if  len(talys_jobs) >= self.args.processes:
			                        """ Use the set number of processes. Wait for available
			                             Gets blocked until something is put on the queue, i.e. of the the
			                             subprocesses has finished
			                        """
			                        self.logger.debug("Waiting for available process")
			                        pid = self.talys_queue.get()
			                        # To prevent any fuckups, wait for the process to finished if, by any chance, it hasn't
			                        time.sleep(1)
			                        for process in talys_jobs:
				                        if process.pid == pid:
					                        if process.is_alive():
						                        self.logger.critical("{} didn't die!!".format(pid))
						                        process.join()
					                        # remove it from the list
					                        self.logger.debug("Removing {} from list".format(pid))
					                        talys_jobs.remove(process)
					                        break
                                talys_job = multiprocessing.Process(target=self.run_talys, args=(directories, e, ))
                                talys_jobs.append(talys_job)
                                talys_job.start()
                        else:
                                self.run_talys(directories, e)

                # Wait for all of the talys_jobs to complete
                for talys_job in talys_jobs:
                        talys_job.join()

        def run_talys(self, directories, element):
                """ Runs TALYS """
                directories = copy.deepcopy(directories)
                assert directories["input_file"] != directories["output_file"]   # Prevent headaches

                _start = time.time()
                with Cd(directories["variable_directory"]):
	                os.system('talys <{}> {}'.format(directories["input_file"], directories["output_file"]))
	        elapsed = time.strftime("%M:%S", time.localtime(time.time() - _start))
	        self.logger.info("Execution time: {} by {}".format(elapsed, directories["variable_directory"]))
                 ## move result file to TALYS-calculations-date-time/original_data/astro-a/ZZ-X/isotope
                try:
                        shutil.copy(directories["src_result_file"], directories["dst_result_file"])
                except IOError as ioe:
                        self.logger.error( "An error occured while trying to copying the result: {}".format(ioe))
                        mkdir(directories["error_directory"])
                        ## put head of error file here?
                        error_outfile = open(os.path.join(directories["error_directory"], 'Z%s%s-error.txt' %(Z_nr[element], element)), 'a+')
                        error_outfile.write('%s\n' %directories["isotope_results"])

                        ## write talys output.txt to error file:
                        error_talys = open(directories["src_error"], 'r')
                        error_lines = error_talys.readlines()

                        error_outfile.write('Talys output file: \n')
                        error_outfile.writelines(str(error_lines))
                        error_outfile.write('\n\n')

                        error_talys.close()
                        error_outfile.close()

                self.logger.info('variable directory = {}'.format(directories["variable_directory"]))

                # Tell the parent process that the child has finnished
                self.logger.debug("{} is terminating".format(multiprocessing.current_process().pid))
                self.talys_queue.put(multiprocessing.current_process().pid)

        def run(self):
                """ Runs the simulations """
                talys_input = copy.deepcopy(self.user_input)
                directories = {"input_file": self.user_input['input_file'], "output_file": self.user_input['output_file']}
                ### make sure inputs given are iterable
                self.user_input = make_iterable(self.user_input)
                ## mkdir: > TALYS-calculations-date-time
                date_directory = time.strftime('%y%m%d')
                time_directory = time.strftime('%H%M%S')
                directories["date_directory"] = date_directory
                directories["time_directory"] = time_directory

                self.top_directory = 'TALYS-calculations-%s-%s' %(date_directory, time_directory)
                directories["top_directory"] = self.top_directory
                mkdir(self.top_directory)

                # Initialize and start the logging
                self.init_logger()
                try:
                        self.make_info_file()
                except Exception as e:
                        self.logger.error( "An error occured while writing info file: {}".format(e))
                        sys.exit("Fatal error")

                ## mkdir: > TALYS-calculations-date-time/original_data
                original_data = '%s/original_data' %self.top_directory
                directories["original_data"] = original_data
                mkdir(original_data)

                ## mkdir: > TALYS-calculations-date-time/results_data
                results_data = '%s/results_data' %self.top_directory
                directories["results_data"] = results_data
                mkdir(results_data)

                for a in self.user_input['astro']:
                        """ Loop through each value of astro """

                        talys_input['astro'] = a

                        ## mkdir: TALYS-calculations-date-time/original_data/astro-a
                        astro_original = '%s/astro-%s' %(original_data, correct(a))
                        directories["astro_original"] = astro_original
                        mkdir(astro_original)

                        ## mkdir: > TALYS-calculations-date-time/results_data/astro-a
                        astro_results = '%s/astro-%s' %(results_data, correct(a))
                        directories["astro_results"] = astro_results
                        mkdir(astro_results)

                        #Reset elements job list
                        element_jobs = [] 

                        for element in self.user_input['element']:
                                if self.args.multi_elements:
                                        """ Use multiprocessing for each element """
                                        element_job = multiprocessing.Process(target=self.run_element,
                                                                              args=(element,  talys_input, directories, ))
                                        element_jobs.append(element_job)
                                        element_job.start()
                                else:
                                        self.run_element(element, talys_input, directories)

                        # Wait for the element_jobs to complete
                        for element_job in element_jobs:
                                element_job.join()

# Keep the script from running if imported as a module
if __name__ == "__main__":
        # Handle the arguments from terminal
        parser = argparse.ArgumentParser()
        parser.add_argument("--multi_elements", help="Use multiprocessing on each element", action="store_true")
        parser.add_argument("--multi_mass", help="Use multiprocessing on each mass", action="store_true")
        parser.add_argument("--multi_talys", help="Use multiprocessing on each combination in product", action="store_true")
        parser.add_argument("--debug", help="Show debugging information. Overrules log and verbosity", action="store_true")
        parser.add_argument("--combinations", help="Give a summary over how many TALYS-runs are needed to exhaust all of the combinations", action="store_true", default=False)
        parser.add_argument("-l", "--log", help="Set the log level",
                            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                            type=str.upper, default="INFO")
        parser.add_argument("-v", "--verbosity", help="Set the verbosity level",
                            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                            type=str.upper, default="INFO")
        parser.add_argument("--lfilename", help="Filename of the log file", type=str, default="talys.log")
        parser.add_argument("-p", "--processes", help="Set the number of processes the script will use. Should be less than or equal to number of CPU cores",
                            type=int, default=0)
        
        args = parser.parse_args()

        # Set up  logging
        args.log = getattr(logging, args.log)
        args.verbosity = getattr(logging, args.verbosity)
        if args.debug:
	        args.log = logging.DEBUG
	        args.verbosity = logging.DEBUG
        logging.basicConfig(level=args.log, filename=args.lfilename, filemode="w")

        # Get the options
        options = import_options()
        if args.combinations:
                print( "Astro: {}\nElements: {}\nMasses: {}\nRest: {}\nTotal: {}".format(*count_combinations(options)))
                sys.exit()
        
        # Create an instance of Manager to run the simulation
        simulations = Manager(user_input=options, args=args)
        simulations.run()
