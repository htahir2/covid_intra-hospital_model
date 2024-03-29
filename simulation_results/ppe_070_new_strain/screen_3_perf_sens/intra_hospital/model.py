'''
"""

    @author: hannantahir

"""

================================

'''
from intra_hospital import params
#from intra_hospital.community_seir_model import *
import random
import copy
import numpy as np
import pandas as pd
from scipy.stats import weibull_min, lognorm, gamma
import scipy.linalg as la
from mesa import Model
from intra_hospital.agents import *
from intra_hospital.schedule import RandomActivationByType


class IntraHospModel(Model):
    verbose = False  # Print-monitoring
    ''' Specify path to model directory where run.py exist '''
    results_dir = '/scratch/HT1301/ppe_070_new_strain/screen_3_perf_sens/'
#    results_dir = '/Users/hannantahir/Documents/mesa/COVID19/covid19_lisa/final_simulations/Final_simulations_20210204/ppe_070_new_strain/screen_3_perf_sens/'
    
    ### output dataframes for patients and HCWs
    data_patient_state_count = pd.DataFrame(columns=['SUSCEPTIBLE','EXPOSED','MILD','MODERATE','SEVERE','RECOVERED','ASYMPTOMATIC'])
    data_transmissions_state_count = pd.DataFrame(columns=['SUSCEPTIBLE','EXPOSED','MILD','MODERATE','SEVERE','RECOVERED','ASYMPTOMATIC'])
    number_covid19_patients_to_community = 0
    data_covid19_patients_to_community = pd.DataFrame(columns=['count'])
    daily_corona_arrivals = pd.DataFrame(columns=['Daily_Covid_Arrivals'])
    patient_seco_trans_counts = pd.DataFrame(columns=['infect_symptomatic', 'infect_asymptomatic', 'trans_counts_to_pat', 'trans_counts_to_hcw'])
    data_physician_state_count = pd.DataFrame(columns=['SUSCEPTIBLE','EXPOSED','MILD','MODERATE','SEVERE','RECOVERED','ASYMPTOMATIC'])
    data_physician_transmissions_state_count = pd.DataFrame(columns=['SUSCEPTIBLE','EXPOSED','MILD','MODERATE','SEVERE','RECOVERED','ASYMPTOMATIC'])
    data_nurse_state_count = pd.DataFrame(columns=['SUSCEPTIBLE','EXPOSED','MILD','MODERATE','SEVERE','RECOVERED','ASYMPTOMATIC'])
    data_nurse_transmissions_state_count = pd.DataFrame(columns=['SUSCEPTIBLE','EXPOSED','MILD','MODERATE','SEVERE','RECOVERED','ASYMPTOMATIC'])    
    daily_transmission_count = pd.DataFrame(columns=['Total_Transmission_counts','Patient_transmission_counts','hcw_transmission_count'])
    daily_infected_hcw = pd.DataFrame(columns=['Daily_infected_hcw'])
    daily_absent_hcw = pd.DataFrame(columns=['Daily_absent_hcw'])    
    hcw_seco_trans_counts = pd.DataFrame(columns=['infect_symptomatic', 'infect_asymptomatic', 'trans_counts_to_pat', 'trans_counts_to_hcw'])
    ward_num_array = [item for item in range(1, len(params.room_num)+1)]
    cols = ['w' + str(x) for x in ward_num_array]
    daily_pat_discharge = [0]*len(params.room_num)
    data_pat_discharge_per_ward = pd.DataFrame(columns = cols)    
    data_pat_per_ward = pd.DataFrame(columns = cols)
    data_prev_full_hosp = pd.DataFrame(columns = ['total_prev', 'nosocomial_prev'])
    data_total_prev_per_ward = pd.DataFrame(columns = cols)
    screening_counts = pd.DataFrame(columns=['Day','total_screened', 'positive_detected']) # total_contacts,total_contacts_traced,positive_contacts, sympt_patient_contacts, trace_time, 1, hcw.unique_id, hcw.time_of_infection
    contact_tracing_counts = pd.DataFrame(columns=['Num_contacts', 'num_contacts_traced','num_positive_contacts', 'num_sympt_patients_traced','contact_tracing_time','tracing_round', 'hcw_id', 'hcw_time_of_infection','hcw_current_ward', 'num_sympt_hcws_traced', 'hcws_put_on_ppe','patients_put_in_isolation']) ## tracing round 1 means immediately when hcw become symptomatic, 2  means round after 2 days
    Time_btw_trans_and_sym_onset = pd.DataFrame(columns=['transmission_time', 'incubation_time', 'infection_time', 'disease_state'])
    available_rooms = list()
    available_rooms_corona_icu = list()
    available_rooms_corona_nonicu = list()
    rooms_to_be_visited = list()
    rooms_to_be_visited_by_nurses = list()
    rooms_occupied = list()
    ### to track contributions of different transmission routes
    daily_transmissions = 0
    daily_transmissions_pat = 0
    daily_transmissions_hcw = 0
    total_transmissions = 0
    total_transmissions_non_covid_wards = 0
    total_transmissions_covid_wards = 0
    p_n_transmission = 0 ## patient to nurse
    p_hc_transmission = 0 ## patient to physicians
    n_p_transmission = 0 # nurse to patient
    n_hc_transmission = 0 # nurse to physician
    n_n_transmission = 0 ## nurse to nurse
    hc_p_transmission = 0 # physician to patient
    hc_n_transmission = 0 # physician to nurse
    hc_hc_transmission = 0 # physician to physician
    num_suscep_pat = 0 ## counts number of susceptible patients admitted to the hospital
    num_replace_hcw = 0 ##  counts number of replacement hcws
    data_transmission_routes = pd.DataFrame(columns=['Total_transmission','P-N','P-HC','N-P','N-HC','N-N','HC-P','HC-N','HC-HC','HCW_community_trans_count','Total_trans_non_covid_wards','Total_trans_covid_wards', 'Asympt_patient_admission_count', 'Exposed_patient_admission_count', 'Total_patients_admitted', 'Num_susceptible_patients','num_replacement_hcw','trans_counts_from_pre_symptomatic','trans_counts_from_symptomatic', 'trans_counts_from_assymptomatic'])
    trans_counts_from_pre_symptomatic = 0
    trans_counts_from_symptomatic = 0
    trans_counts_from_asymptomatic = 0
    ## community transmission count HCWs
    total_hcw_community_transmissions = 0
    shift_tracker = 1
#    df = pd.DataFrame(columns=range(60))
    exposed_adm_count = 0
    asym_adm_count = 0

    
    def __init__(self):
        '''
        Model initialization. Patients are admitted to hospital rooms
        HCWs (nurses and physicians) are initialized and assigned to wards
        '''
        # set parameters
        self.schedule = RandomActivationByType(self)
#        self.iteration = 0
#        self.max_iter = int(params.max_iter)
        self.newuniqueID = 5000 ### patients unique id starts at 5000 (Range 5000 - depending on how many patients get admited)
        self.room_num = params.room_num
#        self.patient_max = sum(self.room_num)
        self.patient_max_without_corona = sum(self.room_num[8:len(self.room_num)+1])
        self.patient_max_corona_icu = sum(self.room_num[0:4])
        self.patient_max_corona_nonicu = sum(self.room_num[4:8])
        self.corona_start_sim_time = params.corona_start_sim_time
        self.num_steps_per_day = params.num_steps_per_day
        self.patient_avg_arrival_rate = params.patient_avg_arrival_rate
        self.quarantine_period = params.quarantine_period
        self.num_pat_1_20 = 0 ## age group 1-20 years
        self.num_pat_20_45 = 0 ## age group 20-45 years
        self.num_pat_45_65 = 0 ## age group 45-65 years
        self.num_pat_65_80 = 0 ## age group 65-80 years
        self.num_pat_80_plus = 0 ## age group 80+ years
        self.lar_eig_val = 15.50 ## this is an initial estimation. This will be updated before corona start time based on actual number of patients present in the hospital.
        self.number_new_corona_icu_patients = 0
        self.number_new_corona_nonicu_patients = 0
        self.covid_patients_los = pd.read_excel(self.results_dir+'intra_hospital/covid_patient_admissions_los_UMCU_subset95_new.xlsx', sheet_name = 'los')
        self.icu_los_list = self.covid_patients_los['Los_days_icu'].dropna().tolist()
        self.nonicu_los_list = self.covid_patients_los['Los_days_non-icu'].dropna().tolist()
        self.df_covid_hospitalizations = pd.read_excel(self.results_dir+'intra_hospital/covid_patient_admissions_los_UMCU_subset95_new.xlsx', sheet_name = 'covid_admissions')
        self.df_community_prev = pd.read_csv(self.results_dir+'intra_hospital/covid_cases_for_model_FINAL_prev_catchment_100.csv', index_col=0)
        self.test_sensitivity = pd.read_excel(self.results_dir+'intra_hospital/abm_sensitivity_ferguson_new.xlsx')
        ## proportion related
        self.Pa_p = params.Pa_p
        self.Pa_hcws = params.Pa_hcws
        self.Ps = params.Ps
        self.Ra = params.Ra
        self.Rs = params.Rs
        ### transmision, incubation and infectiouness related
        self.shape = params.shape
        self.scale = params.shape
        self.inc_period = params.inc_period
        self.gamma_pdf = gamma.pdf(self.inc_period, params.inc_shape, 0, scale=params.inc_scale)
        self.gamma_pdf /= self.gamma_pdf.sum() # normalize the weight to 100% otherwise random.choice will give error
        self.gear_effectiveness = params.gear_effectiveness

        #### physician related
        self.phy_pat_ratio = params.phy_pat_ratio
        self.phy_per_ward = params.phy_per_ward
        self.shifts_per_day = params.shifts_per_day
        self.phyuniqueID = 1  ## physicians id starts at 1 (range from 1 - 999) 
        self.rounds_during_shift = params.rounds_during_shift
        self.phy_service_time = params.phy_service_time

        #### nurse related
        self.nur_pat_ratio = params.nur_pat_ratio
        self.nur_per_ward = params.nur_per_ward
        self.nuruniqueID = 1000 ### nurse unique ID starts at 1000 (range from 1000 - 4999)
        self.nurse_rounds_during_shift = params.nurse_rounds_during_shift
        self.nur_service_time = params.nur_service_time
        
        ### create rooms in the hospitals with ward number. e.g 1.10 refers to ward 1, room # 10
        for ward, val in enumerate(self.room_num, start=1):
            for room in range(1,val+1):
                num_room = str(str(ward)+"."+str(room))
                if ward < 5: ## first 4 wards are covid ICUs
                    self.available_rooms_corona_icu.append(num_room)
                elif ward >= 5 and ward < 9: # ward 4-8 are covid normal wards
                    self.available_rooms_corona_nonicu.append(num_room)
                elif ward >= 9: #wards 9 is normal ICU, ward 10-28 are regular wards 
                    self.available_rooms.append(num_room)
        random.shuffle(self.available_rooms)  # shuffle room list randomly
        random.shuffle(self.available_rooms_corona_icu)  # shuffle room list randomly
        random.shuffle(self.available_rooms_corona_nonicu)  # shuffle room list randomly

        #### LOS for corona ICU - severe cases
        self.elements = np.arange(1,params.los_max_days,0.1)
        self.weights_coronaicu = gamma.pdf(self.elements, params.shape_icu, 0, scale=1/params.rate_icu)
        self.weights_coronaicu /= self.weights_coronaicu.sum() # normalize the weight to 100% otherwise random.choice will give error
        #### LOS for corona wards - mild cases
        self.weights_corona = gamma.pdf(self.elements, params.shape_nonicu, 0, scale=1/params.rate_nonicu)
        self.weights_corona /= self.weights_corona.sum()
        #### LOS for normal ICU
        self.weights_normalicu = lognorm.pdf(self.elements, params.sdlog_norm_icu, 0, np.exp(params.meanlog_norm_icu))
        self.weights_normalicu /= self.weights_normalicu.sum()
        #### LOS for regular wards
        self.weights_regularward = weibull_min.pdf(self.elements, params.shape_reg_ward, loc=0, scale=params.scale_reg_ward)
        self.weights_regularward /= self.weights_regularward.sum()
        
        ''' Add patients to hospital rooms '''
        rooms_free = int(len(self.available_rooms) * params.perc_hosp_room_vaccant_initially / 100)
        copy_available_rooms = self.available_rooms[:]
        for idx, val in enumerate(copy_available_rooms):
            if len(self.available_rooms) > rooms_free:
                ward_room_num = val.split('.') # split the string to get room and ward number
                ward_room_num = [int(x) for x in ward_room_num] ## make ward_room_num list into integers
                los_realtime, los_sim_time, initial_state, time_of_infection, incubationtime, symptom_state, transmission_type, movementflag,symp_trans_count, asymp_trans_count, trans_count_to_pat, trans_count_to_hcw, patient_isolated = 0.00, 0, 0, 0, None, 0, 0, False, 0, 0, 0, 0, 0 # initially keep all patients susceptible
    
                #### add patients only to ward number 9 and above. No corona patient at model initialization
                if ward_room_num[0] == 9: ## This is normal ICU
                    los_realtime = abs(np.random.choice(self.elements, p=self.weights_normalicu))
                    los_sim_time = int(los_realtime * self.num_steps_per_day)
                    patient = Patient(self.newuniqueID, self, initial_state, ward_room_num[0], ward_room_num[1], los_sim_time, los_sim_time, transmission_type, time_of_infection, incubationtime, symptom_state, movementflag, symp_trans_count, asymp_trans_count, trans_count_to_pat, trans_count_to_hcw, patient_isolated)
                    self.schedule.add(patient)
                    self.available_rooms.remove(val) #
                    self.newuniqueID += 1
    
                ###### admissions to ward 10-28
                elif ward_room_num[0] >= 10: ## These are regular wards
                    los_realtime = abs(np.random.choice(self.elements, p=self.weights_regularward))
                    los_sim_time = int(los_realtime * self.num_steps_per_day)
                    patient = Patient(self.newuniqueID, self, initial_state, ward_room_num[0], ward_room_num[1], los_sim_time, los_sim_time, transmission_type, time_of_infection, incubationtime, symptom_state, movementflag, symp_trans_count, asymp_trans_count, trans_count_to_pat, trans_count_to_hcw, patient_isolated)
                    self.schedule.add(patient)
                    self.available_rooms.remove(val) #
                    self.newuniqueID += 1
                self.num_suscep_pat += 1     

        del copy_available_rooms[:]

        ### make a list of rooms occupied
        for pat in self.schedule.agents_by_type[Patient]:
            self.rooms_occupied.append([pat.ward,pat.room])

        self.rooms_to_be_visited = copy.copy(self.rooms_occupied) # make a copy of all occupied rooms for physicians
        self.rooms_to_be_visited_by_nurses = copy.copy(self.rooms_occupied) # make a copy of all occupied rooms for nurses
        
        ''' Add HCWs to hospital wards '''
        # Create Physicians
        shift = 1
        protective_gear = 0 # initiate without protective_gear
#        con_tracing = [] ### empty array to keep track of HCWs contacts (id, time, type of agent (HCspecialist = 1, Nurse = 2)) 
        con_tracing = None
        con_tracing_output = None
        for ward, num in enumerate(self.phy_per_ward, start=1):
#            if ward == 1 or ward == 2:
            if ward <= 8: # give physcians protective gear on corona wards/ICU
                protective_gear = params.ppe_covid_wards
            else:
                protective_gear = params.ppe_noncovid_wards
            # schedule all physicians in hospital
            for i in range(1,num+1):
                if shift > self.shifts_per_day:
                    shift = 1
                initial_state = 0
                pat_attend_counter, incubationtime, symptom_state, time_outofwork, time_of_infection, transmission_type, replacement_added, symp_trans_count, asymp_trans_count, trans_count_to_pat, trans_count_to_hcw = 0, None, 0, 0, 0, 0, False, 0, 0, 0, 0
                physician = Physician(self.phyuniqueID, self, initial_state, ward, pat_attend_counter, shift, time_of_infection, protective_gear, incubationtime, symptom_state, time_outofwork, transmission_type, con_tracing, replacement_added, 0, False, symp_trans_count, asymp_trans_count, trans_count_to_pat, trans_count_to_hcw, con_tracing_output, 0)
                self.schedule.add(physician)
                self.phyuniqueID +=1
                shift += 1

        # Create Nurses
        nshift = 1
        protective_gear = 0 # initiate without protective_gear
        for ward, num in enumerate(self.nur_per_ward, start=1):
