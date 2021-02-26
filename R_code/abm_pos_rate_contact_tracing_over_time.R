# ============================================================================ #
# Agent-based modelling for nosocomial transmission of COVID-19
# ----------------------------------------------------------------------------
# Positivity rates for contact tracing over time
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

data <- plot <- plot_ma <- plot_ma_leg <- ratio <- leg <-  plot_leg <- plot_error <- plot_smooth <- plot_conf <- list()
n_ma <- 7
for(i in 1:length(data_list)){
  data[[i]] <- data_list[[i]] %>% group_by(date) %>% summarize(n_contacts_traced = sum(n_contacts_traced)-sum(n_sympt_patients_traced)-sum(n_sympt_hcws_traced), 
                                                               p_rate=ifelse(sum(n_pos_contacts)>0, 100*sum(n_pos_contacts)/sum(n_contacts_traced), NA),
                                                               n_contacts = sum(n_contacts_traced),
                                                               n_pos_contacts = sum(n_pos_contacts),
                                                               n_index = sum(n_pos),
                                                               mean=mean(pos_rate),median=median(pos_rate), 
                                                               ci_lower = quantile(pos_rate, 0.025), 
                                                               ci_upper = quantile(pos_rate, 0.975))
  data[[i]] <- cbind(data[[i]], ma=ma(data[[i]]$mean, n=n_ma), ma_ci_lower = ma(data[[i]]$ci_lower, n=n_ma), ma_ci_upper = ma(data[[i]]$ci_upper, n=n_ma))
  data[[i]] <- cbind(data[[i]], scenario=scenarios[6+i])
  pos_rate <- conf_lower <- conf_upper <- NULL
  for(j in 1:nrow(data[[i]])){
    temp <- binom.bayes(x=data[[i]]$n_pos_contacts[j],n=data[[i]]$n_contacts_traced[j])
    pos_rate <- c(pos_rate, temp["mean"]*100)
    conf_lower <- c(conf_lower, temp["lower"]*100)
    conf_upper <- c(conf_upper, temp["upper"]*100)
    # temp <- binom_test(x=data[[i]]$n_pos_contacts[j],n=data[[i]]$n_contacts_traced[j])
    # pos_rate <- c(pos_rate, temp[,"estimate"]*100)
    # conf_lower <- c(conf_lower, temp[,"conf.low"]*100)
    # conf_upper <- c(conf_upper, temp[,"conf.high"]*100)
  }
  data[[i]] <- cbind(data[[i]], pos_rate=ma(unlist(pos_rate), n=n_ma),
                     conf_lower=ma(unlist(conf_lower),n=n_ma),
                     conf_upper=ma(unlist(conf_upper), n=n_ma))
  # data[[i]] <- cbind(data[[i]], pos_rate=unlist(pos_rate), 
  #                    conf_lower=unlist(conf_lower), 
  #                    conf_upper=unlist(conf_upper))
  plot_conf[[i]] <- ggplot(data[[i]], aes(x=date)) + 
    geom_point(aes(y=pos_rate, colour="Positivity rate")) + 
    geom_line(aes(y=pos_rate, colour="Positivity rate"), size=1.3) + 
    geom_ribbon(aes(ymin=conf_lower, ymax=conf_upper, fill="(95% confidence interval)"), alpha=0.5) + 
    scale_colour_manual(values=c("Positivity rate"=colors_PR[3+i])) +
    scale_fill_manual(values=c("(95% confidence interval)"=colors_PR[3+i])) +
    theme_publication() + 
    theme(legend.position="none",
          panel.background = element_blank(),
          axis.title=element_blank()) 
  ratio[[i]] <- ceiling(max(data[[i]]$n_contacts_traced, na.rm = T)/max(data[[i]]$p_rate, na.rm = T))
  plot[[i]] <- ggplot(data[[i]], aes(x=date, y=p_rate)) + 
    geom_bar(stat="identity", aes(y=n_contacts/ratio[[i]], fill="Number of tested contacts"), alpha=0.5) + 
    geom_point(aes(y=p_rate, colour="Positivity rate")) + 
    geom_bar(stat="identity", aes(y=n_pos_contacts/ratio[[i]], fill="Number of positive contacts"), alpha=0.8) +
    scale_colour_manual(values=c("Positivity rate"=colors_PR[3+i])) +
    scale_fill_manual(values=c("Number of tested contacts"="dimgrey","Number of positive contacts"="grey20")) +
    scale_y_continuous(sec.axis = sec_axis(~.*ratio[[i]])) + 
    theme_publication() + 
    theme(legend.position="none",
          panel.background = element_blank(),
          axis.title=element_blank()) 
  plot_leg[[i]] <- ggplot(data[[i]], aes(x=date, y=p_rate)) + 
    geom_bar(stat="identity", aes(y=n_contacts/ratio[[i]], fill="Number of tested contacts"), alpha=0.5) + 
    geom_point(aes(y=p_rate, colour="Positivity rate")) + 
    geom_bar(stat="identity", aes(y=n_pos_contacts/ratio[[i]], fill="Number of positive contacts"), alpha=0.8) +
    scale_colour_manual(values=c("Positivity rate"=colors_PR[3+i])) +
    scale_fill_manual(values=c("Number of tested contacts"="dimgrey","Number of positive contacts"="grey20")) +
    scale_y_continuous(sec.axis = sec_axis(~.*ratio[[i]])) + 
    theme_publication() + 
    theme(legend.position="bottom",
          panel.background = element_blank(),
          axis.title=element_blank(), 
          legend.text = element_text(size=18),
          legend.title = element_blank()) 
  leg[[i]] <- get_legend(plot_leg[[i]])
  plot_ma[[i]] <- ggplot(data[[i]], aes(x=date, y=p_rate)) + 
    geom_bar(stat="identity", aes(y=n_contacts/ratio[[i]], fill="Number of tested contacts"), alpha=0.5) + 
    geom_line(aes(y=ma, colour="Positivity rate (7-day moving average)"), size=1.3) + 
    geom_bar(stat="identity", aes(y=n_pos_contacts/ratio[[i]], fill="Number of positive contacts"), alpha=0.8) +
    scale_colour_manual(values=c("Positivity rate (7-day moving average)"=colors_PR[3+i])) +
    scale_fill_manual(values=c("Number of tested contacts"="dimgrey","Number of positive contacts"="grey20")) +
    scale_y_continuous(sec.axis = sec_axis(~.*ratio[[i]])) + 
    theme_publication() + 
    theme(legend.position="none",
          panel.background = element_blank(),
          axis.title=element_blank())
  plot_ma_leg[[i]] <- ggplot(data[[i]], aes(x=date, y=p_rate)) + 
    geom_bar(stat="identity", aes(y=n_contacts/ratio[[i]], fill="Number of tested contacts"), alpha=0.5) + 
    geom_line(aes(y=ma, colour="Positivity rate (7-day moving average)"), size=1.3) + 
    geom_bar(stat="identity", aes(y=n_pos_contacts/ratio[[i]], fill="Number of positive contacts"), alpha=0.8) +
    scale_colour_manual(values=c("Positivity rate (7-day moving average)"=colors_PR[3+i])) +
    scale_fill_manual(values=c("Number of tested contacts"="dimgrey","Number of positive contacts"="grey20")) +
    scale_y_continuous(sec.axis = sec_axis(~.*ratio[[i]])) + 
    theme_publication() + 
    theme(legend.position="bottom",
          panel.background = element_blank(),
          axis.title=element_blank(), 
          legend.text = element_text(size=18),
          legend.title = element_blank())
  plot_error[[i]] <- ggplot(data[[i]], aes(x=date)) + 
    # geom_point(aes(y=ma, colour="Positivity rate (mean)"), size=1.3)+
    geom_line(aes(y=ma, colour="Positivity rate (mean)"), size=1.3) + 
    geom_ribbon(aes(ymin=ma_ci_lower, ymax=ma_ci_upper, fill="Uncertainty interval"),alpha=0.5) + 
    scale_colour_manual(values=c("Positivity rate (mean)"=colors_PR[3+i])) +
    scale_fill_manual(values=c("Uncertainty interval"=colors_PR[3+i])) +
    theme_publication() + 
    theme(legend.position="none",
          panel.background = element_blank(),
          axis.title=element_blank())
  plot_smooth[[i]] <- ggplot(data[[i]], aes(x=date, y=p_rate)) + 
    geom_point(colour=colors_PR[3+i]) + 
    geom_smooth(method = "lm", formula = y ~ poly(x, 10), se=T, colour=colors_PR[3+i]) +
    geom_bar(stat="identity", aes(y=n_contacts/ratio[[i]], fill="Number of tested contacts"), alpha=0.5) + 
    geom_bar(stat="identity", aes(y=n_pos_contacts/ratio[[i]], fill="Number of positive contacts"), alpha=0.8) +
    scale_y_continuous(sec.axis = sec_axis(~.*ratio[[i]])) + 
    scale_colour_manual(values=c("Positivity rate (mean)"=colors_PR[3+i])) +
    scale_fill_manual(values=c("Number of tested contacts"="dimgrey","Number of positive contacts"="grey20")) +
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
                        hjust=2.6,label_size=20)
