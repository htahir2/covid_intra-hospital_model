#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 10 11:16:33 2020
@author: hannantahir
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import math

indir = '/Users/tm-pham/PhD/covid-19/abm/data/Final_simulations_20210204_results/ppe_090_new_strain_30min_contact_hcws/'

resultdir_inter = indir+'combined_results/interventions/'

print("Running plot_combined_results_cleaned_short.py")
print("Current folder: ", indir)

#### Define interventions
all_interv = ["ppe_070", "ppe_070_no_WaCh", "ppe_070_all_hcws", "screen_3_perf_sens", "screen_3", "screen_7", "cont_trac_7_perf_sens", "cont_trac_2", "cont_trac_7"]
screen = ["screen_3_perf_sens","screen_3", "screen_7"]
ct = ["cont_trac_7_perf_sens","cont_trac_2", "cont_trac_7"]
all_indir = ["ppe", "ppe_wo_hcw_change", "ppe_all_hcws", "screen_3_perf_sens", "screen_3", "screen_7","cont_trac_7_perf_sens", "cont_trac_2", "cont_trac_7"]
all_names = ['Baseline','No HCW ward change','PPE everywhere','Screening 3 days perf sens','Screening 3 days','Screening 7 days','Cont Trace 7 perf sens','Cont Trace 2','Cont Trace 7']
scr_names = ['Screening 3 days perf sens','Screening 3 days','Screening 7 days']
ct_names = ['Cont Trace 7 perf sens','Cont Trace 2','Cont Trace 7']

#### Define number of wards in covid and non-covid
n_covid_wards = 8
n_noncovid_wards = 20

#### Directories for all interventions
indir_interv = {}
for i in range(0,len(all_interv)):
  indir_interv[all_interv[i]] =  indir+all_indir[i]+'/results/'
  print(indir_interv[all_interv[i]])

#### ---------------------------------------------------------------------- ####
#### Occupied beds by covid patients (mean, percentile)
#### ---------------------------------------------------------------------- ####
occ_beds_input = {}
occ_beds_output = {}
with pd.ExcelWriter(resultdir_inter+'occ_beds_covid_wards_over_time.xlsx') as writer:
    for i in range(0, len(all_interv)):
        occ_beds_input[all_interv[i]] = pd.read_csv(indir_interv[all_interv[i]]+'occupied_beds_covid_wards.csv')
        occ_beds_output[all_interv[i]] = pd.DataFrame(columns = ['mean','ci_upper','ci_lower'])
        occ_beds_output[all_interv[i]]['mean'] = occ_beds_input[all_interv[i]]['mean']
        occ_beds_output[all_interv[i]]['ci_lower'] = occ_beds_input[all_interv[i]]['ci_lower']
        occ_beds_output[all_interv[i]]['ci_upper'] = occ_beds_input[all_interv[i]]['ci_upper']
        occ_beds_output[all_interv[i]].to_excel(writer, sheet_name=all_names[i], index = False)

#### ---------------------------------------------------------------------- ####
#### Symptomatic patients (mean, percentile)
#### ---------------------------------------------------------------------- ####
pat_input = {}
pat_output = {}
with pd.ExcelWriter(resultdir_inter+'Symptomatic_patients_over_time.xlsx') as writer:
    for i in range(0, len(all_interv)):
        pat_input[all_interv[i]] = pd.read_csv(indir_interv[all_interv[i]]+'patients_by_state_per_day.csv')
        pat_output[all_interv[i]] = pd.DataFrame(columns = ['mean','ci_upper','ci_lower'])
        pat_output[all_interv[i]]['mean'] = pat_input[all_interv[i]]['symptomatic_mean']
        pat_output[all_interv[i]]['ci_lower'] = pat_input[all_interv[i]]['symptomatic_ci_lower']
        pat_output[all_interv[i]]['ci_upper'] = pat_input[all_interv[i]]['symptomatic_ci_upper']
        pat_output[all_interv[i]].to_excel(writer, sheet_name=all_names[i], index = False)


#### ---------------------------------------------------------------------- ####
#### HCWs Recovered
#### ---------------------------------------------------------------------- ####
#### percentage HCW recovered New method, proportion estimated from every simulation for every scenario

### Infector state and transmission data
#ppe_070_test_sens_high_recov.hist(column="Recovered_percentage")
recov_input = {}
recov_output = {}
with pd.ExcelWriter(resultdir_inter+'Recovered_HCWs.xlsx') as writer:
    for i in range(0, len(all_interv)):
        recov_input[all_interv[i]] = pd.read_csv(indir_interv[all_interv[i]]+'precent_recovered_hcws.csv')
        recov_output[all_interv[i]] = pd.DataFrame(columns = ['recovered mean','ci_upper','ci_lower'])
        recov_output[all_interv[i]].loc[0,:] = recov_input[all_interv[i]]['Recovered_percentage'].mean(),np.percentile(recov_input[all_interv[i]]['Recovered_percentage'],97.5),np.percentile(recov_input[all_interv[i]]['Recovered_percentage'],2.5)
        recov_output[all_interv[i]].to_excel(writer, sheet_name=all_names[i], index = False)