#            if ward == 1 or ward == 2:
            if ward <= 8: # give nurses protective gear on corona wards/ICU
                protective_gear = params.ppe_covid_wards
            else:
                protective_gear = params.ppe_noncovid_wards
            # schedule all nurses in hospital
            for i in range(1,num+1):
                if nshift > self.shifts_per_day:
                    nshift = 1
                initial_state = 0
                pat_attend_counter, incubationtime, symptom_state, time_outofwork, time_of_infection, transmission_type, replacement_added, symp_trans_count, asymp_trans_count, trans_count_to_pat, trans_count_to_hcw = 0, None, 0, 0, 0, 0, False, 0, 0, 0, 0
                nurse = Nurse(self.nuruniqueID, self, initial_state, ward, pat_attend_counter, nshift, time_of_infection, protective_gear, incubationtime, symptom_state, time_outofwork, transmission_type, con_tracing, replacement_added, 0, False, symp_trans_count, asymp_trans_count, trans_count_to_pat, trans_count_to_hcw, con_tracing_output, 0)
                self.schedule.add(nurse)
                self.nuruniqueID +=1
                nshift += 1




    def new_patient_arrivals(self): 
        '''
        Daily patient arrival into the hospital based on average daily arrival rate and admitted to non-covid wards
        COVID hospitalaized patients also added in the code in to the hospital and admitted to COVID wards. 
        patients in exposed and asymptomatic state also arrive and admitted to non-covid wards
        '''
        if self.schedule.time%self.num_steps_per_day == 0:
            ### covid patients based on actual number of hospitalizations
            if self.schedule.time >= self.corona_start_sim_time:
                self.number_new_corona_icu_patients = self.number_new_corona_icu_patients + self.df_covid_hospitalizations['icu_admissions'].loc[int(self.schedule.time/self.num_steps_per_day)]
                self.number_new_corona_nonicu_patients = self.number_new_corona_nonicu_patients + self.df_covid_hospitalizations['non-icu_admissions'].loc[int(self.schedule.time/self.num_steps_per_day)]
            ### age group related incidence estimation in the community
            Num_new_daily_patients = 0
            Num_new_daily_patients = np.random.poisson(self.patient_avg_arrival_rate)
            self.num_pat_1_20 = self.num_pat_1_20 + round(Num_new_daily_patients * self.df_community_prev['prop_hosp_1-20'].loc[int(self.schedule.time/self.num_steps_per_day)])
            self.num_pat_20_45 = self.num_pat_20_45 + round(Num_new_daily_patients * self.df_community_prev['prop_hosp_20-45'].loc[int(self.schedule.time/self.num_steps_per_day)])
            self.num_pat_45_65 = self.num_pat_45_65 + round(Num_new_daily_patients * self.df_community_prev['prop_hosp_45-65'].loc[int(self.schedule.time/self.num_steps_per_day)])
            self.num_pat_65_80 = self.num_pat_65_80 + round(Num_new_daily_patients * self.df_community_prev['prop_hosp_65-80'].loc[int(self.schedule.time/self.num_steps_per_day)])
            self.num_pat_80_plus = self.num_pat_80_plus + round(Num_new_daily_patients * self.df_community_prev['prop_hosp_80+'].loc[int(self.schedule.time/self.num_steps_per_day)])
 
        if self.available_rooms:            
            while self.available_rooms and (self.num_pat_1_20 > 0 or self.num_pat_20_45 > 0 or self.num_pat_45_65 > 0 or self.num_pat_65_80 > 0 or self.num_pat_80_plus > 0) and (self.count_noncorona_patients() < self.patient_max_without_corona):
                los_realtime, los_sim_time, initial_state, time_of_infection, incubationtime, symptom_state, transmission_type, movementflag, symp_trans_count, asymp_trans_count, trans_count_to_pat, trans_count_to_hcw, patient_isolated  = 0.00, 0, 0, 0, None, 0, 0, False, 0, 0, 0, 0, 0
                copy_available_rooms = self.available_rooms[:]               
                ### create an empty list and if age groups admission counters are > 0, append numbers based on age groups (1-20 = 1, 20-45=2 45-65=3, 65-80=4, 80+=5)
                group_list = []
                if self.num_pat_1_20 > 0:
                    group_list.append(1) 
                if self.num_pat_20_45 > 0:
                    group_list.append(2)
                if self.num_pat_45_65 > 0:
                    group_list.append(3)
                if self.num_pat_65_80 > 0:
                    group_list.append(4)
                if self.num_pat_80_plus > 0:
                    group_list.append(5)
                ### now pick up a random age group from where patient will be admitted to the hospital
                selected_age_group = 0
                if group_list:
                    selected_age_group = random.choice(group_list)
                    group_list.clear()
                else:
                    pass

                for idx, val in enumerate(copy_available_rooms):
                    if selected_age_group == 1: ## age group 1-20
                        community_incid = self.df_community_prev['prop_prev_pat_1-20'].loc[int(self.schedule.time/self.num_steps_per_day)]
                    elif selected_age_group == 2: ## age group 20-45
                        community_incid = self.df_community_prev['prop_prev_pat_20-45'].loc[int(self.schedule.time/self.num_steps_per_day)]
                    elif selected_age_group == 3: ## age group 45-65
                        community_incid = self.df_community_prev['prop_prev_pat_45-65'].loc[int(self.schedule.time/self.num_steps_per_day)]
                    elif selected_age_group == 4: ## age group 65-80
                        community_incid = self.df_community_prev['prop_prev_pat_65-80'].loc[int(self.schedule.time/self.num_steps_per_day)]
                    elif selected_age_group == 5: ## age group 80+
                        community_incid = self.df_community_prev['prop_prev_pat_80+'].loc[int(self.schedule.time/self.num_steps_per_day)]
                    else:
                        community_incid = 0.0000000000000
                        
#                    community_incid = 0 ### just for testing
                    if random.random() < community_incid: ### if true, patient is admited as exposed or asymptomatic. If this is not true, ptient is admited as suseptible
                        if random.random() < self.Pa_p:
                            initial_state = 6 ## patient is admitted as asymptomatic
                            incubationtime = 0 ## No incubation period for asymptomatic individuals
                            symptom_state = 1 ## 1 means asymptomatic.
                            time_of_infection_realtime = random.uniform(0, 14) ### just draw a unifrom sample between 0 and 14 days
                            time_of_infection = self.schedule.time - int(time_of_infection_realtime * self.num_steps_per_day)
                            self.asym_adm_count += 1
                        else:    
                            initial_state = 1 ## patient is admitted as exposed                           
                            incubation_realtime = abs(np.random.choice(self.inc_period, p=self.gamma_pdf))
                            exposure_realtime = random.uniform(0, incubation_realtime) ### draw a unifrom sample between 0 and incubation_realtime to find random time of exposure in the community
                            time_of_infection = self.schedule.time - int(exposure_realtime * self.num_steps_per_day)
                            incubationtime = int((incubation_realtime - exposure_realtime) * self.num_steps_per_day) ## subtract the incubation time which has already been passed in the community
                            symptom_state = 2 ## 2 means patient will follow symptomatic route 
                            self.exposed_adm_count += 1                        
                        transmission_type = 1 ## 1 means community acquired

                    ward_room_num = val.split('.') # split the string to get room and ward number
                    ward_room_num = [int(x) for x in ward_room_num] ## make ward_room_num list into integers
                    #### add patients only to ward number 9 and above. No identified corona patient in these wards
                    if ward_room_num[0] == 9: ## This is normal ICU
                        los_realtime = abs(np.random.choice(self.elements, p=self.weights_normalicu))
                        los_sim_time = int(los_realtime * self.num_steps_per_day)
                    elif ward_room_num[0] >= 10: ## These are regular wards
                        los_realtime = abs(np.random.choice(self.elements, p=self.weights_regularward))
                        los_sim_time = int(los_realtime * self.num_steps_per_day)
                    
                    ''' add patient here '''                            
                    patient = Patient(self.newuniqueID, self, initial_state, ward_room_num[0], ward_room_num[1], los_sim_time, los_sim_time, transmission_type, time_of_infection, incubationtime, symptom_state, movementflag, symp_trans_count, asymp_trans_count, trans_count_to_pat, trans_count_to_hcw, patient_isolated)
                    self.schedule.add(patient)
                    if initial_state == 0:
                        self.num_suscep_pat += 1 
                    self.available_rooms.remove(val) ## remove the room from available rooms list
                    self.newuniqueID += 1
#                    self.number_of_new_agents -= 1
                    self.rooms_occupied.append([ward_room_num[0], ward_room_num[1]])
                    ''' now decrement the value of the selected age group by 1 '''
                    if selected_age_group == 1:
                        self.num_pat_1_20 -= 1
                    elif selected_age_group == 2:
                        self.num_pat_20_45 -= 1
                    elif selected_age_group == 3:
                        self.num_pat_45_65 -= 1
                    elif selected_age_group == 4:
                        self.num_pat_65_80 -= 1
                    elif selected_age_group == 5:
                        self.num_pat_80_plus -= 1
                    break
                del copy_available_rooms[:]

        ''' to add corona patients from corona start time '''
        if self.schedule.time >= self.corona_start_sim_time:
            ## first add severe covid patients to covid ICUs
            if self.available_rooms_corona_icu:
                while self.available_rooms_corona_icu and self.number_new_corona_icu_patients > 0 and (self.count_corona_icu_patients() < self.patient_max_corona_icu):
                    los_realtime, los_sim_time, initial_state, time_of_infection, incubationtime, symptom_state, transmission_type, movementflag, symp_trans_count, asymp_trans_count, trans_count_to_pat, trans_count_to_hcw, patient_isolated = 0.00, 0, 0, 0, None, 0, 0, False, 0, 0, 0, 0, 0
                    copy_available_rooms_corona_icu = self.available_rooms_corona_icu[:]
                    for idx, val in enumerate(copy_available_rooms_corona_icu):
                        ward_room_num = val.split('.') # split the string to get room and ward number
                        ward_room_num = [int(x) for x in ward_room_num] ## make ward_room_num list into integers
                        los_realtime = self.icu_los_list[0]
                        los_sim_time = int(los_realtime * self.num_steps_per_day)
#                        print('In covid icu admissions',los_sim_time,  los_realtime, self.number_new_corona_icu_patients, len(self.available_rooms_corona_icu))
                        initial_state = 4 ## ICU covid patients have severe disease state
                        transmission_type = 1 ## 1 means community acquired
                        incubationtime = 0 #None ## we put it to None since incubation period has already passed
                        symptom_state = 2 ## 2 means patient follow symptomatic route
                        incubation_realtime = abs(np.random.choice(self.inc_period, p=self.gamma_pdf))
                        incubation_simtime = int(incubation_realtime * self.num_steps_per_day)
                        time_of_infection = self.schedule.time - incubation_simtime ## subtract the incubation period from current time to get time of infection
                        patient = Patient(self.newuniqueID, self, initial_state, ward_room_num[0], ward_room_num[1], los_sim_time, los_sim_time, transmission_type, time_of_infection, incubationtime, symptom_state, movementflag, symp_trans_count, asymp_trans_count, trans_count_to_pat, trans_count_to_hcw, patient_isolated)
                        self.schedule.add(patient)
                        self.available_rooms_corona_icu.remove(val)
                        self.icu_los_list.pop(0)
                        self.newuniqueID += 1
                        self.number_new_corona_icu_patients -= 1
                        self.rooms_occupied.append([ward_room_num[0], ward_room_num[1]])
#                        print('In covid icu admission',self.schedule.time, self.schedule.time/self.num_steps_per_day, los_sim_time, los_realtime, (self.newuniqueID-1), self.number_new_corona_icu_patients)
                        break
                    del copy_available_rooms_corona_icu[:]
            
            ## second add mild symptomatic patients to covid wards
            if self.available_rooms_corona_nonicu:
                while self.available_rooms_corona_nonicu and self.number_new_corona_nonicu_patients > 0 and (self.count_corona_nonicu_patients() < self.patient_max_corona_nonicu):
                    los_realtime, los_sim_time, initial_state, time_of_infection, incubationtime, symptom_state, transmission_type, movementflag, symp_trans_count, asymp_trans_count, trans_count_to_pat, trans_count_to_hcw, patient_isolated = 0.00, 0, 0, 0, None, 0, 0, False, 0, 0, 0, 0, 0
                    copy_available_rooms_corona_nonicu = self.available_rooms_corona_nonicu[:]
                    for idx, val in enumerate(copy_available_rooms_corona_nonicu):
                        ward_room_num = val.split('.') # split the string to get room and ward number
                        ward_room_num = [int(x) for x in ward_room_num] ## make ward_room_num list into integers
                        los_realtime = self.nonicu_los_list[0] ## pick up the first element from the list
                        los_sim_time = int(los_realtime * self.num_steps_per_day)
#                        print('In covid non-icu admissions',los_sim_time,  los_realtime, self.number_new_corona_nonicu_patients, len(self.available_rooms_corona_nonicu))
                        initial_state = 2 ## covid ward patients have mild disease state
                        transmission_type = 1 ## 1 means community acquired
                        incubationtime = 0 #None ## we put it to None since incubation period has already passed
                        symptom_state = 2 ## 2 means patient follows symptomatic route.
                        incubation_realtime = abs(np.random.choice(self.inc_period, p=self.gamma_pdf))
                        incubation_simtime = int(incubation_realtime * self.num_steps_per_day)
                        time_of_infection = self.schedule.time - incubation_simtime ## subtract the incubation period from current time to get time of infection
                        patient = Patient(self.newuniqueID, self, initial_state, ward_room_num[0], ward_room_num[1], los_sim_time, los_sim_time, transmission_type, time_of_infection, incubationtime, symptom_state, movementflag, symp_trans_count, asymp_trans_count, trans_count_to_pat, trans_count_to_hcw, patient_isolated)
                        self.schedule.add(patient)
                        self.available_rooms_corona_nonicu.remove(val)
                        self.nonicu_los_list.pop(0) ## remove the first element from the list
                        self.newuniqueID += 1
                        self.number_new_corona_nonicu_patients -= 1
                        self.rooms_occupied.append([ward_room_num[0], ward_room_num[1]])
