import streamlit as st
import time
import numpy as np
import datetime
import pm4py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils import *

st.set_page_config(page_title="PM4POS - Activity Transition Analysis", layout= 'wide')
st.title('Activity Transition Analysis')
st.markdown("""Here you can analyze the activity transitions in a heatmap. The main idea is to identify specific activity types resulting in bottlenecks.""")

sample = pd.read_csv(('cache.csv'), index_col=0)
try:
    sample = data_prep(sample)
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

activities = pos_1.loc[:, ['Case', 'Activity', 'TimeStamp']]
activities.sort_values(by = ['Case', 'TimeStamp'], inplace= True)  
activities.loc[:,'Prev_act'] = activities.groupby('Case')['Activity'].shift()
activities.loc[:,'Interval_seconds'] = activities.groupby('Case')['TimeStamp'].diff().dt.total_seconds()

frequency_pivot = pd.pivot_table(activities, values='Case', index='Prev_act', columns='Activity', aggfunc='count', fill_value=0)
mean_seconds_pivot = pd.pivot_table(activities, values='Interval_seconds', index='Prev_act', columns='Activity', aggfunc='mean', fill_value=0)
median_seconds_pivot = pd.pivot_table(activities, values='Interval_seconds', index='Prev_act', columns='Activity', aggfunc='median', fill_value=0)

fig, axes = plt.subplots(3, 1, figsize=(12, 8))

sns.heatmap(frequency_pivot, annot=True, cmap="Greens", ax=axes[0], linewidths= .8, annot_kws= {'size' : 10}, fmt = 'g')
axes[0].set_title('Frequency of Transitions', size = 16 )
axes[0].set_xticks([])
axes[0].set_xlabel(None)
sns.heatmap(mean_seconds_pivot, annot=True, cmap="Blues", ax=axes[1], linewidths= .8, annot_kws= {'size' : 10}, fmt = '.0f')
axes[1].set_title('Mean Interval Seconds', size = 16 )
axes[1].set_xticks([])
axes[1].set_xlabel(None)
sns.heatmap(median_seconds_pivot, annot=True, cmap="Oranges", ax=axes[2], linewidths= .8, annot_kws= {'size' : 10}, fmt = '.0f')
axes[2].set_title('Median Interval Seconds', size = 16 )

st.header('Transition between activities')

st.markdown(('Total activites counted: ' + str(frequency_pivot.values.sum())))

st.pyplot(fig)


