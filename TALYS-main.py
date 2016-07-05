"""
######################
##### USER INPUT #####
######################
"""

#Energies
energy_file = 'energies.txt'

E1 = 0.0025E-03
E2 = 5000E-03
step = 100

# name of input file:
input_file = 'input.txt'

#name of output file:
output_file = 'output.txt'

#name of energy file:
energy_file = 'energies.txt'

#element = 'Ge', 'Fe', 'Kg'
#element = ['Fe', 'Co', 'Kg']

element = 'Fe', 'Co', 'Ni', 'Ge'

projectile = 'n'

#mass = 76
mass = 87, 99, 198
#mass = 86, 87, 88, 110, 300, 241

massmodel = 3, 4
#massmodel = 1, 2, 3

ldmodel = 2, 3
#ldmodel = 2, 3, 1
#ldmodel = 1, 2, 3, 4

strength = 1, 4
#strength = 1, 2, 3, 4

gnorm = 1.

localomp = 'y', 'n'
#localomp = ['n', 'y']

#jlmomp = 'n'
jlmomp = 'n' , 'y'
#jlmomp = ['y', 'n']
#jlmomp = ['y', 'h']


#astro = 'y'
astro = 'n', 'y'

preequilibrium = 'y'
fileresidual = 'y'
outlevels = 'y'
outdensity = 'y'
outgamma = 'y'

transeps = 1.00E-15
xseps = 1.00E-25
popeps = 1.00E-25



"""
########################
#### END USER INPUT ####
########################
"""
"""
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################
"""


