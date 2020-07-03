#!/bin/bash

MAX_Q=1

decision_made='n'

while [ "$decision_made" != "y" ]; do

	echo "Forcing: "
	read forcing

	echo "Observable: "
	read obs_main

	echo "Statistics: "
	read obs_sec

	obs=$obs_main"_"$obs_sec

	echo "obs: "$obs
	echo "Is it ok? [y/n]"
	read decision_made

done;

main_data_path="data/response/lorenz96/rk4/"$forcing"/"$obs_main

for q in $(seq 0.0 0.01 1.001); do

	if [ "$obs_sec" == "below" ] || [ "$obs_sec" == "exceed" ]; then
		outfilename=~/$main_data_path"/response_lorenz96_rk4_"$obs"_"$q"q_"$forcing".nc"
		if test ! -f "$outfilename"; then
			echo "sbatch response_avg.sh" $forcing $obs $q; 
        		sbatch response_avg.sh $forcing $obs $q;
    		fi; 
	elif [ "$obs_sec" == "bin" ]; then
		if (( $(echo "$q < $MAX_Q" | bc -l) )); then
			q2=$(printf '%.2f\n' $(echo "scale=2; $q+0.01" | bc -l))
			outfilename=~/$main_data_path"/response_lorenz96_rk4_"$obs"_"$q"q_"$q2"q_"$forcing".nc"
			if test ! -f "$outfilename"; then 
				echo "sbatch response_avg.sh" $forcing $obs $q $q2;
        			sbatch response_avg.sh $forcing $obs $q $q2;
    			fi; 
		fi;
	fi;

done
