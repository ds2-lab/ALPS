import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

init_policy = {1: [1, 200], 2: [2, 200]}

def read_data(file = "data.csv"):
    df = pd.read_csv(file, sep=";")
    dataTs = {}
    dataWt = {}
    count_class = {}
    func_map = {}
    for classid in df[' classid'].unique():
        if classid not in count_class:
            count_class[classid] = 0
        dataTs[classid] = []
        dataWt[classid] = []
        sub_df = df[df[' classid'] == classid]
        func_map[classid] = list(sub_df[' funcid'].unique())
        count_class[classid] += len(sub_df)
        for d in sub_df[' timeSlice']:
            try:
                dataTs[classid].extend([int(a) for a in d.strip().split()])
            except:
                dataTs[classid].append(d)
        for d in sub_df[' wait']:
            dataWt[classid].append(int(d))
    return dataTs, dataWt,count_class,func_map

def LinerRegression(cpu_ulilization, args, old_policy = {}):
    """
    policy: func_id: [priority, timeSlice]
    """
    if len(old_policy) == 0:
        old_policy = init_policy
    dataTs, dataWt, count_class, func_map = read_data()
    
    data_stat = {}
    for k in dataTs:
        y = np.array(dataTs[k]).reshape(-1, 1)
        x = np.arange(1, len(dataTs[k])+1).reshape(-1, 1)
        model = LinearRegression()
        model.fit(x, y)
        tp1 = np.array([[len(dataTs[k])+1]]) 
        prediction = model.predict(tp1)
        data_stat[k] = [int(prediction), np.std(dataTs[k]), np.median(dataWt[k])]

    sorted_keys = sorted(data_stat.keys(), key=lambda x: data_stat[x][0])
    if 1 not in sorted_keys:
        sorted_keys.insert(0,1)

    for i in range(len(sorted_keys)):
        if sorted_keys[i] not in old_policy:
            old_policy[sorted_keys[i]] = [sorted_keys[i], 0]
        old_policy[sorted_keys[i]] = [sorted_keys[i],0]
        old_policy[sorted_keys[i]][0] = i + 1
    
    up_ts = 0
    updated_policy = {}
    for k in sorted_keys:
        if k in data_stat:
            alpha = args.alpha
            upperBound = data_stat[k][0] if data_stat[k][0] <= 200 else 200
            upperBound = int(upperBound * alpha)
            if upperBound >= 200:
                upperBound= 200
            b = args.beta
            penalty = b * data_stat[k][1]
            #penalty = a * (data_stat[k][2]) + data_stat[k][1]
            new_v = upperBound - penalty if upperBound - penalty > 0 else 0
            if up_ts !=0 and new_v > up_ts:
                new_v = up_ts
            if k in old_policy and old_policy[k][1] > 1:
                up_ts = int(0.7 * new_v + 0.3 * old_policy[k][1])
            else:
                up_ts = new_v
            penalty = 1 if cpu_ulilization < args.theta else b * (100 + args.theta - cpu_ulilization)/(100*args.gamma)
            up_ts = int(new_v * penalty)
            updated_policy[k] = [k, up_ts]
    new_policy = {}
    for class_id in func_map:
        for func_id in func_map[class_id]:
            if class_id in data_stat:
                new_policy[func_id] = updated_policy[class_id]

    for k in old_policy:
        if k not in new_policy:
            new_policy[k] = old_policy[k]
    return new_policy

def RandomForest(cpu_ulilization, args, old_policy = {}):
    if len(old_policy) == 0:
        old_policy = init_policy
    dataTs, dataWt, count_class, func_map = read_data()
    
    data_stat = {}
    for k in dataTs:
        y = np.array(dataTs[k]).reshape(-1, 1)
        x = np.arange(1, len(dataTs[k])+1).reshape(-1, 1)
        model = RandomForestRegressor(n_estimators=10, random_state=42)
        model.fit(x, y)
        tp1 = np.array([[len(dataTs[k])+1]])
        prediction = model.predict(tp1)
        data_stat[k] = [int(prediction), np.std(dataTs[k]), np.median(dataWt[k])]
    sorted_keys = sorted(data_stat.keys(), key=lambda x: data_stat[x][0])
    if 1 not in sorted_keys:
        sorted_keys.insert(0,1)
    for i in range(len(sorted_keys)):
        if sorted_keys[i] not in old_policy:
            old_policy[sorted_keys[i]] = [sorted_keys[i], 0]
        old_policy[sorted_keys[i]] = [sorted_keys[i],0]
        old_policy[sorted_keys[i]][0] = i + 1
    
    up_ts = 0
    updated_policy = {}
    for k in sorted_keys:
        if k in data_stat:
            alpha = args.alpha
            upperBound = data_stat[k][0] if data_stat[k][0] <= 200 else 200
            upperBound = int(upperBound * alpha)
            if upperBound >= 200:
                upperBound= 200
            b = args.beta
            penalty = b * data_stat[k][1]
            new_v = upperBound - penalty if upperBound - penalty > 0 else 0
            if up_ts !=0 and new_v > up_ts:
                new_v = up_ts
            if k in old_policy and old_policy[k][1] > 1:
                up_ts = int(0.7 * new_v + 0.3 * old_policy[k][1])
            else:
                up_ts = new_v
            penalty = 1 if cpu_ulilization < args.theta else b * (100 + args.theta - cpu_ulilization)/(100*args.gamma)
            up_ts = int(new_v * penalty)
            updated_policy[k] = [k, up_ts]
    new_policy = {}
    for class_id in func_map:
        for func_id in func_map[class_id]:
            if class_id in data_stat:
                new_policy[func_id] = updated_policy[class_id]

    for k in old_policy:
        if k not in new_policy:
            new_policy[k] = old_policy[k]
    return new_policy

