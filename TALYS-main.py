#! /usr/bin/python
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

#element
element = 'Ce', 'Pr'

#projectile
projectile = 'n'

#mass = 76
mass = {'Ce': [156, 160, 158, 160, 162, 163, 164],
        'Pr':[158, 163, 160]}
#mass = 86, 87, 88, 110, 300, 241

massmodel = 3
#massmodel = 1, 2, 3

ldmodel = 3, 3
#ldmodel = 2, 3, 1
#ldmodel = 1, 2, 3, 4

strength = 1, 2
#strength = 1, 2, 3, 4

gnorm = 1.

optical = 'localomp n', 'jlmomop y'


#localomp = ['n', 'y']

#jlmomp = 'y'
#jlmomp = 'n' , 'y'
#jlmomp = ['y', 'n']
#jlmomp = ['y', 'h']


#astro = 'y'
astro = 'n'

#epr = 50
#gpr = 34
#spr = 70

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

def run_talys(src, input_file, output_file):
	with cd('%s' %(src)):
		os.system('talys <%s> %s' %(input_file, output_file))


def run_main(user_input):

	talys_input = {}

	### make sure input given are iterable
	## if not, put into list
	
	for key in user_input:

		if not isinstance(user_input[key], (tuple, list)):
			## put single input noe iterable into talys_input
			talys_input[key] = user_input[key]
			## put single entries into list if iterable variable
			user_input[key] = [user_input[key]]
		else:
			pass

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
			
			else:
				pass
		
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

			else:
				pass



	## mkdir: > TALYS-calculations-date-time
	date_directory = time.strftime('%y%m%d')
	time_directory = time.strftime('%H%M%S')
	top_directory = 'TALYS-calculations-%s-%s' %(date_directory, time_directory)
	os.makedirs(top_directory)

	## create info_file
	info_file = '%s-info.txt' %top_directory
	date_file = time.strftime('%d %B %Y')
	time_file = time.strftime('%H:%M:%S-%Z')

	outfile_info = open(info_file, 'w')
	info_input = dict(user_input)

	## write date, time and input info to info_file
	outfile_info.write('TALYS-calculations')

	outfile_info.write('\nDate: %s' %date_file)
	outfile_info.write('\nTime: %s' %time_file)
	outfile_info.write('\n\n# name of energy file: %s' %info_input['energy_file'])
	outfile_info.write('\n# energy min: %s' %info_input.pop('E1'))
	outfile_info.write('\n# energy max: %s' %info_input.pop('E2'))
	outfile_info.write('\n# energy step: %s' %info_input.pop('step'))

	outfile_info.write('\n\n# name of input file: %s' %info_input.pop('input_file'))
	outfile_info.write('\n# name of output file: %s' %info_input.pop('output_file'))
	outfile_info.write('\n\nVariable input:') 
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
	dst_energy_info = top_directory
	shutil.move(src_energy, dst_energy_info)
	shutil.move(src_info, dst_energy_info)

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