#                        print('In covid non-icu admission',self.schedule.time, self.schedule.time/self.num_steps_per_day, los_sim_time, los_realtime, (self.newuniqueID-1), self.number_new_corona_nonicu_patients)
                        break
                    del copy_available_rooms_corona_nonicu[:]        
            
        else:
            pass    
            

    def remove_agents_on_discharge(self):
        '''
        When patient length of stay is equal zero, patient discharge from the hospital.
        patient related data is added to respective dataframes before removing them from the agent list
        We also recover symptomatic patients before discharge if patient was not yet recovered due to shorter LOS
        This is because we do not want to count symptomatic patients into the data that counts patients sent to community as exposed
        '''
        agent_list_copy = self.schedule.agents_by_type[Patient][:]
        for pat in agent_list_copy:
            if pat.los_remaining <= 0:
                if (pat.state == State.EXPOSED or pat.state == State.ASYMPTOMATIC): ## mild and severe infected patients will get extended LOS and remain in the hospital until recovered
                    self.number_covid19_patients_to_community += 1
                if (pat.state == State.MILD or pat.state == State.SEVERE):
                    pat.state = State.RECOVERED

                if pat.symptom_state == 1:
                    self.patient_seco_trans_counts.loc[len(self.patient_seco_trans_counts),:] = np.NaN, pat.asymp_secon_trans_count, pat.trans_count_to_pat, pat.trans_count_to_hcw
                if pat.symptom_state == 2:
                    self.patient_seco_trans_counts.loc[len(self.patient_seco_trans_counts),:] = pat.symp_secon_trans_count, np.NaN, pat.trans_count_to_pat, pat.trans_count_to_hcw
                ## remove patient from the hospital
                room_num = pat.room
                ward_num = pat.ward
                num_room = str(str(ward_num)+"."+str(room_num))
                self.schedule.remove(pat)
                self.daily_pat_discharge[ward_num-1] += 1
                # append empty room to the available rooms list
                if ward_num < 5: ## rooms in corona wards
                    self.available_rooms_corona_icu.append(num_room)
                elif ward_num >= 5 and ward_num < 9: ## rooms in corona wards
                    self.available_rooms_corona_nonicu.append(num_room)
                elif ward_num >= 9: ## remaining wards
                    self.available_rooms.append(num_room)
                # remove room and ward informtion from occupied room list
                for i, j in enumerate(self.rooms_occupied):
                    if j[0] == ward_num and j[1] == room_num:
                        del self.rooms_occupied[i]



    def data_write(self):
        '''
        The below method is called every 24 hours and write output data to respective dataframes
        '''        
        cor_arr_count = self.count_patient_by_state(2) + self.count_patient_by_state(4)
        self.daily_corona_arrivals.loc[len(self.daily_corona_arrivals),:] = cor_arr_count

        infected_exposed_count = [0]*len(self.room_num)
        for ward in range(1,len(self.room_num)+1):
            if self.count_patient_per_ward(ward) > 0:
                infected_exposed_count[ward-1] = self.count_covid_positive_patients_by_ward(ward)/self.count_patient_per_ward(ward)
        self.data_total_prev_per_ward.loc[len(self.data_total_prev_per_ward), :] = infected_exposed_count
        
        patient_count = [0]*len(self.room_num)
        for ward in range(1,len(self.room_num)+1):
            patient_count[ward-1] = self.count_patient_per_ward(ward)
        self.data_pat_per_ward.loc[len(self.data_pat_per_ward), :] = patient_count
        self.data_pat_discharge_per_ward.loc[len(self.data_pat_discharge_per_ward),:] = self.daily_pat_discharge
        
        self.data_covid19_patients_to_community = self.data_covid19_patients_to_community.append({'count':self.number_covid19_patients_to_community}, ignore_index=True)
        self.daily_transmission_count.loc[len(self.daily_transmission_count),:] = self.daily_transmissions,self.daily_transmissions_pat, self.daily_transmissions_hcw 

        ### patient prevalence data full hospital. Infected states are 1 (exposed), 2(mild), 4(severe), 6(asympto)
        total_patients = self.schedule.get_type_count(Patient)
        total_infected = self.count_patient_by_state(1) + self.count_patient_by_state(2) + self.count_patient_by_state(4) + self.count_patient_by_state(6)
        
        if total_patients > 0:
            total_prevalence = total_infected/total_patients
        else:
            total_prevalence = 0
        ### prevalence nosocomial tranmissions in patients
        total_nosocomial_infected = self.count_patient_by_state_hospital_transmission(1) + self.count_patient_by_state_hospital_transmission(2) + self.count_patient_by_state_hospital_transmission(4) + self.count_patient_by_state_hospital_transmission(6)
        if total_patients > 0:
            total_nosocomial_prev = total_nosocomial_infected/total_patients
        else:
            total_nosocomial_prev = 0
        self.data_prev_full_hosp.loc[len(self.data_prev_full_hosp), :] = total_prevalence, total_nosocomial_prev

        ##### patient count by state data (only hospital transmisison patients)
        num_states = 7 ## seven disease states for patients
        transmissions_by_state_count = [0]*num_states
        for state in range(0,num_states):
            transmissions_by_state_count[state] = self.count_patient_by_state_hospital_transmission(state)
        self.data_transmissions_state_count.loc[len(self.data_transmissions_state_count), :] = transmissions_by_state_count

        ##### patient count by state data (incl. transmisison and community acquired patients)
        state_count = [0]*num_states
        for state in range(0,num_states):
            state_count[state] = self.count_patient_by_state(state)
        self.data_patient_state_count.loc[len(self.data_patient_state_count), :] = state_count

        ##### physicians count by state (nosocomial transmissions only)
        phy_transmissions_by_state_count = [0]*num_states
        for state in range(0,num_states):
            phy_transmissions_by_state_count[state] = self.count_physician_by_state_hospital_transmission(state)
        self.data_physician_transmissions_state_count.loc[len(self.data_physician_transmissions_state_count), :] = phy_transmissions_by_state_count

        ##### physicians count by state (incl. community acquired and hospital transmisisons)
        phy_state_count = [0]*num_states
        for state in range(0,num_states):
            phy_state_count[state] = self.count_physician_by_state(state)
        self.data_physician_state_count.loc[len(self.data_physician_state_count), :] = phy_state_count

        ##### nurses count by state (only hospital transmisisons)
        nur_transmissions_by_state_count = [0]*num_states
        for state in range(0,num_states):
            nur_transmissions_by_state_count[state] = self.count_nurse_by_state_hospital_transmission(state)
        self.data_nurse_transmissions_state_count.loc[len(self.data_nurse_transmissions_state_count), :] = nur_transmissions_by_state_count

        ##### nurses count by state (incl. community acquired and hospital transmisisons)
        nur_state_count = [0]*num_states
        for state in range(0,num_states):
            nur_state_count[state] = self.count_nurse_by_state(state)
        self.data_nurse_state_count.loc[len(self.data_nurse_state_count), :] = nur_state_count

        self.daily_infected_hcw.loc[len(self.daily_infected_hcw), :] = self.count_infected_hcw()        
        self.daily_absent_hcw.loc[len(self.daily_absent_hcw),:] = self.count_absent_hcws()
        
        

    def write_final_dataframes(self):
        '''
        This method is called at the last time step to write output data to csv files
        '''        
        for pat in self.schedule.agents_by_type[Patient]:
            if pat.symptom_state == 1:
                self.patient_seco_trans_counts.loc[len(self.patient_seco_trans_counts),:] = np.NaN, pat.asymp_secon_trans_count, pat.trans_count_to_pat, pat.trans_count_to_hcw
            elif pat.symptom_state == 2:
                self.patient_seco_trans_counts.loc[len(self.patient_seco_trans_counts),:] = pat.symp_secon_trans_count, np.NaN, pat.trans_count_to_pat, pat.trans_count_to_hcw
        self.patient_seco_trans_counts.to_csv(self.results_dir+'simulations/patient_seco_trans_count.csv')
        
        hcws_list = np.concatenate([self.schedule.agents_by_type[Physician],self.schedule.agents_by_type[Nurse]]) ## list of all HCWs
        for hcw in hcws_list:
            if any(val > 0 for val in hcw.contact_tracing_output):
                self.contact_tracing_counts.loc[len(self.contact_tracing_counts), :] = hcw.contact_tracing_output[0],hcw.contact_tracing_output[1], hcw.contact_tracing_output[2], hcw.contact_tracing_output[3], hcw.contact_tracing_output[4], hcw.contact_tracing_output[5], hcw.contact_tracing_output[6], hcw.contact_tracing_output[7], hcw.contact_tracing_output[8], hcw.contact_tracing_output[9], hcw.contact_tracing_output[10], hcw.contact_tracing_output[11]            
            if hcw.symptom_state == 1:
                self.hcw_seco_trans_counts.loc[len(self.hcw_seco_trans_counts),:] = np.NaN, hcw.asymp_secon_trans_count, hcw.trans_count_to_pat, hcw.trans_count_to_hcw
            elif hcw.symptom_state == 2:
                self.hcw_seco_trans_counts.loc[len(self.hcw_seco_trans_counts),:] = hcw.symp_secon_trans_count, np.NaN, hcw.trans_count_to_pat, hcw.trans_count_to_hcw
                
        self.hcw_seco_trans_counts.to_csv(self.results_dir+'simulations/hcw_seco_trans_count.csv')
        self.data_total_prev_per_ward.to_csv(self.results_dir+'simulations/data_total_prev_per_ward.csv')
        self.data_pat_per_ward.to_csv(self.results_dir+'simulations/patients_per_ward_every_day.csv')
        self.data_pat_discharge_per_ward.to_csv(self.results_dir+'simulations/daily_patients_discharge_per_ward.csv')
        self.data_patient_state_count.to_csv(self.results_dir+'simulations/patients_by_state_per_day.csv')
        self.data_transmissions_state_count.to_csv(self.results_dir+'simulations/patients_by_state_per_day_hospital_transmissions_only.csv')
        self.data_physician_state_count.to_csv(self.results_dir+'simulations/physicians_by_state_per_day.csv')
        self.data_physician_transmissions_state_count.to_csv(self.results_dir+'simulations/physicians_by_state_per_day_hospital_transmissions_only.csv')
        self.data_nurse_state_count.to_csv(self.results_dir+'simulations/nurses_by_state_per_day.csv')
        self.data_nurse_transmissions_state_count.to_csv(self.results_dir+'simulations/nurses_by_state_per_day_hospital_transmissions_only.csv')
        self.data_covid19_patients_to_community.to_csv(self.results_dir+'simulations/covid19_patients_Discharge_count.csv')
        self.data_prev_full_hosp.to_csv(self.results_dir+'simulations/prev_full_hosp.csv')        
        self.screening_counts.to_csv(self.results_dir+'simulations/screening_counts.csv')
        self.contact_tracing_counts.to_csv(self.results_dir+'simulations/contact_tracinng_counts.csv')
        self.daily_transmission_count.to_csv(self.results_dir+'simulations/daily_transmissions_count.csv')
        self.daily_infected_hcw.to_csv(self.results_dir+'simulations/daily_infected_hcw_count.csv')
        self.daily_absent_hcw.to_csv(self.results_dir+'simulations/daily_absent_hcw_count.csv')
        self.data_transmission_routes.loc[len(self.data_transmission_routes), :] =self.total_transmissions,self.p_n_transmission,self.p_hc_transmission,self.n_p_transmission,self.n_hc_transmission,self.n_n_transmission,self.hc_p_transmission,self.hc_n_transmission,self.hc_hc_transmission,self.total_hcw_community_transmissions,self.total_transmissions_non_covid_wards,self.total_transmissions_covid_wards, self.asym_adm_count, self.exposed_adm_count, (self.newuniqueID-5000), self.num_suscep_pat,self.num_replace_hcw, self.trans_counts_from_pre_symptomatic, self.trans_counts_from_symptomatic,self.trans_counts_from_asymptomatic
        self.data_transmission_routes.to_csv(self.results_dir+'simulations/transmission_routes_contribution_count.csv')
        self.Time_btw_trans_and_sym_onset.to_csv(self.results_dir+'simulations/time_btw_transm_sym_onset.csv')
        df_occupied_beds = pd.DataFrame()
        df_occupied_beds['occupied_bed'] = self.data_pat_per_ward.iloc[:,0:8].sum(axis=1) + self.data_pat_discharge_per_ward.iloc[:,0:8].sum(axis=1)
        df_occupied_beds.to_csv(self.results_dir+'simulations/occupied_beds.csv')

    def physician_visits(self):
        '''
        This method takes care of physcicians visiting individual patient in their rooms.
        This is moment where transmission event can take place
        in every shift, physicians make different rounds depending on the parameters.
        '''        
        ### make a list of rooms to be visited after a fixed period
        if self.schedule.time%(int(self.num_steps_per_day/(self.shifts_per_day*self.rounds_during_shift))) == 0:
            for phy in self.schedule.agents_by_type[Physician]:
                if phy.time_outofwork == 0:
                    phy.pat_attend_counter = 0
            self.rooms_to_be_visited = copy.copy(self.rooms_occupied) # make a copy of all occupied rooms
        self.rooms_to_be_visited = [list( map(int,i) ) for i in self.rooms_to_be_visited] # to convert str list into integer list
        self.rooms_to_be_visited.sort()

        ### this is the code for person to person contact during rounds in each shift
        for ward_num in range(1,len(self.room_num)+1):
            ward_list = []
            if self.schedule.time%(self.phy_service_time[ward_num-1]) == 0:
                ward_list = self.physician_list_by_ward_and_current_shift(ward_num)
                for phy in ward_list:
                    if phy.pat_attend_counter < self.phy_pat_ratio[ward_num-1] and phy.time_outofwork == 0: ## physician has not attended all patients and is working
                        for i, j in enumerate(self.rooms_to_be_visited):
                            if phy.ward == j[0]: ## select physician by ward
                                for pat in self.schedule.agents_by_type[Patient]:
                                    if (int(pat.ward) == j[0] and int(pat.room) == j[1]): ## select patient by ward and room
                                        beta, infec_time = 0.0, 0.0
                                        beta_sym, beta_asym,foi = 0,0,0

                                        ### for contact tracing
                                        match_found = False
                                        for idx, val in enumerate(phy.contact_tracing):
                                            if val[0] == pat.unique_id:
                                                if self.schedule.time  > val[1]:
                                                    val[1] = self.schedule.time
                                                    match_found = True
                                                else:
                                                    match_found = True
                                        if not match_found:
                                            phy.contact_tracing.append([pat.unique_id,self.schedule.time])

                                        '''### transmission event '''
                                        ### first check if HCW is positive and patient is susceptible 
                                        if (pat.state == State.SUSCEPTIBLE) and (phy.state == State.EXPOSED or phy.state == State.ASYMPTOMATIC):
                                            if phy.time_of_infection != 0:
                                                infec_time = (self.schedule.time - phy.time_of_infection)/self.num_steps_per_day ## real infection time
                                                if phy.protective_gear == 1:
                                                    r1 = self.gear_effectiveness ## reduction factor of an infected person wearing protective gear
                                                else:
                                                    r1 = 1 ## when it is 1, it means HCW is not wearing any protective gear therefore r1 has no effect on the transmission
                                                
                                                ## reduction in transmission due to patient isolation
                                                if pat.patient_isolated == 1:
                                                    p1 = self.gear_effectiveness ## this will reduce the Beta calculation assuming that hcw is wearing ppe
                                                else:
                                                    p1 = 1 ## when this is 1, means that patient is not in isloation and there will be no reduction in the Beta calculation. 
                                                
                                                ### Beta calculation
                                                if phy.symptom_state == 1: ## Physician is asymptomatic
                                                    beta = p1* r1 * (self.Ra * weibull_min.pdf(infec_time, self.shape, loc=0, scale=self.scale))
                                                elif phy.symptom_state == 2: ## Physician is symptomatic
                                                    beta = p1 * r1 * (self.Rs * weibull_min.pdf(infec_time, self.shape, loc=0, scale=self.scale))
                                                ### now do a Bernoulli Trial and see if transmission is successful or not
                                                b_trial = self.get_bernoulli_trial(beta/self.lar_eig_val)
                                                if b_trial == 1:
                                                    self.Time_btw_trans_and_sym_onset.loc[len(self.Time_btw_trans_and_sym_onset),:] = self.schedule.time, phy.incubationtime, phy.time_of_infection,phy.state
                                                    pat.state = State.EXPOSED
                                                    pat.time_of_infection = self.schedule.time
                                                    pat.transmission_type = 2 ## within-in hospital transmission
                                                    self.daily_transmissions += 1
                                                    self.daily_transmissions_pat += 1
                                                    self.total_transmissions += 1 ## add transmission event to total transmissions counter
                                                    if phy.state == State.EXPOSED:
                                                        self.trans_counts_from_pre_symptomatic += 1
                                                    if phy.state == State.ASYMPTOMATIC:
                                                        self.trans_counts_from_asymptomatic += 1
                                                    if pat.ward < 9:
                                                        self.total_transmissions_covid_wards += 1
                                                    elif pat.ward >= 9:
                                                        self.total_transmissions_non_covid_wards += 1
                                                    #### to write data of secondary tranmissions count stratified by ifector state (symptomatic or asymptomatic)
                                                    if phy.state == State.EXPOSED:
                                                        phy.symp_secon_trans_count += 1
                                                    elif phy.state == State.ASYMPTOMATIC:
                                                        phy.asymp_secon_trans_count += 1
                                                    phy.trans_count_to_pat += 1 ## transmission was from hcw to pat, so it is counted in trans_count_to_pat
                                                    self.hc_p_transmission += 1 ## add transmission event hc-p transmission counter.                            
                                                    if random.random() < self.Pa_p: ## proportion of asymptomatic patients
                                                        pat.symptom_state = 1 ## 1 means asymptomatic,
                                                        pat.incubationtime = 0 ### we assume that asymptomatic patients do not stay in the exposed compartment and move to asymptomatic in the next time step.
                                                    else:
                                                        incubation_realtime = abs(np.random.choice(self.inc_period, p=self.gamma_pdf))
                                                        incubation_simtime = int(incubation_realtime * self.num_steps_per_day)
                                                        pat.incubationtime = incubation_simtime
                                                        pat.symptom_state = 2 ## 2 means symptomatic

                                        
                                        ### check if patient is positive and hcw is susceptible 
                                        elif (phy.state == State.SUSCEPTIBLE) and (pat.state == State.EXPOSED or pat.state == State.ASYMPTOMATIC or pat.state == State.MILD or pat.state == State.MODERATE or pat.state == State.SEVERE):
                                            if pat.time_of_infection != 0:
                                                infec_time = (self.schedule.time - pat.time_of_infection)/self.num_steps_per_day
                                                if phy.protective_gear == 1:
                                                    rs = self.gear_effectiveness ## reduction factor of an infected person wearing protective gear
                                                else:
                                                    rs = 1 ## when it is 1, it means HCW is not wearing any protective gear therefore r1 has no effect on the transmission
                                                ## reduction in Beta due to patient isolation
                                                if pat.patient_isolated == 1:
                                                    p1 = self.gear_effectiveness ## this will reduce the Beta calculation assuming that hcw is wearing ppe
                                                else:
                                                    p1 = 1 ## when this is 1, means that patient is not in isloation and there will be no reduction in the Beta calculation. 
                                                ### Beta calculation
                                                if pat.symptom_state == 1: #### Patient is asymptomatic
                                                    beta = p1 * rs * (self.Ra * weibull_min.pdf(infec_time, self.shape, loc=0, scale=self.scale))
                                                elif pat.symptom_state == 2: #### Patient is symptomatic
                                                    beta = p1 * rs * (self.Rs * weibull_min.pdf(infec_time, self.shape, loc=0, scale=self.scale))
                                                ### now do a Bernoulli Trial and see if transmission is successful or not
                                                b_trial = self.get_bernoulli_trial(beta/self.lar_eig_val) ## beta is used as a probability of infecting others
                                                if b_trial == 1:
                                                    self.Time_btw_trans_and_sym_onset.loc[len(self.Time_btw_trans_and_sym_onset),:] = self.schedule.time, pat.incubationtime, pat.time_of_infection,pat.state
                                                    phy.state = State.EXPOSED
                                                    phy.time_of_infection = self.schedule.time
                                                    phy.transmission_type = 2 ## within-hospital transmission
                                                    self.daily_transmissions += 1
                                                    self.daily_transmissions_hcw += 1
                                                    self.total_transmissions += 1 ## add transmission event to total transmissions counter
                                                    if pat.state == State.EXPOSED:
                                                        self.trans_counts_from_pre_symptomatic += 1
                                                    elif pat.state == State.ASYMPTOMATIC:
                                                        self.trans_counts_from_asymptomatic += 1
                                                    elif pat.state == State.MILD or pat.state == State.MODERATE or pat.state == State.SEVERE:
                                                        self.trans_counts_from_symptomatic += 1
                                                    if phy.ward < 9:
                                                        self.total_transmissions_covid_wards += 1
                                                    elif phy.ward >= 9:
                                                        self.total_transmissions_non_covid_wards += 1
                                                    #### to write data of secondary tranmissions count stratified by ifector state (symptomatic or asymptomatic)
                                                    if pat.state == State.EXPOSED or pat.state == State.MILD or pat.state == State.MODERATE or pat.state == State.SEVERE:
                                                        pat.symp_secon_trans_count += 1
                                                    elif pat.state == State.ASYMPTOMATIC:
                                                        pat.asymp_secon_trans_count += 1
                                                    pat.trans_count_to_hcw += 1 ## transmission was from pat to hcw, so it is counted in trans_count_to_hcw
                                                    self.p_hc_transmission += 1 ## add transmission event to patient to hc transmission counter.                                                    
                                                    if random.random() < self.Pa_hcws: ## proportion of asymptomatic hcws
                                                        phy.symptom_state = 1 ## 1 means asymptomatic,
                                                        phy.incubationtime = 0 ## we assume that asymptomatic patients/hcws do not stay in the exposed compartment and move to asymptomatic in the next time step.
                                                    else:
                                                        incubation_realtime = abs(np.random.choice(self.inc_period, p=self.gamma_pdf))
                                                        incubation_simtime = int(incubation_realtime * self.num_steps_per_day)
                                                        phy.incubationtime = incubation_simtime
                                                        phy.symptom_state = 2 ## 2 means symptomatic, 0 means not in both

                                        phy.pat_attend_counter += 1 ## physician has attended the patient
                                        if i < len(self.rooms_to_be_visited):
                                            del self.rooms_to_be_visited[i]  ## room has been visited, so remove it from the list
                                            break
                                        else:
                                            pass
                                break


    def nurse_visits(self):
        '''
        This method takes care of nursess visiting individual patient in their rooms.
        This is moment where transmission event can take place
        in every shift, nursess make different rounds depending on the parameters.
        '''        
        ### make a list of rooms to be visited after a fixed period
        if self.schedule.time%(int(self.num_steps_per_day/(self.shifts_per_day*self.nurse_rounds_during_shift))) == 0:
            for nur in self.schedule.agents_by_type[Nurse]:
                if nur.time_outofwork == 0:
                    nur.pat_attend_counter = 0 
            self.rooms_to_be_visited_by_nurses = copy.copy(self.rooms_occupied) # make a copy of all occupied rooms
        self.rooms_to_be_visited_by_nurses = [list( map(int,i) ) for i in self.rooms_to_be_visited_by_nurses] # to convert str list into integer list
        self.rooms_to_be_visited_by_nurses.sort()
        
        ### this is the code for person to person contact during rounds in each shift
        for ward_num in range(1,len(self.room_num)+1):
            ward_list = []
            if self.schedule.time%(self.nur_service_time[ward_num-1]) == 0:
                ward_list = self.nurse_list_by_ward_and_current_shift(ward_num)
                for nur in ward_list:
                    if nur.pat_attend_counter < self.nur_pat_ratio[ward_num-1] and nur.time_outofwork == 0:  ## nurse has not attended all patients and is working
                        for i, j in enumerate(self.rooms_to_be_visited_by_nurses):
                            if nur.ward == j[0]: ## select nurse by ward
                                for pat in self.schedule.agents_by_type[Patient]:
                                    if (int(pat.ward) == j[0] and int(pat.room) == j[1]): ## select patient by ward and room
                                        beta, infec_time = 0.0, 0.0
                                        beta_sym, beta_asym,foi = 0,0,0
                                        
                                        ### for contact tracing
                                        match_found = False
                                        for idx, val in enumerate(nur.contact_tracing):
                                            if val[0] == pat.unique_id:
                                                if self.schedule.time  > val[1]:
                                                    val[1] = self.schedule.time
                                                    match_found = True
                                                else:
                                                    match_found = True
                                        if not match_found:
                                            nur.contact_tracing.append([pat.unique_id,self.schedule.time])
                                        
                                        '''### transmission event '''
                                        ### first check if HCW is positive and patient is susceptible 
                                        if (pat.state == State.SUSCEPTIBLE) and (nur.state == State.EXPOSED or nur.state == State.ASYMPTOMATIC):
                                            if nur.time_of_infection != 0:
                                                infec_time = (self.schedule.time - nur.time_of_infection)/self.num_steps_per_day
                                                if nur.protective_gear == 1:
                                                    r1 = self.gear_effectiveness ## reduction factor of an infected person wearing protective gear
                                                else:
                                                    r1 = 1 ## when it is 1, it means HCW is not wearing any protective gear therefore r1 has no effect on the transmission
                                                ## reduction in Beta due to patient isolation
                                                if pat.patient_isolated == 1:
                                                    p1 = self.gear_effectiveness ## this will reduce the Beta calculation assuming that hcw is wearing ppe
                                                else:
                                                    p1 = 1 ## when this is 1, means that patient is not in isloation and there will be no reduction in the Beta calculation. 
                                                ### Beta calculation
                                                if nur.symptom_state == 1: ## nurse is asymptomatic
                                                    beta = p1*r1 * (self.Ra * weibull_min.pdf(infec_time, self.shape, loc=0, scale=self.scale))
                                                elif nur.symptom_state == 2: ## nurse is symptomatic
                                                    beta = p1*r1 * (self.Rs * weibull_min.pdf(infec_time, self.shape, loc=0, scale=self.scale))
                                                b_trial = self.get_bernoulli_trial(beta/self.lar_eig_val)
                                                ### now do a Bernoulli Trial and see if transmission is successful or not
                                                if b_trial == 1:
                                                    self.Time_btw_trans_and_sym_onset.loc[len(self.Time_btw_trans_and_sym_onset),:] = self.schedule.time, nur.incubationtime, nur.time_of_infection,nur.state
                                                    pat.state = State.EXPOSED
                                                    pat.time_of_infection = self.schedule.time
                                                    pat.transmission_type = 2 ## within-hospital tranmision
                                                    self.daily_transmissions += 1
                                                    self.daily_transmissions_pat += 1
                                                    self.total_transmissions += 1 ## add transmission event to total transmissions counter
                                                    if nur.state == State.EXPOSED:
                                                        self.trans_counts_from_pre_symptomatic += 1
                                                    elif nur.state == State.ASYMPTOMATIC:
                                                        self.trans_counts_from_asymptomatic += 1
                                                    if pat.ward < 9:
                                                        self.total_transmissions_covid_wards += 1
                                                    elif pat.ward >= 9:
                                                        self.total_transmissions_non_covid_wards += 1
                                                    ## write data about secondary tranmission
                                                    if nur.state == State.EXPOSED:
                                                        nur.symp_secon_trans_count += 1
                                                    elif nur.state == State.ASYMPTOMATIC:
                                                        nur.asymp_secon_trans_count += 1
                                                    nur.trans_count_to_pat += 1 ## transmission was from hcw to pat, so it is counted in trans_count_to_pat
                                                    self.n_p_transmission += 1 ## add transmission event to nurse to patient transmission counter.
                                                    if random.random() < self.Pa_p: ## proportion of asymptomatic patients
                                                        pat.symptom_state = 1 ## 1 means asymptomatic,
                                                        pat.incubationtime = 0 ### we assume that asymptomatic patients do not stay in the exposed compartment and move to asymptomatic in the next time step.
                                                    else:
                                                        incubation_realtime = abs(np.random.choice(self.inc_period, p=self.gamma_pdf))
                                                        incubation_simtime = int(incubation_realtime * self.num_steps_per_day)
                                                        pat.incubationtime = incubation_simtime
                                                        pat.symptom_state = 2 ## 2 means symptomatic, 0 means not in both

                                        ### check if patient is positive and hcw is susceptible 
                                        elif (nur.state == State.SUSCEPTIBLE) and (pat.state == State.EXPOSED or pat.state == State.ASYMPTOMATIC or pat.state == State.MILD or pat.state == State.MODERATE or pat.state == State.SEVERE):
                                            if pat.time_of_infection != 0:
                                                infec_time = (self.schedule.time - pat.time_of_infection)/self.num_steps_per_day
                                                if nur.protective_gear == 1:
                                                    rs = self.gear_effectiveness ## reduction factor of an infected person wearing protective gear
                                                else:
                                                    rs = 1 ## when it is 1, it means HCW is not wearing any protective gear therefore r1 has no effect on the transmission
                                                ## reduction in Beta due to patient isolation
                                                if pat.patient_isolated == 1:
                                                    p1 = self.gear_effectiveness ## this will reduce the Beta calculation assuming that hcw is wearing ppe
                                                else:
                                                    p1 = 1 ## when this is 1, means that patient is not in isloation and there will be no reduction in the Beta calculation. 
                                                ## Beta Calculation
                                                if pat.symptom_state == 1: #### Patient is asymptomatic
                                                    beta = p1*rs * (self.Ra * weibull_min.pdf(infec_time, self.shape, loc=0, scale=self.scale))
                                                elif pat.symptom_state == 2: #### Patient is symptomatic
                                                    beta = p1*rs * (self.Rs * weibull_min.pdf(infec_time, self.shape, loc=0, scale=self.scale))
                                                b_trial = self.get_bernoulli_trial(beta/self.lar_eig_val) ## beta is used as a probability of infecting others
                                                ### now do a Bernoulli Trial and see if transmission is successful or not
                                                if b_trial == 1:
                                                    self.Time_btw_trans_and_sym_onset.loc[len(self.Time_btw_trans_and_sym_onset),:] = self.schedule.time, pat.incubationtime, pat.time_of_infection,pat.state
                                                    nur.state = State.EXPOSED
                                                    nur.time_of_infection = self.schedule.time
                                                    nur.transmission_type = 2 ## within-hospital tranmision
                                                    self.daily_transmissions += 1
                                                    self.daily_transmissions_hcw += 1
                                                    self.total_transmissions += 1 ## add transmission event to total transmissions counter
                                                    if pat.state == State.EXPOSED:
                                                        self.trans_counts_from_pre_symptomatic += 1
                                                    elif pat.state == State.ASYMPTOMATIC:
                                                        self.trans_counts_from_asymptomatic += 1
                                                    elif pat.state == State.MILD or pat.state == State.MODERATE or pat.state == State.SEVERE:
                                                        self.trans_counts_from_symptomatic += 1
                                                    if nur.ward < 9:
                                                        self.total_transmissions_covid_wards += 1
                                                    elif nur.ward >= 9:
                                                        self.total_transmissions_non_covid_wards += 1
                                                    #### to write data of econdary tranmissions count stratified by ifector state (symptomatic or asymptomatic)
                                                    if pat.state == State.EXPOSED or pat.state == State.MILD or pat.state == State.MODERATE or pat.state == State.SEVERE:
                                                        pat.symp_secon_trans_count += 1
                                                    elif pat.state == State.ASYMPTOMATIC:
                                                        pat.asymp_secon_trans_count += 1
                                                    pat.trans_count_to_hcw += 1 ## transmission was from pat to hcw, so it is counted in trans_count_to_hcw    
                                                    self.p_n_transmission += 1 ## add transmission event to patient to nurse transmission counter.                                                    
                                                    if random.random() < self.Pa_hcws: ## proportion of asymptomatic hcws
                                                        nur.symptom_state = 1 ## 1 means asymptomatic,
                                                        nur.incubationtime = 0 ## we assume that asymptomatic patients/hcws do not stay in the exposed compartment and move to asymptomatic in the next time step.
                                                    else:
