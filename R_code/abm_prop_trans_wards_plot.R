# ============================================================================ #
# Agent-based modelling for nosocomial transmission of COVID-19
# ----------------------------------------------------------------------------
# Barplots for proportion of transmissions in different wards
# ============================================================================ #
rm(list=ls())

# Load paths, packages, and functions
source("abm_path_packages.R")
source("abm_functions.R")

# File with percentage of prey-symptomatic, symptomatic and asymptomatic transmission
transmission_wards <- read_excel_allsheets(paste0("../",dataPath, "Perc_transm_covid_and_non_covid_wards.xlsx"))
transm_data <- NULL
for(i in 1:length(transmission_wards)) transm_data <- rbind(transm_data, transmission_wards[[i]])
scenarios <- scenarios[1:length(transmission_wards)]
transm_data <- cbind(scenarios, transm_data)

# Mean values
df <- transm_data[, c(1,which(grepl(" mean",colnames(transm_data))))]
df <- reshape2::melt(df)
colnames(df)[3] <- "mean"

# 95% confidence interval upper bound
df_sdu <- transm_data[, c(1,which(grepl(" ci_upper",colnames(transm_data))))]
df_sdu <- reshape2::melt(df_sdu)
colnames(df_sdu)[3] <- "ci_upper"

# 95% confidence interval lower bound
df_sdl <- transm_data[, c(1,which(grepl(" ci_lower",colnames(transm_data))))]
df_sdl <- reshape2::melt(df_sdl)
colnames(df_sdl)[3] <- "ci_lower"

levels(df$variable) <- levels(df_sdu$variable) <- levels(df_sdl$variable)<- c("COVID", "non-COVID")

data <- merge(df, df_sdu)
data <- merge(data, df_sdl)

data$scenarios <- factor(data$scenarios, levels = scenarios)

# Colors for the different infection states
colors_state <- c("black", "lightgrey")

ward_plot_with_error <- ggplot(data=data, aes(x=scenarios,y=mean, fill=variable)) + 
                          geom_bar(position="dodge", stat="identity", color="black") +
                          geom_errorbar(aes(ymax = ci_upper, ymin=ci_lower), 
                                        position = position_dodge(0.9), width = 0.5) + 
                          coord_flip() +
                          labs(title="Proportion of transmissions in different wards") + 
                          ylab("Proportion of transmissions") + 
                          guides(fill=guide_legend(title=""), reverse=T) +
                          scale_x_discrete(limits = rev(levels(data$scenarios))) + 
                          scale_fill_manual(values=colors_state) + 
                          theme(title = element_text(size=20),
                                plot.title = element_text(hjust=0.5),
                                legend.position = "top",
                                legend.text = element_text(size=14),
                                panel.background = element_blank(),
                                axis.title.y = element_blank(),
                                axis.line = element_line(colour = "black"),
                                axis.title.x=element_text(size=16), 
                                axis.text.x=element_text(size=14),
                                axis.text=element_text(size=14)) 
ward_plot_with_error  

ggsave(plot = ward_plot_with_error, file = paste0(figuresPath, "trans_ward_plot_with_error.pdf"),
       width=12, height=9)

ward_plot <- ggplot(data=data, aes(x=scenarios,y=mean, fill=variable)) + 
                  geom_bar(stat="identity", color="black") +
                  coord_flip() +
                  labs(title="Proportion of transmissions in different wards", color="STATE") + 
                  ylab("Proportion of transmissions (%)") + 
                  guides(fill=guide_legend(title="", reverse = T)) + 
                  scale_x_discrete(limits = rev(levels(data$scenarios))) + 
                  scale_fill_manual(values=colors_state) + 
                  theme(title = element_text(size=26),
                        # plot.title = element_text(hjust=0.5),
                        plot.title = element_blank(),
                        legend.position = "top",
                        legend.text = element_text(size=20),
                        panel.background = element_blank(),
                        axis.title.y = element_blank(),
                        axis.line = element_line(colour = "black"),
                        axis.title.x=element_text(size=20), 
                        axis.text.x=element_text(size=18),
                        axis.text=element_text(size=18)) 
ward_plot  
ggsave(plot = ward_plot, file = paste0(figuresPath, "trans_ward_plot.pdf"),width=12, height=9)



