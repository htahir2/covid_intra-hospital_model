# ============================================================================ #
# Functions for ABM
# ============================================================================ #
read_excel_allsheets <- function(filename, tibble = FALSE) {
  # If you like tidyverse tibbles (the default with read_excel)
  # then just pass tibble = TRUE
  sheets <- readxl::excel_sheets(filename)
  x <- lapply(sheets, function(X) readxl::read_excel(filename, sheet = X))
  if(!tibble) x <- lapply(x, as.data.frame)
  names(x) <- sheets
  return(x)
}

# Moving average
ma <- function(x, n = 7){stats::filter(x, rep(1 / n, n), sides = 2)}


plot.pos.rate.prev <- function(df, title="A"){
  p <- ggplot(data = df, mapping = aes(x=tags)) + 
          geom_point(aes(y=pos_rate)) + 
          geom_errorbar(aes(ymin=ci_lower, ymax=ci_upper), width=0.1) + 
          # labs(title=title, y="positivity rate (%)") +
          scale_y_continuous(limits=c(0, max(df$ci_upper))) + 
          guides(color=FALSE) +
          theme_publication() +
          theme(plot.caption = element_text(hjust=0),
                plot.title = element_text(size=22),
                plot.title.position = "plot",
                plot.caption.position = "plot",
                axis.title = element_blank(),
                axis.text.x = element_text(size=16, angle=45, hjust=1),
                axis.text.y = element_text(size=18),
                panel.grid.minor.x=element_blank(),
                panel.grid.major.x=element_blank(),
                plot.margin = unit(c(0.1,0.1,0.1,2),"cm"),)
  return(p)
}


binomial.prop <- function(data, nbreaks=100, ct=F){
  if(ct){
    prev <- data$prev*100
  }else{
    prev <- data$prev*100
  }
  # Bin prevalence
  group_tags <- cut(prev, breaks=nbreaks)
  prev_groups <- factor(group_tags, levels = as.character(unique(group_tags[order(group_tags)])), ordered = TRUE)
  
  if(ct){
    df <- data[,c("n_contacts_traced","n_pos_contacts","n_sympt_patients_traced","n_sympt_hcws_traced","contact_tracing_time","day","n_total","n_pos","pos_rate","prev")]
  }else{
    df <- data[,c("day","n_contacts_traced","n_pos_contacts","prev", "pos_rate")]
  }

  df <- as.data.frame(df)
  # Add tags of prevalence groups
  df <- as_tibble(df) %>% mutate(tags=prev_groups)
  
  if(ct) dff <- df %>% group_by(tags) %>% summarise(n_pos = sum(n_pos_contacts), n_contacts = sum(n_contacts_traced)-sum(n_sympt_patients_traced)-sum(n_sympt_hcws_traced))
  else dff <- df %>% group_by(tags) %>% summarise(n_pos = sum(n_pos_contacts), n_contacts = sum(n_contacts_traced))

  if(length(which(is.na(dff)))>0) dff <- dff[-which(is.na(dff)),]
  # Compute respective binomial confidence intervals
  ci_lower <- ci_upper <- pos_rate <- NULL
  for(i in 1:nrow(dff)){
    temp <- binom.bayes(x=dff$n_pos[i],n=dff$n_contacts[i])
    pos_rate <- c(pos_rate, temp["mean"]*100)
    ci_lower <- c(ci_lower, temp["lower"]*100)
    ci_upper <- c(ci_upper, temp["upper"]*100)
    
    # temp <- binom_test(x=dff$n_pos[i],n=dff$n_contacts[i])
    # pos_rate <- c(pos_rate, temp[,"estimate"]*100)
    # ci_lower <- c(ci_lower, temp[,"conf.low"]*100)
    # ci_upper <- c(ci_upper, temp[,"conf.high"]*100)
  }
  dff <- dff %>% mutate(pos_rate = unlist(pos_rate), ci_lower=unlist(ci_lower), ci_upper=unlist(ci_upper))
  return(dff)
}