#                                                        incubation_realtime = abs(np.random.choice(self.inc_period, p=self.lognorm_pdf))
                                                        incubation_realtime = abs(np.random.choice(self.inc_period, p=self.gamma_pdf))
                                                        incubation_simtime = int(incubation_realtime * self.num_steps_per_day)
                                                        nur.incubationtime = incubation_simtime
                                                        nur.symptom_state = 2 ## 2 means symptomatic, 0 means not in both

                                        nur.pat_attend_counter += 1  ## nurse has attend patient
                                        if i < len(self.rooms_to_be_visited_by_nurses):
                                            del self.rooms_to_be_visited_by_nurses[i]  ## room has been visitied, now remove it from the list
                                            break
                                        else:
                                            pass
                                break


    def exposed_to_infection(self):
        '''
        This code move exposed individuals to infection state
        Patient who developed severe state will get an increase in the LOS
        No increase in LOS for mild state patients
        movement flags for mild and severe patients is set to True so that they can be moved to covid wards 
        symptomatic HCWs are sent home for quarantine and a replacement susceptible HCW is added phy.state == State.SEVERE
        '''        
        #### for patients
        for pat in self.schedule.agents_by_type[Patient]:
            if pat.incubationtime == 0 and pat.symptom_state == 2 and (pat.state == State.EXPOSED or pat.state == State.ASYMPTOMATIC):
#                print('I entered here 1', pat.state, pat.unique_id)
                los_realtime,los_sim_time = 0.00, 0
                if random.random() < self.Ps: ## proportion of patients which develop severe infections
                    pat.state = State.SEVERE
                    los_realtime = abs(np.random.choice(self.elements, p=self.weights_coronaicu))
                    los_sim_time = int(los_realtime * self.num_steps_per_day)
                    pat.los = los_sim_time + (pat.los - pat.los_remaining) ## this is done just to keep track of total patient LOS
                    pat.los_remaining = los_sim_time # LOS increase due to severe infection,taken from LOS distribution of severe patients                   
                    pat.incubationtime = None ## set incubation time to None so that same patient will not be considered in this loop next time.
                    if pat.ward >= 9:
                        pat.movementflag = True ## When this is True, patient will be moved to corona wards as soon as possible
                else:
                    pat.state = State.MILD
                    pat.incubationtime = None ## set incubation time to None so that same patient will not be considered in this loop in the next step.
                    if pat.ward >= 9:
                        pat.movementflag = True ## When this is True, patient will be moved to corona wards as soon as possible
            ### for asymptomatic patients, There is no incubation time for asymptomatics, it is set to zero. so they are moved to Asymptomatic state immediately after exposure.
            if pat.incubationtime == 0 and pat.symptom_state == 1:
#                print('I entered here 2')
                pat.state = State.ASYMPTOMATIC
                pat.incubationtime = None

        #### for physicians
        for phy in self.schedule.agents_by_type[Physician]:
            ## for symptomatic physicians
            if phy.incubationtime == 0 and phy.symptom_state == 2:
#                print('I entered here 3')
                if random.random() < self.Ps: ## proportion of physicians which develop severe infections
                    phy.state = State.SEVERE
                else:
                    phy.state = State.MILD
                phy.time_outofwork = int(self.quarantine_period)
                phy.incubationtime = None ## set incubation time to None so that same physcician will not be considered in this loop in the next step.
                phy.replacement_added = True ## this boolean keeps track if a replacement HCW was added (True)
                
                ## check if hcw was asked to wear ppe in contact tracing
                ppe = 0
                if phy.hcw_on_ppe_cont_tracing == 1: ## hcw was asked to wear ppe
                    if phy.ward >= 9:
                        ppe = 0
                    else:
                        ppe = 1
                elif phy.hcw_on_ppe_cont_tracing == 0: ## hcw was asked not asked to wear ppe
                    ppe = phy.protective_gear 

                #### a replacement susceptible physcician is added with similar ward, shift, and protective gear details
                physician = Physician(self.phyuniqueID, self, 0, phy.ward, phy.pat_attend_counter, phy.shift, 0, ppe, None, 0, 0, 0, None, False, 0, False, 0, 0, 0, 0, None, 0)
                self.schedule.add(physician)
                self.phyuniqueID +=1
                self.num_replace_hcw += 1
            ### for asymptomatic physicians    
            if phy.incubationtime == 0 and phy.symptom_state == 1:
