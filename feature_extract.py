#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import codecs
import itertools
##############读取圣女果题目的学生数据文件夹下的到目标文件夹###########
#/usr/bin/python
#coding=utf-8
import os,sys
import zipfile
import shutil
def Decompression(files,file_path,save_path):
    os.getcwd()#当前路径
    os.chdir(file_path)#转到路径
    for file_name in files:
        try:
            r = zipfile.is_zipfile(file_name)#判断是否解压文件
            if r:
                print(file_name)
                zpfd = zipfile.ZipFile(file_name,"r")#读取压缩文件
                save_path_1=save_path+"/"+file_name[10:12]
                os.chdir(save_path)
                zpfd.extract("PSA-T023.json",save_path_1)
                zpfd.close()
        except:
            pass
# save_path="/home/zijun/PSAADIY/pssa/data/圣女果学生数据解压/"
# for file_path,sub_dirs,files in os.walk("/home/zijun/PSAADIY/pssa/data/raw_data_zipped"):
#     print(file_path, sub_dirs, files)
#     Decompression(files, file_path, save_path)

def file_move(path):
    files=os.listdir(path)
    for i in files:
        from_path=path+i+"/"+"PSA-T023.json"
        to_path="/home/zijun/PSAADIY/pssa/data/log_data/"+i+".json"
        shutil.move(from_path,to_path)
#file_move("./data/圣女果学生数据解压/")
#######################################################################
def find_not_new(verb_state_list):
    for i in range(len(verb_state_list)):
        verb=verb_state_list[i].verb
        if verb=="消毒方案优选":
            return i

def verb_state_subtask_feature(verb_state_list):
    verb_state_simple_subtask=[]
    drag_state_init = "0"
    color_state_init = "red"
    subtask_action=None
    index=find_not_new(verb_state_list)
    for i in range(index,(len(verb_state_list)+1)):
        try:
            verb=verb_state_list[i].verb
            state=verb_state_list[i].state
        except:
            pass
        if verb in subtask_name_1 or i==len(verb_state_list):
            verb_state_simple_subtask.append(subtask_action)
            subtask_action=[]
            subtask_action.append(" ".join([verb]))
        elif verb=="click" and state=="restart":
            subtask_action.append(" ".join([verb,state]))
        elif verb == "click" and state == "des":
            subtask_action.append(" ".join([verb, state]))
        elif verb=="liberary":
            subtask_action.append(" ".join([verb, state]))
        elif verb=="Determine" and state!="0":
            if int(state)>int(drag_state_init):
                subtask_action.append(" ".join([verb, "up"]))
            else:
                subtask_action.append(" ".join([verb, "down"]))
            drag_state_init=int(state)
        elif verb=="Determine" and state=="0":
            drag_state_init="0"
        elif verb=="completed":
            subtask_action.append(" ".join([verb, state]))
        elif verb == "fill":
            subtask_action.append(" ".join([verb, state]))
        elif verb=="changecolor":
            if (state[0] >= u'\u4e00' and state[0]<=u'\u9fa5'):
                subtask_action.append(" ".join([verb, state]))
            elif ord(state[0])==114:
                color_state_init = "red"
                subtask_action.append(" ".join([verb, state]))
            else:
                subtask_action.append(" ".join([verb, state]))
                if corlor_list.index(state) > corlor_list.index(color_state_init):
                    subtask_action.append(" ".join(["Determine", "up"]))
                else:
                    subtask_action.append(" ".join(["Determine", "down"]))
                    color_state_init = state
        else:
            pass
    return verb_state_simple_subtask



##阅读有关资料，且答案正确
# def related_correct(feature_subtask):
#     related_correct_count=0
#     for i in feature_subtask:
#         if i is not None and "completed correct" in i:
#             for j in list(reversed(i)):
#                 if j=="liberary related":
#                     related_correct_count=related_correct_count+1
#                     break
#     return related_correct_count

##重做任务（点击“重做”按钮），且答案正确
# def restart_correct(feature_subtask):
#     restart_correct_count=0
#     for i in feature_subtask:
#         if "completed correct" in i:
#             for j in list(reversed(i)):
#                 if j=="click restart":
#                     restart_correct_count=restart_correct_count+1
#                     break
#     return restart_correct_count
# ##有策略探究，且答案正确
# def strategy_correct(feature_subtask):
#     strategy_correct_count=0
#     for i in feature_subtask:
#         if "completed correct" in i:
#             Determine_list=[j for j in i if "Determine" in j]
#             try:
#                 if max([len(list(v)) for k, v in itertools.groupby((Determine_list))])>=3:
#                     strategy_correct_count=strategy_correct_count+1
#             except:
#                 pass
#     return strategy_correct_count
###有策略探究
def divide(c):
    return c//3


def find_not_new_time(Stu):
    for i in range(len(Stu.pbs)):
        if Stu.pbs[i].obj_cn=="消毒方案优选" and Stu.pbs[i].verb=="launched":
            return i