plots_conf <- annotate_figure(plots_conf, 
                              left = text_grob("Positivity rate (%)", size=20, rot=90))
plots_conf <- annotate_figure(plots_conf, 
                              left = text_grob("", size=20, rot=90))
# plots_conf
ggsave(plots_conf, file=paste0(figuresPath, "pos_rate_contact_tracing_over_time_bayes_binom.pdf"), width=12, height=9)



# # Moving average with percentile plot
# error_y_max <- max(data[[1]]$ma_ci_upper, data[[2]]$ma_ci_upper, data[[3]]$ma_ci_upper, na.rm = T)
# plots_error <- plot_grid(plot_error[[1]] + scale_y_continuous(limits=c(0,error_y_max)), 
#                          plot_error[[2]] + scale_y_continuous(limits=c(0,error_y_max)),
#                          plot_error[[3]] + scale_y_continuous(limits=c(0,error_y_max)), 
#                          nrow=3, labels = "AUTO",
#                          hjust=2.6,label_size=20,
#                          rel_heights = c(3.2/10,3.2/10,3.6/10))
# plots_error <- annotate_figure(plots_error, 
#                                left = text_grob("Positivity rate (%)", size=20, rot=90))
# plots_error <- annotate_figure(plots_error, 
#                                left = text_grob("", size=20, rot=90))
# plots_error
# 
# ggsave(plots_error, file=paste0(figuresPath, "positivity_rate_contact_tracing_percentile.pdf"), width = 12, height=9)
# 
# 
# # Smoothing
# {
#   smooth_y_max <- max(data[[1]]$p_rate, data[[2]]$p_rate, data[[3]]$p_rate, na.rm = T)
#   plots_smooth <- plot_grid(plot_smooth[[1]]+ scale_y_continuous(limits=c(0,smooth_y_max),sec.axis = sec_axis(~.*ratio[[i]])), 
#                             plot_smooth[[2]]+ scale_y_continuous(limits=c(0,smooth_y_max),sec.axis = sec_axis(~.*ratio[[i]])), 
#                             plot_smooth[[3]]+ scale_y_continuous(limits=c(0,smooth_y_max),sec.axis = sec_axis(~.*ratio[[i]])), 
#                             nrow=3, labels = "AUTO", hjust=2.6,label_size=20,
#                             rel_heights = c(3.2/10,3.2/10,3.6/10))
#   plots_smooth <- annotate_figure(plots_smooth, 
#                                   left = text_grob("Positivity rate (%)", size=20, rot=90))
#   plots_smooth <- annotate_figure(plots_smooth,
#                                   left = text_grob("", size=20, rot=90))
#   plots_smooth
#   
#   ggsave(plots_smooth, file=paste0(figuresPath, "positivity_rate_contact_tracing_spline_smooth.pdf"), 
#          width = 12, height=9)
# }
# 
# # Moving average with bar plots
# {
#   plots_ma <- plot_grid(plot_ma[[1]], plot_ma[[2]], plot_ma_leg[[3]], nrow=3, 
#                         labels = "AUTO", hjust=1.0, label_size=18, 
#                         rel_heights = c(3.2/10,3.2/10,3.6/10))
#   plots_ma <- annotate_figure(plots_ma, 
#                               right = text_grob("Number of tests", size=20, rot=270),
#                               left = text_grob("Positive tests (%)", size=20, rot=90))
#   plots_ma
# }
# 
# # Point plot with bar plots
# {
#   plots <- plot_grid(plot[[1]], plot[[2]], plot_leg[[3]], nrow=3, labels = "AUTO",
#                      hjust=1,label_size=20,
#                      rel_heights = c(3.2/10,3.2/10,3.6/10))
#   plots <- annotate_figure(plots, 
#                            right = text_grob("Number of tests", size=20, rot=270),
#                            left = text_grob("Positive tests (%)", size=20, rot=90))
#   plots
# }
# 
# ggsave(plots, file=paste0(figuresPath, "pos_rate_contact_tracing_per_day.pdf"), width=12, height=9)
# ggsave(plots_ma, file=paste0(figuresPath, "pos_rate_ma_contact_tracing_per_day.pdf"), width=12, height=9)