#                print('I entered here 4')
                phy.state = State.ASYMPTOMATIC
                phy.incubationtime = None ## set incubation time to None so that same physcician will not be considered in this loop in the next step.
                
        #### for nurses
        for nur in self.schedule.agents_by_type[Nurse]:
            if nur.incubationtime == 0 and nur.symptom_state == 2:
                if random.random() < self.Ps: ## proportion of nurses which develop severe infections
                    nur.state = State.SEVERE
                else:
                    nur.state = State.MILD
                nur.time_outofwork = int(self.quarantine_period)
                nur.incubationtime = None ## set incubation time to None so that same nurse will not be considered in this loop in the next step.
                nur.replacement_added = True
                ## check if hcw was asked to wear ppe in contact tracing
                ppe = 0
                if nur.hcw_on_ppe_cont_tracing == 1: ## hcw was asked to wear ppe
                    if nur.ward >= 9:
                        ppe = 0
                    else:
                        ppe = 1
                elif nur.hcw_on_ppe_cont_tracing == 0: ## hcw was asked not asked to wear ppe
                    ppe = nur.protective_gear
                #### replacement susceptible physcician is added with similar ward, shift, and protective gear details
                nurse = Nurse(self.nuruniqueID, self, 0, nur.ward, nur.pat_attend_counter, nur.shift, 0, ppe, None, 0, 0, 0,None, False, 0, False, 0, 0, 0, 0, None, 0)
                self.schedule.add(nurse)
                self.nuruniqueID +=1
                self.num_replace_hcw += 1
            ### for asymptomatic nurses    
            if nur.incubationtime == 0 and nur.symptom_state == 1:
                nur.state = State.ASYMPTOMATIC
                nur.incubationtime = None ## set incubation time to None so that same physcician will not be considered in this loop in the next step.


    def infected_to_recovered(self):
        '''
        This infected to recovered method is only applied to patients
        depending on the disease state, patients recover either after 14 days or 35 days   
        '''
        for pat in self.schedule.agents_by_type[Patient]:
            ### if patient is asymptomatic
            if pat.state == State.ASYMPTOMATIC:
                if pat.time_of_infection != 0:
                    if (self.schedule.time - pat.time_of_infection)>params.recov_asymp:
                        pat.state = State.RECOVERED
                        pat.time_of_infection = 0
            ## recovery of symptomatic patients
            if pat.state == State.SEVERE:
                if (self.schedule.time - pat.time_of_infection)>params.recov_severe:
                    pat.state = State.RECOVERED    
            if pat.state == State.MILD:
                if (self.schedule.time - pat.time_of_infection)>params.recov_mild:
                    pat.state = State.RECOVERED


    def HCW_recovered_and_back_to_work(self):
        '''
        ### This method is only for HCWs and here HCWs recover and come back to work. 
        ### Since we keep constant number of HCWs in the hospital, when a hcw comes back to work, we need to remove another hcw from the same ward and shift as of the hcw coming back
        ### To remove another HCW, we first look in the list of susceptible hcws, if exist, then remove a susceptible hcw
        ### if there is no susceptible, then look and remove an exposed or asymptomatic hcw
        ### if this is also not successful, then remove a recovered hcw.
        '''
        ### for physicians
        phy_list_copy = self.schedule.agents_by_type[Physician][:]
        for phy in phy_list_copy:
            if phy.time_outofwork == 0 and (phy.state == State.SEVERE or phy.state == State.MILD or phy.state == State.ASYMPTOMATIC):
                susceptible_phy_wardlist = []
                exposed_asymp_phy_wardlist = []
                recovered_phy_wardlist = []
                phy_wardlist = self.physician_list_by_ward_and_shift(phy.ward, phy.shift)
                for hcw in phy_wardlist:
                    if hcw.state == State.SUSCEPTIBLE:
                        susceptible_phy_wardlist.append(hcw)
                    elif hcw.time_outofwork == 0 and (hcw.state == State.EXPOSED or hcw.state == State.ASYMPTOMATIC):
                        exposed_asymp_phy_wardlist.append(hcw)
                    elif hcw.state == State.RECOVERED:
                        recovered_phy_wardlist.append(hcw)

                ##### Removal of another hcw to account for recovered hcw to come back to work.
                if phy.replacement_added is True: ### if True means that we need to remove another Hcw from the same ward and shift
                    replacement_removed = False ## just to keep track if another hcw is removed if a replacement was added 
                    if susceptible_phy_wardlist:
                        susc_hcw_to_be_removed = random.choice(susceptible_phy_wardlist)  ## randomly pick a susceptible hcw and remove it from the hospital             
                        self.schedule.remove(susc_hcw_to_be_removed)
                        replacement_removed = True
                        phy.state = State.RECOVERED
                        phy.time_of_infection = 0 ## set time of infection back to zero
                        phy.replacement_added = False

                    elif replacement_removed is False and exposed_asymp_phy_wardlist:
                        exp_asym_hcw_to_be_removed = random.choice(exposed_asymp_phy_wardlist) ## randomly pick an exposed or asymptomatic hcw and remove it from the hospital
                        if any(val > 0 for val in exp_asym_hcw_to_be_removed.contact_tracing_output):
                            self.contact_tracing_counts.loc[len(self.contact_tracing_counts), :] = exp_asym_hcw_to_be_removed.contact_tracing_output[0],exp_asym_hcw_to_be_removed.contact_tracing_output[1], exp_asym_hcw_to_be_removed.contact_tracing_output[2], exp_asym_hcw_to_be_removed.contact_tracing_output[3], exp_asym_hcw_to_be_removed.contact_tracing_output[4], exp_asym_hcw_to_be_removed.contact_tracing_output[5], exp_asym_hcw_to_be_removed.contact_tracing_output[6], exp_asym_hcw_to_be_removed.contact_tracing_output[7], exp_asym_hcw_to_be_removed.contact_tracing_output[8], exp_asym_hcw_to_be_removed.contact_tracing_output[9], exp_asym_hcw_to_be_removed.contact_tracing_output[10], exp_asym_hcw_to_be_removed.contact_tracing_output[11]
                        if exp_asym_hcw_to_be_removed.symptom_state == 1:
                            self.hcw_seco_trans_counts.loc[len(self.hcw_seco_trans_counts),:] = np.NaN, exp_asym_hcw_to_be_removed.asymp_secon_trans_count, exp_asym_hcw_to_be_removed.trans_count_to_pat, exp_asym_hcw_to_be_removed.trans_count_to_hcw
                        elif exp_asym_hcw_to_be_removed.symptom_state == 2:
                            self.hcw_seco_trans_counts.loc[len(self.hcw_seco_trans_counts),:] = exp_asym_hcw_to_be_removed.symp_secon_trans_count, np.NaN, exp_asym_hcw_to_be_removed.trans_count_to_pat, exp_asym_hcw_to_be_removed.trans_count_to_hcw
                        self.schedule.remove(exp_asym_hcw_to_be_removed)
                        replacement_removed = True
                        phy.state = State.RECOVERED
                        phy.time_of_infection = 0 ## set time of infection back to zero
                        phy.replacement_added = False

                    elif replacement_removed is False and recovered_phy_wardlist:
                        reco_hcw_to_be_removed = random.choice(recovered_phy_wardlist) ## randomly pick a recovered hcw and remove it from the hospital
                        if any(val > 0 for val in reco_hcw_to_be_removed.contact_tracing_output):
                            self.contact_tracing_counts.loc[len(self.contact_tracing_counts), :] = reco_hcw_to_be_removed.contact_tracing_output[0],reco_hcw_to_be_removed.contact_tracing_output[1], reco_hcw_to_be_removed.contact_tracing_output[2], reco_hcw_to_be_removed.contact_tracing_output[3], reco_hcw_to_be_removed.contact_tracing_output[4], reco_hcw_to_be_removed.contact_tracing_output[5], reco_hcw_to_be_removed.contact_tracing_output[6], reco_hcw_to_be_removed.contact_tracing_output[7], reco_hcw_to_be_removed.contact_tracing_output[8], reco_hcw_to_be_removed.contact_tracing_output[9], reco_hcw_to_be_removed.contact_tracing_output[10], reco_hcw_to_be_removed.contact_tracing_output[11]
                        if reco_hcw_to_be_removed.symptom_state == 1:
                            self.hcw_seco_trans_counts.loc[len(self.hcw_seco_trans_counts),:] = np.NaN, reco_hcw_to_be_removed.asymp_secon_trans_count, reco_hcw_to_be_removed.trans_count_to_pat, reco_hcw_to_be_removed.trans_count_to_hcw
                        elif reco_hcw_to_be_removed.symptom_state == 2:
                            self.hcw_seco_trans_counts.loc[len(self.hcw_seco_trans_counts),:] = reco_hcw_to_be_removed.symp_secon_trans_count, np.NaN, reco_hcw_to_be_removed.trans_count_to_pat, reco_hcw_to_be_removed.trans_count_to_hcw
                        self.schedule.remove(reco_hcw_to_be_removed)
                        replacement_removed = True
                        phy.state = State.RECOVERED
                        phy.time_of_infection = 0 ## set time of infection back to zero
                        phy.replacement_added = False
                
                if phy.replacement_added is False and phy.state == State.ASYMPTOMATIC:
                    if phy.time_of_infection != 0:
                        if (self.schedule.time - phy.time_of_infection)>params.recov_asymp:
                            phy.state = State.RECOVERED
                            phy.time_of_infection = 0 ## set time of infection back to zero
 
        ### for nurses
        nur_list_copy = self.schedule.agents_by_type[Nurse][:]
        for nur in nur_list_copy:
            if nur.time_outofwork == 0 and (nur.state == State.SEVERE or nur.state == State.MILD or nur.state == State.ASYMPTOMATIC):
                susceptible_nur_wardlist = []
                exposed_asymp_nur_wardlist = []
                recovered_nur_wardlist = []
                nur_wardlist = self.nurse_list_by_ward_and_shift(nur.ward, nur.shift)
                for nhcw in nur_wardlist:
                    if nhcw.state == State.SUSCEPTIBLE:
                        susceptible_nur_wardlist.append(nhcw)
                    elif nhcw.time_outofwork == 0 and (nhcw.state == State.EXPOSED or nhcw.state == State.ASYMPTOMATIC):
                        exposed_asymp_nur_wardlist.append(nhcw)
                    elif nhcw.state == State.RECOVERED:
                        recovered_nur_wardlist.append(nhcw)

                ##### Removal of another hcw to account for recovered hcw to come back to work.
                if nur.replacement_added is True: ### if True means that we need to remove another Hcw from the same ward and shift
                    replacement_removed = False ## just to keep track if another nurse is removed if a replacement was added

                    if susceptible_nur_wardlist:
                        susc_hcw_to_be_removed = random.choice(susceptible_nur_wardlist) ## randomly pick a susceptible hcw and remove it from the hospital 
                        self.schedule.remove(susc_hcw_to_be_removed)
                        replacement_removed = True
                        nur.state = State.RECOVERED
                        nur.time_of_infection = 0 ## set time of infection back to zero
                        nur.replacement_added = False

                    elif replacement_removed is False and exposed_asymp_nur_wardlist:
                        exp_asym_hcw_to_be_removed = random.choice(exposed_asymp_nur_wardlist) ## randomly pick an exposed or asymptomatic hcw and remove it from the hospital
                        if any(val > 0 for val in exp_asym_hcw_to_be_removed.contact_tracing_output):
                            self.contact_tracing_counts.loc[len(self.contact_tracing_counts), :] = exp_asym_hcw_to_be_removed.contact_tracing_output[0],exp_asym_hcw_to_be_removed.contact_tracing_output[1], exp_asym_hcw_to_be_removed.contact_tracing_output[2], exp_asym_hcw_to_be_removed.contact_tracing_output[3], exp_asym_hcw_to_be_removed.contact_tracing_output[4], exp_asym_hcw_to_be_removed.contact_tracing_output[5], exp_asym_hcw_to_be_removed.contact_tracing_output[6], exp_asym_hcw_to_be_removed.contact_tracing_output[7], exp_asym_hcw_to_be_removed.contact_tracing_output[8], exp_asym_hcw_to_be_removed.contact_tracing_output[9], exp_asym_hcw_to_be_removed.contact_tracing_output[10], exp_asym_hcw_to_be_removed.contact_tracing_output[11]
                        if exp_asym_hcw_to_be_removed.symptom_state == 1:
                            self.hcw_seco_trans_counts.loc[len(self.hcw_seco_trans_counts),:] = np.NaN, exp_asym_hcw_to_be_removed.asymp_secon_trans_count, exp_asym_hcw_to_be_removed.trans_count_to_pat, exp_asym_hcw_to_be_removed.trans_count_to_hcw
                        elif exp_asym_hcw_to_be_removed.symptom_state == 2:
                            self.hcw_seco_trans_counts.loc[len(self.hcw_seco_trans_counts),:] = exp_asym_hcw_to_be_removed.symp_secon_trans_count, np.NaN, exp_asym_hcw_to_be_removed.trans_count_to_pat, exp_asym_hcw_to_be_removed.trans_count_to_hcw
                        self.schedule.remove(exp_asym_hcw_to_be_removed)
                        replacement_removed = True
                        nur.state = State.RECOVERED
                        nur.time_of_infection = 0 ## set time of infection back to zero
                        nur.replacement_added = False

                    elif replacement_removed is False and recovered_nur_wardlist:
                        reco_hcw_to_be_removed = random.choice(recovered_nur_wardlist) ## randomly pick a recovered hcw and remove it from the hospital
                        if any(val > 0 for val in reco_hcw_to_be_removed.contact_tracing_output):
                            self.contact_tracing_counts.loc[len(self.contact_tracing_counts), :] = reco_hcw_to_be_removed.contact_tracing_output[0],reco_hcw_to_be_removed.contact_tracing_output[1], reco_hcw_to_be_removed.contact_tracing_output[2], reco_hcw_to_be_removed.contact_tracing_output[3], reco_hcw_to_be_removed.contact_tracing_output[4], reco_hcw_to_be_removed.contact_tracing_output[5], reco_hcw_to_be_removed.contact_tracing_output[6], reco_hcw_to_be_removed.contact_tracing_output[7], reco_hcw_to_be_removed.contact_tracing_output[8], reco_hcw_to_be_removed.contact_tracing_output[9], reco_hcw_to_be_removed.contact_tracing_output[10], reco_hcw_to_be_removed.contact_tracing_output[11]
                        if reco_hcw_to_be_removed.symptom_state == 1:
                            self.hcw_seco_trans_counts.loc[len(self.hcw_seco_trans_counts),:] = np.NaN, reco_hcw_to_be_removed.asymp_secon_trans_count, reco_hcw_to_be_removed.trans_count_to_pat, reco_hcw_to_be_removed.trans_count_to_hcw
                        elif reco_hcw_to_be_removed.symptom_state == 2:
                            self.hcw_seco_trans_counts.loc[len(self.hcw_seco_trans_counts),:] = reco_hcw_to_be_removed.symp_secon_trans_count, np.NaN, reco_hcw_to_be_removed.trans_count_to_pat, reco_hcw_to_be_removed.trans_count_to_hcw
                        self.schedule.remove(reco_hcw_to_be_removed)
                        replacement_removed = True
                        nur.state = State.RECOVERED
                        nur.time_of_infection = 0 ## set time of infection back to zero
                        nur.replacement_added = False
                
                if nur.replacement_added is False and nur.state == State.ASYMPTOMATIC:
                    if nur.time_of_infection != 0:
                        if (self.schedule.time - nur.time_of_infection)>params.recov_asymp:
                            nur.state = State.RECOVERED
                            nur.time_of_infection = 0 ## set time of infection back to zero        


    def HCW_transmission_in_common_areas(self):
        '''
        ## We assume that HCWs do not wear protective gear in the common rooms unless asked to wear PPE in contact tracing 
        ##first loop over all the wards
        ## then get ids of HCWs and nurses in that ward
        ## then randomly pick 2 IDs:
        ## then check the state of those HCWs
        ### then do the transmission event if any one of them is exposed or asymptomatic
        '''        
        for ward_num in range(1,len(self.room_num)+1):
            randomly_selected_list = []
            hcw_list = np.concatenate([self.physician_list_by_ward_and_current_shift(ward_num),self.nurse_list_by_ward_and_current_shift(ward_num)])
            if len(hcw_list) > 2:
                randomly_selected_list = np.random.choice(hcw_list, 2, replace=False) ## this draws two random samples from the combined nurse and physician list
                if randomly_selected_list[0].hcw_on_ppe_cont_tracing == 1:
                    r0 = self.gear_effectiveness ## reduction factor due to wearing PPE, r0 for index 0 hcw
                else:
                    r0 = 1
                if randomly_selected_list[1].hcw_on_ppe_cont_tracing == 1:
                    r1 = self.gear_effectiveness ## reduction factor due to wearing PPE. r1 for index 1 hcw
                else:
                    r1 = 1
                ## check if index 0 hcw is positive and index 1 is susceptible
                if (randomly_selected_list[0].state == State.EXPOSED or randomly_selected_list[0].state == State.ASYMPTOMATIC) and randomly_selected_list[1].state == State.SUSCEPTIBLE:
                    if randomly_selected_list[0].time_of_infection != 0:
                        infec_time = (self.schedule.time - randomly_selected_list[0].time_of_infection)/self.num_steps_per_day # check infections time for infectiousness
                        ### Beta Calculation
                        if randomly_selected_list[0].symptom_state == 1: #### randomly_selected_list[0] is asymptomatic
                            beta = r0*r1*self.Ra * weibull_min.pdf(infec_time, self.shape, loc=0, scale=self.scale)
                        elif randomly_selected_list[0].symptom_state == 2: #### randomly_selected_list[0] is symptomatic
                            beta = r0*r1*self.Rs * weibull_min.pdf(infec_time, self.shape, loc=0, scale=self.scale)
                        ## do a Bernoulli Trail and see if transmission is successful or not
                        b_trial = self.get_bernoulli_trial(beta/self.lar_eig_val)
                        if b_trial == 1:
                            self.Time_btw_trans_and_sym_onset.loc[len(self.Time_btw_trans_and_sym_onset),:] = self.schedule.time, randomly_selected_list[0].incubationtime, randomly_selected_list[0].time_of_infection,randomly_selected_list[0].state
                            randomly_selected_list[1].state = State.EXPOSED
                            randomly_selected_list[1].time_of_infection = self.schedule.time
                            randomly_selected_list[1].transmission_type = 2 ## hospital tranmision
                            if randomly_selected_list[0].unique_id < 1000: ## this is physician, physician id range from 1-999
                                if randomly_selected_list[1].unique_id < 1000: ## this is physician
                                    self.hc_hc_transmission += 1
                                elif randomly_selected_list[1].unique_id >= 1000 and randomly_selected_list[1].unique_id < 5000: ## this is nurse, nurse id range from 1000 - 4999
                                    self.hc_n_transmission += 1
                            elif randomly_selected_list[0].unique_id >= 1000 and randomly_selected_list[0].unique_id < 5000: ## this is nurse
                                if randomly_selected_list[1].unique_id < 1000: ## this is physician
                                    self.n_hc_transmission += 1
                                elif randomly_selected_list[1].unique_id >= 1000 and randomly_selected_list[1].unique_id < 5000: ## this is nurse
                                    self.n_n_transmission += 1
                            self.daily_transmissions += 1
                            self.daily_transmissions_hcw += 1
                            self.total_transmissions += 1
                            if randomly_selected_list[0].state == State.EXPOSED:
                                self.trans_counts_from_pre_symptomatic += 1
                                randomly_selected_list[0].symp_secon_trans_count += 1
                            elif randomly_selected_list[0].state == State.ASYMPTOMATIC:
                                self.trans_counts_from_asymptomatic += 1
                                randomly_selected_list[0].asymp_secon_trans_count += 1
                            randomly_selected_list[0].trans_count_to_hcw += 1 ## transmission was from hcw to hcw, so it is counted in trans_count_to_hcw
                            if randomly_selected_list[1].ward < 9:
                                self.total_transmissions_covid_wards += 1
                            elif randomly_selected_list[1].ward >= 9:
                                self.total_transmissions_non_covid_wards += 1
                            
                            if random.random() < self.Pa_hcws: ## proportion of asymptomatic hcws
                                randomly_selected_list[1].symptom_state = 1 ## 1 means asymptomatic,
                                randomly_selected_list[1].incubationtime = 0
                            else:
                                incubation_realtime = abs(np.random.choice(self.inc_period, p=self.gamma_pdf))
                                incubation_simtime = int(incubation_realtime * self.num_steps_per_day)
                                randomly_selected_list[1].incubationtime = incubation_simtime
                                randomly_selected_list[1].symptom_state = 2 ## 2 means symptomatic

                ## check if index 1 hcw is positive and index 0 is susceptible            
                elif (randomly_selected_list[1].state == State.EXPOSED or randomly_selected_list[1].state == State.ASYMPTOMATIC) and randomly_selected_list[0].state == State.SUSCEPTIBLE:
                    if randomly_selected_list[1].time_of_infection != 0:
                        infec_time = (self.schedule.time - randomly_selected_list[1].time_of_infection)/self.num_steps_per_day
                        if randomly_selected_list[1].symptom_state == 1: ### is asymptomatic
                            beta = r0*r1*self.Ra * weibull_min.pdf(infec_time, self.shape, loc=0, scale=self.scale)
                        elif randomly_selected_list[1].symptom_state == 2: #### randomly_selected_list[0] is symptomatic
                            beta = r0*r1*self.Rs * weibull_min.pdf(infec_time, self.shape, loc=0, scale=self.scale)
                        b_trial = self.get_bernoulli_trial(beta/self.lar_eig_val)
                        if b_trial == 1:
                            self.Time_btw_trans_and_sym_onset.loc[len(self.Time_btw_trans_and_sym_onset),:] = self.schedule.time, randomly_selected_list[1].incubationtime, randomly_selected_list[1].time_of_infection,randomly_selected_list[1].state
                            randomly_selected_list[0].state = State.EXPOSED
                            randomly_selected_list[0].time_of_infection = self.schedule.time
                            randomly_selected_list[0].transmission_type = 2 ## hospital tranmision
                            if randomly_selected_list[1].unique_id < 1000: ## this is physician
                                if randomly_selected_list[0].unique_id < 1000: ## this is physician
                                    self.hc_hc_transmission += 1
                                elif randomly_selected_list[0].unique_id >= 1000 and randomly_selected_list[0].unique_id < 5000: ## this is nurse
                                    self.hc_n_transmission += 1
                            elif randomly_selected_list[1].unique_id >= 1000 and randomly_selected_list[1].unique_id < 5000: ## this is nurse
                                if randomly_selected_list[0].unique_id < 1000: ## this is physician
                                    self.n_hc_transmission += 1
                                elif randomly_selected_list[0].unique_id >= 1000 and randomly_selected_list[0].unique_id < 5000: ## this is nurse
                                    self.n_n_transmission += 1
                            self.daily_transmissions += 1
                            self.daily_transmissions_hcw += 1
                            self.total_transmissions += 1
                            if randomly_selected_list[1].state == State.EXPOSED:
                                self.trans_counts_from_pre_symptomatic += 1
                                randomly_selected_list[1].symp_secon_trans_count += 1
                            elif randomly_selected_list[1].state == State.ASYMPTOMATIC:
                                self.trans_counts_from_asymptomatic += 1
                                randomly_selected_list[1].asymp_secon_trans_count += 1
                            randomly_selected_list[1].trans_count_to_hcw += 1 ## transmission was from hcw to hcw, so it is counted in trans_count_to_hcw
                            if randomly_selected_list[0].ward < 9:
                                self.total_transmissions_covid_wards += 1
                            elif randomly_selected_list[0].ward >= 9:
                                self.total_transmissions_non_covid_wards += 1                        
                            if random.random() < self.Pa_hcws: ## proportion of asymptomatic individuals
                                randomly_selected_list[0].symptom_state = 1 ## 1 means asymptomatic,
                                randomly_selected_list[0].incubationtime = 0
                            else:
                               incubation_realtime = abs(np.random.choice(self.inc_period, p=self.gamma_pdf))
                               incubation_simtime = int(incubation_realtime * self.num_steps_per_day)
                               randomly_selected_list[0].incubationtime = incubation_simtime 
                               randomly_selected_list[0].symptom_state = 2 ## 2 means symptomatic, 0 means not in both

                ### for contact tracing records of individuals meeting with each other (physicians and nurses)
                match_found_0 = False
                for idx, val in enumerate(randomly_selected_list[0].contact_tracing):
                    if val[0] == randomly_selected_list[1].unique_id:
                        if self.schedule.time  > val[1]:
                            val[1] = self.schedule.time
                            match_found_0 = True
                        else:
                            match_found_0 = True
                if not match_found_0:
                    randomly_selected_list[0].contact_tracing.append([randomly_selected_list[1].unique_id,self.schedule.time])
                
                match_found_1 = False
                for idx, val in enumerate(randomly_selected_list[1].contact_tracing):
                    if val[0] == randomly_selected_list[0].unique_id:
                        if self.schedule.time  > val[1]:
                            val[1] = self.schedule.time
                            match_found_1 = True
                        else:
                            match_found_1 = True
                if not match_found_1:
                    randomly_selected_list[1].contact_tracing.append([randomly_selected_list[0].unique_id,self.schedule.time])

            else:
                pass



    def HCW_community_transmission(self):        
        '''
        This method simulates if a hcw gets the COVID-19 in the community
        We call this method once every day (before the start of each day)
        and then see how many workers get transmission in the community every day
        a hcw can become either exposed or asymptomatic in the community
        '''
        community_perc = self.df_community_prev['prop_prev_HCW'].loc[int(self.schedule.time/self.num_steps_per_day)]
        hcws = np.concatenate([self.schedule.agents_by_type[Physician],self.schedule.agents_by_type[Nurse]]) ## list of active nurses and physicians, without considering duty shift
        for hcw in hcws:
            if hcw.state == State.SUSCEPTIBLE and random.random() < community_perc: ## check if HCW state is susceptible and randomly select the hcw
                if random.random() < self.Pa_hcws: ## proportion of asymptomatic hcws
                    hcw.state = State.ASYMPTOMATIC
                    hcw.incubationtime = 0 
                    hcw.symptom_state = 1 ## 1 means asymptomatic.
                else:
                    hcw.state = State.EXPOSED 
                    incubation_realtime = abs(np.random.choice(self.inc_period, p=self.gamma_pdf))
                    incubation_simtime = int(incubation_realtime * self.num_steps_per_day)
                    hcw.incubationtime = incubation_simtime
                    hcw.symptom_state = 2 ## 2 means symptomatic, 0 means not in both 
                hcw.time_of_infection = self.schedule.time ## for simplicity, we just took the time at which we call this method as time of infection
                hcw.transmission_type = 1 ## 1 stands for community transmission
                self.total_hcw_community_transmissions += 1

    def contact_tracing_perf_sens(self):
        '''
        This method is for testing contacts of a symptomatic HCW assuming perfect test sensitivity
        all contacts are tested at the moment the index hcw becomes symptomatic
        if a hcw contact is detected positive, we quarantine the hcw at home and add a replacement hcw
        if a patient contact is positive, we move the patient to covid wards.
        '''
        total_contacts = 0
        positive_contacts = 0
        hcws = np.concatenate([self.schedule.agents_by_type[Physician],self.schedule.agents_by_type[Nurse]])
        for hcw in hcws:
