import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go

# --------------------
# 데이터 불러오기
# --------------------
@st.cache_data
def load_data():
    df = pd.read_csv("성_연령별_실업률_20250615233240.csv", encoding="cp949")
    df = df[df['연령계층별'] == '20 - 29세'].copy()
    df = df.melt(id_vars=['성별', '연령계층별'], var_name='년월', value_name='실업률')
    df['년월'] = pd.to_datetime(df['년월'], format='%Y.%m')
    df = df.sort_values('년월')
    return df

df = load_data()

# --------------------
# 실제 그래프 (남녀) - 선택 범위 없이 전체
# --------------------
st.title("📊 남녀 청년 실업률 (실제 데이터)")
fig_real = go.Figure()

for gender, color in zip(['남자', '여자'], ['blue', 'orange']):
    subset = df[df['성별'] == gender]
    fig_real.add_trace(go.Scatter(
        x=subset['년월'], y=subset['실업률'],
        mode='lines+markers',
        name=f"{gender} (실제)", line=dict(color=color)
    ))

fig_real.update_layout(
    title="실제 실업률 추이 (남녀)",
    xaxis_title="년월",
    yaxis_title="실업률 (%)"
)

st.plotly_chart(fig_real)

# --------------------
# 예측 데이터 준비
# --------------------
future_months = 60
pred_df_list = []

for gender, color in zip(['남자', '여자'], ['blue', 'orange']):
    gender_df = df[df['성별'] == gender][['년월', '실업률']].reset_index(drop=True)
    gender_df['month_index'] = np.arange(len(gender_df))

    # 모델 학습
    X = gender_df[['month_index']]
    y = gender_df['실업률']
    model = LinearRegression().fit(X, y)

    # 예측
    last_date = gender_df['년월'].iloc[-1]
    future_index = np.arange(len(gender_df), len(gender_df) + future_months)
    preds = model.predict(future_index.reshape(-1, 1))
    future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=future_months, freq='MS')

    pred_df = pd.DataFrame({
        '년월': future_dates,
        '실업률': preds,
        '성별': gender
    })

    # "실제 마지막 값"을 예측 앞에 이어 붙이기 위해 삽입
    last_point = pd.DataFrame({
        '년월': [last_date],
        '실업률': [gender_df['실업률'].iloc[-1]],
        '성별': [gender]
    })

    pred_df = pd.concat([last_point, pred_df], ignore_index=True)
    pred_df_list.append((pred_df, color))

# --------------------
# 예측 그래프
# --------------------
st.title("🔮 향후 5년 실업률 예측 (남녀)")
fig_pred = go.Figure()

for pred_df, color in pred_df_list:
    gender = pred_df['성별'].iloc[0]
    fig_pred.add_trace(go.Scatter(
        x=pred_df['년월'], y=pred_df['실업률'],
        mode='lines+markers',
        name=f"{gender} (예측)", line=dict(dash='dash', color=color)
    ))

fig_pred.update_layout(
    title="예측 실업률 추이 (남녀, 이어서 표시)",
    xaxis_title="년월",
    yaxis_title="실업률 (%)"
)

st.plotly_chart(fig_pred)
