import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression
import plotly.express as px

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
# 과거 + 예측 데이터 결합
# --------------------
future_months = 60
all_combined = []

for gender in ['남자', '여자']:
    gender_df = df[df['성별'] == gender][['년월', '실업률']].reset_index(drop=True)
    gender_df['month_index'] = np.arange(len(gender_df))

    # 학습
    X = gender_df[['month_index']]
    y = gender_df['실업률']
    model = LinearRegression().fit(X, y)

    # 예측
    future_index = np.arange(len(gender_df), len(gender_df) + future_months)
    preds = model.predict(future_index.reshape(-1, 1))
    last_date = gender_df['년월'].iloc[-1]
    future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=future_months, freq='MS')

    # 실제 + 예측 데이터 결합
    df_actual = gender_df[['년월', '실업률']].copy()
    df_actual.columns = ['년월', '실업률']
    df_actual['성별'] = gender
    df_actual['구분'] = '실제'

    df_future = pd.DataFrame({
        '년월': future_dates,
        '실업률': preds,
        '성별': gender,
        '구분': '예측'
    })

    all_combined.append(pd.concat([df_actual, df_future]))

df_final = pd.concat(all_combined).reset_index(drop=True)

# --------------------
# 📈 Plotly 그래프 출력
# --------------------
st.title("📈 20–29세 청년 실업률 추이 및 향후 5년 예측")

fig = px.line(
    df_final,
    x='년월',
    y='실업률',
    color='성별',
    line_dash='구분',
    markers=True,
    title="실제 + 예측 실업률 추이 (남녀)"
)

fig.update_layout(
    xaxis_title="년월",
    yaxis_title="실업률 (%)",
    legend_title="성별 / 구분"
)

st.plotly_chart(fig)

# --------------------
# 📋 데이터 테이블
# --------------------
st.subheader("📋 전체 데이터 (실제 + 예측)")
st.dataframe(df_final)
