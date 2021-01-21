# ============================================================================ #
# Agent-based modelling for nosocomial transmission of COVID-19
# ----------------------------------------------------------------------------
# Admission of COVID-19 patients in UMCU
# ============================================================================ #
rm(list=ls())

# Load paths, packages, and functions
source("abm_path_packages.R")
source("abm_functions.R")
source("abm_covid_admissions_umcu.R")

colnames(data) <- c("date", "icu", "count", "los")
data <- data[data$date%in%dates, ]

colors_icu <- c("dimgrey","black")

# Data 
adm_plot <- ggplot(data, aes(x=date, fill=icu)) +
              geom_bar(stat="count", position="stack") +
              labs(y="Number of admissions") + 
              scale_fill_manual(labels=c("regular ward", "ICU"), values=c("grey", "black")) + 
              scale_x_date(date_breaks="1 week", date_labels="%d %b") +
              theme_publication() +
              theme(legend.title = element_blank(),
                    legend.text = element_text(size=18),
                    axis.title.x = element_blank(), 
                    axis.text.x = element_text(angle=45, hjust=1))
adm_plot
ggsave(adm_plot, file="../figures/admissions_covid_UMCU.eps", width=12, height=9)


los_plot <- ggplot(data, aes(x=as.numeric(los), fill=icu)) + 
              facet_grid(~icu, labeller = labeller(icu=icu.labs)) + 
              geom_histogram(position = "identity", binwidth=1) +
              theme_bw() + 
              labs(title="Length-of-stay distributions of COVID-19 patients in UMCU",
                   y="Number of patients", 
                   x = "Length of stay (days)") + 
              scale_fill_manual(values = colors_icu) +
              theme(title = element_text(size=20), 
                    plot.title = element_text(hjust=0.5),
                    legend.position = "none",
                    panel.background = element_blank(),
                    axis.line = element_line(colour = "black"),
                    axis.title = element_text(size=14), 
                    axis.text = element_text(size=14),
                    strip.text = element_text(size=14)) 
los_plot
ggsave(los_plot, file="../figures/los_covid.eps", width=12, height=9)

# Fit distributions to non-ICU patients
plot.legend <- c("weibull", "gamma", "exponential", "lognormal")
f_weibull_noICU <- fitdist(data$los[data$icu==0], "weibull")
f_gamma_noICU <- fitdist(data$los[data$icu==0], "gamma")
f_exp_noICU <- fitdist(data$los[data$icu==0], "exp")
f_lnorm_noICU <- fitdist(data$los[data$icu==0], "lnorm")
f_list0 <- list(f_weibull_noICU, f_gamma_noICU, f_exp_noICU, f_lnorm_noICU)

# Goodness-of-fit plots
p01 <- denscomp(f_list0, addlegend=F, plotstyle="ggplot")
p02 <- cdfcomp(f_list0, legendtext = plot.legend, plotstyle="ggplot")
p03 <- qqcomp(f_list0, addlegend=F, plotstyle="ggplot") 
p04 <- ppcomp(f_list0, legendtext = plot.legend, plotstyle="ggplot")

p0 <- grid.arrange(p01, p02, p03, p04, nrow=2)

# Fit distributions to ICU patients
f_weibull_ICU <- fitdist(data$los[data$icu==1], "weibull")
f_gamma_ICU <- fitdist(data$los[data$icu==1], "gamma")
f_exp_ICU <- fitdist(data$los[data$icu==1], "exp")
f_lnorm_ICU <- fitdist(data$los[data$icu==1], "lnorm")
f_list1 <- list(f_weibull_ICU, f_gamma_ICU, f_exp_ICU, f_lnorm_ICU)

# Goodness-of-fit plots
p11 <- denscomp(f_list1, addlegend=F, plotstyle="ggplot")
p12 <- cdfcomp(f_list1, legendtext = plot.legend, plotstyle="ggplot")
p13 <- qqcomp(f_list1, addlegend=F, plotstyle="ggplot") 
p14 <- ppcomp(f_list1, legendtext = plot.legend, plotstyle="ggplot")

p1 <- grid.arrange(p11, p12, p13, p14, nrow=2)

ggsave(p0, file="../figures/los_covid_umcu_icu_fitdistr.eps", width=12, height=9)
ggsave(p1, file="../figures/los_covid_umcu_nonicu_fitdistr.eps", width=12, height=9)

# Save parameters of gamma distribution (best fit)
write.table(as.data.frame(t(f_gamma_ICU$estimate)), file="../data/los_covid_icu_gamma_param.txt", 
            row.names = F, sep=",")
write.table(as.data.frame(t(f_gamma_noICU$estimate)), file="../data/los_covid_nonicu_gamma_param.txt", 
            row.names = F, sep=",")

distr <- list(f_covid_icu=f_gamma_ICU, f_covid_nonicu=f_gamma_noICU)
save(distr, file="../data/distr_covid.RData")
