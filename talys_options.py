# Write this file in Python-syntax

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
element = 'Pm'

#projectile
projectile = 'n'

mass = {'Ce': [156, 160, 158, 160, 162, 163, 164],
        'Pr':[158, 163, 160],
	'Pm':[168]}

massmodel = 1

ldmodel = 6

strength = 2

gnorm = 1.

optical = 'localomp n', 'jlmomp y'

astro = 'y'

preequilibrium = 'y'
fileresidual = 'y'
outlevels = 'y'
outdensity = 'y'
outgamma = 'y'

transeps = 1.00E-15
xseps = 1.00E-25
popeps = 1.00E-25
