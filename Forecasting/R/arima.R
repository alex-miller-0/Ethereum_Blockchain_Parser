#!/usr/bin/Rscript
library("forecast", lib.loc="/home/alex/miniconda2/lib/R/library")

endog = read.csv("R/endog.csv")
exog = read.csv("R/exog.csv")

fit <- Arima(endog[,1], order=c(1,0,0))
pred = predict(fit, 3)

write.csv(pred, file="R/tmp.csv")
