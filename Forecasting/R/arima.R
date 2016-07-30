#!/usr/bin/Rscript
library("forecast", lib.loc="/home/alex/miniconda2/lib/R/library")

# Command line args
options(echo=TRUE)
args <- commandArgs(trailingOnly=TRUE)
p = strtoi(args[1], base=0L)
d = strtoi(args[2], base=0L)
q = strtoi(args[3], base=0L)


endog = read.csv("R/endog.csv")
exog = read.csv("R/exog.csv")

fit <- Arima(endog[,1], order=c(p,d,q))
pred = predict(fit, 1)

write.csv(pred, file="R/tmp.csv")
