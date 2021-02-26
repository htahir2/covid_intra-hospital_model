#!/bin/bash

echo "Bash version ${BASH_VERSION}..."
foldername='/scratch/HT1301/ppe_090_new_strain/cont_trac_7_perf_sens'

resultdir=$foldername'/simulations'
#echo $resultdir
#pwd
for i in {1..100} #specify here how many time you want to run the model
do
#echo "Welcome $i times"
python3 $foldername/run.py
mv -v $resultdir/contact_tracinng_counts.csv $resultdir/contact_tracinng_counts_"$(printf "%04d" "$i")".csv
mv -v $resultdir/screening_counts.csv $resultdir/screening_counts_"$(printf "%04d" "$i")".csv
mv -v $resultdir/covid19_patients_Discharge_count.csv $resultdir/covid19_patients_Discharge_count_"$(printf "%04d" "$i")".csv
mv -v $resultdir/data_total_prev_per_ward.csv $resultdir/data_total_prev_per_ward_"$(printf "%04d" "$i")".csv
mv -v $resultdir/nurses_by_state_per_day_hospital_transmissions_only.csv $resultdir/nurses_by_state_per_day_hospital_transmissions_only_"$(printf "%04d" "$i")".csv
mv -v $resultdir/nurses_by_state_per_day.csv $resultdir/nurses_by_state_per_day_"$(printf "%04d" "$i")".csv
mv -v $resultdir/patients_by_state_per_day_hospital_transmissions_only.csv $resultdir/patients_by_state_per_day_hospital_transmissions_only_"$(printf "%04d" "$i")".csv
mv -v $resultdir/patients_by_state_per_day.csv $resultdir/patients_by_state_per_day_"$(printf "%04d" "$i")".csv
mv -v $resultdir/physicians_by_state_per_day_hospital_transmissions_only.csv $resultdir/physicians_by_state_per_day_hospital_transmissions_only_"$(printf "%04d" "$i")".csv
mv -v $resultdir/physicians_by_state_per_day.csv $resultdir/physicians_by_state_per_day_"$(printf "%04d" "$i")".csv
mv -v $resultdir/prev_full_hosp.csv $resultdir/prev_full_hosp_"$(printf "%04d" "$i")".csv
mv -v $resultdir/transmission_routes_contribution_count.csv $resultdir/transmission_routes_contribution_count_"$(printf "%04d" "$i")".csv
mv -v $resultdir/daily_transmissions_count.csv $resultdir/daily_transmissions_count_"$(printf "%04d" "$i")".csv
mv -v $resultdir/daily_absent_hcw_count.csv $resultdir/daily_absent_hcw_count_"$(printf "%04d" "$i")".csv
mv -v $resultdir/daily_infected_hcw_count.csv $resultdir/daily_infected_hcw_count_"$(printf "%04d" "$i")".csv
mv -v $resultdir/time_btw_transm_sym_onset.csv $resultdir/time_btw_transm_sym_onset_"$(printf "%04d" "$i")".csv
mv -v $resultdir/patient_seco_trans_count.csv $resultdir/patient_seco_trans_count_"$(printf "%04d" "$i")".csv
mv -v $resultdir/hcw_seco_trans_count.csv $resultdir/hcw_seco_trans_count_"$(printf "%04d" "$i")".csv
mv -v $resultdir/patients_per_ward_every_day.csv $resultdir/patients_per_ward_every_day_"$(printf "%04d" "$i")".csv
mv -v $resultdir/daily_patients_discharge_per_ward.csv $resultdir/daily_patients_discharge_per_ward_"$(printf "%04d" "$i")".csv
mv -v $resultdir/occupied_beds.csv $resultdir/occupied_beds_"$(printf "%04d" "$i")".csv
done
