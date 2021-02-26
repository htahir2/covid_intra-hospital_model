# ============================================================================ #
# Agent-based modelling for nosocomial transmission of COVID-19
# ----------------------------------------------------------------------------
# Barplots for transmission route contributions
# ============================================================================ #
rm(list=ls())

# Load paths, packages, and functions
source("abm_path_packages.R")
source("abm_functions.R")

# File with route contributions
route_contr <- read_excel_allsheets(paste0("../", dataPath, "transmissions_route.xlsx"))
scenarios <- scenarios[1:length(route_contr)]
route_data <- NULL
for(i in 1:length(route_contr)) route_data <- rbind(route_data, route_contr[[i]])
route_data <- cbind(scenarios, route_data)
route_data
ncol_route <- ncol(route_data)

df <- route_data[, c(1,seq(2,ncol_route,by=3))]
df <- reshape2::melt(df)
colnames(df)[3] <- "mean"

df_sdu <- route_data[, c(1,seq(3,ncol_route,by=3))]
df_sdu <- reshape2::melt(df_sdu)
colnames(df_sdu)[3] <- "ci_upper"

df_sdl <- route_data[, c(1,seq(4,ncol_route,by=3))]
df_sdl <- reshape2::melt(df_sdl)
colnames(df_sdl)[3] <- "ci_lower"

levels(df$variable) <- levels(df_sdu$variable) <- levels(df_sdl$variable)<- c("Pat-Nurse", "Pat-HC", "Nurse-Pat", "Nurse-HC","Nurse-Nurse", "HC-Pat", "HC-Nurse", "HC-HC")

level_order <- c("Pat-Nurse", "Nurse-Pat", "Pat-HC", "HC-Pat", "Nurse-HC","Nurse-Nurse", "HC-Nurse", "HC-HC")
df$variable <- factor(df$variable)
df_sdu$variable <- factor(df_sdu$variable)
df_sdl$variable <- factor(df_sdl$variable)

data <- merge(df, df_sdu)
data <- merge(data, df_sdl)

data$scenarios <- factor(data$scenarios, levels = scenarios)
colnames(data)[2] <- "route"


route_plot_with_error <- ggplot(data=data, aes(x=route,y=mean, fill=scenarios)) + 
                            geom_bar(position=position_dodge(width=0.7), stat="identity", width=0.5) +
                            geom_errorbar(aes(ymax = ci_upper, ymin=ci_lower), 
                                          position = position_dodge(0.7), width = 0.3, colour="grey") + 
                            labs(title="Transmission route contributions") + 
                            ylab("Proportion of transmissions") + 
                            guides(fill=guide_legend(title="",nrow=3,byrow=F), reverse=T) +
                            scale_x_discrete(limits = level_order) + 
                            scale_fill_manual(values=colors_all) +
                            theme_publication() + 
                            theme(title = element_text(size=20), 
                                  plot.title = element_text(hjust=0.5),
                                  legend.position = "top",
                                  legend.text = element_text(size=12),
                                  panel.background = element_blank(),
                                  axis.title.y = element_text(size=16),
                                  axis.line = element_line(colour = "black"),
                                  axis.title.x=element_blank(), 
                                  axis.text.x=element_text(size=14),
                                  axis.text=element_text(size=14)) 
# route_plot_with_error

# ggsave(plot = route_plot_with_error, file = paste0(figuresPath, "route_contr_plot_with_error.eps"), 
#        width=12, height=9)



# Merge Nurses and HC specialists
hcw <- c("Nurse-HC","Nurse-Nurse", "HC-Nurse", "HC-HC")
p_hcw <- c("Pat-Nurse", "Pat-HC")
hcw_p <- c("Nurse-Pat", "HC-Pat")
data_small <- temp <- NULL
for(s in scenarios){
  ind <- intersect(which(data$scenarios==s), which(data$route%in%hcw))
  temp <- data[ind, c("mean", "ci_upper", "ci_lower")]
  temp <- apply(temp, 2, sum)
  temp$scenarios <- s
  temp$route <-"HCW-HCW"
  data_small <- as.data.frame(rbind(data_small, unlist(temp)))
  
  ind_p_hcw <- intersect(which(data$scenarios==s), which(data$route%in%p_hcw))
  temp_p_hcw <- data[ind_p_hcw, c("mean", "ci_upper", "ci_lower")]
  temp_p_hcw <- apply(temp_p_hcw, 2, sum)
  temp_p_hcw$scenarios <- s
  temp_p_hcw$route <-"Patient-HCW"
  data_small <- as.data.frame(rbind(data_small, unlist(temp_p_hcw)))
  
  ind_hcw_p <- intersect(which(data$scenarios==s), which(data$route%in%hcw_p))
  temp_hcw_p <- data[ind_hcw_p, c("mean", "ci_upper", "ci_lower")]
  temp_hcw_p <- apply(temp_hcw_p, 2, sum)
  temp_hcw_p$scenarios <- s
  temp_hcw_p$route <-"HCW-Patient"
  data_small <- as.data.frame(rbind(data_small, unlist(temp_hcw_p)))
}

data_small <- data_small[,c("scenarios","route", "mean", "ci_upper", "ci_lower")]
data_small <- as.data.frame(data_small)
data_small$route <- factor(data_small$route, levels=c("Patient-HCW", "HCW-Patient", "HCW-HCW"))
data_small$scenarios <- factor(data_small$scenarios, levels = scenarios)
for(i in c("mean", "ci_upper", "ci_lower")) data_small[,i] <- as.numeric(data_small[,i])
data_small$ci_upper[data_small$ci_upper>=100] <- 100


route_plot_with_errors <- ggplot(data=data_small, aes(x=route,y=mean, fill=scenarios)) + 
                            geom_bar(position=position_dodge(width=0.7), stat="identity", width=0.5) +
                            geom_errorbar(aes(ymax = ci_upper, ymin=ci_lower), 
                                          position = position_dodge(0.7), width = 0.3, colour="darkgrey") + 
                            labs(title="Transmission route contributions") + 
                            ylab("Proportion of transmissions (%)") + 
                            guides(fill=guide_legend(title="",nrow=3,byrow=F)) +
                            theme_publication() + 
                            scale_fill_manual(values=colors_all) +
                            theme(title = element_text(size=20),
                                  # plot.title = element_text(hjust=0.5),
                                  plot.title = element_blank(),
                                  legend.position = "top",
                                  legend.text = element_text(size=14),
                                  panel.background = element_blank(),
                                  axis.title.y = element_text(size=20),
                                  axis.line = element_line(colour = "black"),
                                  axis.title.x=element_blank(), 
                                  axis.text.x=element_text(size=16),
                                  axis.text=element_text(size=16)) 
route_plot_with_errors

ggsave(plot = route_plot_with_errors, file = paste0(figuresPath, "route_contr_merged_plot_with_errors.pdf"), 
       width=12, height=9)


