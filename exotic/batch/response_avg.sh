#!/bin/bash
 
#SBATCH --ntasks=1 #(default, so here optional)
#SBATCH --cpus-per-task=1  #(default, so here optional)
#SBATCH --job-name=response_avg
#SBATCH --output=response_avg.out 
#SBATCH --partition=cluster #(optional, default is cluster)
#SBATCH --time=6:00:00 #(optional, default is 24 hours)
#SBATCH --mem-per-cpu=1024

#SBATCH --mail-type=FAIL
#SBATCH --mail-user=chosky87@gmail.com

# {1}: forcing_sn
# {2}: obs_sn
# {3}: q1
# {4}: q2

python3 ../scripts/response_avg.py ${1} ${2} ${3} ${4}
