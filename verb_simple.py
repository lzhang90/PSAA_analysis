#!/usr/bin/python
# -*- coding: utf-8 -*-
# from util import Util, HMM
from datetime import datetime
from collections import OrderedDict
import numpy as np
import codecs
import json
import os
import collections
import csv
import re
import pandas as pd
import itertools
import csv
import numpy as np
from hmmlearn import hmm
import json

#################################HMM动作处理############################
class PB:
    def __init__(self, verb, obj_id, obj_cn, timestamp):
        self.verb = verb
        self.obj_id = obj_id  # 行为的对象id 任务(#具体对象)
        self.obj_cn = obj_cn  # 对象的中文
        self.timestamp = timestamp  # 行为发生的时间


# class Subtask:
#     def __init__(self,duration,score,answer):
#         self.duration=duration
#         self.score=score
#         self.answer=answer


class Student:
    def __init__(self, id):
        self.id = id  # 学生编号
        self.pbs = []  # 学生一系列的行为序列
        self.task_time = None  # 做题时间
        self.subtask_dict = None  # 子任务字典（包含每一个子任务的完成时间，score和answer）


def data_read(path):
    file = './data/log_data/' + path
    with codecs.open(file, 'r', 'utf-8') as f:
        data = json.load(f)
    return data


def student_name_get(data):
    name = data[0]["actor"]["name"]
    return name


def task_or_lib(json_data):  # 暂时没有找到查阅资料的记录
    pass


def get_obj_id(obj):
    obj_id = obj[obj.rindex('/') + 1:]

    if obj_id.__contains__('?'):
        obj_id = obj_id.split('?')[0]

    return obj_id


def get_verb(s):
    s = s[s.rindex('/') + 1:]
    return s


def time_lag(begin_str, end_str):
    begin_time = datetime.strptime(begin_str, '%Y-%m-%dT%H:%M:%S')
    end_time = datetime.strptime(end_str, '%Y-%m-%dT%H:%M:%S')
    lag = end_time - begin_time
    return lag.total_seconds()


def process_behavior(data):
    '''

    :param data: 读取一个学生的json日志文件形成的list
    :return:
    '''
    pbs = []
    subtask_dict = collections.defaultdict(dict)  ###用于存储某个学生各个子任务的duration,score,answer
    begin_timestamp = None
    end_timestamp = None
    for i in range(0, len(data)):
        obj_id = get_verb(data[i]["object"]["id"])
        obj_cn = data[i]["object"]["definition"]["name"]["zh_CN"]
        timestamp = data[i]['timestamp'][:-6]
        verb = get_verb(data[i]["verb"]["id"])
        if "json" in obj_id and verb == "launched":
            verb = "liberary"
            obj_id = obj_id + "#" + str(data[i]["result"]["score"]["raw"])
        pbs.append(PB(verb, obj_id, obj_cn, timestamp))
        if i == 0:
            begin_timestamp = timestamp
        try:
            if verb == "completed":
                end_timestamp = timestamp
                subtask_dict[obj_cn]["answer"] = data[i]["result"]["response"]
                if data[i]["result"].get("duration") != None:
                    duration = data[i]["result"].get("duration")
                    subtask_dict[obj_cn]["duration"] = duration
                else:
                    score = data[i]["result"]["response"]["score"]
                    subtask_dict[obj_cn]["score"] = score
        except:
            pass

    task_time = time_lag(begin_timestamp, end_timestamp)

    return pbs, subtask_dict, task_time


def Stu_to_csv(Stu, path):
    '''

    :param Stu:
    :param path: verb_data 文件夹
    :return:
    '''
    f = open(path, 'a+')
    student_name = Stu.id
    f.write(student_name)
    f.write("\n")
    for i in range(len(Stu.pbs)):
        f.write(Stu.pbs[i].obj_cn + ",")
        f.write(Stu.pbs[i].obj_id + ",")
        f.write(Stu.pbs[i].verb + ",")
        f.write(Stu.pbs[i].timestamp)
        f.write("\n")
    for k, v in Stu.subtask_dict.items():
        f.write(k + ",")
        f.write(str(v))
        f.write("\n")
    f.close()


########################上面是原始数据处理，下面是将各个动作分门别类######################