#### ---------------------------------------------------------------------- ####
#### Positivity rates
#### ---------------------------------------------------------------------- ####

### write screening_positivity_rate data_over time (per day)
scr_3_rate_perf = pd.read_csv(indir_interv['screen_3_perf_sens']+'screening_data_time_dependant.csv')
scr_3_rate_perf.rename(columns = {'Unnamed: 0': 'time in days'}, inplace = True)
scr_3_rate_perf['time in days'] = (scr_3_rate_perf['time in days']*3)+3

scr_3_rate = pd.read_csv(indir_interv['screen_3']+'screening_data_time_dependant.csv')
scr_3_rate.rename(columns = {'Unnamed: 0': 'time in days'}, inplace = True)
scr_3_rate['time in days'] = (scr_3_rate['time in days']*3)+3

scr_7_rate = pd.read_csv(indir_interv['screen_7']+'screening_data_time_dependant.csv')
scr_7_rate.rename(columns = {'Unnamed: 0': 'time in days'}, inplace = True)
scr_7_rate['time in days'] = (scr_7_rate['time in days']*7)+7

with pd.ExcelWriter(resultdir_inter+'Positivity_rate_screening.xlsx') as writer:
    scr_3_rate_perf.to_excel(writer, sheet_name='Screening 3 days perf sens', index = False)
    scr_3_rate.to_excel(writer, sheet_name='Screening 3 days', index = False)
    scr_7_rate.to_excel(writer, sheet_name='Screening 7 days', index = False)


### Positivity rates for screeening and contact tracing over the whole simulation period
pos_rate_input = {}
pos_rate_output = {}
with pd.ExcelWriter(resultdir_inter+'positivity_rates.xlsx') as writer:
    for i in range(0,len(screen)):
        pos_rate_input[screen[i]] =  pd.read_csv(indir_interv[screen[i]]+'screening_outbreak_period.csv')
        pos_rate_input[screen[i]].drop(pos_rate_input[screen[i]].columns[[0,1,2]], axis=1, inplace=True)
        pos_rate_output[screen[i]] = pd.DataFrame(columns = ['mean','max','ci_upper','ci_lower','std'])
        pos_rate_output[screen[i]].loc[0,:] = pos_rate_input[screen[i]]['positivity_rate'].mean(),pos_rate_input[screen[i]]['positivity_rate'].max(),np.percentile(pos_rate_input[screen[i]]['positivity_rate'],97.5),np.percentile(pos_rate_input[screen[i]]['positivity_rate'],2.5),pos_rate_input[screen[i]]['positivity_rate'].std()
        pos_rate_output[screen[i]].to_excel(writer, sheet_name=scr_names[i], index = False)
    for i in range(0,len(ct)):
        pos_rate_input[ct[i]] =  pd.read_csv(indir_interv[ct[i]]+'contact_tracing.csv')
        #pos_rate_input[ct[i]].drop(pos_rate_input[ct[i]].columns[[0]], axis=1, inplace=True)
        pos_rate_output[ct[i]] = pd.DataFrame(columns = ['mean','max','ci_upper','ci_lower'])
        pos_rate_output[ct[i]].loc[0,:] = pos_rate_input[ct[i]]['positivity_rate'].mean(),pos_rate_input[ct[i]]['positivity_rate'].max(),np.percentile(pos_rate_input[ct[i]]['positivity_rate'],97.5),np.percentile(pos_rate_input[ct[i]]['positivity_rate'],2.5)
        pos_rate_output[ct[i]].to_excel(writer, sheet_name=ct_names[i], index = False)

pos_rate_sim_input = {}
pos_rate_sim_output = {}
with pd.ExcelWriter(resultdir_inter+'positivity_rates_contact_tracing_sim.xlsx') as writer:
    for i in range(0,len(ct)):
        pos_rate_sim_input[ct[i]] =  pd.read_csv(indir_interv[ct[i]]+'contact_tracing_per_sim.csv')
        pos_rate_sim_input[ct[i]].drop(pos_rate_sim_input[ct[i]].columns[[0]], axis=1, inplace=True)
        pos_rate_sim_input[ct[i]].to_excel(writer, sheet_name=ct_names[i], index = False)


pos_rate_over_time = {}
with pd.ExcelWriter(resultdir_inter+'positivity_rates_contact_tracing_over_time_all_sim_appended.xlsx') as writer:
    for i in range(0,len(ct)):
        pos_rate_over_time[ct[i]] =  pd.read_csv(indir_interv[ct[i]]+'contact_tracing_with_time_data_appended.csv')
        pos_rate_over_time[ct[i]].drop(pos_rate_over_time[ct[i]].columns[[0]], axis=1, inplace=True)
        pos_rate_over_time[ct[i]].to_excel(writer, sheet_name=ct_names[i], index = False)

