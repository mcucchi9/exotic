#!/bin/bash
 
#SBATCH --ntasks=1 #(default, so here optional)
#SBATCH --cpus-per-task=1  #(default, so here optional)
#SBATCH --job-name=sim_step
#SBATCH --output=sim_step.out 
#SBATCH --partition=cluster #(optional, default is cluster)
#SBATCH --time=24:00:00 #(optional, default is 24 hours)

#SBATCH --mail-type=ALL
#SBATCH --mail-user=mcucchi9@gmail.com

# {1}: force_intensity_delta
# {2}: sim_num

source ../devel/phd/set_environ_var.sh
python3 ../devel/phd/scripts/run_simulation_forcing_step.py ${1} ${2} ${3} ${4}
