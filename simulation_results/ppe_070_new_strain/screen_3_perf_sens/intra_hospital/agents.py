"""

    @author: hannantahir

"""

from enum import Enum
from mesa import Agent

class State(Enum):
    SUSCEPTIBLE = 0
    EXPOSED = 1
    MILD = 2
    MODERATE = 3
    SEVERE = 4
    RECOVERED = 5
    ASYMPTOMATIC = 6

class Patient(Agent):
    """ A patient agent with all of its characteristics / attributes."""
    def __init__(self, unique_id, model, initial_state, ward, room, los, los_remaining, transmission_type, time_of_infection, incubationtime, symptom_state, movementflag, sympt_trans_count, asymp_trans_count, trans_count_to_pat, trans_count_to_hcw, patient_isolated):
        super().__init__(unique_id, model)
        if initial_state == 0:
            self.state = State.SUSCEPTIBLE
        elif initial_state == 1:
            self.state = State.EXPOSED
        elif initial_state == 2:
            self.state = State.MILD
        elif initial_state == 3:
            self.state = State.MODERATE
        elif initial_state == 4:
            self.state = State.SEVERE
        elif initial_state == 5:
            self.state = State.RECOVERED
        elif initial_state == 6:
            self.state = State.ASYMPTOMATIC

        self.unique_id = unique_id ## this is unique id of the patient
        self.ward = int(ward) ## This stores in which ward patient is admitted to
        self.room = int(room) ## This is the room number where patient is staying in a ward
        self.los = int(los) ## length of stay (LOS). This is kept fixed or changed when patient LOS is extended.
        self.los_remaining = int(los_remaining) ## This LOS counter is being counted down every step. Once over, patient is discharged
        self.transmission_type = transmission_type ## 0 for no tranmission, 1 for community, 2 for hospital tranmission
        self.time_of_infection = time_of_infection ## time at which someone gets exposed, in model time steps
        self.incubationtime = incubationtime ## incubation period in the exposed state
        self.symptom_state = symptom_state ## 1 means asymptomatic, 2 means symptomatic, 0 means not in both
        self.movementflag = movementflag ## When this is true, patient is moved to COVID wards as soon as possible
        self.symp_secon_trans_count = sympt_trans_count ## This is to count symptomatic secodnary transmissions
        self.asymp_secon_trans_count = asymp_trans_count ## This is to count asymptomatic secodnary transmissions
        self.trans_count_to_pat = trans_count_to_pat ## counts secondary transmission if infector infects a patient
        self.trans_count_to_hcw = trans_count_to_hcw ## counts secondary transmission if infector infects a hcw
        self.patient_isolated = patient_isolated ## 0 means patient is not isloated, 1 means patient is isolated - This attribute is used for contact tracing code where testing is done on day 5. 
        
    ''' patient length of stay count down '''
    def LOS_countdown(self):
        if self.los_remaining <= 0:
            self.los_remaining = 0
        elif self.los_remaining > 0:
            self.los_remaining -= 1

    ''' incubation time count down '''
    def incubationtime_countdown(self):  ## this will also change the time in the exposed state
        if self.incubationtime is not None:
            if self.incubationtime <= 0:
                self.incubationtime = 0
            elif self.incubationtime > 0:
                self.incubationtime -= 1

    def step(self):
        ''' methods thats are called at every time step for every agent '''
        self.LOS_countdown()
        self.incubationtime_countdown()