scr_pos_rate_over_time = {}
with pd.ExcelWriter(resultdir_inter+'positivity_rates_screening_over_time_all_sim_appended.xlsx') as writer:
    for i in range(0,len(screen)-1):
        scr_pos_rate_over_time[screen[i]] =  pd.read_csv(indir_interv[screen[i]]+'screening_with_time_data_appended.csv')
        scr_pos_rate_over_time[screen[i]].drop(scr_pos_rate_over_time[screen[i]].columns[[0]], axis=1, inplace=True)
        scr_pos_rate_over_time[screen[i]].to_excel(writer, sheet_name=scr_names[i], index = False)
    scr_pos_rate_over_time[screen[2]] =  pd.read_csv(indir_interv[screen[2]]+'screening_7days_with_time_data_appended.csv')
    scr_pos_rate_over_time[screen[2]].drop(scr_pos_rate_over_time[screen[2]].columns[[0]], axis=1, inplace=True)
    scr_pos_rate_over_time[screen[2]].to_excel(writer, sheet_name=scr_names[2], index = False)


#### ---------------------------------------------------------------------- ####
#### Transmission route contribution
#### ---------------------------------------------------------------------- ####
route_input = {}
count = {}
attack_rate_output = {}
infect_state_trans_output = {}
route_output = {}

for i in range(0,len(all_interv)):
    route_input[all_interv[i]] = pd.read_csv(indir_interv[all_interv[i]]+'transmission_route.csv')
    count[all_interv[i]] = route_input[all_interv[i]][['Total_transmission','HCW_community_trans_count','Total_trans_non_covid_wards','Total_trans_covid_wards']]
    count[all_interv[i]]['percent_transm_covid_wards'] = count[all_interv[i]]['Total_trans_covid_wards']*100/count[all_interv[i]]['Total_transmission']
    count[all_interv[i]]['percent_transm_non-covid_wards'] = count[all_interv[i]]['Total_trans_non_covid_wards']*100/count[all_interv[i]]['Total_transmission']
    count[all_interv[i]]['total_transm_per_ward'] = count[all_interv[i]]['Total_trans_non_covid_wards']/n_noncovid_wards + count[all_interv[i]]['Total_trans_covid_wards']/n_covid_wards
    count[all_interv[i]]['percent_transm_covid_per_ward'] = (count[all_interv[i]]['Total_trans_covid_wards']/n_covid_wards)*100/count[all_interv[i]]['total_transm_per_ward']
    count[all_interv[i]]['percent_transm_non-covid_per_ward'] = (count[all_interv[i]]['Total_trans_non_covid_wards']/n_noncovid_wards)*100/count[all_interv[i]]['total_transm_per_ward']
    attack_rate_output[all_interv[i]]= route_input[all_interv[i]][['N-P_count','HC-P_count','Num_susceptible_patients']]
    attack_rate_output[all_interv[i]]['trans_patients'] = attack_rate_output[all_interv[i]]['N-P_count'] + attack_rate_output[all_interv[i]]['HC-P_count']
    attack_rate_output[all_interv[i]]['Total Attack Rate'] = attack_rate_output[all_interv[i]]['trans_patients'] / attack_rate_output[all_interv[i]]['Num_susceptible_patients']
    attack_rate_output[all_interv[i]].drop(attack_rate_output[all_interv[i]].columns[[0,1,2,3]], axis=1, inplace=True)
    infect_state_trans_output[all_interv[i]] = route_input[all_interv[i]][['trans_counts_from_pre_symptomatic','trans_counts_from_symptomatic','trans_counts_from_assymptomatic','Total_transmission']]
    infect_state_trans_output[all_interv[i]]['Exposed'] = infect_state_trans_output[all_interv[i]]['trans_counts_from_pre_symptomatic']*100/infect_state_trans_output[all_interv[i]]['Total_transmission']
    infect_state_trans_output[all_interv[i]]['Symptomatic'] = infect_state_trans_output[all_interv[i]]['trans_counts_from_symptomatic']*100/infect_state_trans_output[all_interv[i]]['Total_transmission']
    infect_state_trans_output[all_interv[i]]['Asymptomatic'] = infect_state_trans_output[all_interv[i]]['trans_counts_from_assymptomatic']*100/infect_state_trans_output[all_interv[i]]['Total_transmission']
    infect_state_trans_output[all_interv[i]].drop(infect_state_trans_output[all_interv[i]].columns[[0,1,2,3]], axis=1, inplace=True)
    route_input[all_interv[i]].drop(route_input[all_interv[i]].columns[[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]], axis=1, inplace=True)

### Infector state and transmission data
infect_state_output = {}
with pd.ExcelWriter(resultdir_inter+'infector_state_and_transmissions.xlsx') as writer:
        for i in range(0,len(all_interv)):
            infect_state_output[all_interv[i]] = pd.DataFrame(columns = ['Pre_sypmtomatic_mean','Pre_sypmtomatic_ci_upper','Pre_sypmtomatic_ci_lower', 'Sypmtomatic_mean','Sypmtomatic_ci_upper','Sypmtomatic_ci_lower', 'Asypmtomatic_mean','Asypmtomatic_ci_upper','Asypmtomatic_ci_lower'])
            infect_state_output[all_interv[i]].loc[0,:]=infect_state_trans_output[all_interv[i]]['Exposed'].mean(), np.percentile(infect_state_trans_output[all_interv[i]]['Exposed'],97.5), np.percentile(infect_state_trans_output[all_interv[i]]['Exposed'],2.5), infect_state_trans_output[all_interv[i]]['Symptomatic'].mean(), np.percentile(infect_state_trans_output[all_interv[i]]['Symptomatic'],97.5), np.percentile(infect_state_trans_output[all_interv[i]]['Symptomatic'],2.5), infect_state_trans_output[all_interv[i]]['Asymptomatic'].mean(), np.percentile(infect_state_trans_output[all_interv[i]]['Asymptomatic'],97.5), np.percentile(infect_state_trans_output[all_interv[i]]['Asymptomatic'],2.5)
            infect_state_output[all_interv[i]].to_excel(writer, sheet_name = all_names[i], index = False)

