import pandas as pd
import pm4py


def data_prep(sample):
    sample['TimeStamp'] = pd.to_datetime(sample['TimeStamp'])
    sample['BusinesDate'] = sample['TimeStamp'].dt.date
    sample['OrderID'] = sample['OrderID'].astype('int')
    sample['PosID'] = sample['PosID'].astype('str')
    return sample

def case_identifier(filtered):
    pos_1 = filtered.loc[:,['BusinesDate', 'PosID', 'Activity', 'TimeStamp', 'OrderID', 'OperatorID']].sort_values(by = ['BusinesDate', 'OrderID', 'TimeStamp', 'OperatorID']).reset_index(drop = True)
    pos_1['Case'] = 1
    order_change_points = pos_1['OrderID'].ne(pos_1['OrderID'].shift()).cumsum()
    pos_1['Case'] = order_change_points
    return pos_1

def event_log(pos_1):
    initial = pos_1[['Case', 'Activity', 'TimeStamp']]
    event_log = pm4py.format_dataframe(initial, case_id = 'Case', activity_key= 'Activity', timestamp_key= 'TimeStamp', timest_format= '%Y-%m-%d %H:%M:%S')
    event_log.drop(['Case', 'TimeStamp', 'Activity', '@@index', '@@case_index'], axis = 1, inplace = True)
    return event_log

def frequencies(event_log):
    acts = event_log["concept:name"].value_counts().to_frame()
    acts['Occurence'] = event_log.groupby(["case:concept:name", "concept:name"]).first().reset_index()["concept:name"].value_counts()
    acts.rename(columns = {'concept:name': 'Recurrence'}, inplace = True)  
    return acts


