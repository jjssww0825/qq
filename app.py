import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# 기존 전처리 및 데이터 불러오는 코드 생략 (load_data 함수 동일)

# 필터링된 데이터로부터 그래프 출력
st.subheader("연도별 평균 실업률 추이 (성별)")

fig, ax = plt.subplots(figsize=(8, 5))  # 🔹 크기 축소 (기존보다 작음)

for gender in filtered_df['성별'].unique():
    subset = filtered_df[filtered_df['성별'] == gender]
    ax.plot(subset['연도'], subset['실업률'], label=gender, marker='o')

# 🔹 축 설정 깔끔하게
ax.set_xlabel("연도", fontsize=11)
ax.set_ylabel("평균 실업률 (%)", fontsize=11)
ax.xaxis.set_major_locator(ticker.MultipleLocator(2))  # 2년 간격으로 눈금
ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))  # 정수 눈금만
ax.grid(True, linestyle='--', alpha=0.4)

# 🔹 폰트 및 범례 설정
ax.tick_params(axis='both', labelsize=10)
ax.legend(title='성별', fontsize=10, title_fontsize=11)
fig.tight_layout()

st.pyplot(fig)
