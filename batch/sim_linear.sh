#!/bin/bash
 
#SBATCH --ntasks=1 #(default, so here optional)
#SBATCH --cpus-per-task=1  #(default, so here optional)
#SBATCH --job-name=sample_simulation
#SBATCH --output=sim_linear.out 
#SBATCH --partition=cluster #(optional, default is cluster)
#SBATCH --time=24:00:00 #(optional, default is 24 hours)

#SBATCH --mail-type=ALL
#SBATCH --mail-user=mcucchi9@gmail.com

# {1}: force_intensity_linear_coeff
# {2}: deactivation_time
# {3}: sim_num

source ../devel/phd/set_environ_var.sh
python3 ../devel/phd/scripts/run_simulation_forcing_linear.py ${1} ${2} ${3}
