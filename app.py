import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression

# 폰트 설정
plt.rcParams['font.family'] = 'NanumGothic'

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
# 🎛️ 성별 선택 & 예측 기간 고정
# --------------------
st.title("📈 20–29세 청년 실업률 분석 및 예측")
selected_gender = st.radio("성별을 선택하세요", ['남자', '여자'], horizontal=True)

# --------------------
# 📅 슬라이더: 분석 범위 선택 (월 단위)
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
# 📊 실제 실업률 추이 (선택 구간)
# --------------------
st.subheader("📊 선택한 기간의 월별 실업률")
filtered_df = df[
    (df['년월'] >= selected_range[0]) &
    (df['년월'] <= selected_range[1]) &
    (df['성별'] == selected_gender)
]

fig1, ax1 = plt.subplots(figsize=(10, 4))
ax1.plot(filtered_df['년월'], filtered_df['실업률'], marker='o', color='orange')
ax1.set_xlabel("년월")
ax1.set_ylabel("실업률 (%)")
ax1.set_title(f"{selected_gender} 청년 실업률 (선택한 구간)")
ax1.grid(True, linestyle='--', alpha=0.4)
fig1.tight_layout()
st.pyplot(fig1)

# --------------------
# 🤖 향후 12개월 예측
# --------------------
st.subheader(f"🔮 {selected_gender} 실업률 예측 (향후 12개월)")

# 예측용 데이터 준비
gender_df = df[df['성별'] == selected_gender][['년월', '실업률']].reset_index(drop=True)
gender_df['month_index'] = np.arange(len(gender_df))

# Linear Regression 모델
X = gender_df[['month_index']]
y = gender_df['실업률']
model = LinearRegression().fit(X, y)

# 향후 12개월 예측
future_months = 12
future_index = np.arange(len(gender_df), len(gender_df) + future_months)
future_preds = model.predict(future_index.reshape(-1, 1))

# 날짜 생성
last_date = gender_df['년월'].iloc[-1]
future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=future_months, freq='MS')

# 예측 결과 정리
pred_df = pd.DataFrame({
    '예측 월': future_dates,
    '예측 실업률': future_preds
})

# 예측 그래프
fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.plot(future_dates, future_preds, label="예측 실업률", marker='o', linestyle='--', color='red')
ax2.set_xlabel("예측 월")
ax2.set_ylabel("실업률 (%)")
ax2.set_title(f"{selected_gender} 청년 실업률 예측 (Linear Regression)")
ax2.grid(True, linestyle='--', alpha=0.3)
ax2.legend()
fig2.tight_layout()
st.pyplot(fig2)

# 예측 테이블
st.subheader("📋 예측 결과 테이블")
st.dataframe(pred_df.reset_index(drop=True))
