# ============================================================================ #
# Agent-based modelling for nosocomial transmission of COVID-19
# ----------------------------------------------------------------------------
# Proportion of infectious patients per day stratified by age
# ============================================================================ #
rm(list=ls())
# Load paths, packages, and functions
source("abm_path_packages.R")
source("abm_functions.R")
source("abm_incidence_infectious.R")


# Incidence in the Netherlands stratified by age
file_name <- "RIVM_NL_age.csv"
data <- read.csv(paste0("../data/", file_name), header=T, sep=",")
data <- data[data$Type=="Totaal",]
data <- data[!data$LeeftijdGroep=="Niet vermeld",] # Remove rows where age was not known, missing at random

age_groups <- c("0-4","5-9","10-14","15-19","20-24","25-29","30-34","35-39","40-44","45-49","50-54",
                "55-59","60-64","65-69","70-74","75-79","80-84","85-89","90-94","95+")

# Data on age-specific hospitalization rates
hosp_data <- read.csv("../data/prop_hosp_age.csv", header=T, sep=",")
groups <- hosp_data$age_group

# Use age groups from hospitalization data
# 1-20, 20-45, 45-65, 65-80
cut <- c(4,9,13,16)
a1 <- age_groups[1:cut[1]]
a2 <- age_groups[(cut[1]+1):cut[2]]
a3 <- age_groups[(cut[2]+1):cut[3]]
a4 <- age_groups[(cut[3]+1):cut[4]]
a5 <- age_groups[(cut[4]+1):length(age_groups)]
data$LeeftijdGroep <- factor(data$LeeftijdGroep, levels=age_groups)
data$Aantal[is.na(data$Aantal)] <- 0
data$Datum <- as.Date(data$Datum, format="%Y-%m-%d")

# Divide data into these age groups
d1 <- data[data$LeeftijdGroep%in%a1,]
d2 <- data[data$LeeftijdGroep%in%a2,]
d3 <- data[data$LeeftijdGroep%in%a3,]
d4 <- data[data$LeeftijdGroep%in%a4,]
d5 <- data[data$LeeftijdGroep%in%a5,]

d1_total <- d1 %>% group_by(Datum) %>% summarize(sum=sum(Aantal), group=groups[1])
d2_total <- d2 %>% group_by(Datum) %>% summarize(sum=sum(Aantal), group=groups[2])
d3_total <- d3 %>% group_by(Datum) %>% summarize(sum=sum(Aantal), group=groups[3])
d4_total <- d4 %>% group_by(Datum) %>% summarize(sum=sum(Aantal), group=groups[4])
d5_total <- d5 %>% group_by(Datum) %>% summarize(sum=sum(Aantal), group=groups[5])

# Combined data set with age-specfic incidence in NL
df <- as.data.frame(rbind(d1_total, d2_total, d3_total, d4_total, d5_total))
df$group <- factor(df$group)

# Remove 0 values
df <- df[!df$sum==0,]
data <- data[!data$Aantal==0,]

# ============================================================================ #
# Plots
# ============================================================================ #
# Stacked barplots: Age-specfific incidence 
barplot <- ggplot(df, aes(x=Datum, y=sum, fill=group)) +
  geom_bar(position="stack", stat="identity") +
  scale_x_date(date_breaks="1 week", date_labels="%d-%b") +
  theme_bw() +
  theme(axis.text.x = element_text(size=14, angle=45, hjust=1))
barplot
# ggsave(barplot, file="../figures/barplot_incidence_NL_per_age_hosp.eps", width=12, height = 9)

# Data frame with proportion of age-specific incidence
# i.e. percentage of people that got infected on day x and belong to age group y
df <- df %>% group_by(Datum) %>% summarize(sum=sum, group=group, total=sum(sum))
df$prop <- df$sum/df$total
df$prop[is.na(df$prop)] <- 0
# Plot of these proportions
prop_plot <- ggplot(df, aes(x=Datum, y=prop, color=group)) +
  geom_point() +
  scale_x_date(date_breaks="1 week", date_labels="%d-%b") +
  theme_bw() +
  theme(axis.text.x = element_text(size=14, angle=45, hjust=1),
        axis.title.x = element_blank())
prop_plot
# ggsave(prop_plot, file="../figures/propplot_incidence_NL_per_age_hosp.eps", width=12, height = 9)

# ============================================================================ #
# Combine incidence and hospitalization rates
# ============================================================================ #
# Dates in model
dates <- seq(as.Date("17-02-2020", format="%d-%m-%Y"),as.Date("24-08-2020", format="%d-%m-%Y"),by=1)

