import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
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

# 2️⃣ 예측 실업률 그래프 (Prophet, 최근 5년만 사용)
st.title("🔮 남녀 청년 실업률 예측 (향후 5년, Prophet, 최근 5년만 사용, 실제와 분리)")
future_months = 60
cut_off = pd.Timestamp('2019-01-01')  # <-- 최근 5년치만 Prophet에 사용
recent_df = df[df['년월'] >= cut_off].copy()
fig_pred = go.Figure()
for gender, color in zip(['남자', '여자'], ['blue', 'orange']):
    gender_df = recent_df[recent_df['성별'] == gender][['년월', '실업률']].rename(columns={"년월": "ds", "실업률": "y"})
    m = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    m.fit(gender_df)
    # 예측 (미래 60개월)
    future = m.make_future_dataframe(periods=future_months, freq='MS')
    forecast = m.predict(future)
    forecast_future = forecast.iloc[-future_months:]
    fig_pred.add_trace(go.Scatter(
        x=forecast_future['ds'],
        y=forecast_future['yhat'],
        mode='lines+markers',
        name=f"{gender} (예측)",
        line=dict(color=color, dash='dash', width=2)
    ))
fig_pred.update_layout(
    title="향후 5년 예측 실업률 (남녀, Prophet, 최근 5년 데이터 기반)",
    xaxis_title="년월",
    yaxis_title="실업률 (%)"
)
st.plotly_chart(fig_pred)
