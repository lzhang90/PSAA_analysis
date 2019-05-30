
##############读取圣女果题目的学生数据文件夹下的到目标文件夹###########
#/usr/bin/python
#coding=utf-8
import os
import zipfile
import json


def unzip(source_path, target_path):
    for file_name in os.listdir(source_path):
        file_path=source_path+"/"+file_name
        try:
            r = zipfile.is_zipfile(file_path)#判断是否解压文件
            if r:
                zpfd = zipfile.ZipFile(file_path,"r")#读取压缩文件
                zpfd.extract("PSA-T023.json",target_path)
                zpfd.close()
                os.rename(target_path+"/PSA-T023.json",target_path+"/"+file_name[10:12]+".json")
                print(file_name+' unzipped')
        except:
            pass


def file_rename(dir_path):
    for file_name in os.listdir(dir_path):
        f=open(dir_path+"/"+file_name, mode="r", encoding="utf-8")
        olist=json.load(f)
        new_name = olist[0]['actor']['name']
        f.close()
        os.rename(dir_path+"/"+file_name,dir_path+"/"+new_name+".json")

