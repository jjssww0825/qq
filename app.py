import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("성_연령별_실업률_20250615233240.csv", encoding="cp949")
    df = df[df['연령계층별'] == '20 - 29세'].copy()
    df = df.melt(id_vars=['성별', '연령계층별'], var_name='년월', value_name='실업률')
    df['년월'] = pd.to_datetime(df['년월'], format='%Y.%m')
    df = df.sort_values('년월')
    return df

df = load_data()
future_months = 60

st.title("🔮 향후 5년 실업률 예측 (실제 + 예측 한 그래프에)")

fig = go.Figure()

for gender, color in zip(['남자', '여자'], ['blue', 'orange']):
    gender_df = df[df['성별'] == gender][['년월', '실업률']].reset_index(drop=True)
    gender_df['month_index'] = np.arange(len(gender_df))

    # 실제 데이터
    fig.add_trace(go.Scatter(
        x=gender_df['년월'],
        y=gender_df['실업률'],
        mode='lines+markers',
        name=f"{gender} (실제)",
        line=dict(color=color, width=2)
    ))

    # 예측 데이터 생성
    X = gender_df[['month_index']]
    y = gender_df['실업률']
    model = LinearRegression().fit(X, y)
    last_date = gender_df['년월'].iloc[-1]
    future_index = np.arange(len(gender_df), len(gender_df) + future_months)
    preds = model.predict(future_index.reshape(-1, 1))
    future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=future_months, freq='MS')

    # 실제 마지막값 + 예측 이어붙이기
    pred_dates = np.concatenate([[last_date], future_dates])
    pred_vals = np.concatenate([[gender_df['실업률'].iloc[-1]], preds])

    fig.add_trace(go.Scatter(
        x=pred_dates,
        y=pred_vals,
        mode='lines+markers',
        name=f"{gender} (예측)",
        line=dict(color=color, dash='dash', width=2)
    ))

fig.update_layout(
    title="실제 실업률 + 이어지는 5년 예측 실업률 (남녀)",
    xaxis_title="년월",
    yaxis_title="실업률 (%)",
    legend_title="범례"
)
st.plotly_chart(fig)