#            if hcw.trace_time > 0: 
#                hcw.trace_time = hcw.trace_time - 1 ## to count down trace_time every step, This is only required if 2 rounds of contact tracing are required
            if hcw.state == State.SEVERE or hcw.state == State.MILD: ## check if HCW is symptomatic (mild or severe)
                if hcw.contact_tracing and hcw.trace_time == 0:
                    total_contacts = 0
                    positive_contacts = 0
                    total_contacts_traced = 0
                    sympt_patient_contacts = 0
                    sympt_hcw_contacts = 0

                    for idx, val in enumerate(hcw.contact_tracing):
                        total_contacts += 1
                        ### search first in the HCWs list
                        for hcw1 in hcws:
                            if hcw1.unique_id == val[0]: ## check if id of hcws match with the individuals contacts
                                total_contacts_traced += 1
                                if hcw1.state == State.MILD or hcw1.state == State.SEVERE:
                                    sympt_hcw_contacts += 1
                                if hcw1.state == State.EXPOSED:
                                    positive_contacts += 1
                                    if hcw1.symptom_state == 2: ## checking if HCW was following symptomatic route
                                        if random.random() < self.Ps: ## proportion of physicians which develop severe infections
                                            hcw1.state = State.SEVERE ### we change the state of positive contacts. It is required in the recovered class to first acquire Severe or Mild symptoms. 
                                        else:
                                            hcw1.state = State.MILD
                                        hcw1.time_outofwork = int(self.quarantine_period) ## time period for quarantine
                                        hcw1.incubationtime = None ## set incubation time to None so that same hcw will not be considered in this loop in the next step.
                                        hcw1.replacement_added = True
                                        #### replacement susceptible HCW is added with similar ward, shift, and protective gear details
                                        if hcw1.unique_id < 1000: ## it is physician
                                            physician = Physician(self.phyuniqueID, self, 0, hcw1.ward, hcw1.pat_attend_counter, hcw1.shift, 0, hcw1.protective_gear, None, 0, 0, 0, None, False, 0, False, 0, 0, 0, 0, None, 0)
                                            self.schedule.add(physician)
                                            self.phyuniqueID +=1
                                            self.num_replace_hcw += 1
                                        elif hcw1.unique_id >= 1000 and hcw1.unique_id < 5000: ## it is a nurse
                                            nurse = Nurse(self.nuruniqueID, self, 0, hcw1.ward, hcw1.pat_attend_counter, hcw1.shift, 0, hcw1.protective_gear, None, 0, 0, 0,None, False, 0, False, 0, 0, 0, 0, None, 0)
                                            self.schedule.add(nurse)
                                            self.nuruniqueID +=1
                                            self.num_replace_hcw += 1
                                    
                                if hcw1.state == State.ASYMPTOMATIC:
                                    if hcw1.time_of_infection != 0:
                                        positive_contacts += 1
                                        if (self.schedule.time - hcw1.time_of_infection) < self.quarantine_period:
                                            hcw1.time_outofwork = int(self.quarantine_period)
                                            hcw1.replacement_added = True
                                            #### replacement susceptible HCW is added with similar ward, shift, and protective gear details
                                            if hcw1.unique_id < 1000: ## it is physician
                                                physician = Physician(self.phyuniqueID, self, 0, hcw1.ward, hcw1.pat_attend_counter, hcw1.shift, 0, hcw1.protective_gear, None, 0, 0, 0, None, False, 0, False, 0, 0, 0, 0, None, 0)
                                                self.schedule.add(physician)
                                                self.phyuniqueID +=1
                                                self.num_replace_hcw += 1
                                            elif hcw1.unique_id >= 1000 and hcw1.unique_id < 5000: ## it is a nurse
                                                nurse = Nurse(self.nuruniqueID, self, 0, hcw1.ward, hcw1.pat_attend_counter, hcw1.shift, 0, hcw1.protective_gear, None, 0, 0, 0,None, False, 0, False, 0, 0, 0, 0, None, 0)
                                                self.schedule.add(nurse)
                                                self.nuruniqueID +=1
                                                self.num_replace_hcw += 1
                    
                        ### search now in the patients list, If positive patient, move it to covid wards
                        for pat in self.schedule.agents_by_type[Patient]:
                            if pat.unique_id == val[0] and val[0] >= 5000: ## check if id of patients match with the individuals contacts
                                total_contacts_traced += 1
                                if pat.state == State.MILD or pat.state == State.SEVERE:
                                    sympt_patient_contacts += 1                                
                                if pat.state == State.EXPOSED or pat.state == State.ASYMPTOMATIC:
                                    positive_contacts += 1
                                    if pat.ward >= 9:
                                        pat.movementflag = True ## When this is True, patient will be moved to corona wards as soon as possible


                    trace_time = self.schedule.time / self.num_steps_per_day
                    hcw.contact_tracing.clear()                        
                    self.contact_tracing_counts.loc[len(self.contact_tracing_counts), :] = total_contacts,total_contacts_traced,positive_contacts, sympt_patient_contacts, trace_time, 1, hcw.unique_id, hcw.time_of_infection/self.num_steps_per_day, hcw.ward, sympt_hcw_contacts, 0, 0


    def contact_tracing_5day_testing_and_ppe(self):
        '''
        contact tracing method where we test contacts on 5th day (from the moment contact was made).
        when contacts are traced, hcws contacts wear ppe until day 5 (testing moment)and on day tested, if positive, then quarantine depending on quarantine parameter
        for patients, all patient contacts are put in isolation and when hcw visit them, they use ppe (a reduction in the tranmission parameter) and if tested postive on day 5, patient moved to covid ward. if not, patient is removed from isolation restriction.
        '''
        total_contacts = 0
        positive_contacts = 0
        hcws = np.concatenate([self.schedule.agents_by_type[Physician],self.schedule.agents_by_type[Nurse]])
        for hcw in hcws:
#            if hcw.trace_time > 0: ## this is required  
#                hcw.trace_time = hcw.trace_time - 1 ## to count down trace_time every step   
            if hcw.state == State.SEVERE or hcw.state == State.MILD: ## check if HCW is symptomatic (mild or severe)
                if hcw.contact_tracing and hcw.trace_time == 0:
                    total_contacts = 0
                    positive_contacts = 0
                    total_contacts_traced = 0
                    sympt_patient_contacts = 0
                    sympt_hcw_contacts = 0
                    hcws_put_on_ppe = 0
                    patients_put_in_isolation = 0
                    for val in hcw.contact_tracing[:]:
                        remove_flag = False
                        total_contacts += 1
                        ### search first in the HCWs list
                        for hcw1 in hcws:
                            if hcw1.unique_id == val[0]: ## check if id of hcws match with the individuals contacts
                                if hcw1.state == State.MILD or hcw1.state == State.SEVERE:
                                    sympt_hcw_contacts += 1
                                    ## there might be few hcws which were exposed on symptom onset and were asked to wear ppe, but later become symptomatic. We need to change ppe for those hcws. 
                                    if hcw1.ward >= 9:
                                        hcw1.protective_gear = params.ppe_noncovid_wards
                                    if hcw1.ward < 9:
                                        hcw1.protective_gear = params.ppe_covid_wards
                                    hcw1.hcw_on_ppe_cont_tracing = 0
                                    if (val in hcw.contact_tracing):
                                        hcw.contact_tracing.remove(val)

                                ### see if contact time is >= than the specified testing time    
                                if (self.schedule.time - val[1])>=params.testing_day_simtime:
                                    total_contacts_traced += 1 ## these are the contacts which are actually tested
                                    if (hcw1.state == State.EXPOSED or hcw1.state == State.ASYMPTOMATIC):
                                        infec_time_in_steps = int((self.schedule.time - hcw1.time_of_infection)/(self.num_steps_per_day/24)) ## this is per hour
                                        test_prob = self.test_sensitivity['probability of detection'].loc[infec_time_in_steps]                                        
                                        if random.random() < test_prob:                                            
                                            if hcw1.state == State.EXPOSED:
                                                if hcw1.symptom_state == 2: ## checking if HCW was following symptomatic route
                                                    if random.random() < self.Ps: ## proportion of physicians which develop severe infections
                                                        hcw1.state = State.SEVERE ### we change the state of positive contacts. It is required in the recovered class to first acquire Severe or Mild symptoms.  
                                                    else:
                                                        hcw1.state = State.MILD
                                            hcw1.time_outofwork = int(self.quarantine_period)
                                            hcw1.incubationtime = None ## set incubation time to None so that same physcician will not be considered in this loop in the next step.
                                            hcw1.replacement_added = True
                                            positive_contacts += 1
                                            ## check if hcw was asked to wear ppe in contact tracing
                                            ppe = 0
                                            if hcw1.hcw_on_ppe_cont_tracing == 1: ## hcw was asked to wear ppe
                                                if hcw1.ward >= 9:
                                                    ppe = 0
                                                else:
                                                    ppe = 1
                                            elif hcw1.hcw_on_ppe_cont_tracing == 0: ## hcw was asked not asked to wear ppe
                                                ppe = hcw1.protective_gear
                                            #### replacement susceptible HCW is added with similar ward, shift, and protective gear details
                                            if hcw1.unique_id < 1000: ## it is physician
                                                physician = Physician(self.phyuniqueID, self, 0, hcw1.ward, hcw1.pat_attend_counter, hcw1.shift, 0, ppe, None, 0, 0, 0, None, False, 0, False, 0, 0, 0, 0, None, 0)
                                                self.schedule.add(physician)
                                                self.phyuniqueID +=1
                                                self.num_replace_hcw += 1
                                            elif hcw1.unique_id >= 1000 and hcw1.unique_id < 5000: ## it is a nurse
                                                nurse = Nurse(self.nuruniqueID, self, 0, hcw1.ward, hcw1.pat_attend_counter, hcw1.shift, 0, ppe, None, 0, 0, 0,None, False, 0, False, 0, 0, 0, 0, None, 0)
                                                self.schedule.add(nurse)
                                                self.nuruniqueID +=1
                                                self.num_replace_hcw += 1
                                    ## remove ppe from all non covid hcw contacts (susceptibles, exposed, asympto)
                                    if hcw1.ward >= 9:
                                        hcw1.protective_gear = params.ppe_noncovid_wards
                                    if hcw1.ward < 9:
                                        hcw1.protective_gear = params.ppe_covid_wards
                                    hcw1.hcw_on_ppe_cont_tracing = 0
                                    ### remove this contact from the contact tracing list so that it will not be counted again
                                    if (val in hcw.contact_tracing):
                                        hcw.contact_tracing.remove(val)
                                 
                                if (self.schedule.time - val[1])<params.testing_day_simtime and hcw1.hcw_on_ppe_cont_tracing == 0 and (hcw1.state == State.SUSCEPTIBLE or hcw1.state == State.EXPOSED or hcw1.state == State.ASYMPTOMATIC or hcw1.state == State.RECOVERED):#(hcw1.state != State.MILD or hcw1.state != State.SEVERE): ## means testing time not yet arrived, put hcw contacts on ppe
                                    hcw1.protective_gear = 1 ## put all hcw contact on ppe. This will be changed when they are tested on day 5. 
                                    hcw1.hcw_on_ppe_cont_tracing = 1 ## 1 mean hcw is asked to wear ppe. 
                                    hcws_put_on_ppe += 1
                                break
                        ### search now in the patients list
                        for pat in self.schedule.agents_by_type[Patient]:
                            if pat.unique_id == val[0] and val[0] >= 5000: ## check if id of patients match with the individuals contacts
                                if pat.state == State.MILD or pat.state == State.SEVERE:
                                    sympt_patient_contacts += 1
                                    pat.patient_isolated = 0 ## remove patient isolation if this was changed before. these patients are moved anyway to covid wards
                                    if (val in hcw.contact_tracing):
                                        hcw.contact_tracing.remove(val)

                                if (self.schedule.time - val[1])>=params.testing_day_simtime:
                                    total_contacts_traced += 1
                                    pat.patient_isolated = 0 ## remove patient isolation if this was changed before.
                                    if pat.state == State.EXPOSED or pat.state == State.ASYMPTOMATIC:
                                        infec_time_in_steps = int((self.schedule.time - pat.time_of_infection)/(self.num_steps_per_day/24))
                                        test_prob = self.test_sensitivity['probability of detection'].loc[infec_time_in_steps]
                                        if random.random() < test_prob:
                                            positive_contacts += 1                                            
                                            if pat.ward >= 9:
                                                pat.movementflag = True ## When this is True, patient will be moved to corona wards as soon as possible
                                    if (val in hcw.contact_tracing):
                                        hcw.contact_tracing.remove(val)
                                
                                if (self.schedule.time - val[1])<params.testing_day_simtime and int(pat.ward) >= 9 and pat.patient_isolated == 0 and (pat.state == State.SUSCEPTIBLE or pat.state == State.EXPOSED or pat.state == State.ASYMPTOMATIC or pat.state == State.RECOVERED):#(pat.state != State.MILD or pat.state != State.SEVERE):## means testing time not yet arrived, put patient contacts on isolation, if we isolated patients in the covid wards also, it will reduce the tranmission even further. there hcw wear ppe + reduction due to patient in isolation.
                                    pat.patient_isolated = 1
                                    patients_put_in_isolation += 1
                                break
                        ## As some patients might be discharged from the hospital and those contact detail will not be deleted automatically in the above statements. 
                        ## to do that manually, delete all contacts older than testing moment + 2 days 
                        if (self.schedule.time - val[1]) > (params.testing_day_simtime + 2*self.num_steps_per_day):
                            if (val in hcw.contact_tracing):
                                hcw.contact_tracing.remove(val)
                    ## Writing data of contact tracing results of symptomatic hcw 
                    if hcw.contact_tracing_output[0] == 0: ## default is 0 and means that no contacts have been counted before.
                        hcw.contact_tracing_output[0] = total_contacts
                    hcw.contact_tracing_output[1] += total_contacts_traced                        
                    hcw.contact_tracing_output[2] += positive_contacts
                    hcw.contact_tracing_output[3] += sympt_patient_contacts                    
                    if hcw.contact_tracing_output[4] == 0: #contact_tracing_time
                        hcw.contact_tracing_output[4] = self.schedule.time / self.num_steps_per_day
                    if hcw.contact_tracing_output[5] == 0: # tracing_round
                        hcw.contact_tracing_output[5] = 1
                    if hcw.contact_tracing_output[6] == 0: # hcw_id
                        hcw.contact_tracing_output[6] = hcw.unique_id
                    if hcw.contact_tracing_output[7] == 0: #hcw_time_of_infection
                        hcw.contact_tracing_output[7] = hcw.time_of_infection/self.num_steps_per_day
                    if hcw.contact_tracing_output[8] == 0: # hcw_current_ward
                        hcw.contact_tracing_output[8] = hcw.ward
                    hcw.contact_tracing_output[9] += sympt_hcw_contacts
                    hcw.contact_tracing_output[10] += hcws_put_on_ppe
                    hcw.contact_tracing_output[11] += patients_put_in_isolation

    def screening(self):
        '''
        This method will screen a specified proportion of hcws periodically after every few days (as specified 3 days or 7 days)
        only exposed and asymptomatic HCWs will be screened.
        time depedant test sensitivity is assumed here
        Symptomatic HCWs will automatically be put out of work when they become infected.
        '''
        total_counts = 0
        positive_counts = 0
        hcws = np.concatenate([self.schedule.agents_by_type[Physician],self.schedule.agents_by_type[Nurse]]) ## list of all hcws
        for hcw in hcws:
            if random.random() < params.scr_perc and hcw.time_outofwork == 0:
                total_counts += 1
                if hcw.state == State.EXPOSED:
                    #### test sensitivity
                    infec_time_in_steps = int((self.schedule.time - hcw.time_of_infection)/(self.num_steps_per_day/24)) ## this is per hour
                    test_prob = self.test_sensitivity['probability of detection'].loc[infec_time_in_steps]
                    if random.random() < test_prob:
                        positive_counts += 1
                        if hcw.symptom_state == 2: ## checking if HCW was following symptomatic route
                            if random.random() < self.Ps: ## proportion of hcws that develop severe infections
                                hcw.state = State.SEVERE ### not sure if we should change the state of positive contacts. But it is required in the recovered class to first acquire Severe or Mild symptoms. 
                            else:
                                hcw.state = State.MILD
                            hcw.time_outofwork = int(self.quarantine_period)
                            hcw.incubationtime = None ## set incubation time to None so that same hcw will not be considered in this loop in the next step.
                            hcw.replacement_added = True
                            #### replacement susceptible HCW is added with similar ward, shift, and protective gear details
                            if hcw.unique_id < 1000: ## it is physician
                                physician = Physician(self.phyuniqueID, self, 0, hcw.ward, hcw.pat_attend_counter, hcw.shift, 0, hcw.protective_gear, None, 0, 0, 0, None, False, 0, False, 0, 0, 0, 0, None, 0)
                                self.schedule.add(physician)
                                self.phyuniqueID +=1
                                self.num_replace_hcw += 1
                            elif hcw.unique_id >= 1000 and hcw.unique_id < 5000: ## it is a nurse
                                nurse = Nurse(self.nuruniqueID, self, 0, hcw.ward, hcw.pat_attend_counter, hcw.shift, 0, hcw.protective_gear, None, 0, 0, 0,None, False, 0, False, 0, 0, 0, 0, None, 0)
                                self.schedule.add(nurse)
                                self.nuruniqueID +=1
                                self.num_replace_hcw += 1

                elif hcw.state == State.ASYMPTOMATIC:
                    if hcw.time_of_infection != 0:
                        #### test sensitivity                        
                        infec_time_in_steps = int((self.schedule.time - hcw.time_of_infection)/(self.num_steps_per_day/24))
                        test_prob = self.test_sensitivity['probability of detection'].loc[infec_time_in_steps]
                        if random.random() < test_prob:
                            positive_counts += 1
                            if (self.schedule.time - hcw.time_of_infection) < self.quarantine_period:
                                hcw.time_outofwork = int(self.quarantine_period)
                                hcw.replacement_added = True
                                #### replacement susceptible HCW is added with similar ward, shift, and protective gear details
                                if hcw.unique_id < 1000: ## it is physician
                                    physician = Physician(self.phyuniqueID, self, 0, hcw.ward, hcw.pat_attend_counter, hcw.shift, 0, hcw.protective_gear, None, 0, 0, 0, None, False, 0, False, 0, 0, 0, 0, None, 0)
                                    self.schedule.add(physician)
                                    self.phyuniqueID +=1
                                    self.num_replace_hcw += 1
                                elif hcw.unique_id >= 1000 and hcw.unique_id < 5000: ## it is a nurse
                                    nurse = Nurse(self.nuruniqueID, self, 0, hcw.ward, hcw.pat_attend_counter, hcw.shift, 0, hcw.protective_gear, None, 0, 0, 0,None, False, 0, False, 0, 0, 0, 0, None, 0)
                                    self.schedule.add(nurse)
                                    self.nuruniqueID +=1
                                    self.num_replace_hcw += 1
        #### write screening related data to dataframe 
        self.screening_counts.loc[len(self.screening_counts), :] = int(self.schedule.time/self.num_steps_per_day), total_counts,positive_counts

    def screening_perf_sens(self):
        '''
        This method will screen a specified proportion of hcws periodically after every few days (as specified 3 days or 7 days)
        Perfect test sensitivity is assumed here
        only exposed and asymptomatic HCWs will be screened.
        Symptomatic HCWs will automatically be put out of work when they become infected.
        '''
        total_counts = 0
        positive_counts = 0
        hcws = np.concatenate([self.schedule.agents_by_type[Physician],self.schedule.agents_by_type[Nurse]]) ## list of all hcws
        for hcw in hcws:
            if random.random() < params.scr_perc and hcw.time_outofwork == 0:
                total_counts += 1
                if hcw.state == State.EXPOSED:
                    positive_counts += 1
                    if hcw.symptom_state == 2: ## checking if HCW was following symptomatic route
                        if random.random() < self.Ps: ## proportion of hcws that develop severe infections
                            hcw.state = State.SEVERE ### not sure if we should change the state of positive contacts. But it is required in the recovered class to first acquire Severe or Mild symptoms. 
                        else:
                            hcw.state = State.MILD
                        hcw.time_outofwork = int(self.quarantine_period)
                        hcw.incubationtime = None ## set incubation time to None so that same hcw will not be considered in this loop in the next step.
                        hcw.replacement_added = True
                        #### replacement susceptible HCW is added with similar ward, shift, and protective gear details
                        if hcw.unique_id < 1000: ## it is physician
                            physician = Physician(self.phyuniqueID, self, 0, hcw.ward, hcw.pat_attend_counter, hcw.shift, 0, hcw.protective_gear, None, 0, 0, 0, None, False, 0, False, 0, 0, 0, 0, None, 0)
                            self.schedule.add(physician)
                            self.phyuniqueID +=1
                            self.num_replace_hcw += 1
                        elif hcw.unique_id >= 1000 and hcw.unique_id < 5000: ## it is a nurse
                            nurse = Nurse(self.nuruniqueID, self, 0, hcw.ward, hcw.pat_attend_counter, hcw.shift, 0, hcw.protective_gear, None, 0, 0, 0,None, False, 0, False, 0, 0, 0, 0, None, 0)
                            self.schedule.add(nurse)
                            self.nuruniqueID +=1
                            self.num_replace_hcw += 1

                elif hcw.state == State.ASYMPTOMATIC:
                    if hcw.time_of_infection != 0:
                        positive_counts += 1
                        if (self.schedule.time - hcw.time_of_infection) < self.quarantine_period:
                            hcw.time_outofwork = int(self.quarantine_period)
                            hcw.replacement_added = True
                            #### replacement susceptible HCW is added with similar ward, shift, and protective gear details
                            if hcw.unique_id < 1000: ## it is physician
                                physician = Physician(self.phyuniqueID, self, 0, hcw.ward, hcw.pat_attend_counter, hcw.shift, 0, hcw.protective_gear, None, 0, 0, 0, None, False, 0, False, 0, 0, 0, 0, None, 0)
                                self.schedule.add(physician)
                                self.phyuniqueID +=1
                                self.num_replace_hcw += 1
                            elif hcw.unique_id >= 1000 and hcw.unique_id < 5000: ## it is a nurse
                                nurse = Nurse(self.nuruniqueID, self, 0, hcw.ward, hcw.pat_attend_counter, hcw.shift, 0, hcw.protective_gear, None, 0, 0, 0,None, False, 0, False, 0, 0, 0, 0, None, 0)
                                self.schedule.add(nurse)
                                self.nuruniqueID +=1
                                self.num_replace_hcw += 1
        #### write screening related data to dataframe 
        self.screening_counts.loc[len(self.screening_counts), :] = int(self.schedule.time/self.num_steps_per_day), total_counts,positive_counts


    def remove_old_contacts(self):
        '''
        ## remove contacts older than specified time period (params.cont_period_simtime)
        '''
        hcws_list = np.concatenate([self.schedule.agents_by_type[Physician],self.schedule.agents_by_type[Nurse]])
        for hcw in hcws_list:
            if hcw.contact_tracing and hcw.time_outofwork == 0 and hcw.contacts_traced_already is False:
                to_remove=[i for i, val in enumerate(hcw.contact_tracing) if (self.schedule.time - val[1])>params.cont_period_simtime] ## this returns indexes of elements to be removed
                for index in reversed(to_remove): # start at the end to avoid recomputing offsets
                    del hcw.contact_tracing[index] ## remove elements stored at index



    def HCW_ward_change(self):
        '''
        This method will randomly select a proportion of HCWs and for each pair, wards will be swapped.
        first a HCW is randomly selected from a ward
        then another hcw is randomly selected from another ward
        and wards are swapped between each other
        we do this separately for nurses and physicians
        '''
        ### for physciains swap
        for phy in self.schedule.agents_by_type[Physician]:
            if random.random() <  params.prop_phy_wardchange and phy.time_outofwork == 0:            
                current_phy_ward = phy.ward
                current_phy_shift = phy.shift
                random_ward = random.choice(list(value for value in range(1,len(self.room_num)+1) if value != current_phy_ward)) ## select a random ward other than current ward
                phy_list = self.physician_list_by_ward(random_ward) ## list of all physicians in a ward who are allowed to work (no symptomatic physicians)
                swapped_phy = random.choice(phy_list) ## select a random physician from the physician ward list
                swapped_phy_ward = swapped_phy.ward
                swapped_phy_shift = swapped_phy.shift
                ### now swap wards of both physicians
                phy.ward = swapped_phy_ward
                phy.shift = swapped_phy_shift
                swapped_phy.ward = current_phy_ward
                swapped_phy.shift = current_phy_shift
                if phy.hcw_on_ppe_cont_tracing == 1: ## this hcw was asked to wear PPE in the contact tracing
                    pass ## do not change hcw current PPE as hcw was asked to wear ppe in contact tracing
                else:
                    if phy.ward >= 9:
                        phy.protective_gear = params.ppe_noncovid_wards
                    else:
                        phy.protective_gear = params.ppe_covid_wards
                if swapped_phy.hcw_on_ppe_cont_tracing == 1: ## this hcw was asked to wear PPE in the contact tracing
                    pass ## do not change hcw current PPE as hcw was asked to wear ppe in contact tracing
                else:
                    if swapped_phy.ward >= 9:
                        swapped_phy.protective_gear = params.ppe_noncovid_wards
                    else:
                        swapped_phy.protective_gear = params.ppe_covid_wards
