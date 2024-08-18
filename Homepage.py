import streamlit as st
import pandas as pd
import datetime as dt
from utils import *

st.set_page_config(page_title="POS Log Analysis", page_icon="📈")

st.title('Welcome')
st.header('LOGPOS - Log Analysis Dashboard for Point of Sales Context')

st.subheader('How it works?')
st.write(
'''This dashboard is created for applying process mining principles in point of sale processes. The main idea here is identfiyng patterns
    in a store, restaurant where there are more than one pos device available in. Different than a simple eventlog the data should include 
    PosID, and OrderID columns from which the case of eventlogs will be extracted. OperatorID plays as a resource role here. These columns are 
    compulsary for the sytem to work.
    Here's an example data:''')

sample = pd.read_csv('Trial_data.csv', index_col = 0).head()
st.dataframe(sample)

uploaded_file = st.file_uploader(
    "Choose a CSV file", type = 'csv', accept_multiple_files=False
)

if uploaded_file != None:
    st.write("filename:", uploaded_file.name)
    sample = pd.read_csv(uploaded_file, index_col = 0)
    st.write(sample)
    sample.to_csv('cache.csv')
    try:
        data_prep(sample)
    except Exception as e:
        st.write(e)
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
else:
    sample = pd.read_csv('Trial_data.csv')
    try:
        data_prep(sample)
    except Exception as e:
        st.write(e)
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