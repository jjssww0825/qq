import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from sklearn.linear_model import LinearRegression

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
# 📌 월 단위 슬라이더
# --------------------
st.title("📅 20–29세 청년 실업률 분석 및 예측 (2004.01–2024.12)")
st.markdown("분석할 **월 단위 기간**을 선택하고, 향후 실업률을 예측해보세요.")

start_date = df['년월'].min().to_pydatetime()
end_date = df['년월'].max().to_pydatetime()

selected_range = st.slider(
    "분석할 월 범위 선택",
    min_value=start_date,
    max_value=end_date,
    value=(start_date, end_date),
    format="YYYY-MM"
)

# 필터링
filtered_df = df[(df['년월'] >= selected_range[0]) & (df['년월'] <= selected_range[1])]

# --------------------
# 📊 실제 실업률 시각화
# --------------------
st.subheader("📊 성별 월별 실업률 추이")
fig1, ax1 = plt.subplots(figsize=(10, 5))

for gender in filtered_df['성별'].unique():
    subset = filtered_df[filtered_df['성별'] == gender]
    ax1.plot(subset['년월'], subset['실업률'], label=gender, marker='o', markersize=3)

ax1.set_xlabel("년월")
ax1.set_ylabel("실업률 (%)")
ax1.grid(True, linestyle='--', alpha=0.4)
ax1.legend(title="성별")
fig1.tight_layout()
st.pyplot(fig1)

# --------------------
# 🤖 예측 기능 (남성만)
# --------------------
st.subheader("📈 남성 실업률 예측 (향후 6개월)")

# 남성 실업률만 추출
male_df = df[df['성별'] == '남자'][['년월', '실업률']].reset_index(drop=True)
male_df['month_index'] = np.arange(len(male_df))

# 모델 학습
X = male_df[['month_index']]
y = male_df['실업률']
model = LinearRegression().fit(X, y)

# 예측
future_months = 6
future_index = np.arange(len(male_df) + future_months)
future_preds = model.predict(future_index.reshape(-1, 1))

# 날짜 생성
last_date = male_df['년월'].iloc[-1]
future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=future_months, freq='MS')
full_dates = list(male_df['년월']) + list(future_dates)

# 결과 저장
pred_df = pd.DataFrame({
    '년월': full_dates,
    '예측 실업률': future_preds
})

# 예측 그래프
fig2, ax2 = plt.subplots(figsize=(10, 5))
ax2.plot(male_df['년월'], y, label="실제 실업률 (남성)", marker='o', color='orange')
ax2.plot(future_dates, future_preds[-future_months:], label="예측 실업률", marker='o', linestyle='--', color='red')
ax2.set_xlabel("년월")
ax2.set_ylabel("실업률 (%)")
ax2.set_title("남성 청년 실업률 예측 (Linear Regression)")
ax2.legend()
ax2.grid(True)
fig2.tight_layout()
st.pyplot(fig2)

# 예측 테이블
st.subheader("📋 예측 결과 (남성, 향후 6개월)")
st.dataframe(pred_df.tail(future_months).reset_index(drop=True))
