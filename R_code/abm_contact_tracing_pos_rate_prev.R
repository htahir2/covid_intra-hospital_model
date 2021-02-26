# ============================================================================ #
# Agent-based modelling for nosocomial transmission of COVID-19
# ----------------------------------------------------------------------------
# Positivity rates for contact tracing
# ============================================================================ #
rm(list=ls())

# Load paths, packages, and functions
source("abm_path_packages.R")
source("abm_functions.R")

# File with positivity rates per simulation for contact tracing
dates <- seq(as.Date("30-12-2019", format="%d-%m-%Y"),as.Date("24-08-2020", format="%d-%m-%Y"),by=1)
data_list <- read_excel_allsheets(paste0("../",dataPath, "positivity_rates_contact_tracing_over_time_all_sim_appended.xlsx"))
for(i in 1:length(data_list)){
  colnames(data_list[[i]]) <- c("n_contacts_traced","n_pos_contacts","contact_tracing_time",
                                "n_sympt_patients_traced", "hcw_time_of_infection","hcw_current_ward",
                                "n_sympt_hcws_traced","day","sim","prevalence","n_total","n_pos","pos_rate")
  data_list[[i]] <- cbind(date = dates[unlist(data_list[[i]]["day"])-1], data_list[[i]])
  data_list[[i]]$prev <-  data_list[[i]]$n_pos/data_list[[i]]$n_total
}

names <- c("7d_perfect_sens","2d","7d")
breaks <- 20
p <- list()
for(j in 1:length(data_list)){
  data <- binomial.prop(data_list[[j]], nbreaks=breaks, ct=T)
  p[[j]] <- plot.pos.rate.prev(data)
  # ggsave(p[[j]], file=paste0(figuresPath, "pos_rate_prev_plot_contact_tracing_", names[j],"_", breaks, "breaks", ".eps"), width=12, height=9)
}

comb <- plot_grid(p[[1]],p[[2]],p[[3]],nrow=3,labels="AUTO",hjust=2.6, vjust=1, label_size=20)
comb <- annotate_figure(comb, 
                bottom = text_grob("prevalence (%)", size=20),
                left = text_grob("positivity rate (%)", size=20, rot=90))
comb <- annotate_figure(comb, 
                        left = text_grob("", size=20, rot=90))
# comb
ggsave(comb, file=paste0(figuresPath, "contact_tracing_pos_rate_prev_plot_",
                         breaks, "breaks", ".pdf"), width=16, height=12)