#                
        ### for nurses swap
        for nur in self.schedule.agents_by_type[Nurse]:
            if random.random() <  params.prop_nur_wardchange:
                current_nur_ward = nur.ward
                current_nur_shift = nur.shift
                random_ward = random.choice(list(value for value in range(1,len(self.room_num)+1) if value != current_nur_ward)) ## select a random ward other than current ward
                nur_list = self.nurse_list_by_ward(random_ward) ## list of all nurses in a ward who are allowed to work (no symptomatic nurses)
                swapped_nur = random.choice(nur_list) ## select a random nurse from the nurse ward list
                swapped_nur_ward = swapped_nur.ward
                swapped_nur_shift = swapped_nur.shift
                ### now swap wards of both nurses
                nur.ward = swapped_nur_ward
                nur.shift = swapped_nur_shift
                swapped_nur.ward = current_nur_ward
                swapped_nur.shift = current_nur_shift
                if nur.hcw_on_ppe_cont_tracing == 1: ## this hcw was asked to wear PPE in the contact tracing 5 days testing
                    pass ## do not change hcw current PPE as hcw was asked to wear ppe in contact tracing
                else:
                    if nur.ward >= 9:
                        nur.protective_gear = params.ppe_noncovid_wards
                    else:
                        nur.protective_gear = params.ppe_covid_wards
#                    phy.protective_gear = swapped_phy_PPE
                if swapped_nur.hcw_on_ppe_cont_tracing == 1: ## this hcw was asked to wear PPE in the contact tracing 5 days testing
                    pass ## do not change hcw current PPE as hcw was asked to wear ppe in contact tracing
                else:
                    if swapped_nur.ward >= 9:
                        swapped_nur.protective_gear = params.ppe_noncovid_wards
                    else:
                        swapped_nur.protective_gear = params.ppe_covid_wards


    def patient_movements_in_corona_wards(self):
        '''
        This method moves detected positive patients to covid wards from non-covid wards
        '''
        for pat in self.schedule.agents_by_type[Patient]:
            ### first check if patient needs to be moved to corona icu or nonicu wards
            if pat.movementflag is True:
                current_room, current_ward = 0, 0
                ## check if patient is in normal iCU and positive or patient is severe, move the patient to COVID icu.
                if (pat.ward == 9 and (pat.state == State.EXPOSED or pat.state == State.MILD or pat.state == State.SEVERE or pat.state == State.ASYMPTOMATIC)) or (pat.ward >  9 and pat.state == State.SEVERE):
                    copy_available_rooms_corona_icu = self.available_rooms_corona_icu[:] ## copy list of avialable corona icu rooms
                    for idx, val in enumerate(copy_available_rooms_corona_icu):
                        ward_room_num = val.split('.') # split the string to get room and ward number
                        ward_room_num = [int(x) for x in ward_room_num] ## make ward_room_num list into integers
                        current_room = pat.room
                        current_ward = pat.ward                            
                        for i, j in enumerate(self.rooms_occupied):
                            if j[0] == current_ward and j[1] == current_room:
                                del self.rooms_occupied[i]
                                break
                        pat.ward = ward_room_num[0]
                        pat.room = ward_room_num[1]
                        self.available_rooms_corona_icu.remove(val)
                        self.rooms_occupied.append([pat.ward,pat.room])
                        pat.movementflag = False
                        num_room = str(str(current_ward)+"."+str(current_room))
                        self.available_rooms.append(num_room)
                        break
                    del copy_available_rooms_corona_icu[:]
                
                #### if patient is follwoing symptomatic route and not in regular ICU, then move to corona ward.
                if pat.movementflag is True and pat.ward > 9 and (pat.state == State.EXPOSED or pat.state == State.MILD or pat.state == State.SEVERE or pat.state == State.ASYMPTOMATIC):
                    copy_available_rooms_corona_nonicu = self.available_rooms_corona_nonicu[:]
                    for idx, val in enumerate(copy_available_rooms_corona_nonicu):
                        ward_room_num = val.split('.') # split the string to get room and ward number
                        ward_room_num = [int(x) for x in ward_room_num] ## make ward_room_num list into integers
                        current_room = pat.room
                        current_ward = pat.ward                            
                        for i, j in enumerate(self.rooms_occupied):
                            if j[0] == current_ward and j[1] == current_room:
                                del self.rooms_occupied[i]
                                break
                        pat.ward = ward_room_num[0]
                        pat.room = ward_room_num[1]
                        self.available_rooms_corona_nonicu.remove(val)
                        self.rooms_occupied.append([pat.ward,pat.room])
                        pat.movementflag = False
                        num_room = str(str(current_ward)+"."+str(current_room))
                        self.available_rooms.append(num_room)
                        break
                    del copy_available_rooms_corona_nonicu[:]

    def get_bernoulli_trial(self, p):
        '''
        Do a Bernoulli Trail given a probability
        '''
        return np.random.binomial(1, p) # when n = 1, random.binomial(n,p) is similar to bernoulli distribution, so we use n=1 here in the return method.

    def count_noncorona_patients(self):
        pat_count = 0
        for pat in self.schedule.agents_by_type[Patient]:
            if pat.ward >= 9: ### first 8 wards are corona related wards
                pat_count += 1
        return(pat_count)

    def count_corona_icu_patients(self):
        pat_count = 0
        for pat in self.schedule.agents_by_type[Patient]:
            if pat.ward < 5: ### first 8 wards are corona related wards
                pat_count += 1
        return(pat_count)

    def count_corona_nonicu_patients(self):
        pat_count = 0
        for pat in self.schedule.agents_by_type[Patient]:
            if pat.ward >= 5 and pat.ward < 9: ### first 8 wards are corona related wards
                pat_count += 1
        return(pat_count)

    def count_patient_by_state_hospital_transmission(self, state):
        count = 0
        for pat in self.schedule.agents_by_type[Patient]:
            if pat.transmission_type == 2 and pat.state.value == state:
                count += 1
        return(count)

    def count_physician_by_state_hospital_transmission(self, state): ## this includes all physcians who acquired COVID19 in the hospital. Those out of work are still included here
        count = 0
        for phy in self.schedule.agents_by_type[Physician]:
            if phy.transmission_type == 2 and phy.state.value == state:
                count += 1
        return(count)

    def count_nurse_by_state_hospital_transmission(self, state): ## this includes all nurses who acquired COVID19 in the hospital. Those out of work are still included here
        count = 0
        for nur in self.schedule.agents_by_type[Nurse]:
            if nur.transmission_type == 2 and nur.state.value == state:
                count += 1
        return(count)

    def count_infected_hcw(self): ## this includes all nurses who acquired COVID19 in the hospital. Those out of work are still included here
        count = 0
        hcws_list = np.concatenate([self.schedule.agents_by_type[Physician],self.schedule.agents_by_type[Nurse]])
        for hcw in hcws_list:
            if hcw.transmission_type == 2 and (hcw.state == State.EXPOSED or hcw.state == State.SEVERE or hcw.state == State.MILD or hcw.state == State.ASYMPTOMATIC):
                count += 1
        return(count)


    def count_absent_hcws(self): ## count based on time out of work
        count = 0
        hcws_list = np.concatenate([self.schedule.agents_by_type[Physician],self.schedule.agents_by_type[Nurse]])
        for hcw in hcws_list:
            if hcw.time_outofwork > 0:
                count += 1
        return(count)

    def count_patient_by_state(self, state):
        count = 0
        for pat in self.schedule.agents_by_type[Patient]:
            if pat.state.value == state:
                count += 1
        return(count)

    def count_physician_by_state(self, state): ## only count HCWs which are active by looking at timeoutofwork == 0, so there should be 0 mild and infected HCWs in the output
        count = 0
        for phy in self.schedule.agents_by_type[Physician]:
            if phy.state.value == state:
                count += 1
        return(count)

    def count_nurse_by_state(self, state): ## only count HCWs which are active by looking at timeoutofwork == 0, so there should be 0 mild and infected HCWs in the output
        count = 0
        for nur in self.schedule.agents_by_type[Nurse]:
            if nur.state.value == state:
                count += 1
        return(count)

    def count_active_physician_by_state(self, state): ## only count HCWs which are active by looking at timeoutofwork == 0, so there should be 0 mild and infected HCWs in the output
        count = 0
        for phy in self.schedule.agents_by_type[Physician]:
            if phy.time_outofwork == 0 and phy.state.value == state:
                count += 1
        return(count)

    def count_active_nurse_by_state(self, state): ## only count HCWs which are active by looking at timeoutofwork == 0, so there should be 0 mild and infected HCWs in the output
        count = 0
        for nur in self.schedule.agents_by_type[Nurse]:
            if nur.time_outofwork == 0 and nur.state.value == state:
                count += 1
        return(count)

    def count_patient_per_ward(self, ward):
        pat_count = 0
        for pat in self.schedule.agents_by_type[Patient]:
            if pat.ward == ward:
                pat_count += 1
        return(pat_count)

    def count_covid_positive_patients_by_ward(self, ward):
        patient_count = 0
        for pat in self.schedule.agents_by_type[Patient]:
            if int(pat.ward) == ward and pat.symptom_state == 2: ### only count exposed patients which will follow symptomatic route. Asymptomatic exposed and asymtopmatic patients are excluded.
                if (pat.state == State.EXPOSED or pat.state == State.MILD or pat.state == State.SEVERE):
                    patient_count += 1
        return(patient_count)

    def count_infected_colonized_in_hosp_by_ward(self, ward): # this counts colonized and infected who became colonized during hospital stay
        count = 0
        for pat in self.schedule.agents_by_type[Patient]:
            if int(pat.ward) == ward:
                if (pat.state == State.INFECTED and pat.prev_colonization_state == 4) or (pat.state == State.COLONIZEDINHOSP):
                    count += 1
        return(count)

    def patient_ids_by_ward(self,ward):
        id_list = []
        for pat in self.schedule.agents_by_type[Patient]:
            if int(pat.ward) == ward:
                id_list.append(pat.unique_id)
        return(id_list)

    def physician_list_by_ward_and_current_shift(self,ward): ## only physicians in a ward which are active and on current shift by looking at phy.shift
        ward_list = []
        for phy in self.schedule.agents_by_type[Physician]:
            if phy.ward == ward and phy.shift == self.shift_tracker and phy.time_outofwork == 0:
                ward_list.append(phy)
        return(ward_list)

    def physician_list_by_ward_and_shift(self,ward, shift): ## only physicians in a ward which are active and on current shift by looking at phy.shift
        ward_list = []
        for phy in self.schedule.agents_by_type[Physician]:
            if phy.ward == ward and phy.shift == shift and phy.time_outofwork == 0:
                ward_list.append(phy)
        return(ward_list)


    def physician_list_by_ward(self,ward): ## all physicians in a ward which are active by looking at timeoutofwork == 0
        ward_list = []
        for phy in self.schedule.agents_by_type[Physician]:
            if phy.ward == ward and phy.time_outofwork == 0:
                ward_list.append(phy)
        return(ward_list)


    def nurse_list_by_ward_and_current_shift(self,ward): ## only nurses in a ward which are active and on current shift by looking at phy.shift
        ward_list = []
        for nur in self.schedule.agents_by_type[Nurse]:
            if nur.ward == ward and nur.shift == self.shift_tracker and nur.time_outofwork == 0:
                ward_list.append(nur)
        return(ward_list)

    def nurse_list_by_ward_and_shift(self,ward, shift): ## only nurses in a ward which are active and on current shift by looking at phy.shift
        ward_list = []
        for nur in self.schedule.agents_by_type[Nurse]:
            if nur.ward == ward and nur.shift == shift and nur.time_outofwork == 0:
                ward_list.append(nur)
        return(ward_list)    

    def nurse_list_by_ward(self,ward): ## all nurses in a ward which are active by looking at timeoutofwork == 0
        ward_list = []
        for nur in self.schedule.agents_by_type[Nurse]:
            if nur.ward == ward and nur.time_outofwork == 0:
                ward_list.append(nur)
        return(ward_list)

    def track_duty_shift(self):
        if self.schedule.time%(self.num_steps_per_day/self.shifts_per_day) == 0:
            self.shift_tracker += 1
        if self.shift_tracker > self.shifts_per_day:
                self.shift_tracker = 1


    def calculate_largest_eig_val(self):
        M = np.array([[params.C_nn, params.C_np, params.C_nhc],\
                      [params.C_pn, 0, params.C_phc],\
                      [params.C_hcn, params.C_hcp, params.C_hchc]])
        eigvals, eigvecs = la.eig(M)
        eigvals = eigvals.real
        largest_eig_val = np.max(eigvals)
        if largest_eig_val <= 0:
            raise ValueError('Largest eigen value of contact Matrix is <= 0 - See def (calculate_largest_eig_val)')
        return(largest_eig_val)
            
    
    def step(self):
        '''
        Below methods will be called at every step or at a fixed interval (every hour, every day etc. ) or at a fixed moment (e.g. last step of the simulation)
        '''
        self.schedule.step()       
        if self.schedule.time == (self.corona_start_sim_time - 1): ## create contact Matrix M and calculate largest eigen value a step before corona start time
            self.lar_eig_val = self.calculate_largest_eig_val()
            
        self.track_duty_shift() ## track the duty shift based on current time step (3 shifts in a day)
        self.remove_agents_on_discharge() ## remove discharged patients
        
        if self.schedule.time%(self.num_steps_per_day/6) == 0: ## functions that are called every 4 hours
            self.patient_movements_in_corona_wards()
        
        #### For screening, uncomment the below if conditions and choose one scenario from the below two lines for screening scenario
        if self.schedule.time%(self.num_steps_per_day*params.screening_moment) == 0 and self.schedule.time >= self.corona_start_sim_time: ## screening will be called either at 3 days or 7 days (see params file)
#            self.screening() ## screening with imperfect test sensitivity
            self.screening_perf_sens() ## screening with perfect sensitivity
        
#        ## functions that are called once every day, at the start of the day.
        if self.schedule.time%self.num_steps_per_day == 0: ## each new day let patients arrive and write the data
            if self.schedule.time > self.corona_start_sim_time:
                self.HCW_community_transmission() ## do this once a day before the start of hcw rounds and ward change. if you do it at this moment, then you do not need to care aboutduty shift.
            self.HCW_ward_change() # this HCW ward change needs to be done once in a day before the hcws visits
        
        if self.schedule.time%(self.num_steps_per_day/24) == 0: ## functions that are called every hour
            self.HCW_transmission_in_common_areas() ## executed every hour. every hour, two HCWs meet in each ward
            self.remove_old_contacts() ## remove contacts older than 2 weeks - specify this in cont_period in the params file.
        
        self.new_patient_arrivals()
        self.exposed_to_infection()
        #### choose one type of contact tracing scenario from the below line. 
#        self.contact_tracing_5day_testing_and_ppe() ## this is with imperfect test sensitivity and hcws contacts asked to wear PPE , patients in isolation       
#        self.contact_tracing_perf_sens() ### immediate contact tracing : this will call the contact tracing function every step. As soon as someone becomes infected, this will be called immediately.
        self.infected_to_recovered()
        self.HCW_recovered_and_back_to_work()
        self.physician_visits()
        self.nurse_visits()
        
        if self.schedule.time%self.num_steps_per_day == 0:
            self.data_write()
            for idx, val in enumerate(self.daily_pat_discharge):
                self.daily_pat_discharge[idx] = 0
            self.daily_transmissions = 0 ## reset this variable every day after writing the data
            self.daily_transmissions_pat = 0
            self.daily_transmissions_hcw = 0

        if self.schedule.time == params.max_iter: ## At end of modelling period write data for plots
            self.write_final_dataframes()
