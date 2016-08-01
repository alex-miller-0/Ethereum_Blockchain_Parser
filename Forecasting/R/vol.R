#!/usr/bin/Rscript
library("timeSeries", lib.loc="/home/alex/miniconda2/lib/R/library")
library("fBasics", lib.loc="/home/alex/miniconda2/lib/R/library")
library("fGarch", lib.loc="/home/alex/miniconda2/lib/R/library")

# Command line args
endog = read.csv("R/endog.csv")
exog = read.csv("R/exog.csv")

vol <- garchFit(data=endog[,1])
pred_volatility = predict(vol, n.ahead=1)

write.csv(pred_volatility[0], file="R/tmpvol.csv")

