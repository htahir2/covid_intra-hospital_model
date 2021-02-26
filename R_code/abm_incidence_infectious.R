# ============================================================================ #
# Agent-based modelling for nosocomial transmission of COVID-19
# ----------------------------------------------------------------------------
# Proportion of infectious patients per day
# ============================================================================ #
rm(list=ls())

# Load paths, packages, and functions
source("abm_path_packages.R")
source("abm_functions.R")

# File from RIVM
nInf_json <- fromJSON(file="../data/COVID-19_prevalentie.json")
nInf_json <- nInf_json[1:190]
nInf_data <- as.data.frame(matrix(unlist(nInf_json), ncol = 5, byrow = T))
nInf_data[,3] <- as.numeric(nInf_data[,3])
nInf_data[,4] <- as.numeric(nInf_data[,4])
colnames(nInf_data) <- c("date", "low", "mean", "high", "population")
nInf_data$date <- as.Date(nInf_data$date, format="%Y-%m-%d")

# nInf_data now includes the absolute number of infectious individuals in the
# Netherlands (mean, lower bound, upper bound)
head(nInf_data, 20)

# Compute number of infectious per catchment area 
catchment <- 100000
nPop <- 17139065
ratio <- nPop/catchment
covid_cases <- nInf_data[,c("date", "mean")]
colnames(covid_cases)[2] <- "mean"
covid_cases$infectious_per_catchment <- covid_cases$mean/ratio

# RIVM data with total number of diagnosed
rivm_data <- read.table("../data/RIVM_NL_municipal.csv", sep=",",header=T)
rivm_data <- rivm_data[rivm_data$Type=="Totaal",]
rivm_data <- rivm_data[rivm_data$Provincienaam=="Utrecht",]
rivm_data$Aantal[is.na(rivm_data$Aantal)] <- 0
head(rivm_data)
rivm_pos <- rivm_data %>% group_by(Datum) %>% summarize(pos=sum(Aantal))
rivm_pos$Datum <- as.Date(rivm_pos$Datum, format="%Y-%m-%d")

# Data frame with estimated number of infectious individuals (prevalence)
# To be used for patients
infectious_after_subtraction <- covid_cases$infectious_per_catchment
cases <- rep(0, nrow(covid_cases))
for(i in 1:length(infectious_after_subtraction)){
  ind <- which(rivm_pos$Datum==covid_cases$date[i])
  if(length(ind)>0) {
    cases[i] <- rivm_pos$pos[ind]
    infectious_after_subtraction[i] <- covid_cases$infectious_per_catchment[i]- rivm_pos$pos[ind]
  }
}
proportion_infectious_after_subtraction <- infectious_after_subtraction/catchment

# Incidence infectious (to be used for HCWs)
incidence_after_subtraction <- NULL
for(i in 1:(nrow(covid_cases)-1)){
  temp <- infectious_after_subtraction[i+1]-infectious_after_subtraction[i]
  incidence_after_subtraction <- c(incidence_after_subtraction, ifelse(temp>0, temp, 0)) 
}
incidence_after_subtraction <- c(incidence_after_subtraction[1], incidence_after_subtraction)
prop_incidence_after_subtraction <- incidence_after_subtraction/catchment

# Cumulative incidence of 10 days (to be used for patients or HCWs, currently not used)
day <- 11
cum_incidence_after_subtraction <- incidence_after_subtraction 
for(i in day:length(cum_incidence_after_subtraction)){
  cum_incidence_after_subtraction[i] <- sum(incidence_after_subtraction[(i-(day-1)):(i-1)])
}
prop_cum_incidence_after_subtraction <- cum_incidence_after_subtraction/catchment

covid_cases <- cbind(covid_cases, infectious_after_subtraction, proportion_infectious_after_subtraction, prop_incidence_after_subtraction, prop_cum_incidence_after_subtraction)

write.table(covid_cases, file=paste0("../data/covid_cases_for_model_cum_inc_",day-1,"_catchment_", catchment/1000,".csv"), sep=",", row.names = F, col.names = T)
