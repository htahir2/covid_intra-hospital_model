#!/bin/bash
#Set job requirements
#SBATCH -n 16
#SBATCH -t 20:00:00

module load 2019
module load Python/3.6.6-intel-2019b

cd $HOME/epidemics_sims/covid19/

Folder="$TMPDIR"/HT1301
mkdir $Folder
cp -r ppe_090_new_strain_sens_high $Folder

cd $Folder/ppe_090_new_strain_sens_high/bash_files/

./screen_7.sh &
./screen_3.sh &
./screen_3_perf_sens.sh &
./ppe.sh &
./ppe_wo_hcw_change.sh &
./ppe_all_hcws.sh &
./cont_trac_7_1.sh &
./cont_trac_7_2.sh &
./cont_trac_2_1.sh &
./cont_trac_2_2.sh &
./cont_trac_7_perf_sens.sh &

wait

#Copy output directory from scratch to home

cd ../../
tar cvfz ppe_090_new_strain_sens_high_results.tar.gz ppe_090_new_strain_sens_high
cp ppe_090_new_strain_sens_high_results.tar.gz $HOME/epidemics_sims/covid19/


