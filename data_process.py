import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.cross_validation import train_test_split
import matplotlib.pyplot as plt
from sklearn.cross_validation import cross_val_score, ShuffleSplit
import seaborn as sns
from sklearn.model_selection import GridSearchCV
####################################################特征聚合###################
sns.set(style="whitegrid",context="notebook")
def data_df1(path):
    df1=pd.read_csv(path)
    cols=[i for i in list(df1.columns) if "3" not in i and "4" not in i]
    df1=df1.loc[:,cols]
    df1["5_score"]=df1["5_score"]*10/6
    df1["6_score"]=df1["6_score"]*10/4
    df1["sum_score"]=df1[["1_score","2_score","5_score","6_score"]].apply(lambda x: x.sum(), axis=1)/4
    df1["click_des_count"]=df1[["1_click_des_count","2_click_des_count","5_click_des_count","6_click_des_count"]].apply(lambda x: x.sum(), axis=1)
    df1["liberary_related_count"]=df1[["1_liberary_related_count","2_liberary_related_count","5_liberary_related_count","6_liberary_related_count"]].apply(lambda x: x.sum(), axis=1)
    df1["liberary_unrelated_count"]=df1[["1_liberary_unrelated_count","2_liberary_unrelated_count","5_liberary_unrelated_count","6_liberary_unrelated_count"]].apply(lambda x: x.sum(), axis=1)
    df1["strategy_count"]=df1[["1_strategy_count","2_control_variable","5_strategy_count","6_strategy_count"]].apply(lambda x: x.sum(), axis=1)
    df1["click_restart_count"]=df1[["1_click_restart_count","2_click_restart_count","5_click_restart_count","6_click_des_count"]].apply(lambda x: x.sum(), axis=1)
    df1["click_determine_count"]=df1[["1_click_determine_count","2_click_determine_count","5_click_determine_count","6_click_determine_count"]].apply(lambda x: x.sum(), axis=1)
    df1["related_time"]=df1[["1_related_time","2_related_time","5_related_time","6_related_time"]].apply(lambda x: x.sum(), axis=1)
    df1["unrelated_time"]=df1[["1_unrelated_time","2_unrelated_time","5_unrelated_time","6_unrelated_time"]].apply(lambda x: x.sum(), axis=1)
    df1["launch_action_diff"]=df1[["1_launch_action_diff","2_launch_action_diff","5_launch_action_diff","6_launch_action_diff"]].apply(lambda x: x.sum(), axis=1)
    df1["first_des_time"]=df1[["1_first_des_time","2_first_des_time","5_first_des_time","6_first_des_time"]].apply(lambda x: x.sum(), axis=1)
    df1["related_time_rate"]=df1["related_time"]/(df1["related_time"]+df1["unrelated_time"])
    df1["related_count_rate"] = df1["liberary_related_count"] / (df1["liberary_related_count"] + df1["liberary_unrelated_count"])
    df1["strage_rate"]=df1["strategy_count"]/df1["click_determine_count"]
    df_tmp=df1[["sum_score","click_des_count","liberary_related_count","liberary_unrelated_count","strategy_count","click_restart_count","click_determine_count","related_time","unrelated_time","launch_action_diff","first_des_time","related_time_rate","related_count_rate","strage_rate"]]
    df_tmp.round(2)
    return df_tmp



df1=data_df1("./data/feature/features_change_123.csv")
df1.fillna(0,inplace=True)
df1.to_csv("./data/feature/features_merge_123.csv")

df_max_min = (df1 - df1.min()) / (df1.max() - df1.min())
df_max_min.to_csv("./data/feature/features_guiyi_123.csv",index=False)

