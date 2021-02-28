# ================================================================= #
# Plots for Figure 2
# ================================================================= #

rm(list=ls())

source("abm_path_packages.R")
source("abm_functions.R")
source("abm_plot_occupied_beds_covid_admissions_umcu.R")


# ================================================================= #
# Compare number of occupied beds (siumulation vs data)
# ================================================================= #
# File with percentage of number of symptomatic patients over time (from simulation)
dates <- seq(as.Date("17-02-2020", format="%d-%m-%Y"),as.Date("24-08-2020", format="%d-%m-%Y"),by=1)
beds_occupied <- read_excel_allsheets(paste0("../", dataPath, "occ_beds_covid_wards_over_time.xlsx"))[[1]]
beds_occupied <- beds_occupied[((nrow(beds_occupied)-190)+1):nrow(beds_occupied),]
beds_data <- as.data.frame(cbind(date=dates, beds_occupied))

labels <- c("Simulated number of patients in COVID wards (wild-type scenario)", "Occupied beds by COVID-19 patients at UMCU")
p <- ggplot(data=beds_data, aes(x=as.Date(date, format="%Y-%m-%d"))) + 
  geom_point(data=N.df[N.df$date%in%dates,], aes(y=N, colour=labels[2])) + 
  geom_line(aes(y=mean, colour=labels[1]), size=1.3) +
  geom_ribbon(aes(x=date, ymin=ci_lower, ymax=ci_upper, fill=labels[1]), alpha=0.3) +
  labs(y="Number of patients") + 
  scale_x_date(date_breaks = "1 week", date_labels = "%d-%b") + 
  scale_colour_manual(values=c("red","black") , name="") +
  scale_fill_manual(values=c("black", "red")) +
  scale_shape_manual(name = "", values = c(0,2)) + 
  guides(colour = guide_legend(nrow = 2), linetype=c(1, "blank")) + guides(fill=FALSE)+ 
  theme_publication() + 
  theme(axis.text.x = element_text(size=16, angle=45, hjust=1),
        axis.title.x = element_blank(),
        # axis.title.y = element_text(size=18),
        # axis.text.y = element_text(size=14),
        legend.position = "bottom",
        legend.background = element_blank(),
        legend.title = element_blank(),
        legend.text = element_text(size=16))
p

# ================================================================= #
# Compare total number of transmissions and R
# (wild-type vs baseline scenario)
# ================================================================= #
# Total transmission of wild-type variant
folder_old <- 'ppe_090'
folder_new <- 'ppe_090_new_strain'
dataPath_old <- paste0("data/", parent_folder,"/", folder_old, "/combined_results/interventions/")
dataPath_new <- paste0("data/", parent_folder,"/", folder_new, "/combined_results/interventions/")
data_old <- read_excel_allsheets(paste0("../",dataPath_old, "transm_covid_and_non_covid_wards.xlsx"))[[1]]
data_new <- read_excel_allsheets(paste0("../",dataPath_new, "transm_covid_and_non_covid_wards.xlsx"))[[1]]

ward_abs_data <- rbind(data_old, data_new)
scenarios <- c("Wild-type scenario", "Baseline scenario")
ward_abs_data <- cbind(scenarios, ward_abs_data)
ward_abs_data$scenarios <- factor(ward_abs_data$scenarios, levels=scenarios)
colors_all <- c("black","#07b4f9")

# Discharged patients
data_list <- list()
data_list[[1]] <- read_excel_allsheets(paste0("../",dataPath_old, "discharged_covid19patients.xlsx"))[[1]]
data_list[[2]] <- read_excel_allsheets(paste0("../",dataPath_new, "discharged_covid19patients.xlsx"))[[1]]
names(data_list) <- scenarios
# Total number of discharged patients at the end of the study period
dis_pat <- lapply(data_list, function(x) c(x$mean[nrow(x)],x$ci_lower[nrow(x)],x$ci_upper[nrow(x)]))
dis_pat_df <- as.data.frame(cbind(scenarios, t(bind_rows(dis_pat, .id="scenarios"))), row.names=F)
colnames(dis_pat_df) <- c("scenarios", "mean", "ci_lower", "ci_upper")
dis_pat_df$mean <- as.numeric(dis_pat_df$mean)
dis_pat_df$ci_lower <- as.numeric(dis_pat_df$ci_lower)
dis_pat_df$ci_upper <- as.numeric(dis_pat_df$ci_upper)
head(dis_pat_df)
dis_pat_df$scenarios <- factor(dis_pat_df$scenarios, levels=scenarios)


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
        axis.text.y = element_blank(),
        axis.ticks.y = element_blank(),
        axis.line = element_line(colour = "black"),
        axis.title.x=element_text(size=20), 
        axis.text.x=element_text(size=18),
        axis.text=element_text(size=18),
        plot.margin = unit(c(0.1,0.5,0.1,0.1),"cm"),
        panel.grid.minor=element_line(linetype = 'dotted'),
        panel.grid.major=element_blank()) 