# Assume that the incidence is the same before available start date
df_begin <- data.frame(Datum=as.POSIXct(character(), format = "%Y-%m-%d", tz="UTC"), group=character(), prop=numeric())
dates_begin <- as.Date(dates[dates<=min(df$Datum)], format="%Y-%m-%d")
j <- 1
for(i in 1:length(dates_begin)){
  for(g in unique(df$group)){
    df_begin[j,"Datum"] <- as.Date(dates_begin[i], format="%Y-%m-%d")
    df_begin[j,"group"] <- g
    df_begin[j,"prop"] <- unlist(df[df$group==g,"prop"])[1]
    j <- j + 1
  }
}
# Assume that the incidence is the same after available end date
df_end <- data.frame(Datum=as.POSIXct(character(), format = "%Y-%m-%d", tz="UTC"), group=character(), prop=numeric())
dates_end <- as.Date(dates[dates>=max(df$Datum)], format="%Y-%m-%d")
j <- 1
for(i in 1:length(dates_end)){
  for(g in unique(df$group)){
    df_end[j,"Datum"] <- as.Date(dates_end[i], format="%Y-%m-%d")
    df_end[j,"group"] <- g
    df_end[j,"prop"] <- unlist(df[df$group==g,"prop"])[nrow(df[df$group==g,"prop"])]
    j <- j + 1
  }
}

# This data frame now contains the percentage/proportion of newly infected 
# individuals per age group
df_new <- rbind(df_begin, df[c("Datum","group","prop")], df_end)

# (Cumulative) incidence 
head(covid_cases)
# inf_col <- "prop_cum_incidence_after_subtraction" # cumulative incidence
# This column contains the percentage of infectious individuals per day (prevalence)
inf_col <- "proportion_infectious_after_subtraction" # prevalence

covid_cases_patient <- data.frame(date=as.POSIXct(character(), format = "%Y-%m-%d", tz="UTC"),
                                  age_group = character(),
                                  prop_hosp = numeric(),
                                  prop_prev_patient = numeric())

# Scale proportion of infectious patients 
j <- 1
for(i in 1:nrow(covid_cases)){
  for(g in unique(df_new$group)){
    covid_cases_patient[j,"date"] <- as.Date(covid_cases[i,"date"], format="%Y-%m-%d")
    covid_cases_patient[j,"age_group"] <- g
    covid_cases_patient[j,"prop_hosp"] <- hosp_data[hosp_data$age_group==g, "prop"]
    covid_cases_patient[j,"prop_prev_patient"] <- covid_cases[i,inf_col]*unlist(df_new[df_new$group==g,"prop"])[i]
    j <- j + 1
  }
}

# Convert from long into wide format
df_prop_hosp_wide <- spread(covid_cases_patient[,-c(ncol(covid_cases_patient))],age_group, prop_hosp)
colnames(df_prop_hosp_wide)[-1] <- paste0("prop_hosp_", colnames(df_prop_hosp_wide)[-1])
df_prop_inc_patient_wide <- spread(covid_cases_patient[,-c(ncol(covid_cases_patient)-1)],age_group, prop_prev_patient)
colnames(df_prop_inc_patient_wide)[-1] <- paste0("prop_prev_pat_", colnames(df_prop_inc_patient_wide)[-1])
covid_cases_patient_long <- merge(df_prop_hosp_wide, df_prop_inc_patient_wide, id="date")
head(covid_cases_patient_long)

# Proportion of infectious among HCWs
# At the moment: based on prevalence
g <- c("20-45", "45-65")
for(i in 1:nrow(covid_cases)){
    prop <- unlist(df_new[df_new$group==g[1],"prop"][i]) + unlist(df_new[df_new$group==g[2],"prop"][i])
    covid_cases_patient_long[i,"prop_incidence_HCW"] <- covid_cases[i,"prop_incidence_after_subtraction"]*prop
    covid_cases_patient_long[i,"prop_cum_incidence_HCW"] <- covid_cases[i,"prop_cum_incidence_after_subtraction"]*prop
    covid_cases_patient_long[i,"prop_prev_HCW"] <- covid_cases[i,inf_col]*prop
    covid_cases_patient_long[i,"prop_prev2_HCW"] <- covid_cases[i,"infectious_after_subtraction"]*prop/(3*catchment)
}

dates_begin <- seq(as.Date("2019-12-30", format="%Y-%m-%d"), 
                   as.Date("2020-02-16", format="%Y-%m-%d"),by=1)
covid_cases_begin <- NULL
zeros <- covid_cases_patient_long[1,7:ncol(covid_cases_patient_long)]
zeros[1,] <- 0
for(i in 1:length(dates_begin)){
  covid_cases_begin <- rbind(covid_cases_begin, cbind(date=dates_begin[i], df_prop_hosp_wide[1,-1], zeros))
}
covid_cases_patient_long <- rbind(covid_cases_begin, covid_cases_patient_long)


write.csv(covid_cases_patient_long, file=paste0(inputPath, "covid_cases_for_model_FINAL_prevPat_cumIncHCW_catchment_",catchment/1000,".csv"), row.names = T)
