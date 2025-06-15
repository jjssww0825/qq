import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression
import matplotlib.font_manager as fm

# ✅ 한글 폰트 설정 (업로드된 ttf 사용)
font_path = "NanumHumanRegular.ttf"
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()

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
st.markdown("과거 실업률은 슬라이더로 기간을 조절하고, 향후 5년간 실업률을 **남녀 동시에 예측**합니다.")

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
# 📊 실제 실업률 시각화
# --------------------
st.subheader("📊 실제 실업률 (선택 구간)")
filtered_df = df[(df['년월'] >= selected_range[0]) & (df['년월'] <= selected_range[1])]

fig1, ax1 = plt.subplots(figsize=(10, 4))
for gender, color in zip(['남자', '여자'], ['blue', 'orange']):
    subset = filtered_df[filtered_df['성별'] == gender]
    ax1.plot(subset['년월'], subset['실업률'], marker='o', label=gender, color=color)

ax1.set_xlabel("년월")
ax1.set_ylabel("실업률 (%)")
ax1.set_title("남녀 청년 실업률 (선택 구간)")
ax1.grid(True, linestyle='--', alpha=0.4)
ax1.legend()
fig1.tight_layout()
st.pyplot(fig1)

# --------------------
# 🤖 예측 (남녀 각각, 향후 5년)
# --------------------
st.subheader("🔮 남녀 실업률 예측 (향후 5년)")

future_months = 60
fig2, ax2 = plt.subplots(figsize=(10, 4))
combined_pred_df = pd.DataFrame()

for gender, color in zip(['남자', '여자'], ['blue', 'orange']):
    gender_df = df[df['성별'] == gender][['년월', '실업률']].reset_index(drop=True)
    gender_df['month_index'] = np.arange(len(gender_df))

    # 모델 학습
    X = gender_df[['month_index']]
    y = gender_df['실업률']
    model = LinearRegression().fit(X, y)

    # 예측
    future_index = np.arange(len(gender_df), len(gender_df) + future_months)
    future_preds = model.predict(future_index.reshape(-1, 1))
    last_date = gender_df['년월'].iloc[-1]
    future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=future_months, freq='MS')

    # 그래프
    ax2.plot(future_dates, future_preds, label=f"{gender} 예측", marker='o', linestyle='--', color=color)

    # 결과 저장
    temp_df = pd.DataFrame({
        '성별': gender,
        '예측 월': future_dates,
        '예측 실업률': future_preds
    })
    combined_pred_df = pd.concat([combined_pred_df, temp_df], ignore_index=True)

# 그래프 마무리
ax2.set_xlabel("예측 월")
ax2.set_ylabel("실업률 (%)")
ax2.set_title("향후 5년간 남녀 청년 실업률 예측")
ax2.grid(True, linestyle='--', alpha=0.3)
ax2.legend()
fig2.tight_layout()
st.pyplot(fig2)

# --------------------
# 📋 예측 결과 테이블
# --------------------
st.subheader("📋 예측 결과 (남녀, 향후 5년)")
st.dataframe(combined_pred_df.reset_index(drop=True))