### transmission route data
trans_route_output = {}
with pd.ExcelWriter(resultdir_inter+'transmissions_route.xlsx') as writer:
    for i in range(0,len(all_interv)):
        trans_route_output[all_interv[i]] = pd.DataFrame(columns = ['P-N mean','P-N ci_upper','P-N ci_lower', 'P-HC mean','P-HC ci_upper','P-HC ci_lower', 'N-P mean','N-P ci_upper','N-P ci_lower','N-HC mean','N-HC ci_upper','N-HC ci_lower', 'N-N mean','N-N ci_upper','N-N ci_lower', 'HC-P mean','HC-P ci_upper','HC-P ci_lower', 'HC-N mean','HC-N ci_upper','HC-N ci_lower', 'HC-HC mean','HC-HC ci_upper','HC-HC ci_lower'])
        trans_route_output[all_interv[i]].loc[0,:] = route_input[all_interv[i]] ['P-N'].mean(),np.percentile(route_input[all_interv[i]] ['P-N'],97.5),np.percentile(route_input[all_interv[i]] ['P-N'],2.5), route_input[all_interv[i]] ['P-HC'].mean(),np.percentile(route_input[all_interv[i]] ['P-HC'],97.5),np.percentile(route_input[all_interv[i]] ['P-HC'],2.5), route_input[all_interv[i]] ['N-P'].mean(),np.percentile(route_input[all_interv[i]] ['N-P'],97.5),np.percentile(route_input[all_interv[i]] ['N-P'],2.5),route_input[all_interv[i]] ['N-HC'].mean(),np.percentile(route_input[all_interv[i]] ['N-HC'],97.5),np.percentile(route_input[all_interv[i]] ['N-HC'],2.5), route_input[all_interv[i]] ['N-N'].mean(),np.percentile(route_input[all_interv[i]] ['N-N'],97.5),np.percentile(route_input[all_interv[i]] ['N-N'],2.5), route_input[all_interv[i]] ['HC-P'].mean(),np.percentile(route_input[all_interv[i]] ['HC-P'],97.5),np.percentile(route_input[all_interv[i]] ['HC-P'],2.5), route_input[all_interv[i]] ['HC-N'].mean(),np.percentile(route_input[all_interv[i]] ['HC-N'],97.5),np.percentile(route_input[all_interv[i]] ['HC-N'],2.5), route_input[all_interv[i]] ['HC-HC'].mean(),np.percentile(route_input[all_interv[i]] ['HC-HC'],97.5),np.percentile(route_input[all_interv[i]] ['HC-HC'],2.5)
        trans_route_output[all_interv[i]].to_excel(writer, sheet_name=all_names[i], index = False)

### percentage transmission covid and non-covid wards
### Compute mean over simulations
perc_trans_output = {}
with pd.ExcelWriter(resultdir_inter+'perc_transm_covid_and_non_covid_wards.xlsx') as writer:
    for i in range(0, len(all_interv)):
        perc_trans_output[all_interv[i]] = pd.DataFrame(columns = ['percent transmissions covid ward mean','percent transmissions covid ward ci_upper','percent transmissions covid ward ci_lower', 'percent transmissions non-covid ward mean','percent transmissions non-covid ward ci_upper','percent transmissions non-covid ward ci_lower'])
        perc_trans_output[all_interv[i]].loc[0,:] = count[all_interv[i]]['percent_transm_covid_wards'].mean(),np.percentile(count[all_interv[i]]['percent_transm_covid_wards'],97.5),np.percentile(count[all_interv[i]]['percent_transm_covid_wards'],2.5), count[all_interv[i]]['percent_transm_non-covid_wards'].mean(),np.percentile(count[all_interv[i]]['percent_transm_non-covid_wards'],97.5),np.percentile(count[all_interv[i]]['percent_transm_non-covid_wards'],2.5)
        perc_trans_output[all_interv[i]].to_excel(writer, sheet_name=all_names[i], index = False)

