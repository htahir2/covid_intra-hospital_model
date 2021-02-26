#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 12 16:09:14 2019

@author: hannantahir
Adapted by Thi Mui Pham
"""
import networkx as nx
import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np
import datetime as dt
from datetime import timedelta
import seaborn as sns
import matplotlib.pyplot as plt
import glob
import os
import math # For using math.floor
#import re

pd.set_option('display.max_columns',30)

dir = '/Users/tm-pham/PhD/covid-19/abm/data/Final_simulations_20210204_results/ppe_090/'

indir = dir + 'ppe_wo_hcw_change/simulations/'

resultdir = dir + 'ppe_wo_hcw_change/results/'

print("Running plot_all_excel_files_2.py")
print("Current folder:", indir)

#### ---------------------------------------------------------------------- ####
#### Occupied beds by symptomatic patients
#### ---------------------------------------------------------------------- ####
df_occ_beds = pd.DataFrame(columns=['mean', 'ci_lower', 'ci_upper'])
sum_covid_wards = pd.DataFrame()
pt_wards_files = glob.glob(indir+ 'occupied_beds_0???.csv')
dfs_pat_wards = {}

for f in pt_wards_files:
    dfs_pat_wards[os.path.splitext(os.path.basename(f))[0]] = pd.read_csv(f)
i = 0
for name in sorted(dfs_pat_wards):
    # Sum up w1 till w8 (COVID wards)
    sum_covid_wards[name] = dfs_pat_wards[name]['occupied_bed']

df_occ_beds['mean'] = sum_covid_wards.mean(axis=1)
df_occ_beds['ci_lower'] = sum_covid_wards.apply(lambda x: np.percentile(x, 2.5), axis=1)
df_occ_beds['ci_upper'] = sum_covid_wards.apply(lambda x: np.percentile(x, 97.5), axis=1)

df_occ_beds.to_csv(resultdir+'occupied_beds_covid_wards.csv')

#### ---------------------------------------------------------------------- ####
#### Tranmission counts
#### ---------------------------------------------------------------------- ####
df_trans_route = pd.DataFrame()
trans_files = glob.glob(indir+'transmission_routes_contribution_count_0???.csv')
dfs_trans = {}

for f in trans_files:
    dfs_trans[os.path.splitext(os.path.basename(f))[0]] = pd.read_csv(f)
i = 0
for name in sorted(dfs_trans):
    df_trans_route.loc[i,'Total_transmission'] = dfs_trans[name]['Total_transmission'].iloc[0]
    df_trans_route.loc[i,'P-N_count'] = dfs_trans[name]['P-N'].iloc[0]
    df_trans_route.loc[i,'P-HC_count'] = dfs_trans[name]['P-HC'].iloc[0]
    df_trans_route.loc[i,'N-P_count'] = dfs_trans[name]['N-P'].iloc[0]
    df_trans_route.loc[i,'N-HC_count'] = dfs_trans[name]['N-HC'].iloc[0]
    df_trans_route.loc[i,'N-N_count'] = dfs_trans[name]['N-N'].iloc[0]
    df_trans_route.loc[i,'HC-P_count'] = dfs_trans[name]['HC-P'].iloc[0]
    df_trans_route.loc[i,'HC-N_count'] = dfs_trans[name]['HC-N'].iloc[0]
    df_trans_route.loc[i,'HC-HC_count'] = dfs_trans[name]['HC-HC'].iloc[0]
    df_trans_route.loc[i,'HCW_community_trans_count'] = dfs_trans[name]['HCW_community_trans_count'].iloc[0]
    df_trans_route.loc[i,'Total_trans_non_covid_wards'] = dfs_trans[name]['Total_trans_non_covid_wards'].iloc[0]
    df_trans_route.loc[i,'Total_trans_covid_wards'] = dfs_trans[name]['Total_trans_covid_wards'].iloc[0]
    df_trans_route.loc[i,'Asympt_patient_admission_count'] = dfs_trans[name]['Asympt_patient_admission_count'].iloc[0]
    df_trans_route.loc[i,'Exposed_patient_admission_count'] = dfs_trans[name]['Exposed_patient_admission_count'].iloc[0]
    df_trans_route.loc[i,'Total_patients_admitted'] = dfs_trans[name]['Total_patients_admitted'].iloc[0]
    df_trans_route.loc[i,'Num_susceptible_patients'] = dfs_trans[name]['Num_susceptible_patients'].iloc[0]
    df_trans_route.loc[i,'num_replacement_hcw'] = dfs_trans[name]['num_replacement_hcw'].iloc[0]
    df_trans_route.loc[i,'trans_counts_from_pre_symptomatic'] = dfs_trans[name]['trans_counts_from_pre_symptomatic'].iloc[0]
    df_trans_route.loc[i,'trans_counts_from_symptomatic'] = dfs_trans[name]['trans_counts_from_symptomatic'].iloc[0]
    df_trans_route.loc[i,'trans_counts_from_assymptomatic'] = dfs_trans[name]['trans_counts_from_assymptomatic'].iloc[0]
    df_trans_route.loc[i,'Trans_count_patients'] = dfs_trans[name]['N-P'].iloc[0] + dfs_trans[name]['HC-P'].iloc[0]
    i += 1

#print('Number of files are ',i)
df_trans_route = df_trans_route.astype(float)
df_trans_route['P-N'] = df_trans_route['P-N_count']*100/df_trans_route['Total_transmission']
df_trans_route['P-HC'] = df_trans_route['P-HC_count']*100/df_trans_route['Total_transmission']
df_trans_route['N-P'] = df_trans_route['N-P_count']*100/df_trans_route['Total_transmission']
df_trans_route['N-HC'] = df_trans_route['N-HC_count']*100/df_trans_route['Total_transmission']
df_trans_route['N-N'] = df_trans_route['N-N_count']*100/df_trans_route['Total_transmission']
df_trans_route['HC-P'] = df_trans_route['HC-P_count']*100/df_trans_route['Total_transmission']
df_trans_route['HC-N'] = df_trans_route['HC-N_count']*100/df_trans_route['Total_transmission']
df_trans_route['HC-HC'] = df_trans_route['HC-HC_count']*100/df_trans_route['Total_transmission']

df_trans_route.to_csv(resultdir+'transmission_route.csv')


#### ---------------------------------------------------------------------- ####
#### Total number of patients and HCWs over time
#### ---------------------------------------------------------------------- ####
patient_files = glob.glob(indir+'patients_by_state_per_day_0???.csv')
nurse_files = glob.glob(indir+'nurses_by_state_per_day_0???.csv')
physician_files = glob.glob(indir+'physicians_by_state_per_day_0???.csv')
dfs_patients = {}
dfs_nurses = {}
dfs_physicians = {}

for p in patient_files:
    dfs_patients[os.path.splitext(os.path.basename(p))[0]] = pd.read_csv(p)
    dfs_patients[os.path.splitext(os.path.basename(p))[0]].rename(columns = {'Unnamed: 0': 'day'}, inplace = True)

for n in nurse_files:
    dfs_nurses[os.path.splitext(os.path.basename(n))[0]] = pd.read_csv(n)
    dfs_nurses[os.path.splitext(os.path.basename(n))[0]].rename(columns = {'Unnamed: 0': 'day'}, inplace = True)

for d in physician_files:
    dfs_physicians[os.path.splitext(os.path.basename(d))[0]] = pd.read_csv(d)
    dfs_physicians[os.path.splitext(os.path.basename(d))[0]].rename(columns = {'Unnamed: 0': 'day'}, inplace = True)

df_total_patients= {}    # Total number of patients
df_total_nurses = {}     # Total number of nurses
df_total_physicians= {}  # Total number of physicians
df_total = {}            # Total number of individuals
df_pos = {}              # Total number of positive patients (exposed, mild, severe, asymptomatics)

for name in sorted(dfs_patients):
    df_total[name] = pd.DataFrame(columns=['day'])
    df_pos[name] = pd.DataFrame(columns=['day'])
    df_total_patients[name] = dfs_patients[name].drop(dfs_patients[name].columns[[1,2,3,4,5,6,7]],axis=1)
    # df_total_patients[name] = dfs_patients[name]['day']
    df_total[name]['day'] = df_total_patients[name]['day']
    df_pos[name]['day'] = df_total_patients[name]['day']
    df_total_patients[name]['n_total'] = dfs_patients[name].iloc[:, dfs_patients[name].columns!='day'].sum(axis=1)
    df_total[name]['n_total'] = df_total_patients[name]['n_total']
    df_pos[name]['n_pos'] = (dfs_patients[name].drop(dfs_patients[name].columns[[0,1,4,6]],axis=1)).sum(axis=1)

i=0
for name in sorted(dfs_nurses):
    df_total_nurses[name] = dfs_nurses[name].drop(dfs_nurses[name].columns[[1,2,3,4,5,6,7]],axis=1)
    df_total_nurses[name]['n_total'] = dfs_nurses[name].iloc[:, dfs_nurses[name].columns!='day'].sum(axis=1)
    df_total[sorted(df_total)[i]]['n_total'] = df_total[sorted(df_total)[i]]['n_total'] + df_total_nurses[name]['n_total']
    df_pos[sorted(df_pos)[i]]['n_pos'] = df_pos[sorted(df_pos)[i]]['n_pos'] + (dfs_nurses[name].drop(dfs_nurses[name].columns[[0,1,4,6]],axis=1)).sum(axis=1)
    i+=1

i=0
for name in sorted(dfs_physicians):
    df_total_physicians[name] = dfs_physicians[name].drop(dfs_physicians[name].columns[[1,2,3,4,5,6,7]],axis=1)
    df_total_physicians[name]['n_total'] = dfs_physicians[name].iloc[:, dfs_physicians[name].columns!='day'].sum(axis=1)
    df_total[sorted(df_total)[i]]['n_total'] = df_total[sorted(df_total)[i]]['n_total'] + df_total_physicians[name]['n_total']
    df_pos[sorted(df_pos)[i]]['n_pos'] = df_pos[sorted(df_pos)[i]]['n_pos'] + (dfs_physicians[name].drop(dfs_physicians[name].columns[[0,1,4,6]],axis=1)).sum(axis=1)
    i+=1

#### ---------------------------------------------------------------------- ####
#### This calculates positivity rates for contact tracing
#### ---------------------------------------------------------------------- ####
df_contact = pd.DataFrame()
df_contact_max = pd.DataFrame()

cont_files = glob.glob(indir+'contact_tracinng_counts_0???.csv')
dfs_contact = {}
for f in cont_files:
    dfs_contact[os.path.splitext(os.path.basename(f))[0]] = pd.read_csv(f, index_col = False)

i = 0
for name in sorted(dfs_contact):
    df_contact.loc[i,'n_contacts_traced'] = dfs_contact[name].num_contacts_traced.sum()
    df_contact.loc[i,'n_pos_contacts'] = dfs_contact[name].num_positive_contacts.sum()
    i += 1

df_contact['positivity_rate'] = df_contact['n_pos_contacts'] * 100/df_contact['n_contacts_traced']
df_contact.to_csv(resultdir+'contact_tracing.csv')

###### This calculates positivity rates for contact tracing and includes time of contact tracing
df_contact_trace = pd.DataFrame(columns =['num_contacts_traced', 'num_positive_contacts','contact_tracing_time'])
cont_files_1 = glob.glob(indir+'contact_tracinng_counts_0???.csv')
prev_files = glob.glob(indir+'prev_full_hosp_0???.csv')
dfs_contact = {}
dfs_prev = {}

for f in cont_files_1:
    dfs_contact[os.path.splitext(os.path.basename(f))[0]] = pd.read_csv(f, index_col = False)

for f in prev_files:
    dfs_prev[os.path.splitext(os.path.basename(f))[0]] = pd.read_csv(f, index_col = False)


for i in range(0,len(dfs_contact)):
    # df_1 = dfs_contact[sorted(dfs_contact)[i]].drop(dfs_contact[sorted(dfs_contact)[i]].columns[[0,1,4,6,7,8,9]], axis=1)
    df_1 = dfs_contact[sorted(dfs_contact)[i]][['num_contacts_traced','num_positive_contacts','contact_tracing_time','num_sympt_patients_traced','hcw_time_of_infection','hcw_current_ward', 'num_sympt_hcws_traced']]
    df_1['day'] = dfs_contact[sorted(dfs_contact)[i]].loc[:,'contact_tracing_time'].apply(lambda x: math.floor(x))
    df_1['sim'] = dfs_contact[sorted(dfs_contact)[i]].loc[:,'contact_tracing_time'].apply(lambda x: i) # Index for simulation
    df_temp_total = df_total[sorted(df_total)[i]]
    df_temp_pos = df_pos[sorted(df_pos)[i]]
    df_temp = dfs_prev[sorted(dfs_prev)[i]].drop(dfs_prev[sorted(dfs_prev)[i]].columns[[2]], axis=1)
    df_temp['day'] = df_temp.iloc[:,0].apply(lambda x: x)
    df_1['prevalence'] = (df_1['day'].apply(lambda x: df_temp.loc[df_temp['day']==x,:]['total_prev'].values)).str.get(0)
    # df_1['prevalence'] = df_1['day'].apply(lambda x: df_temp.loc[df_temp['day']==x,'total_prev'])
    # df_1['prevalence'] = df_1['prevalence'].str.get(0)
    df_1['n_total'] = df_1['day'].apply(lambda x: df_temp_total.loc[df_temp_total['day']==x,:]['n_total'].values)
    df_1['n_total'] = df_1['n_total'].str.get(0) - df_1['num_contacts_traced'] - 1
    df_1['n_pos'] = df_1['day'].apply(lambda x: df_temp_pos.loc[df_temp_pos['day']==x,:]['n_pos'].values)
    df_1['n_pos'] = df_1['n_pos'].str.get(0) - df_1['num_positive_contacts'] - 1
    df_contact_trace = df_contact_trace.append(df_1, ignore_index = True)
    del df_1

df_contact_trace =df_contact_trace[df_contact_trace['num_contacts_traced'] !=0] ## to check if there is no 0 otherwise we will get division by zero error
df_contact_trace['pos_rate'] = 100*df_contact_trace['num_positive_contacts'].divide(df_contact_trace['num_contacts_traced'])

# df_contact_trace.drop(df_contact_trace.columns[[0,1]], axis = 1, inplace = True) # Only time and positivity_rate left
df_contact_trace.to_csv(resultdir+'contact_tracing_with_time_data_appended.csv')

#### Contact tracing positivity rate per simulation
df_contact_over_time = pd.DataFrame()
i=0
for name in sorted(dfs_contact):
    df_contact_over_time.loc[:,i] = dfs_contact[name].num_positive_contacts * 100/dfs_contact[name].num_contacts_traced
    df_contact_max.loc[i,'max'] = df_contact_over_time.loc[:,i].max()
    df_contact_max.loc[i,'std'] = df_contact_over_time.loc[:,i].std()
    i+=1

df_contact_over_time.to_csv(resultdir+'contact_tracing_per_sim.csv')
df_contact_max.to_csv(resultdir+'contact_tracing_max.csv')

#### ---------------------------------------------------------------------- ####
#### This calculates positivity rates for screening
#### ---------------------------------------------------------------------- ####
df_screen = pd.DataFrame(columns=['total_screened','positive_detected'])
pos_rate_scr = pd.DataFrame()
screen_files = glob.glob(indir+'screening_counts_0???.csv')
dfs_screen = {}

for scr in screen_files:
    dfs_screen[os.path.splitext(os.path.basename(scr))[0]] = pd.read_csv(scr)
    dfs_screen[os.path.splitext(os.path.basename(scr))[0]].rename(columns = {'Day': 'day'}, inplace = True)

i = 0
for name in sorted(dfs_screen):
    ### new code for positivity rate over time
    pos_rate_scr[name] = (dfs_screen[name].positive_detected)*100/(dfs_screen[name].total_screened)
    df1 = pd.DataFrame()
    if len(dfs_screen[name]) > 50: ## this means that screening was performed every 3 days
        df1 = dfs_screen[name][3:32] ## day from 10 - 91 will be selected
        df_screen.loc[i,'total_screened'] = df1.total_screened.sum()
        df_screen.loc[i,'positive_detected'] = df1.positive_detected.sum()
    elif len(dfs_screen[name]) < 30: ## this means this was screening weekly
        df1 = dfs_screen[name][1:14] ## 13 weeks will be selected
        df_screen.loc[i,'total_screened'] = df1.total_screened.sum()
        df_screen.loc[i,'positive_detected'] = df1.positive_detected.sum()
    i += 1

df_screen =df_screen[df_screen['total_screened'] !=0]
df_screen['positivity_rate'] = df_screen.positive_detected * 100/df_screen['total_screened']
# df_screening.loc[len(df_screening), :] = df_screen['positivity_rate'].mean(), df_screen['positivity_rate'].std()
df_screen.to_csv(resultdir+'screening_outbreak_period.csv')

if len(pos_rate_scr) > 0:
    scr_pos_rate_over_time = pd.DataFrame()
    scr_pos_rate_over_time['mean'] = pos_rate_scr.mean(axis = 1)
    scr_pos_rate_over_time['ci_lower'] = pos_rate_scr.apply(lambda x: np.percentile(x, 2.5), axis=1)
    scr_pos_rate_over_time['ci_upper'] = pos_rate_scr.apply(lambda x: np.percentile(x, 97.5), axis=1)
    scr_pos_rate_over_time.to_csv(resultdir+'screening_data_time_dependant.csv')

# Screening with day and prevalence appended
# TBD
df_screening_3 = pd.DataFrame(columns=['day','total_screened','positive_detected','prevalence','positivity_rate'])
for i in range(0,len(dfs_screen)):
    df_s = dfs_screen[sorted(dfs_screen)[i]].drop(dfs_screen[sorted(dfs_screen)[i]].columns[[0]], axis=1)
    # df_s['day'] = (df_s['day']*3)+3
    df_s['day'] = dfs_screen[sorted(dfs_screen)[i]]['day']
    df_temp = dfs_prev[sorted(dfs_prev)[i]].drop(dfs_prev[sorted(dfs_prev)[i]].columns[[2]], axis=1)
    df_temp['day'] = df_temp.iloc[:,0].apply(lambda x: x)
    df_s['prevalence'] = df_s['day'].apply(lambda x: df_temp.loc[df_temp['day']==x,:]['total_prev'].values)
    df_s['prevalence'] = df_s['prevalence'].str.get(0)
    df_screening_3 = df_screening_3.append(df_s, ignore_index = True)
    del df_s

df_screening_3 =df_screening_3[df_screening_3['total_screened'] !=0] ## to check if there is no 0 otherwise we will get division by zero error
df_screening_3['positivity_rate'] = 100*df_screening_3['positive_detected'].divide(df_screening_3['total_screened'])
df_screening_3.to_csv(resultdir+'screening_with_time_data_appended.csv')


for scr in screen_files:
    dfs_screen[os.path.splitext(os.path.basename(scr))[0]] = pd.read_csv(scr)
    dfs_screen[os.path.splitext(os.path.basename(scr))[0]].rename(columns = {'Day': 'day'}, inplace = True)

# For screening every 7 days
df_screening_7 = pd.DataFrame(columns=['day','total_screened','positive_detected','prevalence','positivity_rate'])

for i in range(0,len(dfs_screen)):
    df_s7 = dfs_screen[sorted(dfs_screen)[i]].drop(dfs_screen[sorted(dfs_screen)[i]].columns[[0]], axis=1)
    # df_s7['day'] = (dfs_screen[sorted(dfs_screen)[i]]['day']*7)+7
    df_s7['day'] = dfs_screen[sorted(dfs_screen)[i]]['day']
    df_temp7 = dfs_prev[sorted(dfs_prev)[i]].drop(dfs_prev[sorted(dfs_prev)[i]].columns[[2]], axis=1)
    df_temp7['day'] = df_temp7.iloc[:,0].apply(lambda x: x)
    df_s7['prevalence'] = df_s7['day'].apply(lambda x: df_temp7.loc[df_temp7['day']==x,:]['total_prev'].values)
    df_s7['prevalence'] = df_s7['prevalence'].str.get(0)
    df_screening_7 = df_screening_7.append(df_s7, ignore_index = True)
    del df_s7

df_screening_7 =df_screening_7[df_screening_7['total_screened'] !=0] ## to check if there is no 0 otherwise we will get division by zero error
df_screening_7['positivity_rate'] = 100*df_screening_7['positive_detected'].divide(df_screening_7['total_screened'])
df_screening_7.to_csv(resultdir+'screening_7days_with_time_data_appended.csv')


#### ---------------------------------------------------------------------- ####
#### daily covid19 patients discharged to community
#### ---------------------------------------------------------------------- ####
df_discharge = pd.DataFrame()
disch_files = glob.glob(indir+'covid19_patients_Discharge_count_0???.csv')
dfs_discharge = {}
for dsc in disch_files:
    dfs_discharge[os.path.splitext(os.path.basename(dsc))[0]] = pd.read_csv(dsc)
i = 0
for name in sorted(dfs_discharge):
    df_discharge[name] = dfs_discharge[name]['count']

df_discharge['mean'] = df_discharge.mean(axis = 1)
df_discharge['median'] = df_discharge.median(axis = 1)
df_discharge['ci_lower'] = df_discharge.apply(lambda x: np.percentile(x, 2.5), axis=1)
df_discharge['ci_upper'] = df_discharge.apply(lambda x: np.percentile(x, 97.5), axis=1)

df_discharge.to_csv(resultdir+'COVID-19_patients_discharged_to_community.csv', mode='w', columns=['mean','median','ci_lower','ci_upper'])

#### ---------------------------------------------------------------------- ####
#### daily absent hcws
#### ---------------------------------------------------------------------- ####
df_abs_hcw = pd.DataFrame()
abs_hcw_proportions = pd.DataFrame()
abs_hcw_mean_CI = pd.DataFrame()
abs_hcw_files = glob.glob(indir+'daily_absent_hcw_count_0???.csv')
dfs_abs_hcw = {}
for dsc in abs_hcw_files:
    dfs_abs_hcw[os.path.splitext(os.path.basename(dsc))[0]] = pd.read_csv(dsc)
i = 0
for name in sorted(dfs_abs_hcw):
    df_abs_hcw[name] = dfs_abs_hcw[name]['Daily_absent_hcw']


abs_hcw_proportions = df_abs_hcw*100/870 ## this will calculate proportions over time from every simulation
abs_hcw_mean_CI['mean'] = abs_hcw_proportions.mean(axis = 1)
abs_hcw_mean_CI['ci_lower'] = abs_hcw_proportions.apply(lambda x: np.percentile(x, 2.5), axis=1)
abs_hcw_mean_CI['ci_upper'] = abs_hcw_proportions.apply(lambda x: np.percentile(x, 97.5), axis=1)
abs_hcw_mean_CI.to_csv(resultdir+'daily_absent_hcw.csv')

#### ---------------------------------------------------------------------- ####
#### daily infected hcws
#### ---------------------------------------------------------------------- ####
df_infected_hcw = pd.DataFrame()
inf_hcw_files = glob.glob(indir+'daily_infected_hcw_count_0???.csv')
dfs_inf_hcw = {}
for dsc in inf_hcw_files:
    dfs_inf_hcw[os.path.splitext(os.path.basename(dsc))[0]] = pd.read_csv(dsc)
i = 0
for name in sorted(dfs_inf_hcw):
    df_infected_hcw[name] = dfs_inf_hcw[name]['Daily_infected_hcw']

df_infected_hcw['mean'] = df_infected_hcw.mean(axis = 1)
df_infected_hcw['ci_lower'] = df_infected_hcw.apply(lambda x: np.percentile(x, 2.5), axis=1)
df_infected_hcw['ci_upper'] = df_infected_hcw.apply(lambda x: np.percentile(x, 97.5), axis=1)
df_infected_hcw.to_csv(resultdir+'daily_infected_hcw.csv', mode='w', columns=['mean','ci_lower','ci_upper'])

#### ---------------------------------------------------------------------- ####
#### daily transmission counts
#### ---------------------------------------------------------------------- ####
df_trans_total_count = pd.DataFrame()
peak_transm_count_pat = pd.DataFrame(columns = ['peak transmission'])
peak_transm_count_hcw = pd.DataFrame(columns = ['peak transmission'])
df_trans_pat_count = pd.DataFrame()
df_trans_hcw_count = pd.DataFrame()
trans_files = glob.glob(indir+'daily_transmissions_count_0???.csv')
dfs_trans_count = {}
for dsc in trans_files:
    dfs_trans_count[os.path.splitext(os.path.basename(dsc))[0]] = pd.read_csv(dsc)
i = 0
for name in sorted(dfs_trans_count):
    df_trans_total_count[name] = dfs_trans_count[name]['Total_Transmission_counts']
    df_trans_pat_count[name] = dfs_trans_count[name]['Patient_transmission_counts']
    df_trans_hcw_count[name] = dfs_trans_count[name]['hcw_transmission_count']
    peak_transm_count_pat.loc[i,'peak transmission'] = dfs_trans_count[name]['Patient_transmission_counts'].max()
    peak_transm_count_hcw.loc[i,'peak transmission'] = dfs_trans_count[name]['hcw_transmission_count'].max()
    i += 1

df_trans_total_count['mean'] = df_trans_total_count.mean(axis = 1)
df_trans_total_count['ci_lower'] = df_trans_total_count.apply(lambda x: np.percentile(x, 2.5), axis=1)
df_trans_total_count['ci_upper'] = df_trans_total_count.apply(lambda x: np.percentile(x, 2.5), axis=1)
df_trans_total_count.to_csv(resultdir+'daily_total_transmission_count.csv', mode='w', columns=['mean','ci_lower','ci_upper'])

df_trans_pat_count['mean'] = df_trans_pat_count.mean(axis = 1)
df_trans_pat_count['ci_lower'] = df_trans_pat_count.apply(lambda x: np.percentile(x, 2.5), axis=1)
df_trans_pat_count['ci_upper'] = df_trans_pat_count.apply(lambda x: np.percentile(x, 97.5), axis=1)
df_trans_pat_count.to_csv(resultdir+'daily_patient_transmission_count.csv', mode='w', columns=['mean','ci_lower','ci_upper'])

df_trans_hcw_count['mean'] = df_trans_hcw_count.mean(axis = 1)
df_trans_hcw_count['ci_lower'] = df_trans_hcw_count.apply(lambda x: np.percentile(x, 2.5), axis=1)
df_trans_hcw_count['ci_upper'] = df_trans_hcw_count.apply(lambda x: np.percentile(x, 97.5), axis=1)
df_trans_hcw_count.to_csv(resultdir+'daily_hcw_transmission_count.csv', mode='w', columns=['mean','ci_lower','ci_upper'])

peak_transm_count_pat.to_csv(resultdir+'peak transmission patients.csv')
peak_transm_count_hcw.to_csv(resultdir+'peak transmission hcws.csv')


##### data_total_prev_per_ward
df_ward1 = pd.DataFrame()
df_ward2 = pd.DataFrame()
df_ward3 = pd.DataFrame()
df_ward4 = pd.DataFrame()
df_ward5 = pd.DataFrame()
df_ward6 = pd.DataFrame()
df_ward7 = pd.DataFrame()
df_ward8 = pd.DataFrame()
df_ward9 = pd.DataFrame()
df_ward10 = pd.DataFrame()
df_ward11 = pd.DataFrame()
df_ward12 = pd.DataFrame()
df_ward13 = pd.DataFrame()
df_ward14 = pd.DataFrame()
df_ward15 = pd.DataFrame()
df_ward16 = pd.DataFrame()
df_ward17 = pd.DataFrame()
df_ward18 = pd.DataFrame()
df_ward19 = pd.DataFrame()
df_ward20 = pd.DataFrame()
df_ward21 = pd.DataFrame()
df_ward22 = pd.DataFrame()
df_ward23 = pd.DataFrame()
df_ward24 = pd.DataFrame()
df_ward25 = pd.DataFrame()
df_ward26 = pd.DataFrame()
df_ward27 = pd.DataFrame()
df_ward28 = pd.DataFrame()

#### ---------------------------------------------------------------------- ####
#### nurses_by_state_per_day_hospital_transmissions_only
#### ---------------------------------------------------------------------- ####
df_susc = pd.DataFrame()
df_expo = pd.DataFrame()
df_mild = pd.DataFrame()
df_seve = pd.DataFrame()
df_reco = pd.DataFrame()
df_asym = pd.DataFrame()

df_nurse_by_state_tranms = pd.DataFrame()
files_nur = glob.glob(indir+'nurses_by_state_per_day_hospital_transmissions_only_0???.csv')
dfs_nur = {}
for f in files_nur:
    dfs_nur[os.path.splitext(os.path.basename(f))[0]] = pd.read_csv(f)

for name in sorted(dfs_nur):
    df_susc[name] = dfs_nur[name].SUSCEPTIBLE
    df_expo[name] = dfs_nur[name].EXPOSED
    df_mild[name] = dfs_nur[name].MILD
    df_seve[name] = dfs_nur[name].SEVERE
    df_reco[name] = dfs_nur[name].RECOVERED
    df_asym[name] = dfs_nur[name].ASYMPTOMATIC

df_susc['avg'] = df_susc.mean(axis = 1)
df_expo['avg'] = df_expo.mean(axis = 1)
df_mild['avg'] = df_mild.mean(axis = 1)
df_seve['avg'] = df_seve.mean(axis = 1)
df_reco['avg'] = df_reco.mean(axis = 1)
df_asym['avg'] = df_asym.mean(axis = 1)

df_nurse_by_state_tranms['susceptible'] = df_susc['avg']
df_nurse_by_state_tranms['exposed'] = df_expo['avg']
df_nurse_by_state_tranms['mild'] = df_mild['avg']
df_nurse_by_state_tranms['severe'] = df_seve['avg']
df_nurse_by_state_tranms['recovered'] = df_reco['avg']
df_nurse_by_state_tranms['asymptomatic'] = df_asym['avg']

df_nurse_by_state_tranms.to_csv(resultdir+'nurse_by_state_transmission.csv')


#### ---------------------------------------------------------------------- ####
#### HC Specialists_by_state_per_day_hospital_transmissions_only
#### ---------------------------------------------------------------------- ####
df_susc_hc = pd.DataFrame()
df_expo_hc = pd.DataFrame()
df_mild_hc = pd.DataFrame()
df_seve_hc = pd.DataFrame()
df_reco_hc = pd.DataFrame()
df_asym_hc = pd.DataFrame()

df_hc_by_state_tranms = pd.DataFrame()
files_hc = glob.glob(indir+'physicians_by_state_per_day_hospital_transmissions_only_0???.csv')
#files = glob.glob(indir+'*.xlsx')
dfs_hc = {}
for f in files_hc:
    dfs_hc[os.path.splitext(os.path.basename(f))[0]] = pd.read_csv(f)

for name in sorted(dfs_hc):
    df_susc_hc[name] = dfs_hc[name].SUSCEPTIBLE
    df_expo_hc[name] = dfs_hc[name].EXPOSED
    df_mild_hc[name] = dfs_hc[name].MILD
    df_seve_hc[name] = dfs_hc[name].SEVERE
    df_reco_hc[name] = dfs_hc[name].RECOVERED
    df_asym_hc[name] = dfs_hc[name].ASYMPTOMATIC

df_susc_hc['avg'] = df_susc_hc.mean(axis = 1)
df_expo_hc['avg'] = df_expo_hc.mean(axis = 1)
df_mild_hc['avg'] = df_mild_hc.mean(axis = 1)
df_seve_hc['avg'] = df_seve_hc.mean(axis = 1)
df_reco_hc['avg'] = df_reco_hc.mean(axis = 1)
df_asym_hc['avg'] = df_asym_hc.mean(axis = 1)

df_hc_by_state_tranms['susceptible'] = df_susc_hc['avg']
df_hc_by_state_tranms['exposed'] = df_expo_hc['avg']
df_hc_by_state_tranms['mild'] = df_mild_hc['avg']
df_hc_by_state_tranms['severe'] = df_seve_hc['avg']
df_hc_by_state_tranms['recovered'] = df_reco_hc['avg']
df_hc_by_state_tranms['asymptomatic'] = df_asym_hc['avg']

#df_hc_by_state_tranms['susceptible_std'] = df_susc_hc['std']
#df_hc_by_state_tranms['exposed_std'] = df_expo_hc['std']
#df_hc_by_state_tranms['mild_std'] = df_mild_hc['std']
#df_hc_by_state_tranms['severe_std'] = df_seve_hc['std']
#df_hc_by_state_tranms['recovered_std'] = df_reco_hc['std']
#df_hc_by_state_tranms['asymptomatic_std'] = df_asym_hc['std']

df_hc_by_state_tranms.to_csv(resultdir+'HCspecialists_by_state_transmission.csv')

####patients_by_state_per_day_hospital_transmissions_only
df_susc_pat = pd.DataFrame()
df_expo_pat = pd.DataFrame()
df_mild_pat = pd.DataFrame()
df_seve_pat = pd.DataFrame()
df_reco_pat = pd.DataFrame()
df_asym_pat = pd.DataFrame()

df_pat_by_state_tranms = pd.DataFrame()
files_pat = glob.glob(indir+'patients_by_state_per_day_hospital_transmissions_only_0???.csv')
#files = glob.glob(indir+'*.xlsx')
dfs_pat = {}
for f in files_pat:
    dfs_pat[os.path.splitext(os.path.basename(f))[0]] = pd.read_csv(f)

for name in sorted(dfs_pat):
    df_susc_pat[name] = dfs_pat[name].SUSCEPTIBLE
    df_expo_pat[name] = dfs_pat[name].EXPOSED
    df_mild_pat[name] = dfs_pat[name].MILD
    df_seve_pat[name] = dfs_pat[name].SEVERE
    df_reco_pat[name] = dfs_pat[name].RECOVERED
    df_asym_pat[name] = dfs_pat[name].ASYMPTOMATIC

df_susc_pat['avg'] = df_susc_pat.mean(axis = 1)
df_expo_pat['avg'] = df_expo_pat.mean(axis = 1)
df_mild_pat['avg'] = df_mild_pat.mean(axis = 1)
df_seve_pat['avg'] = df_seve_pat.mean(axis = 1)
df_reco_pat['avg'] = df_reco_pat.mean(axis = 1)
df_asym_pat['avg'] = df_asym_pat.mean(axis = 1)

df_pat_by_state_tranms['susceptible'] = df_susc_pat['avg']
df_pat_by_state_tranms['exposed'] = df_expo_pat['avg']
df_pat_by_state_tranms['mild'] = df_mild_pat['avg']
df_pat_by_state_tranms['severe'] = df_seve_pat['avg']
df_pat_by_state_tranms['recovered'] = df_reco_pat['avg']
df_pat_by_state_tranms['asymptomatic'] = df_asym_pat['avg']


df_pat_by_state_tranms.to_csv(resultdir+'patients_by_state_transmission.csv')

#### ---------------------------------------------------------------------- ####
#### patients_by_state_per_day_hospital_total
#### ---------------------------------------------------------------------- ####
df_susc_pat_tot = pd.DataFrame()
df_expo_pat_tot = pd.DataFrame()
df_mild_pat_tot = pd.DataFrame()
df_seve_pat_tot = pd.DataFrame()
df_reco_pat_tot = pd.DataFrame()
df_asym_pat_tot = pd.DataFrame()
df_sympt_pat_tot = pd.DataFrame()

df_pat_tot_by_state = pd.DataFrame()
files_pat_tot = glob.glob(indir+'patients_by_state_per_day_0???.csv')
#files = glob.glob(indir+'*.xlsx')
dfs_pat_tot = {}
for f in files_pat_tot:
    dfs_pat_tot[os.path.splitext(os.path.basename(f))[0]] = pd.read_csv(f)

for name in sorted(dfs_pat_tot):
    df_susc_pat_tot[name] = dfs_pat_tot[name].SUSCEPTIBLE
    df_expo_pat_tot[name] = dfs_pat_tot[name].EXPOSED
    df_mild_pat_tot[name] = dfs_pat_tot[name].MILD
    df_seve_pat_tot[name] = dfs_pat_tot[name].SEVERE
    df_reco_pat_tot[name] = dfs_pat_tot[name].RECOVERED
    df_asym_pat_tot[name] = dfs_pat_tot[name].ASYMPTOMATIC
    df_sympt_pat_tot[name] = dfs_pat_tot[name].MILD + dfs_pat_tot[name].SEVERE ## sum of mild and severe patients


df_pat_tot_by_state['susceptible_mean'] = df_susc_pat_tot.mean(axis = 1)
df_pat_tot_by_state['exposed_mean'] =df_expo_pat_tot.mean(axis = 1)
df_pat_tot_by_state['mild_mean'] = df_mild_pat_tot.mean(axis = 1)
df_pat_tot_by_state['severe_mean'] = df_seve_pat_tot.mean(axis = 1)
df_pat_tot_by_state['recovered_mean'] = df_reco_pat_tot.mean(axis = 1)
df_pat_tot_by_state['asymptomatic_mean'] = df_asym_pat_tot.mean(axis = 1)
df_pat_tot_by_state['symptomatic_mean'] = df_sympt_pat_tot.mean(axis = 1)

df_pat_tot_by_state['susceptible_ci_lower'] = df_susc_pat_tot.apply(lambda x: np.percentile(x, 2.5), axis=1)
df_pat_tot_by_state['exposed_ci_lower'] =df_expo_pat_tot.apply(lambda x: np.percentile(x, 2.5), axis=1)
df_pat_tot_by_state['mild_ci_lower'] = df_mild_pat_tot.apply(lambda x: np.percentile(x, 2.5), axis=1)
df_pat_tot_by_state['severe_ci_lower'] = df_seve_pat_tot.apply(lambda x: np.percentile(x, 2.5), axis=1)
df_pat_tot_by_state['recovered_ci_lower'] = df_reco_pat_tot.apply(lambda x: np.percentile(x, 2.5), axis=1)
df_pat_tot_by_state['asymptomatic_ci_lower'] = df_asym_pat_tot.apply(lambda x: np.percentile(x, 2.5), axis=1)
df_pat_tot_by_state['symptomatic_ci_lower'] = df_sympt_pat_tot.apply(lambda x: np.percentile(x, 2.5), axis=1)

df_pat_tot_by_state['susceptible_ci_upper'] = df_susc_pat_tot.apply(lambda x: np.percentile(x, 97.5), axis=1)
df_pat_tot_by_state['exposed_ci_upper'] =df_expo_pat_tot.apply(lambda x: np.percentile(x, 97.5), axis=1)
df_pat_tot_by_state['mild_ci_upper'] = df_mild_pat_tot.apply(lambda x: np.percentile(x, 97.5), axis=1)
df_pat_tot_by_state['severe_ci_upper'] = df_seve_pat_tot.apply(lambda x: np.percentile(x, 97.5), axis=1)
df_pat_tot_by_state['recovered_ci_upper'] = df_reco_pat_tot.apply(lambda x: np.percentile(x, 97.5), axis=1)
df_pat_tot_by_state['asymptomatic_ci_upper'] = df_asym_pat_tot.apply(lambda x: np.percentile(x, 97.5), axis=1)
df_pat_tot_by_state['symptomatic_ci_upper'] = df_sympt_pat_tot.apply(lambda x: np.percentile(x, 97.5), axis=1)

df_pat_tot_by_state.to_csv(resultdir+'patients_by_state_per_day.csv')

#### ---------------------------------------------------------------------- ####
#### nurses_by_state_per_day_hospital_total
#### ---------------------------------------------------------------------- ####
df_susc_nur_tot = pd.DataFrame()
df_expo_nur_tot = pd.DataFrame()
df_mild_nur_tot = pd.DataFrame()
df_seve_nur_tot = pd.DataFrame()
df_reco_nur_tot = pd.DataFrame()
df_asym_nur_tot = pd.DataFrame()

df_nur_tot_by_state = pd.DataFrame()
files_nur_tot = glob.glob(indir+'nurses_by_state_per_day_0???.csv')
#files = glob.glob(indir+'*.xlsx')
dfs_nur_tot = {}
for f in files_nur_tot:
    dfs_nur_tot[os.path.splitext(os.path.basename(f))[0]] = pd.read_csv(f)

for name in sorted(dfs_nur_tot):
    df_susc_nur_tot[name] = dfs_nur_tot[name].SUSCEPTIBLE
    df_expo_nur_tot[name] = dfs_nur_tot[name].EXPOSED
    df_mild_nur_tot[name] = dfs_nur_tot[name].MILD
    df_seve_nur_tot[name] = dfs_nur_tot[name].SEVERE
    df_reco_nur_tot[name] = dfs_nur_tot[name].RECOVERED
    df_asym_nur_tot[name] = dfs_nur_tot[name].ASYMPTOMATIC

df_susc_nur_tot['avg'] = df_susc_nur_tot.mean(axis = 1)
df_expo_nur_tot['avg'] = df_expo_nur_tot.mean(axis = 1)
df_mild_nur_tot['avg'] = df_mild_nur_tot.mean(axis = 1)
df_seve_nur_tot['avg'] = df_seve_nur_tot.mean(axis = 1)
df_reco_nur_tot['avg'] = df_reco_nur_tot.mean(axis = 1)
df_asym_nur_tot['avg'] = df_asym_nur_tot.mean(axis = 1)

df_nur_tot_by_state['susceptible'] = df_susc_nur_tot['avg']
df_nur_tot_by_state['exposed'] = df_expo_nur_tot['avg']
df_nur_tot_by_state['mild'] = df_mild_nur_tot['avg']
df_nur_tot_by_state['severe'] = df_seve_nur_tot['avg']
df_nur_tot_by_state['recovered'] = df_reco_nur_tot['avg']
df_nur_tot_by_state['asymptomatic'] = df_asym_nur_tot['avg']

df_nur_tot_by_state.to_csv(resultdir+'nurses_by_state_per_day.csv')



####hc_specialist_by_state_per_day_hospital_total
df_susc_hc_tot = pd.DataFrame()
df_expo_hc_tot = pd.DataFrame()
df_mild_hc_tot = pd.DataFrame()
df_seve_hc_tot = pd.DataFrame()
df_reco_hc_tot = pd.DataFrame()
df_asym_hc_tot = pd.DataFrame()

df_hc_tot_by_state = pd.DataFrame()
files_hc_tot = glob.glob(indir+'physicians_by_state_per_day_0???.csv')
#files = glob.glob(indir+'*.xlsx')
dfs_hc_tot = {}
for f in files_hc_tot:
    dfs_hc_tot[os.path.splitext(os.path.basename(f))[0]] = pd.read_csv(f)

for name in sorted(dfs_hc_tot):
    df_susc_hc_tot[name] = dfs_hc_tot[name].SUSCEPTIBLE
    df_expo_hc_tot[name] = dfs_hc_tot[name].EXPOSED
    df_mild_hc_tot[name] = dfs_hc_tot[name].MILD
    df_seve_hc_tot[name] = dfs_hc_tot[name].SEVERE
    df_reco_hc_tot[name] = dfs_hc_tot[name].RECOVERED
    df_asym_hc_tot[name] = dfs_hc_tot[name].ASYMPTOMATIC

df_susc_hc_tot['avg'] = df_susc_hc_tot.mean(axis = 1)
df_expo_hc_tot['avg'] = df_expo_hc_tot.mean(axis = 1)
df_mild_hc_tot['avg'] = df_mild_hc_tot.mean(axis = 1)
df_seve_hc_tot['avg'] = df_seve_hc_tot.mean(axis = 1)
df_reco_hc_tot['avg'] = df_reco_hc_tot.mean(axis = 1)
df_asym_hc_tot['avg'] = df_asym_hc_tot.mean(axis = 1)

df_hc_tot_by_state['susceptible'] = df_susc_hc_tot['avg']
df_hc_tot_by_state['exposed'] = df_expo_hc_tot['avg']
df_hc_tot_by_state['mild'] = df_mild_hc_tot['avg']
df_hc_tot_by_state['severe'] = df_seve_hc_tot['avg']
df_hc_tot_by_state['recovered'] = df_reco_hc_tot['avg']
df_hc_tot_by_state['asymptomatic'] = df_asym_hc_tot['avg']

df_hc_tot_by_state.to_csv(resultdir+'HCspecialists_by_state_per_day.csv')



#### prev_full_hosp
df_tot_prev = pd.DataFrame()
df_trans_prev = pd.DataFrame()
df_total_prevalence = pd.DataFrame()
df_trans_prevalence = pd.DataFrame()


files_prev = glob.glob(indir+'prev_full_hosp_0???.csv')
#files = glob.glob(indir+'*.xlsx')
dfs_prev = {}
for f in files_prev:
    dfs_prev[os.path.splitext(os.path.basename(f))[0]] = pd.read_csv(f)

for name in sorted(dfs_prev):
    df_tot_prev[name] = dfs_prev[name].total_prev
    df_trans_prev[name] = dfs_prev[name].nosocomial_prev


df_total_prevalence['total_prev'] = df_tot_prev.mean(axis = 1)
df_trans_prevalence['trans_prev'] = df_trans_prev.mean(axis = 1)

# df_prevalence['total_prev_std'] = df_tot_prev.std(axis = 1)
# df_prevalence['trans_prev_std'] = df_trans_prev.std(axis = 1)

df_total_prevalence['ci_lower'] = df_tot_prev.apply(lambda x: np.percentile(x, 2.5), axis=1)
df_total_prevalence['ci_upper'] = df_tot_prev.apply(lambda x: np.percentile(x, 97.5), axis=1)

df_trans_prevalence['ci_lower'] = df_trans_prev.apply(lambda x: np.percentile(x, 2.5), axis=1)
df_trans_prevalence['ci_upper'] = df_trans_prev.apply(lambda x: np.percentile(x, 97.5), axis=1)



df_total_prevalence.to_csv(resultdir+'prevalence_total.csv')
df_trans_prevalence.to_csv(resultdir+'prevalence_nosocomial.csv')



df_reco_nur_tot = pd.DataFrame()
nur_by_state_expos = pd.DataFrame()
nur_by_state_sympt = pd.DataFrame()
nur_by_state_asympt = pd.DataFrame()
files_nur_tot = glob.glob(indir+'nurses_by_state_per_day_0???.csv')
dfs_nur_tot = {}
for f in files_nur_tot:
    dfs_nur_tot[os.path.splitext(os.path.basename(f))[0]] = pd.read_csv(f)

for name in sorted(dfs_nur_tot):
    df_reco_nur_tot[name] = dfs_nur_tot[name].RECOVERED
    nur_by_state_expos[name] = dfs_nur_tot[name].EXPOSED
    nur_by_state_sympt[name] = dfs_nur_tot[name].MILD + dfs_nur_tot[name].SEVERE
    nur_by_state_asympt[name] = dfs_nur_tot[name].ASYMPTOMATIC

reco_nur_final = df_reco_nur_tot.loc[189,:].to_frame().reset_index()
reco_nur_final.drop(reco_nur_final.columns[[0]], axis=1, inplace=True)
reco_nur_final.rename(columns={189: 'Mean_recovered_nurses'}, inplace = True)

df_reco_hc_tot = pd.DataFrame()
hc_by_state_expos = pd.DataFrame()
hc_by_state_sympt = pd.DataFrame()
hc_by_state_asympt = pd.DataFrame()
files_hc_tot = glob.glob(indir+'physicians_by_state_per_day_0???.csv')

dfs_hc_tot = {}
for f in files_hc_tot:
    dfs_hc_tot[os.path.splitext(os.path.basename(f))[0]] = pd.read_csv(f)

for name in sorted(dfs_hc_tot):
    df_reco_hc_tot[name] = dfs_hc_tot[name].RECOVERED
    hc_by_state_expos[name] = dfs_hc_tot[name].EXPOSED
    hc_by_state_sympt[name] = dfs_hc_tot[name].MILD + dfs_hc_tot[name].SEVERE
    hc_by_state_asympt[name] = dfs_hc_tot[name].ASYMPTOMATIC

reco_hc_final = df_reco_hc_tot.loc[189,:].to_frame().reset_index()
reco_hc_final.drop(reco_hc_final.columns[[0]], axis=1, inplace=True)
reco_hc_final.rename(columns={189: 'Mean_recovered_hc'}, inplace = True)

total_recovered = pd.DataFrame()
total_recovered['Recovered_percentage'] = (reco_nur_final['Mean_recovered_nurses'] + reco_hc_final['Mean_recovered_hc'])*100/870
total_recovered.to_csv(resultdir+'precent_recovered_hcws.csv', index = False)
#raise Exception('exit')
expo_hcws = pd.DataFrame()
symp_hcws = pd.DataFrame()
asympt_hcws = pd.DataFrame()


for i in range(hc_by_state_expos.shape[1]):
    expo_hcws[i] = hc_by_state_expos.iloc[:,i] + nur_by_state_expos.iloc[:,i]
    symp_hcws[i] = hc_by_state_sympt.iloc[:,i] + nur_by_state_sympt.iloc[:,i]
    asympt_hcws[i] = hc_by_state_asympt.iloc[:,i] + nur_by_state_asympt.iloc[:,i]

disease_state_hcws = pd.DataFrame() ## nurse and hc specialist added together
disease_state_hcws['exposed mean'] = expo_hcws.mean(axis = 1)
disease_state_hcws['exposed stdv'] = expo_hcws.std(axis = 1)

disease_state_hcws['symptomatic mean'] = symp_hcws.mean(axis = 1)
disease_state_hcws['symptomatic stdv'] = symp_hcws.std(axis = 1)

disease_state_hcws['asymptomatic mean'] = asympt_hcws.mean(axis = 1)
disease_state_hcws['saymptomatic stdv'] = asympt_hcws.std(axis = 1)

disease_state_hcws.to_csv(resultdir+'hcws counts in disease states.csv', index = False)


#### ---------------------------------------------------------------------- ####
#### average secondary transmission counts
#### ---------------------------------------------------------------------- ####
### patients
pat_second_counts_mean = pd.DataFrame(columns=['patient_symptomatic','patient_asymptomatic'])
pat_second_counts_sum = pd.DataFrame(columns=['patient_symptomatic_sum','patient_asymptomatic_sum', 'patient_to_hcw_sum','patient_nrow'])

pat_secon_trans_files = glob.glob(indir+'patient_seco_trans_count_0???.csv')
dfs_pat_secon = {}
for f in pat_secon_trans_files:
    # dfs_pat_secon[os.path.splitext(os.path.basename(f))[0]] = pd.read_csv(f, index_col = False, usecols=['infect_symptomatic','infect_asymptomatic','trans_counts_to_pat','trans_counts_to_hcw'])
    dfs_pat_secon[os.path.splitext(os.path.basename(f))[0]] = pd.read_csv(f, index_col = False, usecols=[1,2,3,4])
i = 0
for name in sorted(dfs_pat_secon):
    pat_second_counts_mean.loc[i,'patient_symptomatic'] = dfs_pat_secon[name].infect_symptomatic.mean(skipna = True)
    pat_second_counts_mean.loc[i,'patient_asymptomatic'] = dfs_pat_secon[name].infect_asymptomatic.mean(skipna = True)
    # second_counts[name]['patient'] = dfs_pat_secon[name].fillna(0)['infect_symptomatic'] + dfs_pat_secon[name].fillna(0)['infect_asymptomatic']
    # pat_second_counts_mean.loc[i, 'patient'] = second_counts[name].patient.mean(skipna = True)
    pat_second_counts_sum.loc[i,'patient_symptomatic_sum'] = dfs_pat_secon[name].infect_symptomatic.sum(skipna = True)
    pat_second_counts_sum.loc[i,'patient_asymptomatic_sum'] = dfs_pat_secon[name].infect_asymptomatic.sum(skipna = True)
    pat_second_counts_sum.loc[i,'patient_to_hcw_sum'] = dfs_pat_secon[name].trans_counts_to_hcw.sum(skipna = True)
    pat_second_counts_sum.loc[i,'patient_nrow'] = len(dfs_pat_secon[name].index)
    i += 1

#pat_second_counts_mean.to_csv(resultdir+'average_patient_second_counts_per_simulation_run.csv')

#### HCWs
hcw_second_counts_mean = pd.DataFrame(columns=['hcw_symptomatic','hcw_asymptomatic'])
hcw_second_counts_sum = pd.DataFrame(columns=['hcw_symptomatic_sum','hcw_asymptomatic_sum', 'hcw_to_pat_sum', 'hcw_to_hcw_sum','hcw_nrow'])

hcw_secon_trans_files = glob.glob(indir+'hcw_seco_trans_count_0???.csv')
dfs_hcw_secon = {}
for f in hcw_secon_trans_files:
    dfs_hcw_secon[os.path.splitext(os.path.basename(f))[0]] = pd.read_csv(f, index_col = False, usecols=[1,2,3,4])
i = 0
for name in sorted(dfs_hcw_secon):
    hcw_second_counts_mean.loc[i,'hcw_symptomatic'] = dfs_hcw_secon[name].infect_symptomatic.mean(skipna = True)
    hcw_second_counts_mean.loc[i,'hcw_asymptomatic'] = dfs_hcw_secon[name].infect_asymptomatic.mean(skipna = True)

    # second_counts[name]['hcw'] = dfs_hcw_secon[name].fillna(0)['infect_symptomatic'] + dfs_hcw_secon[name].fillna(0)['infect_asymptomatic']
    # hcw_second_counts_mean.loc[i, 'hcw'] = second_counts[name].hcw.mean(skipna = True)
    hcw_second_counts_sum.loc[i,'hcw_symptomatic_sum'] = dfs_hcw_secon[name].infect_symptomatic.sum(skipna = True)
    hcw_second_counts_sum.loc[i,'hcw_asymptomatic_sum'] = dfs_hcw_secon[name].infect_asymptomatic.sum(skipna = True)
    hcw_second_counts_sum.loc[i,'hcw_to_pat_sum'] = dfs_hcw_secon[name].trans_counts_to_pat.sum(skipna = True)
    hcw_second_counts_sum.loc[i,'hcw_to_hcw_sum'] = dfs_hcw_secon[name].trans_counts_to_hcw.sum(skipna = True)
    hcw_second_counts_sum.loc[i,'hcw_nrow'] = len(dfs_hcw_secon[name].index)
    i += 1

#hcw_second_counts_mean.to_csv(resultdir+'average_hcw_second_counts_per_simulation_run.csv')
second_counts_sum = pd.DataFrame(columns=['total_counts'])
second_counts_sum['total_counts'] = pat_second_counts_sum['patient_symptomatic_sum'] + pat_second_counts_sum['patient_asymptomatic_sum'] + hcw_second_counts_sum['hcw_symptomatic_sum'] + hcw_second_counts_sum['hcw_asymptomatic_sum']

### combined mean secondary transmission counts
average_second_trans_count = pd.concat([pat_second_counts_mean,hcw_second_counts_mean, pat_second_counts_sum, hcw_second_counts_sum, second_counts_sum], axis = 1)



average_second_trans_count.to_csv(resultdir+'average_second_trans_counts_per_simulation_run.csv')