"""
##########################################
Create list of user input. 
Must stay in this location or wont work :p
##########################################
"""

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
"""

import numpy as np
import time
from itertools import product
import sys

import os as os
import shutil

## have no idea how this works. no doc
class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

######################################################



## wtf no doc
def run_talys(src, input_file, output_file):
	with cd('%s' %(src)):
		os.system('talys <%s> %s' %(input_file, output_file))



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

Z_nr = {'Fe':'26', 'Co':'27', 'Ni':'28', 'Cu':'29', 'Zn':'30', 'Ga':'31', 'Ge':'32', 'As':'33', 'Se':'34', 'Br':'35', 'Kr':'36', 'Rb':'37', 'Sr':'38', 'Y':'39', 'Zr':'40', 'Kg':'145'}

def run_talys(src, input_file, output_file):
	with cd('%s' %(src)):
		os.system('talys <%s> %s' %(input_file, output_file))


def run_main(user_input):
	#print user_input

	talys_input = {}

	## make sure input given are iterable
	## if not, put into list
	
	for key in user_input:

		if not isinstance(user_input[key], (tuple, list)):
			## put single input noe iterable into talys_input
			talys_input[key] = user_input[key]
			## put single entries into list if iterable variable
			#print user_input[key]
			user_input[key] = [user_input[key]]
			#print user_input[key]
		else:
			pass


	#print talys_input
	## mkdir: > TALYS-calculations-date-time
	date_directory = time.strftime('%y%m%d')
	time_directory = time.strftime('%H%M%S')
	top_directory = 'TALYS-calculations-%s-%s' %(date_directory, time_directory)
	os.makedirs(top_directory)

	## create info_file
	info_file = '%s-info.txt' %top_directory
	date_file = time.strftime('%d %B %Y')
	time_file = time.strftime('%H:%M:%S-%Z')
	#print time.strftime('%I-%p')
	outfile_info = open(info_file, 'w')
	info_input = dict(user_input)
	## write date and time to info_file
	outfile_info.write('TALYS-calculations')
	#print 'hallo', info_input
	outfile_info.write('\nDate: %s' %date_file)
	outfile_info.write('\nTime: %s' %time_file)
	outfile_info.write('\n\n# name of energy file: %s' %info_input['energy_file'])
	outfile_info.write('\n# energy min: %s' %info_input.pop('E1'))
	outfile_info.write('\n# energy max: %s' %info_input.pop('E2'))
	outfile_info.write('\n# energy step: %s' %info_input.pop('step'))

	outfile_info.write('\n\n# name of input file: %s' %info_input.pop('input_file'))
	outfile_info.write('\n# name of output file: %s' %info_input.pop('output_file'))
	outfile_info.write('\n\nVariable input:') 
	print info_input['element'][0]
	outfile_info.write('\nelement: %s' %str(info_input.pop('element')))
	outfile_info.write('\nprojectile: %s' %str(info_input.pop('projectile')))
	outfile_info.write('\nmass: %s' %str(info_input.pop('mass')))
	outfile_info.write('\nenergy: %s \n' %str(info_input.pop('energy_file')))


	for value, key in info_input.iteritems():
		outfile_info.write('\n%s: %s' %(value, key))

	outfile_info.write('\n\nEnergies: \n')

	## create energy input 
	energies = np.linspace(float(user_input['E1'][0]), float(user_input['E2'][0]), float(user_input['step'][0]))
	## outfile named energy_file 
	outfile_energy = open(user_input['energy_file'][0], 'w')
	## write energies to energy_file and info_file in one column
	for Ei in energies:
		outfile_energy.write('%.2E \n' %Ei) # write energies to file in column
		outfile_info.write('%.2E \n' %Ei) # write energies to info file in one column
	
	outfile_energy.close()
	outfile_info.close()

	
	## move energy_file and info_file to:
	## > TALYS-calculations-date-time
	src_energy = user_input['energy_file'][0]
	src_info = info_file
	dst = top_directory
	shutil.move(src_energy, dst)
	shutil.move(src_info, dst)

	## mkdir: > TALYS-calculations-date-time/original_data
	original_data = '%s/original_data' %top_directory
	os.makedirs(original_data)

	## mkdir: > TALYS-calculations-date-time/results_data
	results_data = '%s/results_data' %top_directory
	os.makedirs(results_data)

	for a in user_input['astro']:

		talys_input['astro'] = a
		
		## mkdir: TALYS-calculations-date-time/original_data/astro-a
		astro_original = '%s/astro-%s' %(original_data, correct(a))
		os.makedirs(astro_original)
		
		## mkdir: > TALYS-calculations-date-time/results_data/astro-a
		astro_results = '%s/astro-%s' %(results_data, correct(a))
		os.makedirs(astro_results)

		for e in user_input['element']:

			talys_input['element'] = e
			
			## mkdir: > TALYS-calculations-date-time/original_data/astro-a/ZZ-X
			element_original = '%s/Z%s-%s' %(astro_original, Z_nr[e], e)
			os.makedirs(element_original)

			## mkdir: > TALYS-calculations-date-time/result_data/astro-a/ZZ-X
			element_results = '%s/Z%s-%s' %(astro_results, Z_nr[e], e)
			os.makedirs(element_results)

			for m in user_input['mass']:

				talys_input['mass'] = m

				## mkdir: > TALYS-calculations-date-time/original_data/astro-a/ZZ-X/isotope
				isotope_original = '%s/%g%s' %(element_original, m, e)
				os.makedirs(isotope_original)

				## mkdir: > TALYS-calculations-date-time/result_data/astro-a/ZZ-X/isotope
				isotope_results = '%s/%g%s' %(element_results, m, e)
				os.makedirs(isotope_results)

				for mm, lm, s, l, j in product(user_input['massmodel'], user_input['ldmodel'], user_input['strength'], user_input['localomp'], user_input['jlmomp']):

					talys_input['massmodel'], talys_input['ldmodel'], talys_input['strength'], talys_input['localomp'], talys_input['jlmomp'] = mm, lm, s, l, j

					### mkdir: > TALYS-calculations-date-time/original_data/astro-a/ZZ-X/isotope/isotope-massmodel-ldmodel-strength-localomp-jlmomp
					variable_directory = '%s/%g%s-0%g-0%g-0%g-%s-%s' %(isotope_original, m, e, mm, lm, s, l, j)
					os.makedirs(variable_directory)

					### make input file
					## copy of input_dictionary => able to delete items and iterate over the rest
					talys_input2 = dict(talys_input)
					## need projectile twice
					projectile = talys_input2.pop(['projectile'][0])
					input_file = talys_input2.pop('input_file')
					output_file = talys_input2.pop('output_file')
					
					## make header
					outfile = open(user_input['input_file'][0], 'w') # create input file
					outfile.write('###################### \n')
					outfile.write('## TALYS input file ## \n')
					outfile.write('##  %s%s(%s,g)%s%s   ## \n' %(m, e, projectile, m+1, e))
					outfile.write('###################### \n \n')
					outfile.write('# All keywords are explained in README. \n \n')

					outfile.write('element %s \n' %talys_input2.pop('element'))
					outfile.write('projectile %s \n' %projectile)
					outfile.write('mass %s \n' %m)
					talys_input2.pop('mass')
					outfile.write('energy %s \n \n' %talys_input2.pop('energy_file'))

					for key, value in talys_input2.iteritems():
						outfile.write('%s %s \n' %(key, str(value)))

					## Move energy file and input file to isotope directory
					## new src energy file
					src_new = '%s/%s' %(top_directory, src_energy)
					## src input file
					src2 = user_input['input_file'][0]
					## dst variable directory
					dst2 = variable_directory
					## copy energy file to variable directory
					shutil.copy(src_new, dst2)
					## move input file to variable directory
					shutil.move(src2, dst2)

					#print input_file

					## run TALYS
					with cd('%s' %(dst2)):
						os.system('talys <%s> %s' %(input_file, output_file))












run_main(user_input_dict)



