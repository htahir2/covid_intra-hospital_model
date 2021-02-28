# ============================================================================ #
# Agent-based modelling for nosocomial transmission of COVID-19
# ----------------------------------------------------------------------------
# Total number of nosocomial transmissions
# ============================================================================ #
rm(list=ls())

# Load paths, packages, and functions
source("abm_path_packages.R")
source("abm_functions.R")

# File from simulation with absolute numbers of transmissions
data_abs <- read_excel_allsheets(paste0("../",dataPath, "transm_covid_and_non_covid_wards.xlsx"))
ward_abs_data <- NULL
for(i in 1:length(data_abs)) ward_abs_data <- rbind(ward_abs_data, data_abs[[i]])
scenarios <- scenarios[1:length(data_abs)]
ward_abs_data <- cbind(scenarios, ward_abs_data)
ward_abs_data$scenarios <- factor(ward_abs_data$scenarios, levels=scenarios)
colors_all <- colors_all[1:length(data_abs)]


# Plot with absolute number of nosocomial transmission accounting for discharged patients
# Figure 5 in main text of the manuscript
source("abm_discharged_to_community.R")
abs_dis_plot <- ggplot(data=ward_abs_data, aes(x=scenarios, y=Total_transmission_mean, color=colors_all)) + 
                  geom_bar(stat="identity", width=0.5, color=colors_all, fill=colors_all, alpha=0.7) +
                  geom_bar_pattern(data=dis_pat_df, aes(x=scenarios, y=ward_abs_data$Total_transmission_mean-mean), 
                                   stat="identity", alpha=1.0, width=0.5, 
                                   color="black", fill=colors_all, pattern_fill=colors_all,
                                   pattern_color=colors_all,
                                   pattern_angle = 45,
                                   pattern_density = 0.1,
                                   pattern_spacing = 0.025,) + 
                  geom_errorbar(aes(ymax = Total_transmission_ci_upper, ymin=Total_transmission_ci_lower), position = position_dodge(0.9), width = 0.3, color="grey") +
                  coord_flip() +       
                  labs(title="Total number of transmissions") + 
                  ylab("Number of nosocomial transmissions") + 
                  theme_publication() +
                  scale_fill_manual(values=colors_all) +
                  scale_x_discrete(limits = rev(levels(ward_abs_data$scenarios))) +
                  # scale_y_continuous(breaks=seq(0,1200,by=200)) + 
                  #guides(size=FALSE) + 
                  theme(title = element_text(size=26), 
                        # plot.title = element_text(hjust=0.5),
                        plot.title = element_blank(),
                        legend.position="none",
                        panel.background = element_blank(),
                        axis.title.y = element_blank(),
                        axis.line = element_line(colour = "black"),
                        axis.title.x=element_text(size=20), 
                        axis.text.x=element_text(size=18),
                        axis.text=element_text(size=18),
                        plot.margin = unit(c(0.1,0.5,0.1,0.1),"cm"),
                        panel.grid.minor=element_line(linetype = 'dotted'),
                        panel.grid.major=element_blank()) 
ggsave(plot=abs_dis_plot, file=paste0(figuresPath, "Figure_5.pdf"), width=12, height=9)

# Proportion of nosocomial transmissions detected in the hospital
perc_dis_data <- as.data.frame(cbind(scenarios, 
                                     detected_mean = 100*as.numeric((ward_abs_data$Total_transmission_mean - dis_pat_df$mean)/ward_abs_data$Total_transmission_mean),
                                     undetected_mean = 100*as.numeric(dis_pat_df$mean/ward_abs_data$Total_transmission_mean)))
perc_dis_data$scenarios <- factor(perc_dis_data$scenarios, levels=scenarios)

