import streamlit as st
import datetime 
import pandas as pd
import pm4py
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.title('Order Analysis')
st.markdown("""Here eventlogs can be analyzed in terms of order durations.""")

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
defined_end_activities = ['Sale item', 'The order enters the payment from the sales inferface']
defined_start_activities = ['Sale item', 'Handling of raw materials: adding and emptying', 'The order enters the payment from the sales inferface']
lasts = event_log.groupby('case:concept:name')['concept:name'].last().to_frame().reset_index()
firsts = event_log.groupby('case:concept:name')['concept:name'].first().to_frame().reset_index()
outliers_last= lasts['case:concept:name'][lasts['concept:name'].isin(defined_end_activities)]
outliers_first = firsts['case:concept:name'][firsts['concept:name'].isin(defined_start_activities)]
inliers = pd.concat([outliers_last, outliers_first]).drop_duplicates()
event_log = event_log[~event_log['case:concept:name'].isin(inliers)]

cases = event_log.groupby('case:concept:name', as_index= False).agg(Length = pd.NamedAgg(column="concept:name", aggfunc="count"), 
                                                                Duration = pd.NamedAgg(column = 'time:timestamp', aggfunc= lambda x : x.max() - x.min()),
                                                                Start = pd.NamedAgg(column = 'time:timestamp' , aggfunc = 'min' ),
                                                                End = pd.NamedAgg(column = 'time:timestamp', aggfunc = 'max'))
cases.sort_values(by = 'Start', inplace= True)                                                           
cases['Interval'] = cases.Start - cases.End.shift(1)                           
cases['Interval'] = cases['Interval'].dt.total_seconds()
cases['Duration'] = cases['Duration'].dt.total_seconds()
case_indexes = cases[cases['Interval']<0]['case:concept:name']
case_dist = cases[~cases['case:concept:name'].isin(case_indexes)] # Mean needs to have positive values only
case_dist['Start Time'] = case_dist['Start'].dt.time
case_dist['Start Hour'] = case_dist['Start'].dt.hour
case_dist['Performance_time'] = case_dist['Duration'] / case_dist['Length']
case_dist['Normalized Performance_time'] = (case_dist['Performance_time'] - case_dist['Performance_time'].mean()) / case_dist['Performance_time'].std()
case_dist['Scaled Performance_time'] = (case_dist['Normalized Performance_time'] - case_dist['Normalized Performance_time'].min())/ (case_dist['Normalized Performance_time'].max()-case_dist['Normalized Performance_time'].min())
case_dist['Performance'] = 1 - case_dist['Scaled Performance_time']
case_dist['case:concept:name'] = case_dist['case:concept:name'].astype(int)

st.markdown(('Total orders evaluated: ' + str(case_dist['case:concept:name'].max())) )
st.markdown(('Total Time Spent: ' + str(case_dist['Duration'].sum()) + ' seconds = ' + str((case_dist['Duration'].sum()/60).round(2)) + ' minute = ' + str((case_dist['Duration'].sum()/3600).round(2)) + ' hours'))
st.markdown(('Average Performance: ' + str(case_dist['Performance'].mean().round(2))))


plt.style.use('ggplot')
fig_1, ax = plt.subplots(figsize=(10,5))
ax.set_title('Events per Hour')
ax = case_dist['Start Hour'].value_counts().sort_index().plot.bar(width = 0.8)
ax.set_xlabel('Hours in a day')
ax.set_ylabel('Frequencies')

st.pyplot(fig_1)

plt.style.use('ggplot')
fig_2, ax = plt.subplots(figsize=(10,5))
ax.set_title('Distribution of Case Durations in Seconds (Up to 2 mins)')
#ax = case_dist['Duration'].value_counts().plot.bar(width = 0.9)
ax.hist(case_dist['Duration'], range = (0, 115), bins = 30)
ax.set_xticks(np.arange(0,120,5))
ax.set_xlabel('Duration of cases')
ax.set_ylabel('Frequencies')

st.pyplot(fig_2)

plt.style.use('ggplot')
fig_3, ax = plt.subplots(figsize=(15,5))
ax.set_title('Distribution of Case Intervals in Seconds (Up to 5 mins)')
#ax = case_dist['Interval'].value_counts().plot.bar(width = 0.8)
ax.hist(case_dist['Interval'], range = (0, 300), bins = 30)
ax.set_xticks(np.arange(0,300,10))
ax.set_xlabel('Interval of cases')
ax.set_ylabel('Frequencies')

st.pyplot(fig_3)

plt.style.use('ggplot')
fig_4, ax = plt.subplots(figsize=(15,5))
ax.set_title('Distribution of Case Performances (Duration / Activity count)')
#ax = case_dist['Interval'].value_counts().plot.bar(width = 0.8)
ax.hist(case_dist['Performance'], range = (0.99, 1), bins = 30)
ax.set_xticks(np.arange(0.99,1,0.003))
ax.set_xlabel('Performances of cases')
ax.set_ylabel('Frequencies')

st.pyplot(fig_4)

st.dataframe(case_dist)
case_dist['case:concept:name'] = case_dist['case:concept:name'].astype('str')
treshold = st.number_input('Select a duration treshold (seconds)', min_value = 0, max_value= 10000)
case_dist['Duration'] = case_dist['Duration'].astype('int')
tresh = case_dist[case_dist['Duration'] >= treshold]['case:concept:name']
tresh_case = event_log[event_log['case:concept:name'].isin(np.array(tresh))]

eşik_tablo = st.button('Show the orders above duration treshold')

if eşik_tablo:
    st.dataframe(tresh_case)



