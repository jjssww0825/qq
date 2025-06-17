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

# 📅 슬라이더: 실제 데이터 구간 이동
start_date = df['년월'].min().to_pydatetime()
end_date = df['년월'].max().to_pydatetime()
selected_range = st.slider(
    "실제 실업률 분석 구간 선택",
    min_value=start_date,
    max_value=end_date,
    value=(start_date, end_date),
    format="YYYY-MM"
)
filtered_df = df[(df['년월'] >= selected_range[0]) & (df['년월'] <= selected_range[1])]

# 1️⃣ 실제 실업률 그래프 (슬라이더 반영)
st.title("📊 남녀 청년 실업률 (실제 데이터, 구간 이동 가능)")
fig_real = go.Figure()
for gender, color in zip(['남자', '여자'], ['blue', 'orange']):
    subset = filtered_df[filtered_df['성별'] == gender]
    fig_real.add_trace(go.Scatter(
        x=subset['년월'],
        y=subset['실업률'],
        mode='lines+markers',
        name=gender,
        line=dict(color=color, width=2)
    ))
fig_real.update_layout(
    title="실제 실업률 추이 (남녀, 구간 이동)",
    xaxis_title="년월",
    yaxis_title="실업률 (%)"
)
st.plotly_chart(fig_real)

# 2️⃣ 예측 실업률 그래프 (전체기간 이후 5년)
st.title("🔮 남녀 청년 실업률 예측 (향후 5년, 실제와 분리)")
future_months = 60
fig_pred = go.Figure()
for gender, color in zip(['남자', '여자'], ['blue', 'orange']):
    gender_df = df[df['성별'] == gender][['년월', '실업률']].reset_index(drop=True)
    gender_df['month_index'] = np.arange(len(gender_df))
    X = gender_df[['month_index']]
    y = gender_df['실업률']
    model = LinearRegression().fit(X, y)
    last_date = gender_df['년월'].iloc[-1]
    future_index = np.arange(len(gender_df), len(gender_df) + future_months)
    preds = model.predict(future_index.reshape(-1, 1))
    future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=future_months, freq='MS')
    fig_pred.add_trace(go.Scatter(
        x=future_dates,
        y=preds,
        mode='lines+markers',
        name=f"{gender} (예측)",
        line=dict(color=color, dash='dash', width=2)
    ))
fig_pred.update_layout(
    title="향후 5년 예측 실업률 (남녀)",
    xaxis_title="년월",
    yaxis_title="실업률 (%)"
)
st.plotly_chart(fig_pred)
