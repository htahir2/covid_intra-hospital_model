# ============================================================================ #
# Agent-based modelling for nosocomial transmission of COVID-19
# ----------------------------------------------------------------------------
# Positivity rates for screening and contact tracing
# ============================================================================ #
rm(list=ls())

# Load paths, packages, and functions
source("abm_path_packages.R")
source("abm_functions.R")


# Files with positivity rates
positivity_rates <- read_excel_allsheets(paste0("../",dataPath, "positivity_rates.xlsx"))
rate_data <- positivity_rates[[1]]
for(i in 2:length(positivity_rates)) rate_data <- rbind(rate_data, positivity_rates[[i]])
rate_data <- as.data.frame(cbind(scenarios_PR, rate_data))
rate_data$scenarios_PR <- factor(rate_data$scenarios_PR, levels=scenarios_PR)
colnames(rate_data) <- c("scenarios", "mean", "max","ci_upper", "ci_lower")
for(i in c("mean","max","ci_upper", "ci_lower")) rate_data[,i] <- as.numeric(rate_data[,i])


rates_plot <- ggplot(data=rate_data, aes(x=scenarios,y=mean, color=scenarios)) + 
  geom_bar(position=position_dodge(width=0.7), stat="identity", width=0.5, color=colors_PR, fill=colors_PR) +
  geom_errorbar(aes(ymax = ci_upper, ymin=ci_lower), position = position_dodge(0.9), width = 0.3, color="grey") +
  coord_flip() +       
  labs(title="Mean positivity rates of screening and contact tracing") + 
  ylab("Percentage of detected cases") + 
  # guides(fill=guide_legend(title="")) +
  theme_bw() +
  scale_fill_manual(values=colors_PR) +
  scale_x_discrete(limits = rev(levels(rate_data$scenarios))) + 
  theme(title = element_text(size=20), 
        plot.title = element_text(hjust=0.5),
        legend.position="none",
        panel.background = element_blank(),
        axis.title.y = element_blank(),
        axis.line = element_line(colour = "black"),
        axis.title.x=element_text(size=14), 
        axis.text.x=element_text(size=14),
        axis.text=element_text(size=14)) 
rates_plot
ggsave(plot = rates_plot, file = "../figures/positivity_rates_plot.eps", width=12, height=9)


rates_max_plot <- ggplot(data=rate_data, aes(x=scenarios,y=max, color=scenarios)) + 
  geom_bar(position=position_dodge(width=0.7), stat="identity", width=0.5, color=colors_PR, fill=colors_PR) +
  coord_flip() +       
  labs(title="Mean positivity rates of screening and contact tracing") + 
  ylab("Percentage of detected cases") + 
  # guides(fill=guide_legend(title="")) +
  theme_bw() +
  scale_fill_manual(values=colors_PR) +
  scale_x_discrete(limits = rev(levels(rate_data$scenarios))) + 
  theme(title = element_text(size=20), 
        plot.title = element_text(hjust=0.5),
        legend.position="none",
        panel.background = element_blank(),
        axis.title.y = element_blank(),
        axis.line = element_line(colour = "black"),
        axis.title.x=element_text(size=14), 
        axis.text.x=element_text(size=14),
        axis.text=element_text(size=14)) 
rates_max_plot
