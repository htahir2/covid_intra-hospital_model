"""

@author: hannantahir

This file contains all the required parameters that are required for the model to work.

"""
import numpy as np

"""
#### Gerneral simulation_parameters #####
"""
#simulation_time = 1 # in months
time_step = 10 # in minutes
num_steps_per_day = 60*24/time_step
max_iter = int(num_steps_per_day * 239) ## 239 corresponds to maximum number of days

'''
##### Hospital structure and patient related parameters ########
'''
patient_avg_arrival_rate = 40 ## Daily patient arrival rate
corona_start_day = 60 ## start admitting colonized patints from day 60 onwards.
corona_start_sim_time = corona_start_day * num_steps_per_day

'''
The below room_num list corresponds to the number of rooms in each ward.
4 types of wards. ward 1-4:Corona ICU, ward 5-8: Corona ward,
ward 9: Normal ICU, ward 10-28: normal wards
'''  
room_num = [17,17,17,17,23,23,23,22,12,\
            20,20,19,19,19,19,18,18,18,\
            18,18,18,18,18,18,18,18,18,18]
perc_hosp_room_vaccant_initially =50 # percentage of rooms remain vaccan at model initialization.
'''
### Length of stay in different wards
'''
## LOS for covid icu patients (Gamma distribution)
shape_icu = 1.58719488513702
rate_icu = 0.0476524364643747
## LOS for covid nonicu patients (Gamma distribution)
shape_nonicu = 1.88256496519631
rate_nonicu = 0.24844307876682
## los for normal ICU  (Lognormal distribution)
meanlog_norm_icu = 0.3680895454008
sdlog_norm_icu = 0.82071280273592
## los for regular wards  (Weibull distribution)
shape_reg_ward = 0.9182222985585
scale_reg_ward = 4.1794422300417
los_max_days = 190 # this is the maximum x value in days until where you want to draw samples from fitting equation.

'''
##### Physicians and Nurse related and contact rates #######
'''
### contact rates for contact matrix - Estimated from model per shift, n : nurses, hc : physicians, p : patients 
C_nn = 4.6 ## nurse to nurse contacts 
C_np = 19.07 ## nurse to patient
C_nhc = 3 ## nurse to physician
C_pn = 6 ## patient to nurse
C_phc = 2 ## patient to physician
C_hcn = 3 ## physician to nurse
C_hcp = 17.4 ## physician to patient
C_hchc = 0.43 ## physician to physician

### physicians related
shifts_per_day = 3 ## 3 shifts a day for both physicians (also true for nurses)
phy_pat_ratio = [6,6,6,6,6,6,6,6,6,\
                 10,10,10,10,10,10,10,10,10,\
                 10,10,10,10,10,10,10,10,10,10] # ratio of phy-patient in every ward. ward 1-4:Corona ICU, ward 5-8: Corona ward, ward 9: Normal ICU, ward 10-28: rest of the hospital
ratio_by_ward = np.ceil(np.divide(room_num,phy_pat_ratio))
phy_per_ward = [x * shifts_per_day for x in ratio_by_ward]
phy_per_ward[:] = [int(x) for x in phy_per_ward]
rounds_during_shift = 2
phy_service_time = [2,2,2,2,2,2,2,2,2,\
                    1,1,1,1,1,1,1,1,1,\
                    1,1,1,1,1,1,1,1,1,1] ## in model time steps , 1 means 10 minutes servcie time, 3 means 30 minutes assuming time step of 10 minutes


## Nurses related Regular ward 1:4, corona ward 1:2, normal ICU 1:1, corona ICU 1:1 based on average ratios calculated by Baastian for UMCU
nur_pat_ratio = [1,1,1,1,2,2,2,2,1,\
                 4,4,4,4,4,4,4,4,4,\
                 4,4,4,4,4,4,4,4,4,4] # ratio of phy-patient in every ward. ward 1-4:Corona ICU, ward 5-8: Corona cohort ward, ward 9: Normal ICU, ward 10-28: rest of the hospital
nurse_ratio_by_ward = np.ceil(np.divide(room_num,nur_pat_ratio))
nur_per_ward = [x * shifts_per_day for x in nurse_ratio_by_ward]
nur_per_ward[:] = [int(x) for x in nur_per_ward]
nurse_rounds_during_shift = 6 
nur_service_time = [3,3,3,3,2,2,2,2,2,\
                    1,1,1,1,1,1,1,1,1,\
                    1,1,1,1,1,1,1,1,1,1] ## in model time steps , 1 means 10 minutes servcie time, 3 means 30 minutes assuming time step of 10 minutes

### proportion of HCWs daily ward change 
prop_phy_wardchange = 0.025 ### 1% of the physician switch wards for the next duty shift. This happens once per day
prop_nur_wardchange = 0.025 ### 1% of the nurse switch wards for the next duty shift. This happens once per day

'''
## Proportions and disease related parameters
'''
Pa_p = 0.20 ## proportion of asymptomatic patients 
Pa_hcws = 0.31 ## proportion of asymptomatic HCWs
Ps = 0.2 ## proportion of symptomatic individuals that develop severe infections
Ra = 1.95 ##0.5 ## reproduction number asymptomatic
Rs = 1.95 # 1.0 ## repoduction number symptomatic

## recovery of individuals
recov_severe = 35*num_steps_per_day ## in simulation steps - severe recover after 35 days
recov_mild = 14*num_steps_per_day ## in simulation steps - mild recover after 14 days
recov_asymp = 14*num_steps_per_day ## in simulation steps - asymp recover after 14 days
quarantine_period = 7*num_steps_per_day ## in simulation steps - 7 days quarantine period

## Infectiousness Curve (Weibull distribution)
shape = 2.83
scale = 6.84

## incubation period (Gamma distribution)
inc_shape = 5.807 
inc_scale = 0.948
inc_period = np.arange(0,14,1/num_steps_per_day)

'''
####### INTERVENTIONS ######
'''
### Personal protective equipment (PPE) effectiveness
gear_effectiveness = 1-0.9 ## 1-0.10 mean 10% effective, 1-0.9 means 90% effective
ppe_covid_wards = 1
ppe_noncovid_wards = 0
### contact tracing related
cont_period = 2 ## in days, 2 days means contacts within the last two days are traced only, change to 7 for contact tracing 7 days scenario
cont_period_simtime = cont_period * num_steps_per_day
#time_to_trace_contacts_again = 2*num_steps_per_day ## contacts will be traced 2 times. one immediately after hcw is symptomatic, and second after 2 days. define here when to trace contacts again
testing_day = 5 ## testing moment for contacts. This does not apply to contact tracing with perfect sensitivity
testing_day_simtime = testing_day * num_steps_per_day 
## screening related
scr_perc = 1.0 ## proportion of HCWs screened. 1.0 means 100% screened, 0 mean no one
screening_moment = 3 ## in days  - every 3rd day or change to 7 for weekly screening
