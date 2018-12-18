import json
a=[[1,2,3],[3,2,1]]
action1={"username":"xx","actions":a}
action2={"username":"xx","actions":a}
with open("/home/zijun/PSAADIY/json_test.json","a+") as f:
    json.dump(action1,f)
    f.write("\n")
    json.dump(action2, f)