abs_dis_plot

# Reproduction number
data_list[[1]] <- read_excel_allsheets(paste0("../",dataPath_old, "reproduction_number.xlsx"))[[1]]
data_list[[2]] <- read_excel_allsheets(paste0("../",dataPath_new, "reproduction_number.xlsx"))[[1]]
data <- data.frame()
prop <- list()
route_contr <- list(); route_data <- data.frame()
transm <- list(); transm_data <- data.frame()
for(i in 1:length(data_list)){
  colnames(data_list[[i]]) <- c("symptomatic patient", "asymptomatic patient", 
                                "pre-symptomatic HCW", "asymptomatic HCW",
                                "symptomatic patient sum", "asymptomatic patient sum", "patient_to_hcw_sum", "patient_nrow",
                                "symptomatic hcw sum", "asymptomatic hcw sum", "hcw_to_pat_sum", "hcw_to_hcw_sum","hcw_nrow",
                                "total counts")
  prop[[i]] <- data.frame(sympt_pat=numeric(), asympt_pat = numeric(), 
                          sympt_hcw=numeric, asympt_hcw =numeric())
  prop[[i]]<- cbind(sympt_pat = data_list[[i]]["symptomatic patient sum"]/data_list[[i]]["total counts"], 
                    asympt_pat = data_list[[i]]["asymptomatic patient sum"]/data_list[[i]]["total counts"],
                    sympt_hcw = data_list[[i]]["symptomatic hcw sum"]/data_list[[i]]["total counts"],
                    asympt_hcw = data_list[[i]]["asymptomatic hcw sum"]/data_list[[i]]["total counts"])
  colnames(prop[[i]]) <- c("sympt_pat", "asympt_pat", "sympt_hcw", "asympt_hcw")
  
  data_list[[i]]["overall_r"] <- (data_list[[i]]["symptomatic patient sum"] + data_list[[i]]["asymptomatic patient sum"] + data_list[[i]]["symptomatic hcw sum"] + data_list[[i]]["asymptomatic hcw sum"])/(data_list[[i]]["patient_nrow"] + data_list[[i]]["hcw_nrow"]) 
  data <- rbind(data, cbind(melt(data_list[[i]][, 1:4]), scenario = scenarios[i]))
}
data$scenario <- factor(data$scenario, levels=scenarios)
# Interpret NA values as 0
data[which(is.na(data$value)),"value"] <- 0

r_plot <- ggplot(data, aes(x=scenario, y=value, fill=scenario)) + 
  geom_hline(yintercept = 1, lty=2) + 
  geom_violin(width=1.4) +
  geom_boxplot(width=0.1, fill="white") + 
  facet_wrap(~variable) + 
  labs(y="Effective reproduction number") + 
  scale_fill_manual(values=colors_all) + 
  guides(fill=guide_legend(title="",nrow=3,byrow=F)) +
  theme_publication() +
  theme(
    legend.position = "bottom",
    legend.title = element_blank(),
    legend.text = element_text(size=16),
    axis.title.x = element_blank(), 
    axis.text.x=element_blank(),
    axis.ticks.x = element_blank(),
    strip.text=element_text(size=18),
  ) 
r_plot

# Compute overall reproduction number 
overall_r_data <- data.frame()
for(i in 1:length(data_list)){
  overall_r_data <- rbind(overall_r_data, cbind(melt(cbind(scenario=scenarios[i], data_list[[i]]["overall_r"]))))
}

overall_r_data$scenario <- factor(overall_r_data$scenario, levels = scenarios)

overall_r <- ggplot(data=overall_r_data, aes(x=scenario, y=value, fill=scenario)) + 
  geom_hline(yintercept = 1, lty=2) + 
  geom_violin(width=1.4) +
  geom_boxplot(width=0.1, fill="white") + 
  labs(y="Overall effective reproduction number") + 
  scale_fill_manual(values=colors_all) + 
  guides(fill=guide_legend(title="",nrow=3,byrow=F)) +
  theme_publication() +
  theme(
    legend.position = "bottom",
    legend.title = element_blank(),
    legend.text = element_text(size=16),
    axis.title.x = element_blank(), 
    axis.text.x=element_blank(),
    axis.ticks.x = element_blank(),
    strip.text=element_text(size=18),
  ) 
overall_r

left_plot <- align_plots(p, abs_dis_plot, align = 'v', axis = 'l')
right_plot <- align_plots(overall_r+ theme(legend.position = "none"), 
                          r_plot, align='v', axis='l')
plot <- plot_grid(p, 
                  overall_r+ theme(legend.position = "none"),
                  left_plot[[2]],  
                  right_plot[[2]], 
                  ncol=2, rel_widths = c(3.5/6,2.5/6),
                  labels=c("A", "C", "B", "D"), label_size=20)
ggsave(plot, 
       file=paste0("../figures/", parent_folder,"/baseline_old_new_plot.pdf"), 
       width=16, height=11)