### Transmissions per covid and non-covid ward
perc_trans_ward_output = {}
with pd.ExcelWriter(resultdir_inter+'perc_transm_covid_and_non_covid_per_ward.xlsx') as writer:
    for i in range(0, len(all_interv)):
        perc_trans_ward_output[all_interv[i]] = pd.DataFrame(columns = ['percent transmissions covid ward mean','percent transmissions covid ward ci_upper','percent transmissions covid ward ci_lower', 'percent transmissions non-covid ward mean','percent transmissions non-covid ward ci_upper','percent transmissions non-covid ward ci_lower'])
        perc_trans_ward_output[all_interv[i]].loc[0,:] = count[all_interv[i]]['percent_transm_covid_per_ward'].mean(),np.percentile(count[all_interv[i]]['percent_transm_covid_per_ward'],97.5),np.percentile(count[all_interv[i]]['percent_transm_covid_per_ward'],2.5), count[all_interv[i]]['percent_transm_non-covid_per_ward'].mean(),np.percentile(count[all_interv[i]]['percent_transm_non-covid_per_ward'],97.5),np.percentile(count[all_interv[i]]['percent_transm_non-covid_per_ward'],2.5)
        perc_trans_ward_output[all_interv[i]].to_excel(writer, sheet_name=all_names[i], index = False)

### percentage transmission covid and non-covid wards
### Sum over all simulations
perc_trans_sum_output = {}
with pd.ExcelWriter(resultdir_inter+'perc_transm_sum_covid_and_non_covid_wards.xlsx') as writer:
    for i in range(0, len(all_interv)):
        perc_trans_sum_output[all_interv[i]] = pd.DataFrame(columns = ['Total_trans_covid_wards','Total_trans_non_covid_wards','Total_transmission','percent transmissions covid ward','percent transmissions non-covid ward'])
        perc_trans_sum_output[all_interv[i]].loc[0,:] = count[all_interv[i]]['Total_trans_covid_wards'].sum(), count[all_interv[i]]['Total_trans_non_covid_wards'].sum(), count[all_interv[i]]['Total_transmission'].sum(), count[all_interv[i]]['Total_trans_covid_wards'].sum()*100/count[all_interv[i]]['Total_transmission'].sum(), count[all_interv[i]]['Total_trans_non_covid_wards'].sum()*100/count[all_interv[i]]['Total_transmission'].sum()
        perc_trans_sum_output[all_interv[i]].to_excel(writer, sheet_name=all_names[i], index = False)

### Absolute numbers
trans_output = {}
with pd.ExcelWriter(resultdir_inter+'transm_covid_and_non_covid_wards.xlsx') as writer:
    for i in range(0, len(all_interv)):
        trans_output[all_interv[i]] = pd.DataFrame(columns = ['Total_trans_covid_wards_mean','Total_trans_covid_wards_ci_lower','Total_trans_covid_wards_ci_upper','Total_trans_non_covid_wards_mean','Total_trans_non_covid_wards_ci_lower','Total_trans_non_covid_wards_ci_upper','Total_transmission_mean','Total_transmission_ci_lower','Total_transmission_ci_upper'])
        trans_output[all_interv[i]].loc[0,:] = count[all_interv[i]]['Total_trans_covid_wards'].mean(),np.percentile(count[all_interv[i]]['Total_trans_covid_wards'], 2.5),np.percentile(count[all_interv[i]]['Total_trans_covid_wards'], 97.5),count[all_interv[i]]['Total_trans_non_covid_wards'].mean(), np.percentile(count[all_interv[i]]['Total_trans_non_covid_wards'],2.5), np.percentile(count[all_interv[i]]['Total_trans_non_covid_wards'],97.5), count[all_interv[i]]['Total_transmission'].mean(), np.percentile(count[all_interv[i]]['Total_transmission'],2.5),np.percentile(count[all_interv[i]]['Total_transmission'],97.5)
        trans_output[all_interv[i]].to_excel(writer, sheet_name=all_names[i], index = False)


### Data for each simulation per scenario in one file
perc_trans_per_sim_output = {}
with pd.ExcelWriter(resultdir_inter+'perc_transm_per_sim_covid_and_non_covid_wards.xlsx') as writer:
    for i in range(0, len(all_interv)):
        perc_trans_per_sim_output[all_interv[i]] = pd.DataFrame(columns = ['Total_trans_covid_wards','Total_trans_non_covid_wards','Total_transmission','percent transmissions covid ward','percent transmissions non-covid ward'])
        perc_trans_per_sim_output[all_interv[i]].loc[:,'Total_trans_covid_wards'] = count[all_interv[i]]['Total_trans_covid_wards']
        perc_trans_per_sim_output[all_interv[i]].loc[:,'Total_trans_non_covid_wards'] = count[all_interv[i]]['Total_trans_non_covid_wards']
        perc_trans_per_sim_output[all_interv[i]].loc[:,'Total_transmission'] = count[all_interv[i]]['Total_transmission']
        perc_trans_per_sim_output[all_interv[i]].loc[:,'percent transmissions covid ward'] = count[all_interv[i]]['Total_trans_covid_wards']*100/count[all_interv[i]]['Total_transmission']
        perc_trans_per_sim_output[all_interv[i]].loc[:,'percent transmissions non-covid ward'] = count[all_interv[i]]['Total_trans_non_covid_wards']*100/count[all_interv[i]]['Total_transmission']
        perc_trans_per_sim_output[all_interv[i]].to_excel(writer, sheet_name=all_names[i], index = False)


