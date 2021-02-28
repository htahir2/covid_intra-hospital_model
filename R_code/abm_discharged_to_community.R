# ============================================================================ #
# Agent-based modelling for nosocomial transmission of COVID-19
# ----------------------------------------------------------------------------
# Discharged patients with COVID-19
# Used for plots in Figure 5
# ============================================================================ #
# Load paths, packages, and functions
source("abm_path_packages.R")
source("abm_functions.R")

# Files with peak numbers (patients)
data_list <- read_excel_allsheets(paste0("../",dataPath, "discharged_covid19patients.xlsx"))
dates <- seq(as.Date("17-02-2020", format="%d-%m-%Y"),as.Date("24-08-2020", format="%d-%m-%Y"),by=1)
data_list <- lapply(data_list, function(x) cbind(date=dates, x[(nrow(x)-length(dates)+1):nrow(x),]))
names(data_list) <- scenarios

# Data in long format
data <- bind_rows(data_list, .id="scenarios")
data$scenarios <- factor(data$scenarios, levels=scenarios)
colnames(data) <- c("scenarios", "date", "mean", "median", "ci_upper", "ci_lower")
data$date <- as.Date(data$date, format="%Y-%m-%d")

# Total number of discharged patients at the end of the study period
dis_pat <- lapply(data_list, function(x) c(x$mean[nrow(x)],x$ci_lower[nrow(x)],x$ci_upper[nrow(x)]))
dis_pat_df <- as.data.frame(cbind(scenarios, t(bind_rows(dis_pat, .id="scenarios"))), row.names=F)
colnames(dis_pat_df) <- c("scenarios", "mean", "ci_lower", "ci_upper")
dis_pat_df$mean <- as.numeric(dis_pat_df$mean)
dis_pat_df$ci_lower <- as.numeric(dis_pat_df$ci_lower)
dis_pat_df$ci_upper <- as.numeric(dis_pat_df$ci_upper)
dis_pat_df$scenarios <- factor(dis_pat_df$scenarios, levels=scenarios)

# Plot with total number of patients discharged with COVID-19
# (pre-symptotmatic and asymptomatic infected patients)
dis_plot <- ggplot(dis_pat_df, aes(x=scenarios, y=mean, colour=scenarios)) + 
  geom_bar(stat="identity", width=0.5, color=colors_all, fill=colors_all) +
  geom_errorbar(aes(ymax = ci_upper, ymin=ci_lower), position = position_dodge(0.9), width = 0.3, color="grey") +
  coord_flip() +       
  ylab("Total number of patients discharged with SARS-CoV-2 infection") + 
  theme_publication() +
  scale_fill_manual(values=colors_all) +
  scale_x_discrete(limits = rev(levels(dis_pat_df$scenarios))) +
  theme(title = element_text(size=26), 
        plot.title = element_blank(),
        legend.position="none",
        panel.background = element_blank(),
        axis.title.y = element_blank(),
        axis.line = element_line(colour = "black"),
        plot.margin = unit(c(0.1,0.5,0.1,0.1),"cm"),
        panel.grid.minor=element_line(linetype = 'dotted'),
        panel.grid.major=element_blank()) 
# ggsave(plot=dis_plot, file = paste0(figuresPath, "discharged_covid19_patients_barplot.pdf"), width=16,height=12)

# Plot of patients discharged with COVID-19 over time
data_plot <- ggplot(data) + 
                geom_line(aes(x=date, y=mean, color = scenarios),size=1.3) + 
                labs(title="Cumulative number of COVID-19 patients discharged to community", y="Cumulative number of patients") +
                scale_colour_manual(values=colors_all) + 
                scale_x_date(date_breaks="1 week", date_labels="%d %b") +
                guides(color = guide_legend(override.aes = list(size = 1.5))) + 
                theme(title = element_text(size=30), 
                      plot.title = element_text(hjust=0.5),
                      legend.position = "bottom",
                      legend.title = element_blank(),
                      legend.text = element_text(size=22),
                      legend.background = element_blank(),
                      panel.background = element_blank(),
                      axis.title.y = element_text(size=24),
                      axis.line = element_line(colour = "black"),
                      axis.title.x=element_blank(), 
                      axis.text.x=element_text(size=18, angle=45, hjust=1),
                      axis.text=element_text(size=18)) 
# ggsave(plot=data_plot, file = paste0(figuresPath, "discharged_covid19_patients_over_time.pdf"), width=16,height=12)

# Same as before but plotted with facet_wrap
facet_plot <- ggplot(data) + 
                facet_wrap(~scenarios) + 
                geom_line(aes(x=date, y=mean, color=scenarios),size=1.1) + 
                geom_ribbon(aes(x=date, ymin=ci_lower, ymax=ci_upper, fill=scenarios), alpha=0.3, color=NA)+
                labs(title="Cumulative number of COVID-19 patients discharged to community", y="Cumulative number of patients") +
                scale_fill_manual(values = colors_all, aesthetics = c("color", "fill")) +
                scale_x_date(date_breaks="1 month", date_labels="%b") +
                theme_bw() + 
                theme(title = element_text(size=30), 
                      plot.title = element_text(hjust=0.5),
                      legend.position = "none",
                      legend.title = element_blank(),
                      legend.text = element_text(size=22),
                      panel.background = element_blank(),
                      axis.title.y = element_text(size=24),
                      axis.line = element_line(colour = "black"),
                      axis.title.x=element_blank(), 
                      axis.text=element_text(size=18),
                      strip.text=element_text(size=18)) 
# ggsave(facet_plot, file = paste0(figuresPath, "discharged_covid19_patients_over_time_facet.pdf"), width=16,height=12)
