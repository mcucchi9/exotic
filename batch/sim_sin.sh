#!/bin/bash
 
#SBATCH --ntasks=1 #(default, so here optional)
#SBATCH --cpus-per-task=1  #(default, so here optional)
#SBATCH --job-name=sample_simulation
#SBATCH --output=sim_sin.out 
#SBATCH --partition=cluster #(optional, default is cluster)
#SBATCH --time=24:00:00 #(optional, default is 24 hours)

#SBATCH --mail-type=ALL
#SBATCH --mail-user=mcucchi9@gmail.com

# {1}: epsilon
# {2}: omega
# {3}: deactivation_time
# {4}: sim_num

source ../devel/phd/set_environ_var.sh
python3 ../devel/phd/scripts/run_simulation_forcing_sin.py ${1} ${2} ${3} ${4}