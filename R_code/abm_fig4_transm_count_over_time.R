# ============================================================================ #
# Agent-based modelling for nosocomial transmission of COVID-19
# ----------------------------------------------------------------------------
# Number of transmissions plot over time
# Plots for Figure 4 in main manuscript
# ============================================================================ #
rm(list=ls())

# Load paths, packages, and functions
source("abm_path_packages.R")
source("abm_functions.R")

# ============================================================================ #
# Files with dates and daily nosocomial transmissions (patients)
dates <- seq(as.Date("17-02-2020", format="%d-%m-%Y"),as.Date("24-08-2020", format="%d-%m-%Y"),by=1)
data_list <- read_excel_allsheets(paste0("../", dataPath, "transm_pat_over_time.xlsx"))
data_list <- lapply(data_list, function(x) cbind(date=dates, x[(nrow(x)-length(dates)+1):nrow(x),]))
scenarios <- scenarios[1:length(data_list)]
names(data_list) <- scenarios

# Moving average of mean and credibility intervals
data_list <- lapply(data_list, function(x){ colnames(x) <- c("date", "mean", "ci_lower", "ci_upper"); 
cbind(x, ma_mean = ma(x$mean, n=7), 
      ma_ci_lower = ma(x$ci_lower, n=7), 
      ma_ci_upper = ma(x$ci_upper, n=7));})

data <- bind_rows(data_list, .id="scenarios")
data$scenarios <- factor(data$scenarios, levels=scenarios)
colnames(data) <- c("scenarios", "date", "mean", "ci_lower", "ci_upper", "ma_mean", "ma_ci_lower", "ma_ci_upper")
data$date <- as.Date(data$date, format="%Y-%m-%d")

# Plot for Figure 4A
data_plot <- ggplot(data) + 
  geom_line(aes(x=date, y=ma_mean, color = scenarios), size=1.3) + 
  # labs(title="Mean number of nosocomial transmissions over time \n(7-day moving average)", y="Number of patients") +
  labs(y="Number of patients") +
  scale_colour_manual(values=colors_all) + 
  scale_x_date(date_breaks="1 week", date_labels="%d %b",breaks=dates, minor_breaks = "4 weeks") +
  guides(color = guide_legend(override.aes = list(size = 1.2))) + 
  theme_publication() + 
  theme(title = element_text(size=20), 
        legend.position = "none",
        panel.background = element_blank(),
        axis.title.y = element_text(size=20),
        axis.line = element_line(colour = "black"),
        axis.title.x=element_blank(), 
        axis.text.x=element_blank(),
        axis.text.y=element_text(size=18), 
        axis.ticks = element_blank(),
        plot.margin = unit(c(1.1, 0.1, 0.1, 1.1), "cm")
  )

# ============================================================================ #
# File daily nosocomial transmissions (HCWs)
data_list2 <- read_excel_allsheets(paste0("../", dataPath, "transm_hcw_over_time.xlsx"))
data_list2 <- lapply(data_list2, function(x) cbind(date=dates, x[(nrow(x)-length(dates)+1):nrow(x),]))
names(data_list2) <- scenarios

data_list2 <- lapply(data_list2, function(x){ colnames(x) <- c("date", "mean", "ci_lower", "ci_upper"); 
cbind(x, ma_mean = ma(x$mean, n=7))})

data2 <- bind_rows(data_list2, .id="scenarios")
data2$scenarios <- factor(data2$scenarios, levels=scenarios)
colnames(data2) <- c("scenarios", "date", "mean", "ci_lower", "ci_upper", "ma_mean")
data2$date <- as.Date(data2$date, format="%Y-%m-%d")

# Plot for Figure 4B
data2_plot <- ggplot(data2) + 
  geom_line(aes(x=date, y=ma_mean, color = scenarios), size=1.3) + 
  # labs(title="Number of nosocomial infected HCWs over time\n(7-day moving average)", y="Number of HCWs") +
  labs(y="Number of HCWs") +
  scale_colour_manual(values=colors_all) + 
  scale_x_date(date_breaks="1 week", date_labels="%d %b", breaks = dates, minor_breaks = "2 weeks") +
  guides(color=guide_legend(override.aes = list(size = 1.4),nrow=3,byrow=F)) +
  theme_publication() + 
  theme(legend.position = "bottom",
        legend.title = element_blank(),
        legend.text = element_text(size=16),
        legend.background = element_blank(),
        panel.background = element_blank(),
        axis.title.x=element_blank(), 
        axis.text.x=element_text(size=18, angle=45, hjust=1),
        axis.text.y=element_text(size=20),
        plot.margin = unit(c(1.1, 0.1, 0.1, 1.1), "cm")
  )
# Combine different panels into one plot (Figure 4)
plots <- plot_grid(data_plot, data2_plot, align = "v", nrow = 2, labels="AUTO", 
                   rel_heights = c(4/10,6/10), label_size=20, hjust=-0.15,vjust=1.5)
ggsave(plot=plots, file=paste0(figuresPath, "nosocomial_hcw_pat_over_time.pdf"), width=12, height=9)