class Physician(Agent):
    '''A physician agent with all of its characteristics / attributes'''
    def __init__(self, unique_id, model, initial_state, ward, pat_attend_counter, shift, time_of_infection, protective_gear, incubationtime, symptom_state, time_outofwork, transmission_type, contact_tracing, replacement_added, trace_time, contact_traced_flag, sympt_trans_count, asymp_trans_count, trans_count_to_pat, trans_count_to_hcw, contact_tracing_output, hcw_on_ppe_cont_tracing):
        super().__init__(unique_id, model)
        if initial_state == 0:
            self.state = State.SUSCEPTIBLE
        elif initial_state == 1:
            self.state = State.EXPOSED
        elif initial_state == 2:
            self.state = State.MILD
        elif initial_state == 3:
            self.state = State.MODERATE
        elif initial_state == 4:
            self.state = State.SEVERE
        elif initial_state == 5:
            self.state = State.RECOVERED
        elif initial_state == 6:
            self.state = State.ASYMPTOMATIC

        self.unique_id = unique_id ## ID of the physician (Range 1-999)
        self.ward = ward ## ward where HCW is working
        self.pat_attend_counter = pat_attend_counter ## this is required in the method of visiting patients. This keep track of how many patients HCW has attended in a round during a shift
        self.shift = shift ## shift in which HCW is working. 3 shifts in a day. 1-3
        self.time_of_infection = time_of_infection ## time at which someone gets exposed, in model time steps
        self.protective_gear = protective_gear ## 1 means hCW is wearing protective gear, 0 means not wearing it
        self.incubationtime = incubationtime ## incubation period in the exposed state
        self.symptom_state = symptom_state ## 1 means asymptomatic, 2 means symptomatic, 0 means not in both
        self.time_outofwork = time_outofwork ## This is the quarantine time for a hcw. As long as this is > 0, hcw remains at home. This is time in simultaion steps and counted down
        self.transmission_type = transmission_type ## 0 for no tranmission, 1 for community, 2 for hospital tranmission
        if contact_tracing is None:
            contact_tracing = []
        self.contact_tracing = contact_tracing ## two dimensional list to keep track of HCWs contacts (id, time in steps)
        self.replacement_added = replacement_added  ## This keeps track if a replacement HCW is added. if True, means a replacement HCW was added in case this hcw turned positive and sent home for quarantine
        self.trace_time = trace_time ## Additional thing for contact tracing perfect sensitivity but not used at the moment. default is set to 0. When contacts of a symptomatic hcw are traced one time, the time is set when contacts will be traced second time 
        self.contacts_traced_already = contact_traced_flag ## Additional thing for contact tracing perfect sensitivity but not used at the moment. Default flag is set to False. After contacts traced one time, this is set to True. and after 2nd time, again set to Flase
        self.symp_secon_trans_count = sympt_trans_count ## This is to count symptomatic secodnary transmissions
        self.asymp_secon_trans_count = asymp_trans_count ## This is to count asymptomatic secodnary transmissions
        self.trans_count_to_pat = trans_count_to_pat ## counts secondary transmission if infector infects a patient
        self.trans_count_to_hcw = trans_count_to_hcw ## counts secondary transmission if infector infects a hcw
        if contact_tracing_output is None:
            contact_tracing_output = [0]*12 ## This is to store output of contact tracing with 5 day testing method ['Num_contacts', 'num_contacts_traced','num_positive_contacts', 'num_sympt_patients_traced','contact_tracing_time','tracing_round', 'hcw_id', 'hcw_time_of_infection','hcw_current_ward', 'num_sympt_hcws_traced', 'num_contacts_quarantined'])
        self.contact_tracing_output = contact_tracing_output ##  list to save contact tracing output data for positivity rate calculations
        self.hcw_on_ppe_cont_tracing= hcw_on_ppe_cont_tracing ## default is 0, 1 when hcw is on ppe during contact tracing.This is just to keep track of a hcw if hcw was asked to wear PPE in the contact tracing
        
    ''' incubation time count down '''
    def incubationtime_countdown(self):  ## this will also change the the time in the exposed state
        if self.incubationtime is not None:  ## 
            if self.incubationtime <= 0:
                self.incubationtime = 0
            elif self.incubationtime > 0:
                self.incubationtime -= 1

    ''' Time out of work count down. This is the time when a hcw is sent home for quarantine '''
    def time_outofwork_countdown(self):  ## change time a physician is not working due to infection
        if self.time_outofwork <= 0:
            self.time_outofwork = 0
        elif self.time_outofwork > 0:
            self.time_outofwork -= 1
    
    def step(self):
        ''' methods thats are called at every time step for every agent '''
        self.incubationtime_countdown()
        self.time_outofwork_countdown()
#        pass

