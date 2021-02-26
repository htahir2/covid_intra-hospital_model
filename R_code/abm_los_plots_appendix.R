# ============================================================================ #
# Agent-based modelling for nosocomial transmission of COVID-19
# ----------------------------------------------------------------------------
# Length-of-stay distribution for non-COVID admissions
# ============================================================================ #
rm(list=ls())

# Load paths, packages, and functions
source("abm_path_packages.R")
source("abm_functions.R")
source("abm_covid_admissions_umcu.R")

# Data on LoS for non-COVID patients
noncovid_icu <- read.table("../data/los_icu.csv", header=T, sep=",")
noncovid_nonicu <- read.table("../data/los_nonicu.csv", header=T, sep=",")
colnames(noncovid_icu) <- colnames(noncovid_nonicu) <- "los"

noncovid <- as.data.frame(rbind(cbind(noncovid_icu, icu=1), cbind(noncovid_nonicu, icu=0)))
summary(noncovid$los)
noncovid$los <- ifelse(noncovid$los<1, 1, noncovid$los)
noncovid <- noncovid[which(noncovid$los<=190),]
head(noncovid)

# Data on LoS for COVID patients (from abm_covid_admissions_umcu.R)
covid <- data
colnames(covid) <- c("date", "icu", "count", "los")
head(covid)

load("../data/distr_noncovid.RData")
f_noncovid_icu <- distr$f_lnorm_ICU
f_noncovid_nonicu <- distr$f_weibull_noICU

load("../data/distr_covid.RData")
f_covid_icu <- distr$f_covid_icu
f_covid_nonicu <- distr$f_covid_nonicu

# ============================================================================ #
# Plot chosen distribution along with data 
title.size <-  18
noncovid_icu_plot <- denscomp(f_noncovid_icu, addlegend=F, plotstyle = "ggplot", fitcol="darkgreen") +
  theme_publication() + 
  geom_line(size=1.3) + 
  labs(title = "non-COVID patients in ICU") + 
  theme(legend.position = "none", 
        axis.title.x = element_blank(),
        title=element_text(face="bold", size=title.size))

noncovid_nonicu_plot <- denscomp(f_noncovid_nonicu, addlegend=F, plotstyle = "ggplot", fitlwd=5, fitcol="green") +
  theme_publication() + 
  geom_line(size=1.3) + 
  labs(title = "non-COVID patients in normal ward") + 
  theme(legend.position = "none", 
        axis.title = element_blank(),
        title=element_text(face="bold", size=title.size))

covid_icu_plot <- denscomp(f_covid_icu, addlegend=F, plotstyle = "ggplot", fitcol="darkred") +
  theme_publication() + 
  geom_line(size=1.3) + 
  labs(title = "COVID patients in ICU") + 
  theme(legend.position = "none", 
        axis.title.x = element_blank(),
        title=element_text(face="bold", size=title.size))

covid_nonicu_plot <- denscomp(f_covid_nonicu, addlegend=F, plotstyle = "ggplot", fitcol="red") +
  theme_publication() + 
  geom_line(size=1.3) + 
  labs(title = "COVID patients in normal ward") + 
  theme(legend.position = "none", 
        axis.title = element_blank(),
        title=element_text(face="bold", size=title.size))


plots <- plot_grid(noncovid_icu_plot, noncovid_nonicu_plot, covid_icu_plot, covid_nonicu_plot, 
                   ncol=2, labels="AUTO", label_size = 20)
plots <- annotate_figure(plots, 
                         bottom = text_grob("Length of Stay (days)", size=20))
plots

ggsave(plots, file="../figures/los_plots_appendix.eps", width=16, height=12)
