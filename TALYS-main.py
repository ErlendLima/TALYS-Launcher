#! /usr/bin/python
"""
##########################################
Create list of user input. 
Must stay in this location or wont work :p
##########################################
"""

from talys_options import *
direct_user_input_keys, direct_user_input_values = locals().keys(), locals().values()

user_input_keys = []
user_input_values = []

for key in range(len(direct_user_input_keys)):
	if '__' not in(direct_user_input_keys[key]):
		user_input_keys.append(direct_user_input_keys[key])
		user_input_values.append(direct_user_input_values[key])
	else:
		pass

user_input_dict = dict(zip(user_input_keys, user_input_values))

"""
##########################################
Imports
##########################################
"""

import numpy as np                                # Numerical calculations
import time                                              # Time and date
from itertools import product                  # Nested for-loops
import sys                                              # Functions to access system functions
import os                                                # Functions to access IO of the OS
import shutil                                           # ?
import platform                                      # Information about the platform
import multiprocessing                         # Multiprocessing
import logging                                       # Logging progress from the processes
import argparse                                    # Parsing arguments given in terminal

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

## OK+ a little more doc
def correct(input_argument):
	"""
	Function to check syntax of input arguments given by user.
	"""

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

def run_talys(dst, input_file, output_file, src_result_file, dst_result_file, variable_directory):
        assert input_file != output_file   # Prevent headaches

        with Cd(dst):
                os.system('talys <{}> {}'.format(input_file, output_file))

        ## move result file to TALYS-calculations-date-time/original_data/astro-a/ZZ-X/isotope
        try:
                shutil.copy(src_result_file, dst_result_file)
        except IOError as ioe:
                print "An error occured while trying to copying the result: ", ioe
                # mkdir(error_directory)
                # ## put head of error file here?

                # error_outfile = open('%s/Z%s%s-error.txt' %(error_directory, Z_nr[e], e), 'a+')
                # error_outfile.write('%s\n' %isotope_results)

                # ## write talys output.txt to error file:
                # error_talys = open(src_error, 'r')
                # error_lines = error_talys.readlines()

                # error_outfile.write('Talys output file: \n')
                # error_outfile.writelines(str(error_lines))
                # error_outfile.write('\n\n')

                # error_talys.close()
                # error_outfile.close()

        print 'variable directory =', variable_directory


def make_iterable(user_input, talys_input):
        """ Makes the user_input iterable by changing it to a list """
        for key in user_input:

		if not isinstance(user_input[key], (tuple, list)):
			## put single input noe iterable into talys_input
			talys_input[key] = user_input[key]
			## put single entries into list if iterable variable
			user_input[key] = [user_input[key]]

	## #check if every item in user given list is unique
	for key, value in user_input.iteritems():

		try:
			## if variable tuple or list => new list with value only once
			if len(set(value)) != len(value):
				newlist = []
				for val in value:
					if val not in newlist:
						newlist.append(val)
				                user_input[key] = newlist
		                                
		except TypeError:
			## if variable == dict => new dict with value only once inside user_input[key]
			for keys, values in value[0].iteritems():
				if len(set(values)) != len(values):
					newlist = []
					for val in values:
						if val not in newlist:
							newlist.append(val)
					                value[0][keys] = newlist

				user_input[key] = value[0]

"""
##########################################
Classes
##########################################
"""
class Cd:
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

