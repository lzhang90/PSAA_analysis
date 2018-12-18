#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
df=pd.read_excel("/home/zijun/PSAADIY/pssa/data/feature/features_change_gai.xlsx",sheet_name="nor_norm")
# df=df[["sum_score","性别","额外查看任务说明次数","第一次查看任务说明时间","初步思考时间","策略运用次数","相关资料时间","不相关资料时间","相关资料次数","不相关资料次数"]]

# df.fillna(3,inplace=True)   #有的同学没有查看不相关资料，用5代替
def code_sex(x):
    if x=="男":
        return 0
    else:
        return 1
#####标准化处理
#############简单相关系数
# print("标准化处理")
df["性别"]=df["性别"].apply(code_sex)
# df.drop(columns=['name'],inplace=True)
# df_norm = (df - df.mean()) / (df.std())
# print(df_norm.corrwith(df_norm['sum_score']))
#
#
#
# # print(df_norm)
# ##########线性回归
# X=df_norm[["性别","相关资料与不相关资料时间比","相关资料与不相关资料次数比","额外查看任务说明次数","第一次查看任务说明时间","初步思考时间","策略运用次数"]]
# Y=df_norm["sum_score"]
# # X=sm.add_constant(X)
# est=sm.OLS(Y,X).fit()
# print(est.summary())
##########归一化
print("###########归一化")
# df_max_min = (df - df.min()) / (df.max() - df.min())
# df_max_min.to_excel("/home/zijun/PSAADIY/pssa/data/feature/all_subtasks.xlsx")
print(df.corrwith(df['sum_score']))
aa=df.corr()
X1=df[["性别","额外查看任务说明次数","第一次查看任务说明时间","初步思考时间","策略运用次数","相关资料时间","不相关资料时间","相关资料次数","不相关资料次数"]]
Y1=df["sum_score"]
# X1=sm.add_constant(X1)
est1=sm.OLS(Y1,X1).fit()
print(est1.summary())
#
# X2=df_max_min["相关资料时间"]
# Y2=df_max_min["sum_score"]
# fig = plt.figure()
# ax1 = fig.add_subplot(111)
# ax1.scatter(X2,Y2,c = 'r',marker = 'o')
# plt.show()
#
# # X2=sm.add_constant(X2)
# est2=sm.OLS(Y2,X2).fit()
# print(est2.summary())






