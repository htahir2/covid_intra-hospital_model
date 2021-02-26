# ============================================================================ #
# Agent-based modelling for nosocomial transmission of COVID-19
# ----------------------------------------------------------------------------
# Positivity rates per day for screening
# ============================================================================ #
rm(list=ls())

# Load paths, packages, and functions
source("abm_path_packages.R")
source("abm_functions.R")

# ============================================================================ #
# Files with positivity rates for screening all simulation runs appended 
# ============================================================================ #
dates <- seq(as.Date("30-12-2019", format="%d-%m-%Y"),as.Date("24-08-2020", format="%d-%m-%Y"),by=1)
data_list <- read_excel_allsheets(paste0("../",dataPath, "positivity_rates_screening_over_time_all_sim_appended.xlsx"))
abbrev <- c("Scr3_perfect", "Scr3", "Scr7")
data_list <- lapply(1:length(data_list), function(x) data_list[[x]] <- cbind(date = dates[unlist(data_list[[x]]["day"])-1], data_list[[x]]))

data <- NULL
plot_conf <- list()
for(i in 1:length(data_list)){
  # data_list[[i]] <- cbind(date = dates[unlist(data_list[[i]]["day"])-1], data_list[[i]])
  data[[i]] <- data_list[[i]] %>% group_by(date) %>% summarize(positive_detected = sum(positive_detected), 
                                                               total_screened=sum(total_screened))
  pos_rate <- conf_lower <- conf_upper <- NULL
  for(j in 1:nrow(data[[i]])){
    # temp <- binom_test(x=data[[i]]$positive_detected[j],n=data[[i]]$total_screened[j])
    # pos_rate <- c(pos_rate, temp[,"estimate"]*100)
    # conf_lower <- c(conf_lower, temp[,"conf.low"]*100)
    # conf_upper <- c(conf_upper, temp[,"conf.high"]*100)
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
# plots_conf
ggsave(plots_conf, file=paste0(figuresPath, "pos_rate_screening_over_time_bayes_binom.pdf"), width=12, height=9)



# ============================================================================ #
# Files with positivity rates and percentiles over simulation runs
# ============================================================================ #
# dates <- seq(as.Date("17-02-2020", format="%d-%m-%Y"),as.Date("24-08-2020", format="%d-%m-%Y"),by=1)
# positivity_rates <- read_excel_allsheets(paste0("../",dataPath, "Positivity_rate_screening.xlsx"))
# abbrev <- c("Scr3_perfect", "Scr3", "Scr7")
# for(i in 1:length(positivity_rates)){
#   positivity_rates[[i]] <- cbind(date=dates[positivity_rates[[i]][,1]-1], positivity_rates[[i]][,-1])
#   colnames(positivity_rates[[i]]) <- c("days", paste0("mean_",abbrev[i]),
#                                        paste0("ci_lower_",abbrev[i]),
#                                        paste0("ci_upper_",abbrev[i]))
# }
# ma_data <- list()
# for(i in 1:length(positivity_rates)){
#   colnames(positivity_rates[[i]]) <- c("days","mean","ci_lower","ci_upper")
#   positivity_rates[[i]] <- as.data.frame(positivity_rates[[i]])
#   ma_temp <- ma(positivity_rates[[i]]$mean, n=7)
#   ma_data[[i]] <- as.data.frame(cbind(days=positivity_rates[[i]]$days, ma=ma_temp))
# }
# 
# colors <- c("#daf33c", "#6ccf43", "#438c23")
# y_max <- max(positivity_rates[[1]]$ci_upper, positivity_rates[[2]]$ci_upper, positivity_rates[[3]]$ci_upper)
# 
# p1 <- ggplot(data=positivity_rates[[1]]) + 
#   geom_point(aes(x=days, y=mean), color=colors[1], size=2) + 
#   geom_line(aes(x=days, y=mean), color=colors[1], size=1.1) + 
#   # geom_line(data=ma_data[[1]], aes(x=days, y=ma)) + 
#   geom_ribbon(aes(x=days, ymin=ci_lower, ymax=ci_upper), alpha=0.3, fill=colors[1])+
#   # ylab("Positivity rate") + 
#   scale_y_continuous(limits = c(0,y_max)) + 
#   theme_publication() + 
#   theme(title = element_text(size=16), 
#         plot.title = element_text(hjust=-0.042),
#         legend.position="none",
#         panel.background = element_blank(),
#         axis.line = element_line(colour = "black"),
#         axis.title=element_blank(), 
#         axis.text.x = element_blank(), 
#         axis.ticks.x = element_blank(), 
#         plot.margin = unit(c(0.4, 0.1, 1.5, 0.1), "lines")) 
# p2 <- ggplot(data=positivity_rates[[2]]) + 
#   geom_point(aes(x=days, y=mean), color=colors[2], size=2) + 
#   geom_line(aes(x=days, y=mean), color=colors[2], size=1.1) + 
#   # geom_line(data=ma_data[[2]], aes(x=days, y=ma)) + 
#   geom_ribbon(aes(x=days, ymin=ci_lower, ymax=ci_upper), alpha=0.3, fill=colors[2])+
#   # ylab("Positivity rate") + 
#   scale_y_continuous(limits = c(0,y_max)) + 
#   theme_publication() + 
#   theme(title = element_text(size=16), 
#         plot.title = element_text(hjust=-0.03),
#         legend.position="none",
#         panel.background = element_blank(),
#         axis.line = element_line(colour = "black"),
#         axis.title=element_blank(), 
#         axis.text.x = element_blank(), 
#         axis.ticks.x = element_blank(), 
#         plot.margin = unit(c(0.1, 0.1, 1.5, 0.1), "lines")) 
# p3 <- ggplot(data=positivity_rates[[3]]) + 
#   geom_point(aes(x=days, y=mean), color=colors[3], size=2) + 
#   geom_line(aes(x=days, y=mean), color=colors[3], size=1.1) +
#   # geom_line(data=ma_data[[3]], aes(x=days, y=ma)) + 
#   geom_ribbon(aes(x=days, ymin=ci_lower, ymax=ci_upper), alpha=0.3, fill=colors[3])+
#   # ylab("Positivity rate") + 
#   scale_y_continuous(limits = c(0,y_max)) + 
#   theme_publication() + 
#   theme(title = element_text(size=16), 
#         plot.title = element_text(hjust=-0.03),
#         legend.position="none",
#         panel.background = element_blank(),
#         axis.line = element_line(colour = "black"),
#         axis.title=element_blank(), 
#         plot.margin = unit(c(0.1, 0.1, 0.1, 0.1), "lines")) 
# 
# combined <- plot_grid(p1,p2,p3, nrow=3, labels="AUTO",
#                       hjust=2.6,vjust=1, label_size=20, align="v")
# combined <- annotate_figure(combined,
#                             left = text_grob("Positivity rate (%)", size=18, rot=90))
# combined <- annotate_figure(combined,
#                             left = text_grob("", size=18, rot=90))
# combined
# 
# ggsave(plot = combined, file = paste0(figuresPath, "positivity_rates_screening_per_day_plot.pdf"),width=12, height=9)
