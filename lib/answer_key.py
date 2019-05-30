# h5页面在fill填空的时候有结果，completed 页面也有填写的结果,   如果有多个答案则列表第一个为满分答案，后面为半满分答案
answer_key_dict = {
    "3301.htm": {"time": "14"},
    "配制种子消毒液": {"count": ["计算"], "weigh": ["称量"], "measure": ["量取"], "dissolve": ["溶解"], "nacl": ["10"],
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


def score_answer(p_id, verb: str, obj_id):
    score = -1
    if p_id == "3301.htm":
        if verb.startswith("fill"):
            ans_key = answer_key_dict["3301.htm"][obj_id]
            stu_ans = verb[4:]
            if ans_key == stu_ans:
                score = 1
            else:
                score = 0
    return score
