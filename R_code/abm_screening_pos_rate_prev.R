# ============================================================================ #
# Agent-based modelling for nosocomial transmission of COVID-19
# ----------------------------------------------------------------------------
# Positivity rates for screening and contact tracing
# ============================================================================ #
rm(list=ls())

# Load paths, packages, and functions
source("abm_path_packages.R")
source("abm_functions.R")
library(tidyverse)

# File with positivity rates per simulation for contact tracing
dates <- seq(as.Date("30-12-2019", format="%d-%m-%Y"),as.Date("24-08-2020", format="%d-%m-%Y"),by=1)
data_list <- read_excel_allsheets(paste0("../", dataPath, "positivity_rates_screening_over_time_all_sim_appended.xlsx"))
for(i in 1:length(data_list)){
  colnames(data_list[[i]]) <- c("day","n_contacts_traced","n_pos_contacts","prev", "pos_rate")
  data_list[[i]] <- cbind(date = dates[unlist(data_list[[i]]["day"])-1], data_list[[i]])
}


names <- c("3d_perfect_sens","3d","7d")
plot_titles <- c("A","B","C")
breaks <- 20
p <- list()
for(j in 1:length(data_list)){
  data <- binomial.prop(data_list[[j]], nbreaks=breaks, ct=F)
  p[[j]] <- plot.pos.rate.prev(data, title=plot_titles[j])
  # ggsave(p[[j]], file=paste0("../figures/pos_rate_prev_plot_screening_", names[j],"_", breaks, "breaks", ".eps"), width=12, height=9)
}
comb <- plot_grid(p[[1]],p[[2]],p[[3]],nrow=3,labels="AUTO",hjust=3.0,vjust=1, align="v")
comb <- annotate_figure(comb, 
                bottom = text_grob("prevalence (%)", size=20),
                left = text_grob("positivity rate (%)", size=20, rot=90))
comb <- annotate_figure(comb, 
                        left = text_grob("", size=20, rot=90))
# comb
ggsave(comb, file=paste0(figuresPath, "screening_pos_rate_prev_plot_",
                         breaks, "breaks", ".pdf"), width=16, height=12)
