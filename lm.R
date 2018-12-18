
df<-read.csv("/home/zijun/PSAADIY/pssa/data/feature/features_guiyi_123.csv")
#df<-subset(df, select = -strategy_count)    #randomforest
lm_xian<-lm(sum_score~.-1,data=df)
#summary(lm_xian)

tstep<-step(lm_xian)
summary(tstep)

#library(car)
#vif(lm_xian)
#library(ridge)
#mod <- linearRidge(sum_score~.-1, data = df)
#summary(mod)
