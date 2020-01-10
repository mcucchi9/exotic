#!/bin/bash
 
#SBATCH --ntasks=1 #(default, so here optional)
#SBATCH --cpus-per-task=1  #(default, so here optional)
#SBATCH --job-name=check_broken_netcdf
#SBATCH --output=check_broken_netcdf.out
#SBATCH --error=check_broken_netcdf_err.out 
#SBATCH --partition=cluster #(optional, default is cluster)
#SBATCH --time=24:00:00 #(optional, default is 24 hours)
#SBATCH --mem=4096

#SBATCH --mail-type=ALL
#SBATCH --mail-user=mcucchi9@gmail.com

python3 ../scripts/check_broken_netcdf.py ${1}
