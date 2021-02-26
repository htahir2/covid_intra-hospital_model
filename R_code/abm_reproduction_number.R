# ============================================================================ #
# Agent-based modelling for nosocomial transmission of COVID-19
# ----------------------------------------------------------------------------
# Reproduction number
# ============================================================================ #
rm(list=ls())

# Load paths, packages, and functions
source("abm_path_packages.R")
source("abm_functions.R")

# File from simulation (reproduction numbers per simulation for each scenario)
data_list <- read_excel_allsheets(paste0("../",dataPath, "reproduction_number.xlsx"))
data <- data.frame()
prop <- list()
route_contr <- list(); route_data <- data.frame()
transm <- list(); transm_data <- data.frame()
for(i in 1:length(data_list)){
  colnames(data_list[[i]]) <- c("symptomatic patient", "asymptomatic patient", 
                                "pre-symptomatic HCW", "asymptomatic HCW",
                                "symptomatic patient sum", "asymptomatic patient sum", "patient_nrow",
                                "symptomatic hcw sum", "asymptomatic hcw sum", "hcw_nrow",
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
data[which(is.na(data$value)),"value"] <- 0 # # Interpret NA values as 0

# Plot of reproduction number stratified by status and type of individual
# symptotmatic/asymptomatic patient
# pre-symptomatic/asymptomatic patient
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
    strip.text=element_text(size=20),
  ) 
ggsave(r_plot, file=paste0(figuresPath, "reproduction_number_per_status_plot.pdf"), width=12,height=9)

# Overall reproduction number 
overall_r_data <- data.frame()
for(i in 1:length(data_list)){
  overall_r_data <- rbind(overall_r_data, cbind(melt(cbind(scenario=scenarios[i], data_list[[i]]["overall_r"]))))
}
overall_r_data$scenario <- factor(overall_r_data$scenario, levels = scenarios)

# Plot of overall reprodcution number
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
    strip.text=element_text(size=20),
  ) 
plot <- plot_grid(overall_r+ theme(legend.position = "none"),r_plot, nrow=2, labels="AUTO", label_size=20)
ggsave(plot, file=paste0(figuresPath, "reproduction_number_plot.pdf"), width=12, height=14)


# summary(overall_r_data$value[overall_r_data$scenario=="Baseline"])
# (mean_overall <- overall_r_data %>% group_by(scenario) %>% summarize(mean=round(mean(value, na.rm=TRUE),2)))
# Reduction in overall R
# overall_r_data %>% group_by(scenario) %>% summarize(reduction=(1-round(mean(value, na.rm=TRUE),2)/mean_overall[mean_overall$scenario=="Baseline","mean"])*100)