# h5页面在fill填空的时候有结果，completed 页面也有填写的结果,   如果有多个答案则列表第一个为满分答案，后面为半满分答案
answer_h5_dict = {"配制种子消毒液": {"count": ["计算"], "weigh": ["称量"], "measure": ["量取"], "dissolve": ["溶解"], "nacl": ["10"],
                              "water": ["190"]},
                  "次氯酸钠称量": {""},  # 只有操作
                  "量取蒸馏水": {"graduate": ["B"]},
                  "消毒方案优选": {"time": ["3", "1", "2"], "cause": ["发芽率高,污染率低", "污染率低", "发芽率高"]},  # 看关键字的暂不处理，输出原来的答案
                  "圣女果的最佳光照条件": {"color": ["红蓝/红蓝光"], "strength": ["2000lx/2000"]},  # 这道题的答案特殊处理
                  "光照恒定": {"strength": ["红蓝/红蓝光", "白/白光", "红橙/红橙光"]},
                  "单一颜色光": {"strength": ["2000lx/2000"]},
                  "选用补光灯": {"lamp": ["LED灯"], "cause": ["CF", "C", "F"]},
                  "补光灯的数量": {"equation": ["ACE", "A", "C", "E"], "lamp": ["1667"]},
                  "调整补光方案": {"led": ["1600"]},  # 暂不处理
                  "影响热水质量的因素": {"physics": ["C"], "hot": ["ABCDEFGH", "A", "B", "C", "D", "E", "F", "G", "H"]},
                  "估算热水质量": {"wendu": ["10"], "volume": ["15000"], "density": ["1.3"], "airheat": ["1.0"],
                             "wendu1": ["25"], "wendu2": ["100"], "wendu3": ["30"], "waterheat": ["4.2"],
                             "mass": ["AC", "A", "C"], "mass1": ["928"]},  # mass1  920-930有待调整
                  "判断营养缺失情况": {"single": ["Mg"], "lack": []},  # lack为原因  看关键字  暂不处理
                  "调节营养液组分": {"normality": ["B"]},
                  "检测营养回收液的酸碱度": {"ph": ["8"], "sour": ["碱"]},
                  "识别害虫": {"worm": ["A", "B", "C"], "because": []},  # because为关键字 暂不处理
                  "放置粘虫板": {"attract": ["B", "A", "C"]},
                  "蚜虫颜色趋性": {"color": ["C/c/黄/黄色", "B/b/橙/橙色", "D/d/绿/绿色"]},
                  "绘制蚜虫颜色趋性图": {"map": ["B/b", "D/d"]}

                  }
# 原始页面只有在completed 页面有填写的结果,列表中全选中则完全正确，选中其中一个为部分正确，选择了不在列表中的则错误
answer_original_dict = {"光合作用的条件": ["A", "C", "D", "E", "F"],
                        "人工补光": ["A", "C"],
                        "调整营养回收液的酸碱度": ["B"],
                        "销售“生活方式”": ["A", "B", "C", "D"],
                        "销售“生活方式”2": ["A", "B", "C", "D"],
                        "智能植物厨房": ["A", "B", "D"]
                        }


class verb_state():
    def __init__(self, verb, state):
        self.verb = verb
        self.state = state


# 处理fill动作的函数，判断填空的状态是correct ，incorrect, halfcorrect,目前看关键字的答案暂时跟普通答案一样处理，可能全部处理为incorrect
def fill_state(answer_h5_dict, pb):
    verb = "fill"
    obj_cn = pb.obj_cn
    obj_id = pb.obj_id
    answer_name = obj_id.split("#")[1].split("==")[0]

    if obj_cn == "消毒方案优选" and obj_id.split("#")[1].split("==")[0] == "cause":  ###这个填写原因的题目单独处理，都给分
        return None
    else:
        try:
            answer = obj_id.split("#")[1].split("==")[1]
            correct_answer = answer_h5_dict[obj_cn][answer_name][0]
            if answer in correct_answer.split("/"):
                state = "correct"
                return verb, state
            # elif len(answer_h5_dict[obj_cn][answer_name])>1:
            #     half_correct_answer = answer_h5_dict[obj_cn][answer_name][1:]
            #     if  answer in "/".join(half_correct_answer).split("/"):
            #         state = "half_correct"
            #         return verb,state
            #     else:
            #         state = "incorrect"
            #         return verb, state
            else:
                state = "incorrect"
                return verb, state
        except:
            pass


# 处理查看资料的动作
def liberary_state(pb):  #################相关的state是1？
    verb = "liberary"
    state = pb.obj_id.split("#")[1]
    if state == "1":
        state = "related"
    else:
        state = "unrelated"
    return verb, state


# 处理completed 的函数（h5页面的结果信息在completed页面，非h5页面的填空题结果在completed页面,如果score =100则correct，大于0小于100 则half_correct，0分incorrect，还有completed页面的时间戳）
def completed_state(Stu, pb):  # 只记录statistic页面内容
    verb = "completed"
    state = pb.timestamp
    try:
        if pb.obj_id.split("#")[1] == "statistic":
            name = pb.obj_cn
            if name == "蚜虫颜色趋性":
                if Stu.subtask_dict[name]["score"] == 60:
                    state = "correct"
                elif Stu.subtask_dict[name]["score"] == 0:
                    state = "incorrect"
                else:
                    state = "half_correct"
            elif name == "绘制蚜虫颜色趋性图":
                if Stu.subtask_dict[name]["score"] == 40:
                    state = "correct"
                elif Stu.subtask_dict[name]["score"] == 0:
                    state = "incorrect"
                else:
                    state = "half_correct"
            else:
                if Stu.subtask_dict[name]["score"] == 100:
                    state = "correct"
                elif Stu.subtask_dict[name]["score"] == 0:
                    state = "incorrect"
                else:
                    state = "half_correct"
        return verb, state
    except:
        pass