#### ---------------------------------------------------------------------- ####
#### Prevalence (total and nosocomial) over time
#### ---------------------------------------------------------------------- ####
prev_total_input = {}
prev_noso_input = {}
prev_total_data_export = pd.DataFrame() #columns = ['Baseline','No HCW ward change','Screening 3 days', 'Screening 7 days', 'Screening 3 days perfect sensitivity','Contact Tracing])
prev_noso_data_export = pd.DataFrame()

for i in range(0, len(all_interv)):
    prev_total_input[all_interv[i]] = pd.read_csv(indir_interv[all_interv[i]]+'prevalence_total.csv')
    prev_noso_input[all_interv[i]] = pd.read_csv(indir_interv[all_interv[i]]+'prevalence_nosocomial.csv')
    prev_total_data_export[all_names[i]] = prev_total_input[all_interv[i]]['total_prev']
    prev_total_data_export[all_names[i]+'_ci_lower'] = prev_total_input[all_interv[i]]['ci_lower']
    prev_total_data_export[all_names[i]+'_ci_upper'] = prev_total_input[all_interv[i]]['ci_upper']
    prev_noso_data_export[all_names[i]] = prev_noso_input[all_interv[i]]['trans_prev']
    prev_noso_data_export[all_names[i]+ '_ci_lower'] = prev_noso_input[all_interv[i]]['ci_lower']
    prev_noso_data_export[all_names[i]+ '_ci_upper'] = prev_noso_input[all_interv[i]]['ci_upper']

prev_total_data_export.to_csv(resultdir_inter+'prevalence_total_over_time.csv')
prev_noso_data_export.to_csv(resultdir_inter+'prevalence_nosocomial_over_time.csv')

#### ---------------------------------------------------------------------- ####
#### Number of transmissions over time
#### ---------------------------------------------------------------------- ####
transm_pat_input = {}
transm_hcw_input = {}
transm_total_input = {}
transm_pat_data_export = {}
transm_hcw_data_export = {}
transm_total_data_export = {}


with pd.ExcelWriter(resultdir_inter+'transm_pat_over_time.xlsx') as writer:
    for i in range(0, len(all_interv)):
        transm_pat_input[all_interv[i]] = pd.read_csv(indir_interv[all_interv[i]]+'daily_patient_transmission_count.csv')
        transm_pat_data_export[all_names[i]] = pd.DataFrame(columns=['mean', 'ci_lower', 'ci_upper'])
        transm_pat_data_export[all_names[i]]['mean'] = transm_pat_input[all_interv[i]]['mean']
        transm_pat_data_export[all_names[i]]['ci_lower'] = transm_pat_input[all_interv[i]]['ci_lower']
        transm_pat_data_export[all_names[i]]['ci_upper'] = transm_pat_input[all_interv[i]]['ci_upper']
        transm_pat_data_export[all_names[i]].to_excel(writer, sheet_name=all_names[i], index = False)


with pd.ExcelWriter(resultdir_inter+'transm_hcw_over_time.xlsx') as writer:
    for i in range(0, len(all_interv)):
        transm_hcw_input[all_interv[i]] = pd.read_csv(indir_interv[all_interv[i]]+'daily_hcw_transmission_count.csv')
        transm_hcw_data_export[all_names[i]] = pd.DataFrame(columns=['mean', 'ci_lower', 'ci_upper'])
        transm_hcw_data_export[all_names[i]]['mean'] = transm_hcw_input[all_interv[i]]['mean']
        transm_hcw_data_export[all_names[i]]['ci_lower'] = transm_hcw_input[all_interv[i]]['ci_lower']
        transm_hcw_data_export[all_names[i]]['ci_upper'] = transm_hcw_input[all_interv[i]]['ci_upper']
        transm_hcw_data_export[all_names[i]].to_excel(writer, sheet_name=all_names[i], index = False)

with pd.ExcelWriter(resultdir_inter+'transm_total_over_time.xlsx') as writer:
    for i in range(0, len(all_interv)):
        transm_total_input[all_interv[i]] = pd.read_csv(indir_interv[all_interv[i]]+'daily_total_transmission_count.csv')
        transm_total_data_export[all_names[i]] = pd.DataFrame(columns=['mean', 'ci_lower', 'ci_upper'])
        transm_total_data_export[all_names[i]]['mean'] = transm_total_input[all_interv[i]]['mean']
        transm_total_data_export[all_names[i]]['ci_lower'] = transm_total_input[all_interv[i]]['ci_lower']
        transm_total_data_export[all_names[i]]['ci_upper'] = transm_total_input[all_interv[i]]['ci_upper']
        transm_total_data_export[all_names[i]].to_excel(writer, sheet_name=all_names[i], index = False)


#### ---------------------------------------------------------------------- ####
#### Absent HCWs
#### ---------------------------------------------------------------------- ####
hcw_abs = {}
with pd.ExcelWriter(resultdir_inter+'percent_daily_absent_hcws.xlsx') as writer:
    for i in range(0, len(all_interv)):
        hcw_abs[all_interv[i]] = pd.read_csv(indir_interv[all_interv[i]]+'daily_absent_hcw.csv')
        hcw_abs[all_interv[i]].drop(hcw_abs[all_interv[i]].columns[[0]], axis=1, inplace=True)
        hcw_abs[all_interv[i]].to_excel(writer, sheet_name=all_names[i], index = False)