def ExponentialWeightedMovingAverage(cpu_ulilization, args, old_policy = {}):
    """
    policy: func_id: [priority, timeSlice]
    """
    if len(old_policy) == 0:
        old_policy = init_policy
    dataTs, dataWt, count_class, func_map = read_data()
    
    data_stat = {}
    for k in dataTs:
        series = pd.Series(dataTs[k])    
        alpha = 0.2
        ewma = series.ewm(alpha=alpha).mean()
        prediction = ewma.iloc[-1]
        data_stat[k] = [int(prediction), np.std(dataTs[k]), np.median(dataWt[k])]
    sorted_keys = sorted(data_stat.keys(), key=lambda x: data_stat[x][0])
    if 1 not in sorted_keys:
        sorted_keys.insert(0,1)
    for i in range(len(sorted_keys)):
        if sorted_keys[i] not in old_policy:
            old_policy[sorted_keys[i]] = [sorted_keys[i], 0]
        old_policy[sorted_keys[i]] = [sorted_keys[i],0]
        old_policy[sorted_keys[i]][0] = i + 1
    
    up_ts = 0
    updated_policy = {}
    for k in sorted_keys:
        if k in data_stat:
            alpha = args.alpha
            upperBound = data_stat[k][0] if data_stat[k][0] <= 200 else 200
            upperBound = int(upperBound * alpha)
            if upperBound >= 200:
                upperBound= 200
            b = args.beta
            penalty = b * data_stat[k][1]
            new_v = upperBound - penalty if upperBound - penalty > 0 else 0
            if up_ts !=0 and new_v > up_ts:
                new_v = up_ts
            if k in old_policy and old_policy[k][1] > 1:
                up_ts = int(0.7 * new_v + 0.3 * old_policy[k][1])
            else:
                up_ts = new_v
            penalty = 1 if cpu_ulilization < args.theta else b * (100 + args.theta - cpu_ulilization)/(100*args.gamma)
            up_ts = int(new_v * penalty)
            updated_policy[k] = [k, up_ts]
    new_policy = {}
    for class_id in func_map:
        for func_id in func_map[class_id]:
            if class_id in data_stat:
                new_policy[func_id] = updated_policy[class_id]

    for k in old_policy:
        if k not in new_policy:
            new_policy[k] = old_policy[k]
    return new_policy

def heurtistic(cpu_ulilization, args, old_policy = {}):
    if len(old_policy) == 0:
        old_policy = init_policy
    dataTs, dataWt, count_class, func_map = read_data()
    
    data_stat = {}
    for k in dataTs:
        data_stat[k] = [np.mean(dataTs[k]), np.std(dataTs[k]), np.median(dataWt[k])]
    sorted_keys = sorted(data_stat.keys(), key=lambda x: data_stat[x][0])
    if 1 not in sorted_keys:
        sorted_keys.insert(0,1)

    for i in range(len(sorted_keys)):
        if sorted_keys[i] not in old_policy:
            old_policy[sorted_keys[i]] = [sorted_keys[i], 0]
        old_policy[sorted_keys[i]] = [sorted_keys[i],0]
        old_policy[sorted_keys[i]][0] = i + 1
    
    up_ts = 0
    updated_policy = {}
    for k in sorted_keys:
        if k in data_stat:
            alpha = args.alpha
            upperBound = data_stat[k][0] if data_stat[k][0] <= 200 else 200
            upperBound = data_stat[k][0]
            upperBound = int(upperBound * alpha)
            if upperBound >= 200:
                upperBound= 200
            b = args.beta
            penalty = b * data_stat[k][1]
            new_v = upperBound - penalty if upperBound - penalty > 0 else 0
            if up_ts !=0 and new_v > up_ts:
                new_v = up_ts
            if k in old_policy and old_policy[k][1] > 1:
                up_ts = int(0.7 * new_v + 0.3 * old_policy[k][1])
            else:
                up_ts = new_v
            penalty = 1 if cpu_ulilization < args.theta else b * (100 + args.theta - cpu_ulilization)/(100*args.gamma)
            up_ts = int(new_v * penalty)
            updated_policy[k] = [k, up_ts]
    new_policy = {}
    for class_id in func_map:
        for func_id in func_map[class_id]:
            if class_id in data_stat:
                new_policy[func_id] = updated_policy[class_id]

    for k in old_policy:
        if k not in new_policy:
            new_policy[k] = old_policy[k]
    return new_policy