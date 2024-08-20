import streamlit as st
import pm4py
import pandas as pd
from utils import *


sample = pd.read_csv('cache.csv', index_col = 0)

try:
    data_prep(sample)
except Exception as e:
    st.warning(e)

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
pos_1 = case_identifier(filtered)
st.subheader('Filtered Table')
st.dataframe(pos_1)
event_log= event_log(pos_1)
st.subheader('Directly Follows Graph')
dfg, start_activities, end_activities = pm4py.discover_dfg(event_log)
pm4py.save_vis_dfg(dfg, start_activities, end_activities, 'dfg.png')
st.image('dfg.png')
st.subheader('Activity Frequency Analysis')
acts= frequencies(event_log)
st.dataframe(acts)