#### ---------------------------------------------------------------------- ####
#### Total number of infected and symptomatic patients per day
#### ---------------------------------------------------------------------- ####
# state_pat_input = {}
# inf_pat_output = pd.DataFrame()
# exposed_pat_output = pd.DataFrame()
# sympt_pat_output = pd.DataFrame()
# asympt_pat_output = pd.DataFrame()
# sum_pat_output = pd.DataFrame()
#
# with pd.ExcelWriter(resultdir_inter+'infected_patients_by_state_over_time.xlsx') as writer:
#     for i in range(0, len(all_interv)):
#         state_pat_input[all_interv[i]] = pd.read_csv(indir_interv[all_interv[i]]+'patients_by_state_per_day.csv')
#         exposed_pat_output[all_names[i]] = state_pat_input[all_interv[i]][['exposed_mean', 'exposed_ci_lower', 'exposed_ci_upper']]
#         sympt_pat_output[all_names[i]] = state_pat_input[all_interv[i]]['symptomatic', 'symptomatic_ci_lower', 'symptomatic_ci_upper']
#         asympt_pat_output[all_names[i]] = state_pat_input[all_interv[i]]['asymptomatic', 'asymptomatic_ci_lower', 'asymptomatic_ci_upper']
#         inf_pat_output[all_names[i]] = exposed_pat_output[all_names[i]] + sympt_pat_output[all_names[i]] + asympt_pat_output[all_names[i]]
#         inf_pat_output.to_excel(writer, sheet_name='Infected', index = False)
#         exposed_pat_output.to_excel(writer, sheet_name='Exposed', index = False)
#         sympt_pat_output.to_excel(writer, sheet_name='Symptomatic', index = False)
#         asympt_pat_output.to_excel(writer, sheet_name='Asymptomatic', index = False)
#
# sympt_pat_output.to_csv(resultdir_inter+'Symptomatic_patients_over_time.csv')







#### ---------------------------------------------------------------------- ####
#### Peak transmission count (Patients)
#### ---------------------------------------------------------------------- ####
peak_trans_pat_input = {}
peak_trans_pat_output = {}
with pd.ExcelWriter(resultdir_inter+'peak_transmissions_patients.xlsx') as writer:
    for i in range(0, len(all_interv)):
        peak_trans_pat_input[all_interv[i]] = pd.read_csv(indir_interv[all_interv[i]]+'peak transmission patients.csv')
        peak_trans_pat_output[all_interv[i]]  = pd.DataFrame(columns = ['mean', 'ci upper', 'ci lower'])
        peak_trans_pat_output[all_interv[i]].loc[1,:] = peak_trans_pat_input[all_interv[i]]['peak transmission'].mean()
        peak_trans_pat_output[all_interv[i]]['ci upper'] = np.percentile(peak_trans_pat_input[all_interv[i]]['peak transmission'],97.5)
        peak_trans_pat_output[all_interv[i]]['ci lower'] = np.percentile(peak_trans_pat_input[all_interv[i]]['peak transmission'],2.5)
        peak_trans_pat_output[all_interv[i]].to_excel(writer, sheet_name=all_names[i], index = False)

### percent reduction_peak prevelance
Z = 1.96 ## represent 95% confidence interval
peak_red_pat = {}
peak_red_pat_output = {}
CV_pat = {}
with pd.ExcelWriter(resultdir_inter+'Percent_reduction_peak_transmissions_patients.xlsx') as writer:
    for i in range(1, len(all_interv)):
        peak_red_pat[all_interv[i]] = ((peak_trans_pat_input[all_interv[0]]['peak transmission'].mean() - peak_trans_pat_input[all_interv[i]]['peak transmission'].mean())*100)/peak_trans_pat_input[all_interv[0]]['peak transmission'].mean()
        peak_red_pat_output[all_interv[i]] = pd.DataFrame(columns = ['percent_reduction', 'ci upper', 'ci lower'])
        CV_baseline_pat = peak_trans_pat_input[all_interv[i]]['peak transmission'].std()/peak_trans_pat_input[all_interv[i]]['peak transmission'].mean() ## cv stands for coefficient of variance calculated as stdev/mean
        CV_pat[all_interv[i]] = peak_trans_pat_input[all_interv[i]]['peak transmission'].std()/peak_trans_pat_input[all_interv[i]]['peak transmission'].mean()
        ci_upp =  (peak_red_pat[all_interv[i]]+1)*((1+(Z*math.sqrt(CV_baseline_pat**2 + CV_pat[all_interv[i]]**2 - ((Z**2)*(CV_baseline_pat**2)*(CV_pat[all_interv[i]]**2)))))/(1-(Z*CV_baseline_pat**2)))-1
        ci_low =  (peak_red_pat[all_interv[i]]+1)*((1-(Z*math.sqrt(CV_baseline_pat**2 + CV_pat[all_interv[i]]**2 - ((Z**2)*(CV_baseline_pat**2)*(CV_pat[all_interv[i]]**2)))))/(1-(Z*CV_baseline_pat**2)))-1
        peak_red_pat_output[all_interv[i]].loc[len(peak_red_pat_output[all_interv[i]]),:] = peak_red_pat[all_interv[i]], ci_upp, ci_low
        peak_red_pat_output[all_interv[i]].to_excel(writer, sheet_name=all_names[i], index = False)


