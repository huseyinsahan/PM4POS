import streamlit as st
import pandas as pd
import datetime as dt
from utils import *

st.set_page_config(page_title="PM4PY")

st.title('Welcome')
st.header('PM4POS - Process Mining for Point of Sales Context')

st.subheader('How it works?')
st.write(
'''This dashboard is created for applying process mining principles in point of sale processes. The main idea here is identifying patterns
    in a store, restaurant where there are more than one pos device available in. Different than a simple event log the data should include 
    PosID, and OrderID columns from which the case of eventlogs will be extracted. OperatorID plays as a resource role here. These columns are 
    compulsary for the sytem to work.
    Here's an example data:''')


sample = pd.read_csv('Trial_data.csv', index_col = 0).head()
st.dataframe(sample)

uploaded_file = st.file_uploader(
   "Choose a CSV file", type = 'csv', accept_multiple_files=False)

if uploaded_file:
    st.write("filename:", uploaded_file.name)
col_name_pair = st.checkbox('Pair column names and cache uploaded file')

if col_name_pair:
    sample = pd.read_csv(uploaded_file, index_col = 0)
    with st.form(key= 'Column_pair'):
        st.write('Select column names corresponding below event log columns')
        columns = list(sample.columns)
        columns.append('None')
        print(columns)
        st.write(columns)
        PosID = st.selectbox("PosID", columns)
        OrderID = st.selectbox('OrderID', columns)
        Activity = st.selectbox('Activity', columns)
        Timestamp = st.selectbox('TimeStamp', columns)
        Operator = st.selectbox('OperatorID', columns)
        
        col_names = {'PosID' : PosID,
                    'OrderID': OrderID,
                    'Activity': Activity,
                    'TimeStamp': Timestamp,
                    'OperatorID': Operator}
        for key, value in col_names.items():
            if value == 'None':
                sample.loc[:, key] = 0
        submit_button = st.form_submit_button(label = 'Submit')
    if submit_button:
        col_names = {y: x for x, y in col_names.items()}
        sample = sample.rename(columns=col_names)
        sample.to_csv('cache.csv')
        st.dataframe(sample)

example = st.button('Continue with example restaurant data')

if example:
    sample = pd.read_csv('Trial_data.csv', index_col= 0)
    sample.to_csv('cache.csv')
    st.dataframe(sample)

cache = st.button('Clear Cache', key = "cache")

if cache:
    pd.DataFrame().to_csv('cache.csv')  
