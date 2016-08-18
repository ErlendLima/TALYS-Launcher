#!/bin/sh
#SBATCH --account=uio
#SBATCH --job-name=Gd
#SBATCH --time=50:0:0
#SBATCH --mem-per-cpu=500M
source /cluster/bin/jobsetup
module purge   # clear any inherited modules
set -o errexit # exit on errors

MAX="$(ls -l indices/ | wc -l)"

arrayrun 1-$MAX workerscript.sh