# sns.set(font_scale=0.5)
# cols=['sum_score', 'click_des_count', 'liberary_related_count', 'liberary_unrelated_count', 'strategy_count', 'click_restart_count', "click_determine_count",'related_time', 'unrelated_time', 'launch_action_diff', 'first_des_time',"related_time_rate","related_count_rate","strage_rate"]
# sns.pairplot(df1,size=1.5)
# plt.show()
# # 获取相关系数矩阵
# cm = np.corrcoef(df1.values.T)
# # 设置字的比例
# # 绘制相关系数图
# hm = sns.heatmap(cm, cbar=True, annot=True, square=True, fmt=".2f",
#                  annot_kws={"size": 7}, yticklabels=cols, xticklabels=cols)
# plt.show()
##########################################通过随机森林或这XGBOOST看特征重要度#################
def random_forest(df):
    x=df[['click_des_count', 'liberary_related_count', 'liberary_unrelated_count', 'strategy_count', 'click_restart_count', "click_determine_count",'related_time', 'unrelated_time', 'launch_action_diff', 'first_des_time',"related_time_rate","related_count_rate","strage_rate"]]
    y=df["sum_score"]
    y=np.array(y)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.6, random_state=33)
    from sklearn.preprocessing import StandardScaler
    # ss_x = StandardScaler()
    # x_train = ss_x.fit_transform(x_train)
    # x_test = ss_x.transform(x_test)
    # ss_y = StandardScaler()
    # y_train = ss_y.fit_transform(y_train.reshape(-1, 1))
    # y_test = ss_y.transform(y_test.reshape(-1, 1))
    rfr = RandomForestRegressor()
    ####调參
    tuned_parameter = [{'min_samples_leaf': [2,3, 4,5,6], 'n_estimators': [30,100,50],"max_depth":[2,3,4,5,6]}]
    # 神器出场,cv设置交叉验证
    # clf = GridSearchCV(estimator=rfr,param_grid=tuned_parameter, cv=5, n_jobs=1,scoring='r2')
    rfr.fit(x, y)
    # print('Best parameters:')
    # print(rfr.best_params_)
    # 预测 保存预测结果
    rfr_y_predict = rfr.predict(x_test)
    print("随机森林回归测试集的R_squared值为：", r2_score(y_test, rfr_y_predict))
    # print("随机森林回归训练集的R_squared值为:", r2_score(y, clf.predict(x)))  # 过拟合
    # print("随机森林回归的均方误差为:", mean_squared_error(ss_y.inverse_transform(y_test),
    #                                           ss_y.inverse_transform(rfr_y_predict)))
    # print("随机森林回归的平均绝对误差为:", mean_absolute_error(ss_y.inverse_transform(y_test),
    #                                              ss_y.inverse_transform(rfr_y_predict)))
    print("随机森林回归的特征重要度为;",rfr.feature_importances_)
    # print("特征选择：")
    scores = []
    names = ['click_des_count', 'liberary_related_count', 'liberary_unrelated_count', 'strategy_count',
            'click_restart_count', "click_determine_count", 'related_time', 'unrelated_time', 'launch_action_diff',
            'first_des_time', "related_time_rate", "related_count_rate", "strage_rate"]
    for i in range(x.shape[1]):
        score = cross_val_score(rfr, x.ix[:, i:i + 1], y, scoring="r2",
                                cv=ShuffleSplit(len(x), 3, .3))
        scores.append((round(np.mean(score), 3), names[i]))
    print(sorted(scores, reverse=True))
random_forest(df_max_min)

def xgb_test(df):
    x=df[['click_des_count', 'liberary_related_count', 'liberary_unrelated_count', 'strategy_count', 'click_restart_count', "click_determine_count",'related_time', 'unrelated_time', 'launch_action_diff', 'first_des_time',"related_time_rate","related_count_rate","strage_rate"]]
    y=df["sum_score"]
    y=np.array(y)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.7, random_state=33)
    import xgboost as xgb
    model = xgb.XGBRegressor(max_depth=4, learning_rate=0.1, n_estimators=100, silent=False, objective="reg:linear")
    model.fit(x_train, y_train)
    rfr_y_predict = model.predict(x_test)
    print("xgboost回归测试集r2_score： ",r2_score(y_test, rfr_y_predict))
    print("xgboost回归的特征重要度为;",model.feature_importances_)
    # print("进行特征选择")
    # from sklearn.feature_selection import f_regression
    # F=f_regression(x,y)
    # print("单变量特征选择：",F)
# xgb_test(df_max_min)

def pretty_print_linear(coefs, names = None, sort = False):
    if names == None:
        names = ["X%s" % x for x in range(len(coefs))]
    lst = zip(coefs, names)
    if sort:
        lst = sorted(lst,  key = lambda x:-np.abs(x[0]))
    return " + ".join("%s * %s" % (round(coef, 3), name)
                                   for coef, name in lst)

def zhengze_L1_L2(df):
    from sklearn.linear_model import Lasso
    from sklearn.linear_model import Ridge
    x=df[['click_des_count', 'liberary_related_count', 'liberary_unrelated_count', 'strategy_count', 'click_restart_count', "click_determine_count",'related_time', 'unrelated_time', 'launch_action_diff', 'first_des_time',"related_time_rate","related_count_rate","strage_rate"]]
    y=df["sum_score"]
    y=np.array(y)
    lasso = Lasso(alpha=.3)
    lasso.fit(x, y)
    names = ['click_des_count', 'liberary_related_count', 'liberary_unrelated_count', 'strategy_count',
            'click_restart_count', "click_determine_count", 'related_time', 'unrelated_time', 'launch_action_diff',
            'first_des_time', "related_time_rate", "related_count_rate", "strage_rate"]

    print("Lasso model: ", pretty_print_linear(lasso.coef_, names, sort=True))
    ridge = Ridge(alpha=10)
    ridge.fit(x,y)
    print("Ridge model:", pretty_print_linear(ridge.coef_,names))
# zhengze_L1_L2(df_max_min)

