import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression
import plotly.express as px

# --------------------
# 📦 데이터 불러오기
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
# 🎛️ 앱 제목 및 설명
# --------------------
st.title("📈 20–29세 청년 실업률 분석 및 예측")

# --------------------
# 📅 슬라이더: 분석 범위 선택
# --------------------
start_date = df['년월'].min().to_pydatetime()
end_date = df['년월'].max().to_pydatetime()

selected_range = st.slider(
    "분석할 월 범위 선택",
    min_value=start_date,
    max_value=end_date,
    value=(start_date, end_date),
    format="YYYY-MM"
)

# --------------------
# 📊 실제 실업률 (Plotly)
# --------------------
st.subheader("📊 남녀 청년 실업률 (선택 구간)")
filtered_df = df[(df['년월'] >= selected_range[0]) & (df['년월'] <= selected_range[1])]

fig1 = px.line(
    filtered_df,
    x='년월',
    y='실업률',
    color='성별',
    markers=True,
    title="실제 실업률 추이 (남녀)"
)
fig1.update_layout(xaxis_title="년월", yaxis_title="실업률 (%)")
st.plotly_chart(fig1)

# --------------------
# 🤖 예측 (남녀 5년 = 60개월)
# --------------------
st.subheader("🔮 향후 5년 예측 (남녀)")

future_months = 60
all_preds = []

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

    # 저장
    temp_df = pd.DataFrame({
        '년월': future_dates,
        '예측 실업률': preds,
        '성별': gender
    })
    all_preds.append(temp_df)

# 결합
pred_df = pd.concat(all_preds).reset_index(drop=True)

# --------------------
# 📋 예측 결과 테이블
# --------------------
st.subheader("📋 예측 결과 (남녀, 향후 5년)")
st.dataframe(pred_df)

# --------------------
# 📈 예측 결과만 시각화 (추가 그래프)
# --------------------
st.subheader("📈 예측 결과만 그래프로 보기")

fig3 = px.line(
    pred_df,
    x='년월',
    y='예측 실업률',
    color='성별',
    markers=True,
    title="예측 실업률 (남녀, 향후 5년)"
)
fig3.update_layout(
    xaxis_title="년월",
    yaxis_title="예측 실업률 (%)",
    legend_title="성별",
    template="plotly_white"
)
st.plotly_chart(fig3)
