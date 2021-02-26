# ============================================================================ #
# Agent-based modelling for nosocomial transmission of COVID-19
# ----------------------------------------------------------------------------
# Positivity rates for contact tracing
# ============================================================================ #
rm(list=ls())

# Load paths, packages, and functions
source("abm_path_packages.R")
source("abm_functions.R")

# Files for positivity rates of contact tracing over time
dates <- seq(as.Date("17-02-2020", format="%d-%m-%Y"),as.Date("24-08-2020", format="%d-%m-%Y"),by=1)
ct_data <- read.csv(paste0("../",dataPath, "contact_tracing_with_time_rounded_off_without_conf_interval.csv"))

ct_data <- as.data.frame(cbind(date=dates[ct_data$Time], ct_data[,-1]))
head(ct_data)


plot <- ggplot(ct_data) + 
  geom_point(aes(x=date,y=positivity_rate)) + 
  labs(y="Percentage of detected cases") +
  scale_x_date(date_breaks="1 week", date_labels="%d %b") +
  theme_bw() + 
  theme(title = element_text(size=20), 
        plot.title = element_text(hjust=0.5),
        legend.position = c(0.8,0.75),
        legend.title = element_blank(),
        legend.text = element_text(size=14),
        panel.background = element_blank(),
        axis.title.y = element_text(size=16),
        axis.line = element_line(colour = "black"),
        axis.title.x=element_blank(), 
        axis.text.x=element_text(size=13, angle=45, hjust=1),
        axis.text=element_text(size=14),
        strip.text=element_text(size=14)) 
plot


ggsave(plot, file="../figures/pos_rate_contact_tracing.eps", width=16, height=9)

