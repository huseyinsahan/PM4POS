import streamlit as st
import time
import numpy as np
import datetime
import pm4py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils import *
st.title('Activity Analysis')
st.markdown("""Here you can analyze the activity transitions in a heatmap. The main idea is to identify specific activity types resulting in bottlenecks.""")

sample = pd.read_csv(('cache.csv'), index_col=0)
sample['TimeStamp'] = pd.to_datetime(sample['TimeStamp'])
sample['BusinesDate'] = sample['TimeStamp'].dt.date
sample['PosID'] = sample['PosID'].astype('str')

cihaz = sample['PosID'].unique()

pos = st.selectbox(
        'Pick the pos device to be analyzed',
        cihaz
    )

start_date = st.date_input(
    'Pick a start date',
    sample['BusinesDate'].min()
)

end_date = st. date_input(
    'Pick an end date',
    sample['BusinesDate'].max()
)

filtered = sample[(sample['BusinesDate'] >= start_date)&(sample['BusinesDate'] <= end_date)&(sample['PosID'] == pos)]
pos_1 = filtered.loc[:,['BusinesDate', 'PosID', 'Activity', 'TimeStamp', 'OrderID', 'OperatorID']].sort_values(by = ['BusinesDate', 'OrderID', 'TimeStamp', 'OperatorID']).reset_index(drop = True)
pos_1['Case'] = 1
# Find the points where OrderID changes
order_change_points = pos_1['OrderID'].ne(pos_1['OrderID'].shift()).cumsum()
# Assign 'Case' values based on order change points
pos_1['Case'] = order_change_points
st.subheader('Filtered Table')
st.dataframe(pos_1)


initial = pos_1[['Case', 'Activity', 'TimeStamp']]
event_log = pm4py.format_dataframe(initial, case_id = 'Case', activity_key= 'Activity', timestamp_key= 'TimeStamp', timest_format= '%Y-%m-%d %H:%M:%S')
event_log.drop(['Case', 'TimeStamp', 'Activity', '@@index', '@@case_index'], axis = 1, inplace = True)

activities = event_log
activities.sort_values(by = ['case:concept:name', 'time:timestamp'], inplace= True)  
activities['Interval'] = activities['time:timestamp'] - activities['time:timestamp'].shift(1) 
activities['Interval_seconds'] = activities['Interval'].dt.total_seconds()
activities['Prev_act'] = activities['concept:name'].shift()

cases = event_log.groupby('case:concept:name', as_index= False).agg(Length = pd.NamedAgg(column="concept:name", aggfunc="count"), 
                                                                Duration = pd.NamedAgg(column = 'time:timestamp', aggfunc= lambda x : x.max() - x.min()),
                                                                Start = pd.NamedAgg(column = 'time:timestamp' , aggfunc = 'min' ),
                                                                End = pd.NamedAgg(column = 'time:timestamp', aggfunc = 'max'))
cases.sort_values(by = 'Start', inplace= True)                                                           
cases['Interval'] = cases.Start - cases.End.shift(1)                           
cases['Interval'] = cases['Interval'].dt.total_seconds()
cases['Duration'] = cases['Duration'].dt.total_seconds()
case_indexes = cases[cases['Interval']<0]['case:concept:name']
fp_mean_time = activities[~activities['case:concept:name'].isin(case_indexes)] # Mean needs to have positive values only
transition = fp_mean_time.groupby(by = ['Prev_act', 'concept:name'])['Interval_seconds'].agg(['count', 'mean']).reset_index()

freq_fp = pd.DataFrame(transition['Prev_act'].unique(), columns= ['Previous Activities'])
for e in freq_fp['Previous Activities']:
    freq_fp[e] = 0
freq_fp.set_index('Previous Activities', inplace= True)
for index, row in transition.iterrows():
    freq_fp.at[row['Prev_act'], row['concept:name']] = round(row['count'],2)
freq_fp.rename({'Cancel the products in the order, including raw material, linked items, common items, choice items': 'Cancel the products in the order including raw mat...'}, inplace = True)
freq_fp.rename({'Cancel the products in the order, including raw material, linked items, common items, choice items': 'Cancel the products in the order including raw mat...'},axis = 1,  inplace = True)
freq_fp.fillna(0, inplace=True)

mean_fp = pd.DataFrame(transition['Prev_act'].unique(), columns= ['Previous Activities'])
for e in mean_fp['Previous Activities']:
    mean_fp[e] = 0
mean_fp.set_index('Previous Activities', inplace= True)
for index, row in transition.iterrows():
    mean_fp.at[row['Prev_act'], row['concept:name']] = round(row['mean'],2)
mean_fp.rename({'Cancel the products in the order, including raw material, linked items, common items, choice items': 'Cancel the products in the order including raw mat...'}, inplace = True)
mean_fp.rename({'Cancel the products in the order, including raw material, linked items, common items, choice items': 'Cancel the products in the order including raw mat...'},axis = 1,  inplace = True)
mean_fp.fillna(0, inplace=True)

fig_1, (ax1,ax2) = plt.subplots(figsize=(12, 8), nrows = 2)

ax1.set_title('Frequency of transition between activities', size = 16 )
g1 = sns.heatmap(freq_fp, annot= True, ax = ax1, linewidths= .3, annot_kws= {'size' : 10}, cmap = 'coolwarm', fmt = 'g')
g1.set_xticks([])
g1.set_xlabel(None)
ax2.set_title('Mean of total seconds spent between activities', size = 16 )
g2 = sns.heatmap(mean_fp, annot= True, ax = ax2, linewidths= .3, annot_kws= {'size' : 10}, cmap = 'coolwarm', fmt = 'g')


st.header('Transition between activities')

st.markdown(('Total activity occured: ' + str(freq_fp.values.sum())))

st.pyplot(fig_1)