# 处理click 的函数（查看任务说明记为click des，其他的click 记为click tips,光的click 记为changcolor red,..)
click_tips = ["F5", "确定", "know", "know1", "know2", "know3", "know4", "know5", "submit"]


def click_state(pb):
    verb = "click"
    if pb.obj_id.split("#")[1] in click_tips:
        state = "tips"
    elif pb.obj_id.split("#")[1] == "查看任务说明":
        state = "des"
    elif pb.obj_id.split("#")[1][-1] == "光":
        verb = "changecolor"
        state = pb.obj_id.split("#")[1]
    elif "运行" in pb.obj_id:
        state = "运行"
    else:
        state = pb.obj_id.split("#")[1]
    return verb, state


# 次氯酸钠称量的drag 是否有用
useful_drag_nacl = ["天平和砝码", "滤纸拖动到左边天平", "滤纸拖动到右边天平", "10g砝码拖动到右边天平", "Na拖动到左边天平", "5g砝码拖动到右边天平"]


def drag_nacl_state(pb):
    verb = "drag"
    if pb.obj_id.split("#")[1].strip().strip('-') in useful_drag_nacl:
        state = "useful"
    else:
        state = "unuseful"
    return verb, state


# 检测营养回收液的酸碱度 drag 是否有用
useful_drag_ph = ["PH试纸被拖动", "玻璃板被拖动", "玻璃棒被拖动", "标准比色卡被拖动"]


def drag_ph_state(pb):
    verb = "drag"
    if pb.obj_id.split("#")[1].strip().strip('-') in useful_drag_ph:
        state = "useful"
    else:
        state = "unuseful"
    return verb, state


# 循环处理每个动作的状态
subtask_name = ["查阅资料", "消毒方案优选", "圣女果的最佳光照条件", "光照恒定", "单一颜色光", "蚜虫颜色趋性", "绘制蚜虫颜色趋性图"]  ####新手任务待处理。


def verb_classify(Stu):
    verb_state_list = []
    time_init = 0
    drag_value_init = 0
    best_light = 0
    subtask_init = "查阅资料"
    state = "actions"
    v_s = verb_state(subtask_init, state)
    verb_state_list.append(v_s)
    for i in range(len(Stu.pbs)):
        if Stu.pbs[i].obj_cn != subtask_init and Stu.pbs[i].obj_cn in subtask_name:
            verb = Stu.pbs[i].obj_cn
            state = "actions"
            v_s = verb_state(verb, state)
            verb_state_list.append(v_s)
            subtask_init = Stu.pbs[i].obj_cn
        elif (Stu.pbs[i].obj_cn != "次氯酸钠称量" and Stu.pbs[i].obj_cn != "检测营养回收液的酸碱度" and Stu.pbs[
            i].obj_cn != "控制热水流入速度") and (Stu.pbs[i].verb.find("drag") != -1 and (
                Stu.pbs[i].obj_id.find("拖动") != -1 or Stu.pbs[i].obj_id.find("bar") != -1)):
            drag_value = "".join(
                re.findall("\d+", Stu.pbs[i].verb) + re.findall("\d+", Stu.pbs[i].obj_id.split("#")[1]))
            if Stu.pbs[i].timestamp != time_init or drag_value != drag_value_init:
                time_init = Stu.pbs[i].timestamp  # 处理拖动滑动条的函数（有限状态自动机，必须根据上一个状态来看下一个动作是否被记录）
                drag_value_init = drag_value
                v_s = verb_state("drag", drag_value)
                verb_state_list.append(v_s)
        elif Stu.pbs[i].obj_cn == "圣女果的最佳光照条件" and Stu.pbs[i].verb == "click" and \
                Stu.pbs[i].obj_id.split("#")[1].split("==")[0][-1] == "光":
            verb = "Determine"
            state = re.findall("\d+", Stu.pbs[i].obj_id.split("#")[1])[0]
            light = Stu.pbs[i].obj_id.split("#")[1].split("==")[0]
            if light != best_light:
                verb1 = "changecolor"
                state1 = light
                v_s1 = verb_state(verb1, state1)
                verb_state_list.append(v_s1)
                best_light = light
            v_s = verb_state(verb, state)
            verb_state_list.append(v_s)
        elif Stu.pbs[i].verb == "fill":
            try:
                verb, state = fill_state(answer_h5_dict, Stu.pbs[i])
                v_s = verb_state(verb, state)
                verb_state_list.append(v_s)
            except:
                pass
        elif Stu.pbs[i].obj_cn == "查阅资料" and "fill" in Stu.pbs[i].verb:  ####处理新手任务-查阅资料
            verb = "fill"
            answer = re.findall("\d+", Stu.pbs[i].verb)[0]
            if answer == "14":
                state = "correct"
            else:
                state = "incorrect"
            v_s = verb_state(verb, state)
            verb_state_list.append(v_s)
        elif Stu.pbs[i].verb == "completed":
            try:
                verb, state = completed_state(Stu, Stu.pbs[i])
                v_s = verb_state(verb, state)
                verb_state_list.append(v_s)
            except:
                pass
        elif "click" in Stu.pbs[i].verb:  # 第8行
            verb, state = click_state(Stu.pbs[i])
            v_s = verb_state(verb, state)
            verb_state_list.append(v_s)
        elif Stu.pbs[i].verb == "gainColor":
            verb = "changecolor"
            state = Stu.pbs[i].obj_id.split("#")[1]
            v_s = verb_state(verb, state)
            verb_state_list.append(v_s)
        elif "查询的值" in Stu.pbs[i].obj_id:  # 处理拖动之后点击确定查询的值
            verb = "Determine"
            state = "".join(re.findall("\d+", Stu.pbs[i].verb) + re.findall("\d+", Stu.pbs[i].obj_id.split("#")[1]))
            v_s = verb_state(verb, state)
            verb_state_list.append(v_s)
        elif Stu.pbs[i].verb == "liberary":
            verb = "liberary"
            verb, state = liberary_state(Stu.pbs[i])
            v_s = verb_state(verb, state)
            verb_state_list.append(v_s)
        else:
            verb, state = Stu.pbs[i].verb, Stu.pbs[i].obj_id
            v_s = verb_state(verb, state)
            verb_state_list.append(v_s)
    return verb_state_list