######################
def features(feature_subtask,Stu):
    all_features=collections.defaultdict(dict)
    for i in feature_subtask:
        all_features[i[0]]["liberary_count"]=0
        all_features[i[0]]["liberary_related_count"] = 0
        all_features[i[0]]["liberary_unrelated_count"] = 0
        all_features[i[0]]["click_des_count"] = 0
        all_features[i[0]]["control_variable"]=0
        all_features[i[0]]["strategy_count"]=0
        if len(i)>0 and i[0]!="圣女果的最佳光照条件":
            Determine_list = [j for j in i if "Determine" in j]
            a = [len(list(v)) for k, v in itertools.groupby((Determine_list))]
            all_features[i[0]]["strategy_count"] = sum(list(map(divide, a)))
        elif len(i) > 0 and i[0] == "圣女果的最佳光照条件":
            Determine_sublist = []
            Determine_list = [j for j in i if "Determine" in j or "changecolor" in j]
            sublist = None
            try:
                for j in range(len(Determine_list) + 1):
                    if Determine_list[j][0:11] == "changecolor" or j == len(Determine_list):
                        Determine_sublist.append(sublist)
                        sublist = []
                    else:
                        sublist.append(Determine_list[j])
                con = [[len(list(v)) for k, v in itertools.groupby((x))] for x in Determine_sublist[1:] if
                       x is not None]
                all_features[i[0]]["control_variable"] =sum([list(map(divide, i)) for i in con])
            except:
                pass
        for j in i:
            if "liberary" in j:
                all_features[i[0]]["liberary_count"]=all_features[i[0]]["liberary_count"]+1
                if "liberary related" in j:
                    all_features[i[0]]["liberary_related_count"] = all_features[i[0]]["liberary_related_count"] + 1
                else:
                    all_features[i[0]]["liberary_unrelated_count"] = all_features[i[0]]["liberary_unrelated_count"] + 1
            elif "click des" in j:
                all_features[i[0]]["click_des_count"]=all_features[i[0]]["click_des_count"]

            else:
                pass
    ##################和时间有关的特征######################
    launch_time_init=0
    launch_time_init_1=0
    not_new_index=find_not_new_time(Stu)
    for i in range(not_new_index,len(Stu.pbs)):
        if Stu.pbs[i].obj_cn in subtask_name_1 and Stu.pbs[i].verb=="launched":
            subtask_name=Stu.pbs[i].obj_cn
            launch_time_init = Stu.pbs[i].timestamp
            all_features[subtask_name]["related_time"]=0
            all_features[subtask_name]["unrelated_time"] = 0
            all_features[subtask_name]["launch_action_diff"] = 0
            all_features[subtask_name]["first_des_time"]=0
            all_features[subtask_name]["answer"]=Stu.subtask_dict[subtask_name]
        elif Stu.pbs[i].verb=="liberary":
            if Stu.pbs[i].obj_id.split("#")[1]=="1":
                diff=time_lag(Stu.pbs[i].timestamp,Stu.pbs[i+1].timestamp)
                all_features[subtask_name]["related_time"]=all_features[subtask_name]["related_time"]+diff
            else:
                diff=time_lag(Stu.pbs[i].timestamp,Stu.pbs[i+1].timestamp)
                all_features[subtask_name]["unrelated_time"]=all_features[subtask_name]["unrelated_time"]+diff
        elif launch_time_init_1!=launch_time_init and Stu.pbs[i].obj_cn in subtask_name_1 and (Stu.pbs[i].verb in ["fill","gainColor"] or (Stu.pbs[i].verb=="click" and Stu.pbs[i].obj_id.split("#")[1][-1]=="光") or Stu.pbs[i].verb.find("drag"))!=-1:
            next_action_time=Stu.pbs[i].timestamp
            launch_diff=time_lag(launch_time_init,next_action_time)
            all_features[subtask_name]["launch_action_diff"]=all_features[subtask_name]["launch_action_diff"]+launch_diff
            launch_time_init_1=launch_time_init
        elif Stu.pbs[i].obj_id.split("#")[1]=="确定":
            all_features[subtask_name]["first_des_time"]=time_lag(launch_time_init,Stu.pbs[i].timestamp)


        else:
            pass


    return all_features


def combine_features(Stu,verb_state_list):
    feature_subtask = verb_state_subtask_feature(verb_state_list)
    feature_subtask=feature_subtask[1:]
    # related_correct_count=related_correct(feature_subtask)
    # restart_correct_count=restart_correct(feature_subtask)
    # strategy_correct_count=strategy_correct(feature_subtask)
    strategy_count=strategy(feature_subtask)
    control_variable_count=control_variable(feature_subtask)
    # fill_correct_count=fill_correct(feature_subtask)
    liberary_count, liberary_related_count, liberary_unrelated_count, click_des_count=liberary_count_1(feature_subtask)
    related_time, unrelated_time, launch_action_diff=time_feature(Stu)
    subtask_counts=len(Stu.subtask_dict)-1
    return strategy_count,liberary_count, liberary_related_count, liberary_unrelated_count, click_des_count,related_time, unrelated_time, launch_action_diff,control_variable_count,subtask_counts





