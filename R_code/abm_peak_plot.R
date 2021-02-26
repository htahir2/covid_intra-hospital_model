# ============================================================================ #
# Agent-based modelling for nosocomial transmission of COVID-19
# ----------------------------------------------------------------------------
# Peak transmissions
# ============================================================================ #
rm(list=ls())

# Load paths, packages, and functions
source("abm_path_packages.R")
source("abm_functions.R")

# Files with peak numbers (patients)
peak_pat <- read_excel_allsheets(paste0("../",dataPath, "peak_transmissions_patients.xlsx"))
pat_data <- NULL
for(i in 1:length(peak_pat)) pat_data <- rbind(pat_data, peak_pat[[i]])
pat_data <- cbind(scenarios, pat_data)
pat_data$scenarios <- factor(pat_data$scenarios, levels=scenarios)
colnames(pat_data) <- c("scenarios", "mean", "ci_upper", "ci_lower")

peak_pat_plot <- ggplot(data=pat_data, aes(x=scenarios,y=mean, color=scenarios)) + 
  geom_bar(position=position_dodge(width=0.7), stat="identity", width=0.5, color=colors_all, fill=colors_all) +
  geom_errorbar(aes(ymax = ci_upper, ymin=ci_lower), position = position_dodge(0.9), width = 0.3, color="grey") +
  coord_flip() +       
  labs(title="Peak number of nosocomial infected patients") + 
  ylab("Peak number of nosocomial infections among patients") + 
  # guides(fill=guide_legend(title="")) +
  theme_bw() +
  scale_fill_manual(values=colors_all) +
  scale_y_continuous(breaks=seq(0,max(pat_data$ci_upper),by=10), limits=c(0, max(pat_data$ci_upper))) +
  scale_x_discrete(limits = rev(levels(pat_data$scenarios))) + 
  theme(title = element_text(size=20), 
        # plot.title = element_text(hjust=0.5),
        plot.title = element_blank(),
        legend.position="none",
        panel.background = element_blank(),
        axis.title.y = element_blank(),
        axis.line = element_line(colour = "black"),
        axis.title.x=element_text(size=20), 
        axis.text=element_text(size=20),
        plot.margin = unit(c(0.1,0.5,0.1,0.1),"cm"),
        panel.grid.minor=element_blank(),
        panel.grid.major=element_blank()) 
# peak_pat_plot
# ggsave(plot = peak_pat_plot, file = paste0(figuresPath, "peak_transm_pat_plot.pdf"), width=12, height=9)


# Files with peak numbers
peak_hcws <- read_excel_allsheets(paste0("../",dataPath, "peak_transmissions_hcws.xlsx"))
hcws_data <- NULL
for(i in 1:length(peak_hcws)) hcws_data <- rbind(hcws_data, peak_hcws[[i]])
hcws_data <- cbind(scenarios, hcws_data)
hcws_data$scenarios <- factor(hcws_data$scenarios, levels=scenarios)
colnames(hcws_data) <- c("scenarios", "mean", "ci_upper", "ci_lower")

peak_hcws_plot <- ggplot(data=hcws_data, aes(x=scenarios,y=mean, color=scenarios)) + 
  geom_bar(position=position_dodge(width=0.7), stat="identity", width=0.5, color=colors_all, fill=colors_all) +
  geom_errorbar(aes(ymax = ci_upper, ymin=ci_lower), position = position_dodge(0.9), width = 0.3, color="grey") +
  coord_flip() +       
  labs(title="Peak number of nosocomial infected HCWs") + 
  ylab("Peak number of nosocomial infections among HCWs") + 
  # guides(fill=guide_legend(title="")) +
  theme_bw() +
  scale_fill_manual(values=colors_all) +
  scale_y_continuous(breaks=seq(0,max(pat_data$ci_upper),by=10), limits=c(0, max(pat_data$ci_upper))) +
  scale_x_discrete(limits = rev(levels(hcws_data$scenarios))) + 
  theme(title = element_text(size=20), 
        # plot.title = element_text(hjust=0.5),
        plot.title = element_blank(),
        legend.position="none",
        panel.background = element_blank(),
        axis.title.y = element_blank(),
        axis.text.y=element_blank(),
        axis.line = element_line(colour = "black"),
        axis.title.x=element_text(size=20), 
        axis.ticks.y = element_blank(),
        axis.text=element_text(size=20),
        plot.margin = unit(c(0.1,0.1,0.1,0.1),"cm"),
        panel.grid.minor=element_blank(),
        panel.grid.major=element_blank()) 
