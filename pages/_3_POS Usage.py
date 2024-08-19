import streamlit as st
import datetime as dt
import pandas as pd
import pm4py
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.title('POS Usage')
st.markdown("""This section provides overview of POS device usage especially focusing on hours of days. Different than other section user don't specify PosID here.""")


sample = pd.read_csv(('cache.csv'), index_col=0)
sample['TimeStamp'] = pd.to_datetime(sample['TimeStamp'])
sample['BusinesDate'] = sample['TimeStamp'].dt.date
sample['PosID'] = sample['PosID'].astype('str')

start_date = st.date_input(
    'Pick a start date',
    sample['BusinesDate'].min()
)

end_date = st. date_input(
    'Pick an end date',
    sample['BusinesDate'].max()
)


df = sample[(sample['BusinesDate'] >= start_date)&(sample['BusinesDate'] <= end_date)]

df1 = df.groupby(['PosID']).agg(Total_usage = ('OrderID', 'count'))


plt.style.use('ggplot')
fig_1, ax = plt.subplots(figsize=(10,5))
ax.set_title('Total POS Device Usage Amount')
ax.bar(df1.index, df1['Total_usage'])
ax.set_xlabel('Pos Device')
ax.set_ylabel('Usage Amount')

st.pyplot(fig_1)

table = st.button('See table')
if table:
    st.dataframe(df1)

df['OperateHour'] = df['TimeStamp'].dt.hour

df2 = df.groupby(['OperateHour', 'PosID']).size().unstack(fill_value=0).reset_index()
df2 = df2[df2['OperateHour'].isin(np.arange(10, 22))]


plt.style.use('ggplot')
fig_2, ax = plt.subplots(figsize=(10,5))
ax.set_title('Hourly Distribution of POS Device Usage')
df2.plot(x = 'OperateHour',kind = 'bar', stacked = True, ax = ax)
ax.set_xlabel('Operate Hour')
ax.set_ylabel('Usage Amount')

st.pyplot(fig_2)

table2 = st.button('See Table', key = '2')
if table2:
    st.dataframe(df2)