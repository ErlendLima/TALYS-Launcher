# TALYS Launcher
<p align="center">
<b><a href="#setup">Setup</a></b>
|
<b><a href="#usage">Usage</a></b>
|
<b><a href="#the-input-file">The Input File</a></b>
|
<b><a href="#multiprocessing">Multiprocessing</a></b>
|
<b><a href="support-for-open-mpi">Support for OpenMPI</a></b>
|
<b><a href="example">Example</a></b>
|
<b><a href="#credits">Credits</a></b>
|
<b><a href="#license">License</a></b>
</p>
<br>

[![](http://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)][license]
![](https://img.shields.io/badge/platform-OS%20X%20%7C%20Linux-808080.svg?style=flat-square)


_TALYS Launcher_ automates the tedious process of writing input files for
[TALYS][talys], running TALYS and organizing the output. The script is written
in Python, and is compatible with both Python 2.7 and 3+

## Setup
Clone this repo with https: 
```console
git clone https://github.com/ErlendLima/TALYS-Launcher.git
```

or with ssh: 
```console
git clone git@github.com:ErlendLima/TALYS-Launcher.git
```

The only requirement is `numpy`, which can be installed with 
```console
pip install numpy
```
If one wishes to use MPI, the package `mpi4py` is also required. All of
the necessary packages can be installed with 
```console
pip install -r requirements
```

## Usage
To run _TALYS launcher_ type 
```console 
python talys.py
```
or
```console
./talys.py
```

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
### The Input File
The script needs an input file in JSON format containing the TALYS keywords and
the keywords to the script. A basic input file is shown below

```json
{    
    "keywords": {
        "strength": [1,2,3,4,5,6,7,8],
        "projectile": "n",
        "element": [
            "Ce", "Dy"
        ],
        "massmodel": [1,2,3],
        "mass": {
            "Ce": [142, 151, 152, 194, 195],
            "Dy": [160, 162, 163]
        },
        "energy": "energies.txt",
    },
    "script_keywords": {
        "energy_start": "0.0025E-03",
        "N": 100,
        "output_file": "output.txt",
        "energy_stop": "5000E-03",
        "input_file": "input.txt",
        "result_files": [
            "astrorate.g",
            "astrorate.tot"
        ]
    },
    "dependents": {
        "comment": "The names, such as 'optical', are irrelevant",
        "Optical":{"localomp":"n", "jlmomp":"y"}
    },
    "scissors":{    
        "Dy": {
            "160": {
                "gpr": 1,
                "spr": 0.47368457989547197,
                "epr": 2.3921663572847525
                }
        } 
    }    
}
```
The first level consists of four elements which the script interprets differently. The two most
important are _keywords_ and _script keywords_.

All of the usual TALYS keywords are put in _keywords_ as one would in a TALYS input file. The difference
is that here one can define ranges which will be iterated over. Should support all possible keywords, ranges and combinations.

The elements in the _script keywords_ describe the names for the files which the script will create, and what energy
range to use.

The _dependents_ block contains exclusive keyword groups. In the example above, _localomp n_ and _jlmomp y_ will never
occur in the same input file for TALYS.

The _scissors_ block is a custom block for implentation of "scissors mode" in TALYS. The reason this is a custom block is that the output format is unusual. Instead of writing overly complex code, one can simply add a custom block and some few lines of code into the script to expand its usage.

[Here][input file] is a complete example of an input file.


### Multiprocessing
TALYS itself does not support multiprocessing, but the script can take
advantage of the cores on your computer by specifying the option `-p N`, where `N`
is the number of cores you wish to use. If `N` is left out, the script will
try to use all of the cores available.
    
### Support for [OpenMPI][openmpi]
Tens of thousands of TALYS-runs can quickly become infeasible on a normal
desktop computer, instead demanding the computing power of a cluster.
_TALYS Launcer_ supports OpenMPI through the package [mpi4py][mpi4pylink]. To use this
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
Therefore, running _TALYS Launcher_ with mpi over Infiband will most
probably lead to memory corruption and segfaults. The solution to this
is to use `python talys.py --dummy` which only creates the directory
structure and input files. It also creates an "indices" directory containing
enumerated files pointing to the input file and result directory. One can then use
an array job to run talys. See the files [arrayscript][arrayscript] and 
[workerscript][workerscript] for an example.

## Example
Here is an example showing the usage of the script on a single machine without MPI. For this,
the files `talys`, `talys.py`, `tools.py`, `readers.py` and `structure.json` are required.
The only file you need to edit is the `structure.json`, which should be thought of as 
a more advanced input file for TALYS.

The file `structure.json` is, as can be seen, a JSON-file. JSON is easy to read for both humans and machines, and is easy to manipulate using various programming languages. 
By default, Talys Launcher looks for `structure.json`, but this can be 
changed to e.g `test.json` by `python talys.py --ifile test.json`. Taking `test.json` as 
an example, they important sections are `keywords` and `script_keywords`. 

`keywords` are the keywords one would put into TALYS' input file, the difference being
that the keywords can be either primitives such as in talys, or lists of primitives (a
primitive is a single value, such as `"strength": 5` or `"localomp": "n"`). If a keyword is
given as a list, TALYS will be run for each value in the list. For example, `"strength": [1,2,4]`
results in 3 TALYS runs, while `"strength: [1,2,3]`, `"localomp": ["y", "n"]` results in 
6.

`script_keywords` is read by TALYS Launcher, and configures the input/output of TALYS which is not controlled by the 
input file. For example, `"energy_start": "0.0025E-03"`, `"energy_stop": "5000E-03"` and `"N": 100` creates
an energy file with energies ranging from `energy_start` to `energy_stop` in `N` steps. 
The keyword `result_files` specifies the files to be copied from the calculation folder to the result folder. The files can be specified as REGEX patterns.

The program can then be run `test.json` using 4 CPU cores by typing

```Shell
python talys.py --ifile test.json -p 4
```

## Credits
The contributors to this project are Erlend Lima, Ellen Wold Hafli, Ina Kristine Berentsen Kullmann and Ann-Cecilie Larsen.

## License
This project is licensed under the terms of the **MIT** license.
You can check out the full license [here][license]

[talys]: "https://www.talys.eu"
[openmpi]: "https://www.open-mpi.org/"
[mpi4pylink]: "https://bitbucket.org/mpi4py/mpi4py"
[license]: LICENSE
[input file]: structure.json
[jobscript]: jobscript
[arrayscript]: arrayscript.sh
[workerscript]: workerscript.sh
