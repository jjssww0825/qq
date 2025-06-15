import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 데이터 불러오기
df = pd.read_csv("성_연령별_실업률_20250615233240.csv")

# 1. 전처리
# 연도형으로 바꾸기, 필요 열만 추출
# 예: df[df['연령대'] == '20~29세']

# 2. Streamlit UI 구성
st.title("20–29세 청년 실업률: 성별 비교 (2004–2024)")

# 연도 선택 슬라이더
years = st.slider("연도 범위 선택", min_value=2004, max_value=2024, value=(2004, 2024))

# 성별별 실업률 변화 시각화
st.subheader("연도별 성별 실업률 변화")
fig, ax = plt.subplots()
# 예: 남자, 여자 각각 plot
# ax.plot(df_men['연도'], df_men['실업률'], label='남성')
# ax.plot(df_women['연도'], df_women['실업률'], label='여성')
ax.set_xlabel("연도")
ax.set_ylabel("실업률 (%)")
ax.legend()
st.pyplot(fig)

# 데이터 테이블 표시
st.subheader("데이터 미리보기")
st.dataframe(df.head())

