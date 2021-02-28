# ============================================================================ #
# Agent-based modelling for nosocomial transmission of COVID-19
# ----------------------------------------------------------------------------
# Daily percentage of absent HCWs
# Figure 6 in main manuscript
# ============================================================================ #
rm(list=ls())

# Load paths, packages, and functions
source("abm_path_packages.R")
source("abm_functions.R")

# Files with dates and daily absent HCWs
dates <- seq(as.Date("17-02-2020", format="%d-%m-%Y"),as.Date("24-08-2020", format="%d-%m-%Y"),by=1)
data_list <- read_excel_allsheets(paste0("../", dataPath, "percent_daily_absent_hcws.xlsx"))
scenarios <- scenarios[1:length(data_list)]
colors_all <- colors_all[1:length(data_list)]

data_list <- lapply(data_list, function(x) cbind(date=dates, x[((nrow(x)-190)+1):nrow(x),]))
names(data_list) <- scenarios

# Moving average of mean and credibility intervals
data_list <- lapply(data_list, function(x){ colnames(x) <- c("date", "mean", "ci_upper", "ci_lower"); 
                                            cbind(x, ma_mean = ma(x$mean, n=7), 
                                                  ma_ci_lower = ma(x$ci_lower, n=7), 
                                                  ma_ci_upper = ma(x$ci_upper, n=7))})

# Data in long format
data <- bind_rows(data_list, .id="scenarios")
data$scenarios <- factor(data$scenarios, levels=scenarios)
colnames(data) <- c("scenarios", "date", "mean", "ci_upper", "ci_lower", "ma_mean", "ma_ci_lower", "ma_ci_upper")
data$date <- as.Date(data$date, format="%Y-%m-%d")


# Plot of daily absent HCWs (moving averages)
ma_plot <- ggplot(data) + 
  geom_line(aes(x=date, y=ma_mean, color = scenarios), size=2) + 
  labs(title="Daily percentage of absent HCWs\n(7-day moving average)", y="Percentage of absent HCWs (%)") +
  scale_colour_manual(values=colors_all) + 
  scale_x_date(date_breaks="1 week", date_labels="%d %b") +
  guides(color=guide_legend(override.aes = list(size = 1.4),nrow=3,byrow=F)) +
  theme_publication() + 
  theme(title = element_text(size=20), 
        plot.title = element_blank(),
        legend.position = "bottom",
        legend.title = element_blank(),
        legend.text = element_text(size=16),
        legend.background = element_blank(),
        panel.background = element_blank(),
        axis.line = element_line(colour = "black"),
        axis.title.x=element_blank(), 
        axis.text.x=element_text(size=18, angle=45, hjust=1),
        axis.text.y=element_text(size=20)#,
  ) 
ggsave(plot = ma_plot, file = paste0(figuresPath, "daily_absent_hcws_ma7_plot.pdf"), 
       width=12, height=9)