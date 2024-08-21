import streamlit as st
import datetime 
import pandas as pd

st.set_page_config(page_title="PM4PY - Duration Analysis")

st.title('Duration Analysis')
st.markdown("""Here the attributes affecting duration of each order can be identified. For this purpose, suitable regression analysis structure is implemented.""")

sample = pd.read_csv(('cache.csv'), index_col=0)
sample['TimeStamp'] = pd.to_datetime(sample['TimeStamp'])
sample['BusinesDate'] = sample['TimeStamp'].dt.date
sample['PosID'] = sample['PosID'].astype('str')

def regressor_data(df, binary_activities, count_activities):
    total_cases = pd.DataFrame()
    for pos_id in df['PosID'].unique():
        filtered = df[df['PosID'] == pos_id]
        pos_1 = filtered.sort_values(by = ['BusinesDate', 'TimeStamp', 'OrderID', 'OperatorID']).reset_index(drop = True)
        pos_1['Case'] = 1
        # Find the points where OrderID changes
        order_change_points = pos_1['OrderID'].ne(pos_1['OrderID'].shift()).cumsum()
        # Assign 'Case' values based on order change points
        pos_1['Case'] = order_change_points
        initial = pos_1.loc[:, ['PosID', 'Case', 'Activity', 'TimeStamp', 'OperatorID']]
        
        cases = initial.groupby('Case', as_index=False).agg(
            PosID = pd.NamedAgg(column = "PosID", aggfunc= 'min'),
            Length=pd.NamedAgg(column="Activity", aggfunc="count"),
            Duration=pd.NamedAgg(column='TimeStamp', aggfunc=lambda x: (x.max() - x.min()).total_seconds()),
            Start_Hour=pd.NamedAgg(column='TimeStamp', aggfunc=lambda x: x.min().hour),
            Operator = pd.NamedAgg(column= 'OperatorID', aggfunc= 'min')
        )
        for activity in binary_activities:
            cases[f'is_{activity}'] = initial.groupby('Case')['Activity'].apply(lambda x: activity in x.values).values.astype('int')
            
        for activity in count_activities:
            cases[f'count_{activity}'] = initial.groupby('Case')['Activity'].apply(lambda x: (x == activity).sum()).values
        total_cases = pd.concat([total_cases, cases])
    return total_cases

from sklearn.preprocessing import LabelEncoder, OneHotEncoder
def encoding(df, col, type):
    if type == 'Label':
        for c in col:
            label_encoder = LabelEncoder()
            df[c] = label_encoder.fit_transform(df[c])
    elif type == 'One Hot':
        for c in col:
            encoder = OneHotEncoder(sparse=False)
            one_hot_encoded = encoder.fit_transform(df[[c]])
            encoded_df = pd.DataFrame(one_hot_encoded, columns=encoder.get_feature_names_out([c]))
            df.reset_index(inplace=True, drop=True)
            df = pd.concat([df.drop(c, axis=1), encoded_df], axis=1)
    else:
        pass
    return df

import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.linear_model import LinearRegression
import numpy as np
def OLS(data, test_size):
    X = data.drop(['Duration'], axis = 1)
    y = data['Duration']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size= test_size, random_state=42)
    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    model = LinearRegression()
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    X_test_scaled = scaler.transform(X_test)
    X2 = sm.add_constant(X_train_scaled)
    est = sm.OLS(y_train, X2)
    est2 = est.fit()
    coefficients = model.coef_
    intercept = model.intercept_
    p_values = est2.pvalues
    results = pd.DataFrame({
        'Coefficient': np.append(intercept, coefficients),
        'P-value': p_values
    })
    column_names = ['const'] + X_train.columns.tolist()
    results.index = column_names
    model_summary = pd.DataFrame({
    'Statistic': ['Number of Observations', 'R-squared', 'Adjusted R-squared', 'F-statistic', 'MAE of Test Set', 'MSE of Test Set'],
    'Value': [est2.nobs, est2.rsquared, est2.rsquared_adj, est2.fvalue, mae, mse]
    })
    return results, model_summary

activities = list(sample['Activity'].unique())

count = st.multiselect(
        'Pick the activities you want to count values of',
        activities
    )

binary = st.multiselect(
        'Pick the activities you want check whether the case includes it or not',
        activities,
        key = 'binary')

cases = regressor_data(sample, binary, count)

columns = cases.columns
label = st.multiselect(
        'Pick the columns you want to apply Label Encoding',
        columns,
        key = 'label')

cases = encoding(cases, label, 'Label')

onehot = st.multiselect(
        'Pick the columns you want to apply One Hot Encoding',
        columns,
        key = 'onehot')

cases = encoding(cases, onehot, 'One Hot')

drop = st.multiselect(
        'Pick the columns you want to drop out',
        columns,
        key = 'drop', default = 'Case')

cases = cases.drop(columns = drop, axis = 1)

if 'PosID' not in drop:
    pos_filter = st.multiselect('Pick the POS device you want to analyze',
                                cases['PosID'].unique(),
                                key = 'pos_filter', default = cases['PosID'].unique())
    cases = cases[cases['PosID'].isin(pos_filter)]


st.subheader('Case Table')
st.write(cases)
st.subheader('Table Descriptive Stats')
st.write(cases.describe())

import seaborn as sns
import matplotlib.pyplot as plt
fig_1, ax = plt.subplots(figsize=(12, 8))
g = sns.heatmap(cases.corr(), annot=True, fmt='.2f', cmap='coolwarm', cbar=True)
plt.title('Correlation Matrix')
st.pyplot(fig_1)

test_size = st.number_input(label= "Define test size of OLS Multiple Regression Model.", step=0.01 ,format="%.2f", min_value= 0.01, max_value=0.99, value = 0.2)

OLS_button = st.button('Perform Multiple Linear Regression', key = "OLS")
if OLS_button:
    result, model_summary = OLS(cases, test_size)
    st.write(model_summary)
    st.write(f' Only {model_summary.iloc[1,1]:.4f} of variability in Duration can be explained by this model.')
    st.write(result)
    sign = result[result['P-value'] < 0.05].index
    posit = result[result['Coefficient'] > 0 ].index
    neg = result[result['Coefficient'] < 0].index
    st.write(f'{posit.to_list()} columns have positive relationship with the dependent variable Duration whereas {neg.to_list()} columns have negative relationship. And only {sign.to_list()} columns are statistically significant predictors of Duration under 0.05 significance level. ')