class Nurse(Agent):
    '''A nurse agent with all of its characteristics / attributes'''
    def __init__(self, unique_id, model, initial_state, ward, pat_attend_counter, shift, time_of_infection, protective_gear, incubationtime, symptom_state, time_outofwork, transmission_type, contact_tracing, replacement_added, trace_time, contact_traced_flag, sympt_trans_count, asymp_trans_count, trans_count_to_pat, trans_count_to_hcw, contact_tracing_output, hcw_on_ppe_cont_tracing):
        super().__init__(unique_id, model)
        if initial_state == 0:
            self.state = State.SUSCEPTIBLE
        elif initial_state == 1:
            self.state = State.EXPOSED
        elif initial_state == 2:
            self.state = State.MILD
        elif initial_state == 3:
            self.state = State.MODERATE
        elif initial_state == 4:
            self.state = State.SEVERE
        elif initial_state == 5:
            self.state = State.RECOVERED
        elif initial_state == 6:
            self.state = State.ASYMPTOMATIC

        self.unique_id = unique_id ## ID of the nurse (Range 1000-4999)
        self.ward = ward ## ward where HCW is working
        self.pat_attend_counter = pat_attend_counter ## this is required in the method of visiting patients. This keep track of how many patients HCW has attended in a round during a shift
        self.shift = shift ## shift in which HCW is working. 3 shifts in a day. 1-3
        self.time_of_infection = time_of_infection # time at which someone gets exposed, in model time steps
        self.protective_gear = protective_gear ## 1 means hCW is wearing protective gear, 0 means not wearing it
        self.incubationtime = incubationtime ## incubation period in the exposed state
        self.symptom_state = symptom_state #### 1 means asymptomatic, 2 means symptomatic, 0 means not in both
        self.time_outofwork = time_outofwork ## This is the quarantine time for a hcw. As long as this is > 0, hcw remains at home. This is time in simultaion steps and counted down
        self.transmission_type = transmission_type ## 0 for no tranmission, 1 for community, 2 for hospital tranmission
        if contact_tracing is None:
            contact_tracing = []
        self.contact_tracing = contact_tracing ## two dimensional array to keep track of HCWs contacts (id, time in steps)
        self.replacement_added = replacement_added  ## This keeps track if a replacement HCW is added. if True, means a replacement HCW was added in case this hcw turned positive and sent home for quarantine
        self.trace_time = trace_time ## Additional thing for contact tracing perfect sensitivity but not used at the moment. default is set to 0. When contacts of a symptomatic hcw are traced one time, the time is set when contacts will be traced second time 
        self.contacts_traced_already = contact_traced_flag ## Additional thing for contact tracing perfect sensitivity but not used at the moment. Default flag is set to False. After contacts traced one time, this is set to True. and after 2nd time, again set to Flase
        self.symp_secon_trans_count = sympt_trans_count ## This is to count symptomatic secodnary transmissions
        self.asymp_secon_trans_count = asymp_trans_count ## This is to count asymptomatic secodnary transmissions
        self.trans_count_to_pat = trans_count_to_pat ## counts secondary transmission if infector infects a patient
        self.trans_count_to_hcw = trans_count_to_hcw ## counts secondary transmission if infector infects a hcw
        if contact_tracing_output is None:
            contact_tracing_output = [0]*12 ## This is to store output of contact tracing with 5 day testing method ['Num_contacts', 'num_contacts_traced','num_positive_contacts', 'num_sympt_patients_traced','contact_tracing_time','tracing_round', 'hcw_id', 'hcw_time_of_infection','hcw_current_ward', 'num_sympt_hcws_traced'])
        self.contact_tracing_output = contact_tracing_output ##  list to save contact tracing output data for positivity rate calculations
        self.hcw_on_ppe_cont_tracing= hcw_on_ppe_cont_tracing ## default is 0, 1 when hcw is on ppe during contact tracing. This is just to keep track of a hcw if hcw was asked to wear PPE in the contact tracing

    ''' incubation time count down '''
    def incubationtime_countdown(self):  ## this will also change the the time in the exposed state
        if self.incubationtime is not None:
            if self.incubationtime <= 0:
                self.incubationtime = 0
            elif self.incubationtime > 0:
                self.incubationtime -= 1

    ''' Time out of work count down. This is the time when a hcw is sent home for quarantine '''
    def time_outofwork_countdown(self):  ## change time a physician is not working due to infection
        if self.time_outofwork <= 0:
            self.time_outofwork = 0
        elif self.time_outofwork > 0:
            self.time_outofwork -= 1

 
    def step(self):
        ''' methods thats are called at every time step for every agent '''
        self.incubationtime_countdown()
        self.time_outofwork_countdown()