corlor_list = ["red", "orange", "yellow", "green", "blue", "deepblue", "purple", "white", "black", "nothing"]


def verb_state_simple_every_subtask(verb_state_list):   #确定Determine是up还是down
    '''
    按子任务划分的动作序列 返回的是一个二维数组
    :param verb_state_list:
    :return:
    '''
    verb_state_simple_subtask = []
    drag_state_init = "0"
    subtask_action = None
    color_state_init = "red"
    for i in range(len(verb_state_list)):
        verb = verb_state_list[i].verb
        state = verb_state_list[i].state
        if verb in subtask_name or i == len(verb_state_list):
            verb_state_simple_subtask.append(subtask_action)
            subtask_action = []
        elif verb == "click" and state == "restart":
            subtask_action.append(" ".join([verb, state]))
            drag_state_init = "0"
            color_state_init = "red"
        elif verb == "click" and state == "des":
            subtask_action.append(" ".join([verb, state]))
        elif verb == "liberary":
            subtask_action.append(" ".join([verb, state]))
        elif verb == "fill":
            subtask_action.append(" ".join([verb, state]))
        elif verb == "Determine" and state != "0":
            if int(state) > int(drag_state_init):
                subtask_action.append(" ".join([verb, "up"]))
            elif int(state) < int(drag_state_init):
                subtask_action.append(" ".join([verb, "down"]))
            else:
                pass
            drag_state_init = int(state)
        elif verb == "Determine" and state == "0":
            drag_state_init = "0"
        elif verb == "changecolor":
            if (state[0] >= u'\u4e00' and state[0] <= u'\u9fa5'):
               pass
            elif ord(state[0]) == 114:
                color_state_init = "red"
                pass
            else:
                subtask_action.append(" ".join([verb, state]))
                if corlor_list.index(state) > corlor_list.index(color_state_init):
                    subtask_action.append(" ".join(["Determine", "up"]))
                elif corlor_list.index(state) < corlor_list.index(color_state_init):
                    subtask_action.append(" ".join(["Determine", "down"]))
                else:
                    pass
                color_state_init = state

        else:
            pass
    verb_state_simple_subtask = [i for i in verb_state_simple_subtask if i is not None]
    verb_state_simple_subtask = [i for i in verb_state_simple_subtask if len(i) > 0]

    return verb_state_simple_subtask

