import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression

plt.rcParams['font.family'] = 'NanumGothic'

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
# 성별 선택 & 예측
# --------------------
st.title("📈 청년 실업률 예측 (향후 1년)")
selected_gender = st.radio("성별을 선택하세요", ['남자', '여자'], horizontal=True)

# 선택된 성별 데이터
gender_df = df[df['성별'] == selected_gender][['년월', '실업률']].reset_index(drop=True)
gender_df['month_index'] = np.arange(len(gender_df))

# 선형 회귀 모델 학습
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

# 결과 저장
pred_df = pd.DataFrame({
    '예측 월': future_dates,
    '예측 실업률': future_preds
})

# --------------------
# 예측 그래프 출력 (예측만!)
# --------------------
st.subheader(f"🔮 {selected_gender} 청년 실업률 예측 (다음 12개월)")

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(future_dates, future_preds, label="예측 실업률", marker='o', color='red', linestyle='--')
ax.set_xlabel("예측 월")
ax.set_ylabel("실업률 (%)")
ax.set_title(f"{selected_gender} 실업률 예측 (Linear Regression)")
ax.grid(True, linestyle='--', alpha=0.3)
ax.legend()
fig.tight_layout()
st.pyplot(fig)

# --------------------
# 예측 테이블
# --------------------
st.subheader("📋 예측 결과 테이블")
st.dataframe(pred_df.reset_index(drop=True))
