#!/bin/bash
 
#SBATCH --ntasks=1 #(default, so here optional)
#SBATCH --cpus-per-task=1  #(default, so here optional)
#SBATCH --job-name=obs_quantile_energy
#SBATCH --output=obs_quantile.out 
#SBATCH --partition=cluster #(optional, default is cluster)
#SBATCH --time=1:00:00 #(optional, default is 24 hours)

#SBATCH --mail-type=ALL
#SBATCH --mail-user=chosky87@gmail.com

source ../devel/phd/set_environ_var.sh
python3 ../devel/phd/scripts/compute_quantile.py ${1} ${2} ${3} ${4}
