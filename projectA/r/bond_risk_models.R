library(tidyverse); library(caret)
bonds <- read.csv("data/bond_portfolio.csv")
set.seed(42)
idx <- createDataPartition(bonds$CleanPrice, p=.8, list=FALSE)
train <- bonds[idx,]; test <- bonds[-idx,]
rf <- train(CleanPrice ~ CouponRate + YieldToMaturity + YearsToMaturity + ModifiedDuration + Convexity + CreditRating + TenorBucket, data=train, method="rf", trControl=trainControl(method="cv", number=5))
print(rf)
print(weighted.mean(bonds$ModifiedDuration, bonds$MarketValue_INR))
print(weighted.mean(bonds$Convexity, bonds$MarketValue_INR))