#

			for m in user_input['mass'][e]:

				talys_input['mass'] = m

				## mkdir: > TALYS-calculations-date-time/original_data/astro-a/ZZ-X/isotope
				isotope_original = '%s/%g%s' %(element_original, m, e)
				if not os.path.exists(isotope_original):
					os.makedirs(isotope_original)
				else:
					pass

				## mkdir: > TALYS-calculations-date-time/result_data/astro-a/ZZ-X/isotope
				isotope_results = '%s/%g%s' %(element_results, m, e)
				if not os.path.exists(isotope_results):
					os.makedirs(isotope_results)
				else:
					pass

				#localomp_jlmomp_pairs = [['n', None], [None, 'y']]
				
				for mm, lm, s, o in product(user_input['massmodel'], user_input['ldmodel'], user_input['strength'], user_input['optical']):

					### split optical input into TALYS variable and value
					optical_name = o.split(' ')[0]
					optical_value = o.split(' ')[1]

					#talys_input['massmodel'], talys_input['ldmodel'], talys_input['strength'], talys_input[optical_name] = mm, lm, s, optical_value
					talys_input['massmodel'], talys_input['ldmodel'], talys_input['strength'] = mm, lm, s

					### mkdir: > TALYS-calculations-date-time/original_data/astro-a/ZZ-X/isotope/isotope-massmodel-ldmodel-strength-localomp-jlmomp
					variable_directory = '%s/%g%s-0%g-0%g-0%g-%s-%s' %(isotope_original, m, e, mm, lm, s, optical_name, optical_value)
					os.makedirs(variable_directory)

					### make input file
					## copy of input_dictionary => able to delete items and iterate over the rest
					talys_input2 = dict(talys_input)
					## need projectile, input_file, output_file twice
					projectile = talys_input2.pop(['projectile'][0])
					input_file = talys_input2.pop('input_file')
					output_file = talys_input2.pop('output_file')
					
					## make header
					outfile_input = open(user_input['input_file'][0], 'w') # create input file
					outfile_input.write('###################### \n')
					outfile_input.write('## TALYS input file ## \n')
					outfile_input.write('##  %s%s(%s,g)%s%s   ## \n' %(m, e, projectile, m+1, e))
					outfile_input.write('###################### \n \n')
					outfile_input.write('# All keywords are explained in README. \n \n')

					outfile_input.write('element %s \n' %talys_input2.pop('element'))
					outfile_input.write('projectile %s \n' %projectile)
					outfile_input.write('mass %s \n' %m)
					talys_input2.pop('mass')
					outfile_input.write('energy %s \n \n' %talys_input2.pop('energy_file'))
					outfile_input.write('%s\n' %o)

					talys_input2.pop('E1')
					talys_input2.pop('E2')
					talys_input2.pop('step')

					for key, value in talys_input2.iteritems():
						outfile_input.write('%s %s \n' %(key, str(value)))

					outfile_input.close()

					## Move energy file and input file to isotope directory
					## new src energy file
					src_energy_new = '%s/%s' %(top_directory, src_energy)
					## src input file
					src_input = user_input['input_file'][0]
					## dst input file > variable directory
					dst_energy_input = variable_directory
					
					## copy energy file to variable directory
					shutil.copy(src_energy_new, dst_energy_input)


					## move input file to variable directory
					shutil.move(src_input, dst_energy_input)

					## run TALYS
					with cd('%s' %(dst_energy_input)):
						os.system('talys <%s> %s' %(input_file, output_file))

					## move result file to TALYS-calculations-date-time/original_data/astro-a/ZZ-X/isotope
					src_result_file = '%s/rp%s%s.tot' %(dst_energy_input, Z_nr[e], m+1)
					dst_result_file = '%s/%s%s-rp%s%s-0%g-0%g-0%g-%s-%s.tot' %(isotope_results, m, e, Z_nr[e], m+1, mm, lm, s, optical_name, optical_value)

					try:
						shutil.copy(src_result_file, dst_result_file)

					except IOError:

						error_directory = '%s/error' %top_directory
						if not os.path.exists(error_directory):
							os.makedirs(error_directory)
							## put head of error file here?
						else:
							pass

						error_file = '%s/%s-error.txt' %(top_directory, Z_nr[e])
	
						error_outfile = open('%s/Z%s%s-error.txt' %(error_directory, Z_nr[e], e), 'a+')
						error_outfile.write('%s\n' %isotope_results)

						## write talys output.txt to error file:
						src_error = '%s/output.txt' %dst_energy_input
						error_talys = open(src_error, 'r')
						error_lines = error_talys.readlines()

						error_outfile.write('Talys output file: \n')
						error_outfile.writelines(str(error_lines))
						error_outfile.write('\n\n')

						error_talys.close()
						error_outfile.close()

					print 'variable directory =', variable_directory




# Keep the script from running if imported as a module
if __name__ == "__main__":
        run_main(user_input_dict)
