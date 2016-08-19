# TALYS Launcher
<p align="center">
<b><a href="#setup">Setup</a></b>
|
<b><a href="#usage">Usage</a></b>
|
<b><a href="#multiprocessing">Multiprocessing</a></b>
|
<b><a href="support for open mpi">Support for OpenMPI</a></b>
|
<b><a href="#credits">Credits</a></b>
|
<b><a href="#license">License</a></b>
</p>
<br>

[![](http://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)][license]
![](https://img.shields.io/badge/platform-OS%20X%20%7C%20Linux-808080.svg?style=flat-square)


_Talys Launcher_ automates the tedious process of writing input files for
[TALYS][talys], running TALYS and organizing the output. The script is written
in Python, and is compatible with both Python 2.7 and 3+

## Setup
Clone this repo with https: `git clone https://github.com/ellenhafli/TALYS-master.git`  
or with ssh: `git clone git@github.com:ellenhafli/TALYS-master.git`

The only requirement is `numpy`, which can be installed with `pip install numpy`.
If one wishes to use MPI, the package `mpi4py` is also required. All of
the necessary packages can be installed with `pip install -r requirements`. 

## Usage
To run _talys launcher_ type `python talys.py` in the terminal.  

Further options:
```console
optional arguments:
  --default-excepthook  use the default excepthook
  --disable-filters     do not filter log messages
  --dummy               for not run TALYS, only create the directories
  --efile ERROR_FILENAME
                        filename of the error file
  --enable-pausing      enable pausing by running a process that checks for input
  --ifile INPUT_FILENAME
                        the filename for where the options are storedDefault is 
  --lfile LOG_FILENAME  filename of the log file
  --multi MULTI [MULTI ...]
                        the name of the level at which multiprocessing will be run.
                        This should only be used if _only_ mass and elements vary
  -d, --debug           show debugging information. Overrules log and verbosity
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        set the verbosity for the log file
  -p [N], --processes [N]
                        set the number of processes the script will use.
                        Should be less than or equal to number of CPU cores.
                        If no N is specified, all available cores are used
  -r, --resume          resume from previous checkpoint. If there are
                        more than one TALYS-directory, it will choose
                        the last directory
  -v {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --verbosity {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        set the verbosity level
```
### Multiprocessing
TALYS itself does not support multiprocessing, but the script can take
advantage of the cores on your computer by specifying the option `-p N`, where `N`
is the number of cores you wish to use. If `N` is left out, the script will
try to use all of the cores available.
    
### Support for [OpenMPI][openmpi]
Tens of thousands of TALYS-runs can quickly become infeasible on a normal
desktop computer, instead demanding the computing power of a cluster.
_Talys Launcer_ supports OpenMPI through the package [mpi4py][mpi4pylink]. To use this
feature, simply type `mpirun -np N python talys.py` in the terminal, where
`N` is the number of cores to be used. Note that standard multiprocessing
can not be used in conjunction with MPI, and will throw and error if
attempted.
    
As a result of how OpenMPI is designed, OpenMPI does not guarantee that the
spawned TALYS-processes recieve one core each. If two or more processes
share a core, a catastrophic increase in computing time will ensue. To
prevent this, ask for more cores from whatever queue-system your cluster is
using than what is specified in `mpirun -np N`. For example, if using
SLURM, the jobscript would contain
    
```Shell
#SBATCH -ntasks=64
...
mpirun --nooversubscribe -np 50 python talys.py
```
A complete example is available [here][jobscript]
        
Do keep in mind that OpenMPI does not support fork() over InfiBand.
Therefore, running _Talys Launcher_ with mpi over Infiband will most
probably lead to memory corruption and segfaults. The solution to this
is to use `python talys.py --dummy` which only creates the directory
structure and input files. It also creates an "indices" directory containing
enumerated files pointing to the input file and result directory. One can then use
an array job to run talys. See the files [arrayscript][arrayscript] and 
[workerscript][workerscript] for an example.

## Credits
The contributors to this project are Erlend Lima, Ellen Wold Hafli, Ina Kristine Berentsen Kullmann and Ann-Cecilie Larsen.

## License
This project is licensed under the terms of the **MIT** license.
You can check out the full license [here][license]

[talys]: "https://www.talys.eu"
[openmpi]: "https://www.open-mpi.org/"
[mpi4pylink]: "https://bitbucket.org/mpi4py/mpi4py"
[license]: LICENSE
[jobscript]: jobscript
[arrayscript]: arrayscript.sh
[workerscript]: workerscript.sh