class Manager:
        def __init__(self, user_input, arguments):
                self.user_input = user_input
                self.args = arguments
                self.jobs = []

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

        def make_header(self, variable_directory, optical):
                ## copy of input_dictionary => able to delete items and iterate over the rest
                talys_input2 = dict(self.talys_input)
                m, e, o = self.talys_input['mass'], self.talys_input['element'], optical
                ## need projectile, input_file, output_file twice
                projectile = talys_input2.pop(['projectile'][0])
                input_file = talys_input2.pop('input_file')
                output_file = talys_input2.pop('output_file')

                outfile_input = open(self.user_input['input_file'][0], 'w') # create input file

                outfile_input.write('###################### \n')
                outfile_input.write('## TALYS input file ## \n')
                outfile_input.write('##  {}{}({},g){}{}   ## \n'.format(m, e, projectile, m+1, e))
                outfile_input.write('###################### \n \n')
                outfile_input.write('# All keywords are explained in README. \n \n')

                outfile_input.write('element {} \n'.format(talys_input2.pop('element')))
                outfile_input.write('projectile {} \n'.format(projectile))
                outfile_input.write('mass {} \n'.format(m))
                talys_input2.pop('mass')
                outfile_input.write('energy {} \n \n'.format(talys_input2.pop('energy_file')))
                outfile_input.write('{}\n'.format(o))

                talys_input2.pop('E1')
                talys_input2.pop('E2')
                talys_input2.pop('step')

                for key, value in talys_input2.iteritems():
                        outfile_input.write('{} {} \n'.format(key, str(value)))

                outfile_input.close()

                ## Move energy file and input file to isotope directory
                ## new src energy file
                src_energy = self.user_input['energy_file'][0]
                src_energy_new = '{}/{}'.format(self.top_directory, src_energy)
                ## src input file
                src_input = self.user_input['input_file'][0]
                ## dst input file > variable directory
                dst_energy_input = variable_directory

                ## copy energy file to variable directory
                shutil.copy(src_energy_new, dst_energy_input)

                ## move input file to variable directory
                shutil.move(src_input, dst_energy_input)


        def run(self):
                """ Runs the simulations """
                self.talys_input = {}

                ### make sure inputs given are iterable
                ## if not, put into list
                make_iterable(self.user_input, self.talys_input) # Note, this changes the lists in-place

                ## mkdir: > TALYS-calculations-date-time
                date_directory = time.strftime('%y%m%d')
                time_directory = time.strftime('%H%M%S')
                self.top_directory = 'TALYS-calculations-%s-%s' %(date_directory, time_directory)
                mkdir(self.top_directory)
                try:
                        self.make_info_file()
                except Exception as e:
                        print "An error occured while writing info file: ", e
                        print "This is unrecoverable. Exiting"
                        sys.exit("Fatal error")

                ## mkdir: > TALYS-calculations-date-time/original_data
                original_data = '%s/original_data' %self.top_directory
                mkdir(original_data)

                ## mkdir: > TALYS-calculations-date-time/results_data
                results_data = '%s/results_data' %self.top_directory

                mkdir(results_data)

                for a in self.user_input['astro']:
                        """ Loop through each value of astro """

                        self.talys_input['astro'] = a

                        ## mkdir: TALYS-calculations-date-time/original_data/astro-a
                        astro_original = '%s/astro-%s' %(original_data, correct(a))
                        mkdir(astro_original)

                        ## mkdir: > TALYS-calculations-date-time/results_data/astro-a
                        astro_results = '%s/astro-%s' %(results_data, correct(a))
                        mkdir(astro_results)

                        for e in self.user_input['element']:
                                """ Loop through each element """

                                self.talys_input['element'] = e

                                ## mkdir: > TALYS-calculations-date-time/original_data/astro-a/ZZ-X
                                element_original = '%s/Z%s-%s' %(astro_original, Z_nr[e], e)
                                mkdir(element_original)

                                ## mkdir: > TALYS-calculations-date-time/result_data/astro-a/ZZ-X
                                element_results = '%s/Z%s-%s' %(astro_results, Z_nr[e], e)
                                mkdir(element_results)

                                for m in self.user_input['mass'][e]:
                                        """ Loop through the given masses of the current element, if given """

                                        self.talys_input['mass'] = m

                                        ## mkdir: > TALYS-calculations-date-time/original_data/astro-a/ZZ-X/isotope
                                        isotope_original = '%s/%g%s' %(element_original, m, e)
                                        mkdir(isotope_original)

                                        ## mkdir: > TALYS-calculations-date-time/result_data/astro-a/ZZ-X/isotope
                                        isotope_results = '%s/%g%s' %(element_results, m, e)
                                        mkdir(isotope_results)

                                        self.jobs = []
                                        for mm, lm, s, o in product(self.user_input['massmodel'], self.user_input['ldmodel'], self.user_input['strength'], self.user_input['optical']):

                                                ### split optical input into TALYS variable and value
                                                optical_name = o.split(' ')[0]
                                                optical_value = o.split(' ')[1]

                                                #self.talys_input['massmodel'], self.talys_input['ldmodel'], self.talys_input['strength'], self.talys_input[optical_name] = mm, lm, s, optical_value
                                                self.talys_input['massmodel'], self.talys_input['ldmodel'], self.talys_input['strength'] = mm, lm, s

                                                ### mkdir: > TALYS-calculations-date-time/original_data/astro-a/ZZ-X/isotope/isotope-massmodel-ldmodel-strength-localomp-jlmomp
                                                variable_directory = '%s/%g%s-0%g-0%g-0%g-%s-%s' %(isotope_original, m, e, mm, lm, s, optical_name, optical_value)
                                                mkdir(variable_directory)

                                                ### make input file
                                                ## make header
                                                try:
                                                        self.make_header(variable_directory, o)
                                                except Exception as exc:
                                                        print "An error occured while writing header for a={} e={} mm={} lm={} s={} o={}:\n{}".format(a, e, mm, lm, s, o, exc)
                                                        print "Skipping"
                                                        continue

                                                dst_energy_input = variable_directory

                                                # Prepare all of the directory names so multiprocessing won't interfer
                                                src_result_file = '%s/rp%s%s.tot' %(dst_energy_input, Z_nr[e], m+1)
                                                dst_result_file = '%s/%s%s-rp%s%s-0%g-0%g-0%g-%s-%s.tot' %(isotope_results, m, e, Z_nr[e], m+1, mm, lm, s, optical_name, optical_value)
                                                error_directory = '%s/error' %self.top_directory
                                                error_file = '%s/%s-error.txt' %(self.top_directory, Z_nr[e])
                                                src_error = '%s/output.txt' %dst_energy_input
                                                ## run TALYS
                                                j = multiprocessing.Process(target=run_talys, args=(dst_energy_input, input_file, output_file, src_result_file, dst_result_file, variable_directory,))
                                                self.jobs.append(j)
                                                j.start()

                                        # Wait for all of the jobs to complete
                                        for j in self.jobs:
                                                j.join()

# Keep the script from running if imported as a module
if __name__ == "__main__":
        # Handle the arguments from terminal
        parser = argparse.ArgumentParser()
        parser.add_argument("--multi-elements", help="Use multiprocessing on each element", action="store_true")
        args = parser.parse_args()

        # Set up multiprocessing.
        # MUST BE IN THE FIRST LEVEL SCOPE OF if __name__ == "__main__", I.E HERE
        multiprocessing.log_to_stderr(logging.DEBUG)

        # Create an instance of Manager to run the simulation
        simulations = Manager(user_input_dict, args)
        simulations.run()
