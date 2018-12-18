#!/usr/bin/python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
import xlrd
path="/home/zijun/Downloads/subject_corr/physical.xls"
data=pd.read_excel(path)
# print(data)
# data.corrwith(data.总分).to_csv("/home/zijun/Downloads/subject_corr/math_1_corr.xls")

for i in range(data.columns.size):
    file=open("/home/zijun/Downloads/subject_corr/physical_corr.txt","a+")
    other_score=data["总分"]-data.iloc[:,(i+1)]
    cor=data.iloc[:,(i+1)].corr(other_score,method="pearson")
    file.write(data.columns[i+1]+","+str(cor)+"\n")