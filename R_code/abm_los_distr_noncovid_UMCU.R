# ============================================================================ #
# Agent-based modelling for nosocomial transmission of COVID-19
# ----------------------------------------------------------------------------
# Length-of-stay distribution for non-COVID admissions
# ============================================================================ #
rm(list=ls())

# Load paths, packages, and functions
source("abm_path_packages.R")
source("abm_functions.R")

los_icu <- read.table("../data/los_icu.csv", header=T, sep=",")
los_nonicu <- read.table("../data/los_nonicu.csv", header=T, sep=",")
colnames(los_icu) <- colnames(los_nonicu) <- "los"

data <- as.data.frame(rbind(cbind(los_icu, icu=1), cbind(los_nonicu, icu=0)))
summary(data$los)
data$los <- ifelse(data$los<1, 1, data$los)
data <- data[which(data$los<=190),]

summary(data$los[data$icu==1])
summary(data$los[data$icu==0])

# Histogram plot of data 
ggplot(data=data) + 
  # facet_wrap(~icu, scales = "free") + 
  facet_wrap(~icu) + 
  geom_histogram(aes(los)) + 
  geom_line(aes(x=los, y=dlnorm(data$los, f_lnorm_ICU$estimate["meanlog"], f_lnorm_ICU$estimate["sdlog"]))) + 
  labs(x="Length of Stay (days)") + 
  theme_publication() + 
  theme(strip.text = element_text(size=20), 
        axis.title.y = element_blank())

# ============================================================================ #
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

# ============================================================================ #
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

ggsave(p0, file="../figures/los_umcu_noncovid_icu_fitdistr.eps", width=12, height=9)
ggsave(p1, file="../figures/los_umcu_noncovid_nonicu_fitdistr.eps", width=12, height=9)

# ============================================================================ #
# Plot chosen distribution along with data 
icu_plot <- denscomp(f_lnorm_ICU, addlegend=F, plotstyle = "ggplot", fitcol="blue") +
              theme_publication() + 
              geom_line(size=1.3) + 
              labs(title = "non-COVID patients in ICU") + 
              theme(legend.position = "none", 
                    axis.title.x = element_blank(),
                    title=element_text(face="bold"))

nonicu_plot <- denscomp(f_weibull_noICU, addlegend=F, plotstyle = "ggplot", fitlwd=5, fitcol="green") +
                  theme_publication() + 
                  geom_line(size=1.3) + 
                  labs(title = "non-COVID patients in normal ward") + 
                  theme(legend.position = "none", 
                        axis.title = element_blank(),
                        title=element_text(face="bold"))

plots <- plot_grid(icu_plot, nonicu_plot, ncol=2, labels="AUTO")
plots <- annotate_figure(plots, 
                         bottom = text_grob("Length of Stay (days)", size=20))
plots
ggsave(plots, file="../figures/los_noncovid_data_distr_plot.eps", width=12, height=7)

# ============================================================================ #
# Choose distribution and save
# ICU = lognormal
# non-ICU = weibull
write.table(as.data.frame(t(f_lnorm_ICU$estimate)), file="../data/los_noncovid_icu_lnorm_param.txt", 
            row.names = F, sep=",")
write.table(as.data.frame(t(f_weibull_noICU$estimate)), file="../data/los_noncovid_nonicu_weibull_param.txt", 
            row.names = F, sep=",")

distr <- list(f_lnorm_ICU=f_lnorm_ICU, f_weibull_noICU=f_weibull_noICU)
save(distr, file="../data/distr_noncovid.RData")
