from itertools import product
import os as os
import time

import pylab as py
import numpy as np

import matplotlib.pyplot as plt

date_calculations = 160705
time_calculations = 154044

energy_file = 'energies.txt'

astro = ['no']
element = ['Ce']
mass = [160]

massmodel = [1, 2, 3]
ldmodel = [1, 2, 3, 4, 5, 6]
strength = [1, 2, 3, 4, 5, 6, 7, 8]

localomp_jlmomp = ['y', 'n']

py.rcParams['figure.figsize'] = 11, 9
py.rcParams['font.size'] = 18
py.rcParams['axes.linewidth'] = .5
py.rcParams['xtick.labelsize'] = 18
py.rcParams['ytick.labelsize'] = 18
py.rcParams['axes.labelsize'] = 24
py.rcParams['axes.titlesize'] = 28
py.rcParams['legend.fontsize'] = 18


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

### current date and time
date_plots = time.strftime('%y%m%d')
time_plots = time.strftime('%H%M%S')


### mkdir > TALYS-plots
plots_directory = 'TALYS-calculations-%s-%s/TALYS-plots' %(date_calculations, time_calculations)
if not os.path.exists(plots_directory):
	os.makedirs(plots_directory)
else:
	pass


### mkdir > TALYS-plots-error-band-date-time
error_band_directory = '%s/TALYS-error-band-%s-%s' %(plots_directory, date_plots, time_plots)
os.makedirs(error_band_directory)


### scr energy file > TALYS-calculations-date_calculations-time_calculations/energy_file
src_energy = 'TALYS-calculations-%s-%s/%s' %(date_calculations, time_calculations, energy_file)
## read energy file:
infile_energy = open(src_energy)
energy = []
for line in infile_energy:
	energy.append(float(line.split(' ')[0]))


for a in astro:

	### mkdir > TALYS-plots-date-time/astro-astro
	astro_directory = '%s/astro-%s' %(error_band_directory, a)
	os.makedirs(astro_directory)

	for e in element:

		### mkdir > TALYS-plots-date-time/astro-a/ZZ-X
		element_directory = '%s/Z%s-%s' %(astro_directory, Z_nr[e], e)
		os.makedirs(element_directory)

		for m in mass:

			### find min and max xs:
			min_xs = np.zeros(len(energy))
			max_xs = np.zeros(len(energy))

			for mm, lm, s, l in product(massmodel, ldmodel, strength, localomp_jlmomp):
				src_xs = 



#		for m in mass:
#
#			### mkdir > TALYS-plots-date-time/astro-a/ZZ-X/isotope
#			isotope_directory = '%s/%s%s' %(element_directory, m, e)
#			os.makedirs(isotope_directory)



				### dst plot file: > TALYS-calculations-date-time/TALYS-plots-date-time/astro-a/ZZ-X/isotope
				#dst_plots = '%s/%s%s-rp%s%s-0%g-0%g-0%g-%s-%s.tot' %(isotope_directory, m, e, Z_nr[e], m+1, mm, lm, s, l, l)


				
				

				### energy, xs from result file:
				#energy, xs = read_file(src_plots)
				#print 'energy', energy
				#print 'xs    ', xs








	