# peak_hcws_plot
# ggsave(plot = peak_hcws_plot, file = paste0(figuresPath, "peak_transm_hcws_plot.pdf"), width=12, height=9)
  
plots <- plot_grid(peak_pat_plot, peak_hcws_plot, align = "l", nrow = 1, rel_heights = c(7/10,3/10), labels="AUTO")
# plots


# Plot using facet_wrap
data_pat <- melt(pat_data[,1:2], id='scenarios')
levels(data_pat$variable) <- "patients"
colnames(data_pat)[3] <- "mean"

data_hcw <- melt(hcws_data[,1:2], id='scenarios')
levels(data_hcw$variable) <- "HCWs"
colnames(data_hcw)[3] <- "mean"

cl_pat <- melt(pat_data[,c(1,3)], id='scenarios')
cu_pat <- melt(pat_data[,c(1,4)], id='scenarios')
data_pat <- cbind(data_pat, ci_lower=cl_pat[,3], ci_upper=cu_pat[,3])

cl_hcw <- melt(hcws_data[,c(1,3)], id='scenarios')
cu_hcw <- melt(hcws_data[,c(1,4)], id='scenarios')
data_hcw <- cbind(data_hcw, ci_lower=cl_hcw[,3], ci_upper=cu_hcw[,3])

data <- rbind(data_pat, data_hcw)

plot <- ggplot(data, aes(x=scenarios, y=mean, group=variable, colors=scenarios)) + 
  facet_wrap(~variable) + 
  coord_flip() +  
  geom_bar(position=position_dodge(width=0.7), stat="identity", width=0.5, color=c(colors_all, colors_all), fill=c(colors_all, colors_all)) +
  geom_errorbar(aes(ymax = ci_upper, ymin=ci_lower), position = position_dodge(0.9), width = 0.3, color="grey") +
  scale_x_discrete(limits = rev(levels(hcws_data$scenarios))) + 
  ylab("Peak number of nosocomial infections") + 
  theme_bw() + 
  theme(title = element_text(size=20), 
        plot.title = element_blank(),
        legend.position="none",
        panel.background = element_blank(),
        axis.title.y = element_blank(),
        axis.line = element_line(colour = "black"),
        axis.title.x=element_text(size=20), 
        axis.text=element_text(size=20),
        plot.margin = unit(c(0.1,0.5,0.1,0.1),"cm"),
        strip.text=element_text(size=20),
        panel.grid.minor=element_blank(),
        panel.grid.major=element_blank())
# plot
ggsave(plot, file=paste0(figuresPath, "peak_transm_pat_hcws.pdf"), width=16, height=9)

# Reduction in peak
# pat_peak_red <- sapply(2:length(scenarios), function(x) 1-pat_data[pat_data$scenarios==scenarios[x],"mean"]/pat_data[pat_data$scenarios==scenarios[1],"mean"])
# hcw_peak_red <- sapply(2:length(scenarios), function(x) 1-hcws_data[hcws_data$scenarios==scenarios[x],"mean"]/hcws_data[hcws_data$scenarios==scenarios[1],"mean"])
# 
# (peak_red_df <- as.data.frame(cbind(scenario=scenarios[-1], pat=round(pat_peak_red, 3), hcw=round(hcw_peak_red, 3))))
# 
# write.table(peak_red_df, file=paste0(figuresPath, "peak_red.csv"), row.names = F, sep=",")
