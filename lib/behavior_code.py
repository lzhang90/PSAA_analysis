import collections
import json
from lib.answer_key import score_answer
import os

uncoded_action_set = set()

def get_name(s):
    s = s[s.rindex('/') + 1:]
    return s

def is_step(full_obj_id):
    if 'step' in full_obj_id:
        return True
    else:
        return False

def simplify_an_action(action_json):
    obj_id = get_name(action_json["object"]["id"])
    obj_id_cn = action_json["object"]["definition"]["name"]["zh_CN"]
    verb = get_name(action_json["verb"]["id"])
    timestamp = action_json['timestamp'][:-6]
    return timestamp, verb, obj_id, obj_id_cn

def code_atom_action(cur_task, action_json):
    is_a_step = is_step(action_json["object"]["id"])
    obj_id = str(get_name(action_json["object"]["id"]))
    task_id = cur_task
    if "#" in obj_id:
        task_id, obj_id = obj_id.split("#")
    obj_id_cn = action_json["object"]["definition"]["name"]["zh_CN"]
    verb = str(get_name(action_json["verb"]["id"]))
    timestamp = action_json['timestamp'][:-6]
    coded_action = 'uncoded'
    ignore_the_action = False
    if obj_id == "submitTimes" or obj_id == "answerTime":
        ignore_the_action = True
    else:
        if verb.startswith('click'):
            if obj_id == '查看任务说明':
                coded_action = 'click des'
            elif obj_id == 'restart':
                coded_action = 'click restart'
            elif obj_id in ['submit', 'submit1']:
                coded_action = 'click submit'
            elif obj_id == 'tipclose':
                coded_action = 'click tipclose'
            elif obj_id == "F5":
                coded_action = 'click restart'
            if task_id == "3303.htm" and "==" in obj_id:
                coded_action = "test_value " + obj_id
            if task_id == "3306.htm" and obj_id == "运行":
                coded_action = "run_test"
        if verb.startswith("fill"):
            score = score_answer(task_id, verb, obj_id)
            if score == 1:
                coded_action = 'fill correct'
            else:
                coded_action = 'fill incorrect'
            if score == -1:
                coded_action = 'uncoded'
        if "drag" in verb:
            if task_id == "3302.htm":
                if "拖动" in obj_id:
                    coded_action = "drag_through "+obj_id.split("===")[1]
                elif "查询的值" in obj_id:
                    coded_action = "test_value "+obj_id.split("===")[1]
            if task_id == "3303.htm":
                value = verb.split("==")[0]
                coded_action = "drag_through " + value
        if verb == "gainColor":
            coded_action = "choose_color " + obj_id
        if verb == "fillColor":
            coded_action = "apply_color " + obj_id.split(" ")[1]

        if verb == 'launched':
            if "json" in obj_id: #the object is a reading material
                if action_json['result']['score']['raw'] == 1: #the reading material is related
                    coded_action = 'enter library_related'
                else:
                    coded_action = 'enter library_unrelated'
            if "htm" in obj_id: #the object is a task
                if is_a_step:
                    coded_action = 'enter task_'+obj_id
                    cur_task = obj_id
                else:
                    ignore_the_action = True
        if verb == 'exited':
            if "json" in obj_id: #the object is a reading material
                if action_json['result']['score']['raw'] == 1: #the reading material is related
                    coded_action = 'excited library_related'
                else:
                    coded_action = 'excited library_unrelated'
            if "htm" in obj_id: #the object is a task
                if is_a_step:
                    coded_action = 'excited task_'+obj_id
                    cur_task = '-1'
                else:
                    ignore_the_action = True

    if coded_action == 'uncoded' and not ignore_the_action:
        coded_action += ': '+verb+' '+obj_id
        if coded_action not in uncoded_action_set:
            print(cur_task+" "+task_id+': '+coded_action)
            uncoded_action_set.add(coded_action)

    return cur_task, coded_action

def process_all_log(dir_path):
    for file_name in os.listdir(dir_path):
        with open(dir_path+"/"+file_name, mode='r', encoding='utf-8') as f:
            all_actions=json.load(f)
            cur_task = '-1'
            for an_action in all_actions:
                cur_task, atom_action = code_atom_action(cur_task, an_action)
                #print(simplified_action)
    print(uncoded_action_set)

process_all_log("../data/raw_data_unzipped")

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