#### ---------------------------------------------------------------------- ####
#### Peak transmission count (HCWs)
#### ---------------------------------------------------------------------- ####
peak_trans_hcw_input = {}
peak_trans_hcw_output = {}
with pd.ExcelWriter(resultdir_inter+'peak_transmissions_hcws.xlsx') as writer:
    for i in range(0, len(all_interv)):
        peak_trans_hcw_input[all_interv[i]] = pd.read_csv(indir_interv[all_interv[i]]+'peak transmission hcws.csv')
        peak_trans_hcw_output[all_interv[i]]  = pd.DataFrame(columns = ['mean', 'ci upper', 'ci lower'])
        peak_trans_hcw_output[all_interv[i]].loc[1,:] = peak_trans_hcw_input[all_interv[i]]['peak transmission'].mean()
        peak_trans_hcw_output[all_interv[i]]['ci upper'] = np.percentile(peak_trans_hcw_input[all_interv[i]]['peak transmission'],97.5)
        peak_trans_hcw_output[all_interv[i]]['ci lower'] = np.percentile(peak_trans_hcw_input[all_interv[i]]['peak transmission'],2.5)
        peak_trans_hcw_output[all_interv[i]].to_excel(writer, sheet_name=all_names[i], index = False)

### percent reduction_peak prevelance
Z = 1.96 ## represent 95% confidence interval
peak_red_hcw = {}
peak_red_hcw_output = {}
CV_hcw = {}
with pd.ExcelWriter(resultdir_inter+'Percent_reduction_peak_transmissions_hcws.xlsx') as writer:
    for i in range(1, len(all_interv)):
        peak_red_hcw[all_interv[i]] = ((peak_trans_hcw_input[all_interv[0]]['peak transmission'].mean() - peak_trans_hcw_input[all_interv[i]]['peak transmission'].mean())*100)/peak_trans_hcw_input[all_interv[0]]['peak transmission'].mean()
        peak_red_hcw_output[all_interv[i]] = pd.DataFrame(columns = ['percent_reduction', 'ci upper', 'ci lower'])
        CV_baseline_hcw = peak_trans_hcw_input[all_interv[i]]['peak transmission'].std()/peak_trans_hcw_input[all_interv[i]]['peak transmission'].mean() ## cv stands for coefficient of variance calculated as stdev/mean
        CV_hcw[all_interv[i]] = peak_trans_hcw_input[all_interv[i]]['peak transmission'].std()/peak_trans_hcw_input[all_interv[i]]['peak transmission'].mean()
        ci_upp =  (peak_red_hcw[all_interv[i]]+1)*((1+(Z*math.sqrt(CV_baseline_hcw**2 + CV_hcw[all_interv[i]]**2 - ((Z**2)*(CV_baseline_hcw**2)*(CV_hcw[all_interv[i]]**2)))))/(1-(Z*CV_baseline_hcw**2)))-1
        ci_low =  (peak_red_hcw[all_interv[i]]+1)*((1-(Z*math.sqrt(CV_baseline_hcw**2 + CV_hcw[all_interv[i]]**2 - ((Z**2)*(CV_baseline_hcw**2)*(CV_hcw[all_interv[i]]**2)))))/(1-(Z*CV_baseline_hcw**2)))-1
        peak_red_hcw_output[all_interv[i]].loc[len(peak_red_hcw_output[all_interv[i]]),:] = peak_red_hcw[all_interv[i]], ci_upp, ci_low
        peak_red_hcw_output[all_interv[i]].to_excel(writer, sheet_name=all_names[i], index = False)


#### ---------------------------------------------------------------------- ####
#### Patients discharged to community
#### ---------------------------------------------------------------------- ####

discharged_pat = {}
with pd.ExcelWriter(resultdir_inter+'discharged_covid19patients.xlsx') as writer:
    for i in range(0, len(all_interv)):
        discharged_pat[all_interv[i]] = pd.read_csv(indir_interv[all_interv[i]]+'COVID-19_patients_discharged_to_community.csv')
        discharged_pat[all_interv[i]].drop(discharged_pat[all_interv[i]].columns[[0]], axis=1, inplace=True)
        discharged_pat[all_interv[i]].to_excel(writer, sheet_name=all_names[i], index = False)


#### ---------------------------------------------------------------------- ####
#### Average number of secondary cases
#### ---------------------------------------------------------------------- ####
r_pat = {}
r_pat_out ={}
with pd.ExcelWriter(resultdir_inter+'reproduction_number.xlsx') as writer:
    for i in range(0, len(all_interv)):
        r_pat[all_interv[i]] = pd.read_csv(indir_interv[all_interv[i]]+'average_second_trans_counts_per_simulation_run.csv')
        r_pat[all_interv[i]].drop(r_pat[all_interv[i]].columns[[0]], axis=1, inplace=True)
        r_pat[all_interv[i]].to_excel(writer, sheet_name=all_names[i], index = False)


raise Exception('exit')
