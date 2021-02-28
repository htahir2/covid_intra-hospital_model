# ============================================================================ #
# Agent-based modelling for nosocomial transmission of COVID-19
# ----------------------------------------------------------------------------
# Positivity rates per day for screening
# Plots for Figure 7 in main manuscript
# ============================================================================ #
rm(list=ls())

# Load paths, packages, and functions
source("abm_path_packages.R")
source("abm_functions.R")

# Files with positivity rates for screening all simulation runs appended 
dates <- seq(as.Date("30-12-2019", format="%d-%m-%Y"),as.Date("24-08-2020", format="%d-%m-%Y"),by=1)
data_list <- read_excel_allsheets(paste0("../",dataPath, "positivity_rates_screening_over_time_all_sim_appended.xlsx"))
abbrev <- c("Scr3_perfect", "Scr3", "Scr7")
data_list <- lapply(1:length(data_list), function(x) data_list[[x]] <- cbind(date = dates[unlist(data_list[[x]]["day"])-1], data_list[[x]]))

# Creating the plots
data <- NULL
plot_conf <- list()
for(i in 1:length(data_list)){
  data[[i]] <- data_list[[i]] %>% group_by(date) %>% summarize(positive_detected = sum(positive_detected), 
                                                               total_screened=sum(total_screened))
  pos_rate <- conf_lower <- conf_upper <- NULL
  for(j in 1:nrow(data[[i]])){
    temp <- binom.bayes(x=data[[i]]$positive_detected[j],n=data[[i]]$total_screened[j])
    pos_rate <- c(pos_rate, temp["mean"]*100)
    conf_lower <- c(conf_lower, temp["lower"]*100)
    conf_upper <- c(conf_upper, temp["upper"]*100)
  }
  data[[i]] <- cbind(data[[i]], pos_rate=unlist(pos_rate), 
                     conf_lower=unlist(conf_lower), 
                     conf_upper=unlist(conf_upper))
  plot_conf[[i]] <- ggplot(data[[i]], aes(x=date)) + 
                      geom_point(aes(y=pos_rate, colour="Positivity rate")) + 
                      geom_line(aes(y=pos_rate, colour="Positivity rate"), size=1.0) + 
                      geom_ribbon(aes(ymin=conf_lower, ymax=conf_upper, fill="(95% confidence interval)"), alpha=0.5) + 
                      scale_colour_manual(values=c("Positivity rate"=colors_PR[i])) +
                      scale_fill_manual(values=c("(95% confidence interval)"=colors_PR[i])) +
                      theme_publication() + 
                      theme(legend.position="none",
                            panel.background = element_blank(),
                            axis.title=element_blank()) 
}
conf_y_max <- max(data[[1]]$conf_upper, data[[2]]$conf_upper, data[[3]]$conf_upper, na.rm = T)
plots_conf <- plot_grid(plot_conf[[1]] + scale_y_continuous(limits=c(0,conf_y_max)), 
                        plot_conf[[2]] + scale_y_continuous(limits=c(0,conf_y_max)),
                        plot_conf[[3]] + scale_y_continuous(limits=c(0,conf_y_max)), 
                        nrow=3, labels = "AUTO",
                        hjust=2.6,vjust=1,label_size=20)
plots_conf <- annotate_figure(plots_conf, 
                              left = text_grob("Positivity rate (%)", size=20, rot=90))
plots_conf <- annotate_figure(plots_conf, 
                              left = text_grob("", size=20, rot=90))
ggsave(plots_conf, file=paste0(figuresPath, "pos_rate_screening_over_time_bayes_binom.pdf"), width=12, height=9)