perc_dis_plot <- ggplot(data=perc_dis_data, aes(x=scenarios)) + 
                  geom_bar(aes(y=100),stat="identity", width=0.5, color=colors_all, fill=colors_all, alpha=0.7) +
                  geom_bar(aes(y=as.numeric(detected_mean)), stat="identity", width=0.5, color="black", fill=colors_all) +
                  coord_flip() +       
                  ylab("Proportion of detected nosocomial transmissions (%)") + 
                  theme_publication() +
                  scale_fill_manual(values=colors_all) +
                  scale_x_discrete(limits = rev(levels(perc_dis_data$scenarios))) +
                  # scale_y_continuous(breaks=seq(0,1200,by=200)) + 
                  #guides(size=FALSE) + 
                  theme(title = element_text(size=26), 
                        # plot.title = element_text(hjust=0.5),
                        plot.title = element_blank(),
                        legend.position="none",
                        panel.background = element_blank(),
                        axis.title.y = element_blank(),
                        axis.line = element_line(colour = "black"),
                        axis.title.x=element_text(size=20), 
                        axis.text.x=element_text(size=18),
                        axis.text=element_text(size=18),
                        plot.margin = unit(c(0.1,0.5,0.1,0.1),"cm"),
                        panel.grid.minor=element_line(linetype = 'dotted'),
                        panel.grid.major=element_blank()) 
# ggsave(plot=perc_dis_plot, file=paste0(figuresPath, "prop_detected_transm_barplot.pdf"), width=12, height=9)

# Plot with only absolute numbers of nosocomial transmissions
abs_plot <- ggplot(data=ward_abs_data, aes(x=scenarios, y=Total_transmission_mean, color=colors_all)) + 
  geom_bar(stat="identity", width=0.5, color=colors_all, fill=colors_all) +
  geom_errorbar(aes(ymax = Total_transmission_ci_upper, ymin=Total_transmission_ci_lower), position = position_dodge(0.9), width = 0.3, color="grey") +
  coord_flip() +       
  labs(title="Total number of transmissions") + 
  ylab("Number of nosocomial transmissions") + 
  theme_bw() +
  scale_fill_manual(values=colors_all) +
  scale_x_discrete(limits = rev(levels(ward_abs_data$scenarios))) +
  # scale_y_continuous(breaks=seq(0,1200,by=200)) + 
  #guides(size=FALSE) + 
  theme(title = element_text(size=26), 
        # plot.title = element_text(hjust=0.5),
        plot.title = element_blank(),
        legend.position="none",
        panel.background = element_blank(),
        axis.title.y = element_blank(),
        axis.line = element_line(colour = "black"),
        axis.title.x=element_text(size=20), 
        axis.text.x=element_text(size=18),
        axis.text=element_text(size=18),
        plot.margin = unit(c(0.1,0.5,0.1,0.1),"cm"),
        panel.grid.minor=element_line(linetype = 'dotted'),
        panel.grid.major=element_blank()) 
# ggsave(plot=abs_plot, file=paste0(figuresPath, "total_transm_barplot.pdf"), width=12, height=9)

# Reductions with respect to baseline
abs_transm_red <- sapply(2:length(scenarios), function(x) 1-ward_abs_data[ward_abs_data$scenarios==scenarios[x],"Total_transmission_mean"]/ward_abs_data[ward_abs_data$scenarios==scenarios[1],"Total_transmission_mean"])
(abs_transm_red_df <- as.data.frame(cbind(scenarios=scenarios[-1], value=100*round(abs_transm_red, 3))))
write.table(abs_transm_red_df, file=paste0(figuresPath, "total_transmission_red.csv"), sep=",", row.names = F)

abs_transm_red_df$scenarios <- factor(abs_transm_red_df$scenarios, levels=scenarios[-1])
red_plot <- ggplot(data = abs_transm_red_df, aes(x=scenarios,y=as.numeric(value))) +
              geom_bar(stat="identity", width=0.5, color=colors_red, fill=colors_red) +
              coord_flip() +
              ylab("Mean reduction in nosocomial transmissions (%)") +
              theme_publication() +
              scale_fill_manual(values=colors_red) +
              scale_x_discrete(limits = rev(levels(abs_transm_red_df$scenarios))) +
              theme(title = element_text(size=26),
                    plot.title = element_blank(),
                    legend.position="none",
                    panel.background = element_blank(),
                    axis.title.y = element_blank(),
                    axis.line = element_line(colour = "black"),
                    axis.title.x=element_text(size=20),
                    axis.text.x=element_text(size=18),
                    axis.text=element_text(size=18),
                    plot.margin = unit(c(0.1,0.5,0.1,0.1),"cm"),
                    panel.grid.minor=element_line(linetype = 'dotted'),
                    panel.grid.major=element_blank())
# ggsave(plot=red_plot, file=paste0(figuresPath, "red_transm_barplot.pdf"), width=12, height=9)
