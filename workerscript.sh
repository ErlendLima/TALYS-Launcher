#!/bin/bash
#SBATCH --account=uio
#SBATCH --job-name=$TASK_ID
#SBATCH --time=1:0:0
#SBATCH --mem-per-cpu=1G
source /cluster/bin/jobsetup
module purge   # clear any inherited modules
set -o errexit # exit on errors

WORKDIR="$SUBMITDIR/$(head -n1 indices/$TASK_ID)"
RESULTDIR="$SUBMITDIR/$(tail -n1 indices/$TASK_ID)"
cleanup "cp * $WORKDIR"
cleanup "cp astrorate.g $RESULTDIR/astrorate.g"
cleanup "cp astrorate.tot $RESULTDIR/astrorate.tot"
cleanup "cp output.txt $RESULTDIR/output.txt"

cp $WORKDIR/input.txt $SCRATCH
cp talys $SCRATCH
cd $SCRATCH
./talys < input.txt > output.txt
rm talys
