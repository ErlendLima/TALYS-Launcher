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

optical = 'localomp n', 'jlmomp y'


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
