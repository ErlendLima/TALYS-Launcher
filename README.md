# TALYS Launcher

_Talys Launcher_ automates the tedious process of writing input files for
[TALYS][talys], running TALYS and organizing the output. The script is written
in Python, and is compatible with both Python 2.7 and 3+



## Setup
Clone this repo with https: `git clone
https://github.com/ellenhafli/TALYS-master.git`  
or with ssh: `git clone git@github.com:ellenhafli/TALYS-master.git`

The only requirement is `numpy`, which can be installed with `pip install
numpy`. If one wishes to use MPI, the package `mpi4py` is also required. All of
the necessary packages can be installed with `pip install -r requirements`. 

## Usage
To run _Talys Launcher_ type `python talys.py` in the terminal.  

Further options:
    ```
     usage: talys.py [-h] [--debug] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-v {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                        [--lfile LOG_FILENAME] [--efile ERROR_FILENAME] [--ifile INPUT_FILENAME] [-p [N]] [--enable-pausing]
                        [--multi MULTI [MULTI ...]] [--default-excepthook] [--disable-filters]
        
        optional arguments:
          -h, --help            show this help message and exit
          --debug               show debugging information. Overrules log and verbosity
          -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                                set the log level
          -v {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --verbosity {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                                set the verbosity level
          --lfile LOG_FILENAME  filename of the log file
          --efile ERROR_FILENAME
                                filename of the error file
          --ifile INPUT_FILENAME
                                the filename for where the options are stored
          -p [N], --processes [N]
                                set the number of processes the script will use. Should be less than or equal to number of CPU cores. If no
                                N is specified, all available cores are used
          --enable-pausing      enable pausing by running a process that checks for input
          --multi MULTI [MULTI ...]
                                The name of the level at which multiprocessing will be run. Do not use if any parameters vary!!
          --default-excepthook  use the default excepthook
          --disable-filters     do not filter log messages
          ```
          
### Multiprocessing
    TALYS itself does not support multiprocessing, but the script can use all
    available cores on your computer by specifying the option `-p N`, where `N`
    is the number of cores you wish to use. If `N` is left out, the script will
    try to use all of the cores available.
    
### Support for [openMPI][openmpi]
    Tens of thousands of TALYS-runs can quickly become infeasible on a normal
    desktop computer, instead demanding the computing power of a cluster.
    _Talys Launcer_ supports openMPI through the package [mpi4py][mpi4pylink]. To use this
    feature, simply type `mpirun -np N python talys.py` in the terminal, where
    `N` is the number of cores to be used. Note that standard multiprocessing
    can not be used in conjunction with MPI, and will throw and error if
    attempted.
    
    As a result of how openMPI is designed, openMPI does not guarantee that the
    spawned TALYS-processes recieve one core each. If two or more processes
    share a core, a catastrophic increase in computing time will ensue. To
    prevent this, ask for more cores from whatever queue-system your cluster is
    using than what is specified in `mpirun -np N`. For example, if using
    SLURM, the jobscript would contain
    
        ```Shell
        #SBATCH -ntasks=64
        ...
        mpirun -np 50 python talys.py
        ```
        

    

## License
>You can check out the full license [here](https://github.com/IgorAntun/node-chat/blob/master/LICENSE)

This project is licensed under the terms of the **GNU** license.

[talys]: "www.talys.eu"
[openmpi]: "https://www.open-mpi.org/"
[mpi4pylink]: "https://bitbucket.org/mpi4py/mpi4py"
        