action_list=['click des','fill correct','fill incorrect','liberary related','liberary unrelated','click restart']
def verb_state_simple_subtask_strategy(verb_state_simple_subtask):     #将determine 改为有无策略
    all_list=[]
    for i in verb_state_simple_subtask:
        sub_list=[]
        d_list=[]
        for k in range(len(i)):
            if i[k] in action_list:
                if len(d_list)>0:
                    sub_list.append(d_list)
                    d_list = []
                sub_list.append(i[k])
            else:
                d_list.append(i[k])
        strage_list=[]
        for j in sub_list:
            if j in action_list:    ###可能会报错
                strage_list.append(j)
            elif j is not None:
                a = [len(list(v)) for k, v in itertools.groupby(j)]
                if sum(list(map(divide, a)))>=1:
                    tmp1=["strategy_yes"] * sum(list(map(divide, a)))
                    for x in tmp1:
                        strage_list.append(x)
                elif sum(a)//3>0:
                    tmp2=["strategy_no"] * (sum(a)//3)
                    for y in tmp2:
                        strage_list.append(y)
                else:
                    strage_list.append("strategy_no" *1)
            else:
                pass
        all_list.append(strage_list)
    all_list = [i for i in all_list if i is not None]
    all_list = [i for i in all_list if len(i) > 0]
    return all_list

action_dict = {"click des": 0, "fill correct": 1, "fill incorrect": 2, "liberary related": 3, "liberary unrelated": 4,
            "click restart": 5,"strategy_no":6,"strategy_yes":7}


def action_code_all(action_dict, verb_state_simple):
    '''
    没有按照子任务划分的序列编码处理
    :param action_dict: 动作编码字典
    :param verb_state_simple: 整理简化后的动作序列
    :return: 编码后的动作序列
    '''
    verb_state_code = []
    for i in range(len(verb_state_simple)):
        code = action_dict[verb_state_simple[i]]
        verb_state_code.append(code)
    return verb_state_code  # 每个学生的动作序列不一样长，一个一个训练


def action_code_subtask(verb_state_simple_subtask, action_dict):
    code_all_subtask = []
    for i in verb_state_simple_subtask:
        code_subtask = []
        if i == None:
            pass
        else:
            for j in i:
                code = action_dict[j]
                code_subtask.append(code)
        code_all_subtask.append(code_subtask)
    return code_all_subtask


def verb_state_txt(verb_state_list, path):
    f = open(path, 'a+')
    for i in range(len(verb_state_list)):
        f.write(verb_state_list[i].verb + ",")

        f.write(verb_state_list[i].state)
        f.write("\n")
    f.close()


##########################################相关特征提取的函数################################
##########新手任务不考虑，新手任务后面的一个任务开始
######################################################################
def find_not_new(verb_state_list):
    for i in range(len(verb_state_list)):
        verb = verb_state_list[i].verb
        if verb == "消毒方案优选":
            return i


def verb_state_subtask_feature(verb_state_list):
    verb_state_simple_subtask = []
    drag_state_init = "0"
    color_state_init = "red"
    subtask_action = None
    index = find_not_new(verb_state_list)
    for i in range(index, (len(verb_state_list) + 1)):
        try:
            verb = verb_state_list[i].verb
            state = verb_state_list[i].state
        except:
            pass
        if verb in subtask_name_1 or i == len(verb_state_list):
            verb_state_simple_subtask.append(subtask_action)
            subtask_action = []
            subtask_action.append(" ".join([verb]))
        elif verb == "click" and state == "restart":
            subtask_action.append(" ".join([verb, state]))
            drag_state_init = "0"
            color_state_init = "red"
        elif verb == "click" and state == "des":
            subtask_action.append(" ".join([verb, state]))
        elif verb == "liberary":
            subtask_action.append(" ".join([verb, state]))
        elif verb == "Determine" and state != "0":
            if int(state) > int(drag_state_init):
                subtask_action.append(" ".join([verb, "up"]))
            elif int(state) < int(drag_state_init):
                subtask_action.append(" ".join([verb, "down"]))
            else:
                pass
            drag_state_init = int(state)
        elif verb == "Determine" and state == "0":
            drag_state_init = "0"
        elif verb == "completed":
            subtask_action.append(" ".join([verb, state]))
        elif verb == "fill":
            subtask_action.append(" ".join([verb, state]))
        elif verb == "changecolor":
            if (state[0] >= u'\u4e00' and state[0] <= u'\u9fa5'):
                subtask_action.append(" ".join([verb, state]))
            elif ord(state[0]) == 114:
                color_state_init = "red"
                subtask_action.append(" ".join([verb, state]))
            else:
                subtask_action.append(" ".join([verb, state]))
                if corlor_list.index(state) > corlor_list.index(color_state_init):
                    subtask_action.append(" ".join(["Determine", "up"]))
                elif corlor_list.index(state) < corlor_list.index(color_state_init):
                    subtask_action.append(" ".join(["Determine", "down"]))
                else:
                    pass
                color_state_init = state

        else:
            pass
    return verb_state_simple_subtask


def divide(c):
    return c // 3


def find_not_new_time(Stu):
    for i in range(len(Stu.pbs)):
        if Stu.pbs[i].obj_cn == "消毒方案优选" and Stu.pbs[i].verb == "launched":
            return i


######################
def features(feature_subtask, Stu):
    all_features = collections.defaultdict(dict)
    for i in feature_subtask:
        all_features[i[0]]["liberary_count"] = 0
        all_features[i[0]]["liberary_related_count"] = 0
        all_features[i[0]]["liberary_unrelated_count"] = 0
        all_features[i[0]]["click_des_count"] = 0
        all_features[i[0]]["control_variable"] = 0
        all_features[i[0]]["strategy_count"] = 0
        all_features[i[0]]["click_restart_count"] = 0
        all_features[i[0]]["click_determine_count"] =0

        if len(i) > 0 and i[0] != "圣女果的最佳光照条件":
            Determine_sublist = []
            Determine_list = [j for j in i if "Determine" in j or "click restart" in j]
            all_features[i[0]]["click_determine_count"] = len([j for j in i if "Determine" in j])
            sublist = []
            for j in range(len(Determine_list) + 1):
                if j == len(Determine_list) or Determine_list[j][0] == "c":
                    Determine_sublist.append(sublist)
                    sublist = []
                else:
                    sublist.append(Determine_list[j])
            con = [[len(list(v)) for k, v in itertools.groupby((x))] for x in Determine_sublist[1:] if
                   x is not None]
            all_features[i[0]]["strategy_count"] = sum(map(sum, [list(map(divide, i)) for i in con]))

        elif len(i) > 0 and i[0] == "圣女果的最佳光照条件":
            all_features[i[0]]["click_determine_count"] = len([j for j in i if "Determine" in j])
            Determine_sublist = []
            Determine_list = [j for j in i if "Determine" in j or "changecolor" in j]
            sublist = None
            for j in range(len(Determine_list) + 1):
                if j == len(Determine_list) or Determine_list[j][0:11] == "changecolor":
                    Determine_sublist.append(sublist)
                    sublist = []
                else:
                    sublist.append(Determine_list[j])
            con = [[len(list(v)) for k, v in itertools.groupby((x))] for x in Determine_sublist[1:] if
                   x is not None]
            all_features[i[0]]["control_variable"] = sum(map(sum, [list(map(divide, i)) for i in con]))

        for j in i:
            if "liberary" in j:
                all_features[i[0]]["liberary_count"] = all_features[i[0]]["liberary_count"] + 1
                if "liberary related" in j:
                    all_features[i[0]]["liberary_related_count"] = all_features[i[0]]["liberary_related_count"] + 1
                else:
                    all_features[i[0]]["liberary_unrelated_count"] = all_features[i[0]]["liberary_unrelated_count"] + 1
            elif "click des" in j:
                all_features[i[0]]["click_des_count"] = all_features[i[0]]["click_des_count"] + 1
            elif 'click restart' in j:
                all_features[i[0]]["click_restart_count"] = all_features[i[0]]["click_restart_count"] + 1
            else:
                pass
    ##################和时间有关的特征######################
    launch_time_init = 0
    launch_time_init_1 = 0
    not_new_index = find_not_new_time(Stu)
    subtask_name_init = "查阅资料"
    for i in range(not_new_index, len(Stu.pbs)):
        if Stu.pbs[i].obj_cn in subtask_name_1 and Stu.pbs[i].obj_cn != subtask_name_init and Stu.pbs[
            i].verb == "launched":
            subtask_name = Stu.pbs[i].obj_cn
            launch_time_init = Stu.pbs[i].timestamp
            subtask_name_init = subtask_name
            all_features[subtask_name]["related_time"] = 0
            all_features[subtask_name]["unrelated_time"] = 0
            all_features[subtask_name]["launch_action_diff"] = 0
            all_features[subtask_name]["first_des_time"] = 0
            try:
                all_features[subtask_name]["score"] = Stu.subtask_dict[subtask_name]["answer"]["score"]
            except:
                pass
        elif Stu.pbs[i].verb == "liberary":
            if Stu.pbs[i].obj_id.split("#")[1] == "1":
                diff = time_lag(Stu.pbs[i].timestamp, Stu.pbs[i + 1].timestamp)
                all_features[subtask_name]["related_time"] = all_features[subtask_name]["related_time"] + diff
            else:
                diff = time_lag(Stu.pbs[i].timestamp, Stu.pbs[i + 1].timestamp)
                all_features[subtask_name]["unrelated_time"] = all_features[subtask_name]["unrelated_time"] + diff
        elif launch_time_init_1 != launch_time_init and Stu.pbs[i].obj_cn in subtask_name_1 and (
                Stu.pbs[i].verb in ["fill", "gainColor"] or (
                Stu.pbs[i].verb == "click" and Stu.pbs[i].obj_id.split("#")[1][-1] == "光") or Stu.pbs[i].verb.find(
            "drag")) != -1:
            next_action_time = Stu.pbs[i].timestamp
            launch_diff = time_lag(launch_time_init, next_action_time)
            all_features[subtask_name]["launch_action_diff"] = all_features[subtask_name]["launch_action_diff"] + launch_diff
            launch_time_init_1 = launch_time_init
        elif "确定" in Stu.pbs[i].obj_id:
            all_features[subtask_name]["first_des_time"] = time_lag(launch_time_init, Stu.pbs[i].timestamp)

        else:
            pass

    return all_features


def combine_features(Stu, verb_state_list):
    feature_subtask = verb_state_subtask_feature(verb_state_list)
    feature_subtask = feature_subtask[1:]
    all_features = features(feature_subtask, Stu)
    return all_features


def features_flaten(all_features):
    features_list = []
    for key in subtask_name_1:
        if all_features.get(key):
            features_list.append(list(all_features[key].values()))
        else:
            features_list.append([0] * 13)
    flaten_list = [i for j in features_list for i in j]
    return flaten_list


###########################################特征和动作整合################################
subtask_name_1 = ["消毒方案优选", "圣女果的最佳光照条件", "光照恒定", "单一颜色光", "蚜虫颜色趋性", "绘制蚜虫颜色趋性图"]
####两层列表展开
def flatten(input_list):
    output_list = []
    while True:
        if input_list == []:
            break
        for index, i in enumerate(input_list):

            if type(i)== list:
                input_list = i + input_list[index+1:]
                break
            else:
                output_list.append(i)
                input_list.pop(index)
                break

    return output_list
class_1=['00113132724',	'00110160714',	'00110160774',	'00110160775',	'00110160778',	'00110160797',	'00109062571',	'00110269940',	'00110160799',	'00110160759',	'00110160725',	'00110160803',	'00110160726',	'00110320803',	'00110160810',	'00110307484',	'00110160824',	'00110160787',	'00113132564',	'00110160733',	'00110160734',	'00110160736',	'00110160812',	'00110160737',	'00110160814',	'00110160514',]
def process_actions(path):
    files_list = os.listdir(path)
    Students = []
    verb_state_code_all_student = []
    csvFile = open("/home/zijun/PSAADIY/pssa/data/feature/features_change.csv", 'w', newline='')
    writer = csv.writer(csvFile)
    writer.writerow(['1_liberary_count', '1_liberary_related_count', '1_liberary_unrelated_count', '1_click_des_count',
                     '1_control_variable', '1_strategy_count', '1_click_restart_count',"1_click_determine_count",'1_related_time',
                     '1_unrelated_time', '1_launch_action_diff', '1_first_des_time', '1_score', '2_liberary_count',
                     '2_liberary_related_count', '2_liberary_unrelated_count', '2_click_des_count',
                     '2_control_variable', '2_strategy_count', '2_click_restart_count', "2_click_determine_count",'2_related_time',
                     '2_unrelated_time', '2_launch_action_diff', '2_first_des_time', '2_score', '3_liberary_count',
                     '3_liberary_related_count', '3_liberary_unrelated_count', '3_click_des_count',
                     '3_control_variable', '3_strategy_count', '3_click_restart_count',"3_click_determine_count" ,'3_related_time',
                     '3_unrelated_time', '3_launch_action_diff', '3_first_des_time', '3_score', '4_liberary_count',
                     '4_liberary_related_count', '4_liberary_unrelated_count', '4_click_des_count',
                     '4_control_variable', '4_strategy_count', '4_click_restart_count', "4_click_determine_count",'4_related_time',
                     '4_unrelated_time', '4_launch_action_diff', '4_first_des_time', '4_score', '5_liberary_count',
                     '5_liberary_related_count', '5_liberary_unrelated_count', '5_click_des_count',
                     '5_control_variable', '5_strategy_count', '5_click_restart_count',"5_click_determine_count" ,'5_related_time',
                     '5_unrelated_time', '5_launch_action_diff', '5_first_des_time', '5_score', '6_liberary_count',
                     '6_liberary_related_count', '6_liberary_unrelated_count', '6_click_des_count',
                     '6_control_variable', '6_strategy_count', '6_click_restart_count', "6_click_determine_count",'6_related_time',
                     '6_unrelated_time', '6_launch_action_diff', '6_first_des_time', '6_score', "name"])
    for i in files_list:  # 编码出现问题  暂时直接输入path
         if i.split(".")[0] not in class_1:
            stu_code_ever_subtask_action = {}
            data = data_read(i)
            # data = data_read("PSA-T022.json")
            student_name = student_name_get(data)  # 从文件中获得学生姓名
            oldname = path + i
            newname = path + str(student_name) + ".json"
            os.rename(oldname, newname)  # 将日志用学生的学号命名，方便查找
            Stu = Student(student_name)
            Stu.pbs, Stu.subtask_dict, Stu.task_time = process_behavior(data)
            verb_path = "/home/zijun/PSAADIY/pssa/data/verb_data/" + student_name + ".txt"
            Stu_to_csv(Stu, verb_path)
            Students.append(Stu)
            verb_state_list = verb_classify(Stu)
            ########相关特征提取#######
            all_features = combine_features(Stu, verb_state_list)
            flaten_list = features_flaten(all_features)
            flaten_list.append(student_name)
            writer.writerow(flaten_list)

            # ############将按照子任务划分的序列放入json文件中#########
            verb_state_simple_every_subtask_list = verb_state_simple_every_subtask(verb_state_list)
            strategy_subtask_list=verb_state_simple_subtask_strategy(verb_state_simple_every_subtask_list)
            code_all_subtask = action_code_subtask(strategy_subtask_list, action_dict)
            stu_code_ever_subtask_action["username"] = student_name
            stu_code_ever_subtask_action["sequences"] = code_all_subtask
            with open("/home/zijun/PSAADIY/pssa/data/verb_code/behavior_code.json", "a+") as f:  # 存放json的路径需要再完善。
                json.dump(stu_code_ever_subtask_action, f)
                f.write("\n")
            #########HMM动作处理##########
            verb_state_path = "/home/zijun/PSAADIY/pssa/data/verb_state_data/" + student_name + ".txt"
            verb_state_txt(verb_state_list, verb_state_path)
            verb_state_simple_list=flatten(strategy_subtask_list)
            verb_state_code = action_code_all(action_dict, verb_state_simple_list)  #####传统的HMM将学生的整个任务序列作为输入
            verb_state_code_all_student.append(verb_state_code)
    csvFile.close()
    return verb_state_code_all_student


###看每个动作有多少学生涉及到了，删除涉及不多的动作,重新定义字典,重新编码各个序列
def code_statistics(verb_state_code_all_student, action_dict):
    value_lists = set(list(action_dict.values()))
    stu_statistics = collections.defaultdict(list)
    stu_statistics_len = {}
    for i in value_lists:
        for j in range(len(verb_state_code_all_student)):
            if i in verb_state_code_all_student[j]:
                stu_statistics[i].append(j)
    for k, v in stu_statistics.items():
        stu_statistics_len[k] = len(v)
    return stu_statistics, stu_statistics_len


####################################################单层HMM#######################
class stu_HMM():
    def __init__(self, startprob, transmat, emissionprob):
        self.startprob = startprob
        self.transmat = transmat
        self.emissionprob = emissionprob


# 删除不是每个动作都有的学生
action_code = list(range(0, 12))  ###12需要根据最后的编码字典更改


def drop_student(verb_state_code_all_student):
    for i in range(verb_state_code_all_student):
        dif = len(list(set(action_code).difference(set(verb_state_code_all_student[i]))))
        if dif > 0:
            del verb_state_code_all_student[i]
    return verb_state_code_all_student

def normalize(a, axis=None):
    """Normalizes the input array so that it sums to 1.

    Parameters
    ----------
    a : array
        Non-normalized input data.

    axis : int
        Dimension along which normalization is performed.

    Notes
    -----
    Modifies the input **inplace**.
    """
    a_sum = a.sum(axis)
    if axis and a.ndim > 1:
        # Make sure we don't divide by zero.
        a_sum[a_sum == 0] = 1
        shape = list(a.shape)
        shape[axis] = 1
        a_sum.shape = shape

    a /= a_sum

def hmm_model_all(verb_state_code_all_student, n_states):
    model1 = hmm.MultinomialHMM(n_components=n_states, random_state=300,n_iter=300, tol=0.01, verbose=False)
    # emissionprob_p=np.random.RandomState(233).rand(n_states, 8)
    # normalize(emissionprob_p, axis=1)
    # model1.emissionprob_=emissionprob_p
    # startprob_p=np.full(n_states, 1/n_states)
    # model1.startprob_=startprob_p
    # transmat_p=np.full((n_states,n_states),1/n_states)
    # model1.transmat_=transmat_p
    X = np.array(flatten(verb_state_code_all_student)).reshape(1, -1)
    model1.fit(X)
    return model1


###转移概率矩阵可视化
def save_transmat_json(model1, path):
    json_list = []
    for i in range(len(model1.startprob_)):
        state_dict = {}
        state_dict["edges"] = list(model1.transmat_[i])
        state_dict["init"] = model1.startprob_[i]
        state_dict["name"] = i
        json_list.append(state_dict)
    # print(json_list)
    with open(path, "w") as f:  # 存放json的路径需要再完善。
        json.dump(json_list, f)
        f.write("\n")


#######################调用函数########################
path = "/home/zijun/PSAADIY/pssa/data/log_data/"
verb_state_code_all_student = process_actions(path)


def l1_hmm_verb_add(verb_state_code_all_student):    #補齊該學生爲出現的動作
    for i in range(len(verb_state_code_all_student)):
        diff = set(list(action_dict.values())) - set(verb_state_code_all_student[i])
        if len(diff) > 0:
            for j in list(diff):
                verb_state_code_all_student[i].append(j)
    return verb_state_code_all_student


verb_state_code_all_student = l1_hmm_verb_add(verb_state_code_all_student)
stu_statistics, stu_statistics_len = code_statistics(verb_state_code_all_student, action_dict)
print(stu_statistics)
print(stu_statistics_len)

for i in range(3, 6):
    model1 = hmm_model_all(verb_state_code_all_student, i)
    emissionprob_path = "/home/zijun/PSAADIY/pssa/data/emissionprob/" + str(i) + ".csv"
    np.savetxt(emissionprob_path, model1.emissionprob_)
    trans_path = "/home/zijun/PSAADIY/pssa/data/state_trans/" + str(i) + ".json"
    save_transmat_json(model1, trans_path)