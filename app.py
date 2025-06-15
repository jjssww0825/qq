import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 📌 한글 폰트 설정
plt.rcParams['font.family'] = 'NanumGothic'

# 📦 데이터 불러오기 (월 단위 그대로)
@st.cache_data
def load_data():
    df = pd.read_csv("성_연령별_실업률_20250615233240.csv", encoding="cp949")
    df = df[df['연령계층별'] == '20 - 29세'].copy()
    df = df.melt(id_vars=['성별', '연령계층별'], var_name='년월', value_name='실업률')
    df['연도'] = df['년월'].str.slice(0, 4).astype(int)
    return df

df = load_data()

# 📌 UI
st.title("📈 20–29세 청년 실업률의 성별 비교 (2004–2024)")
st.markdown("이 앱은 2004년부터 2024년까지 **월 단위 실업률 변화**를 성별로 시각화합니다.")

# 🔻 연도 범위 슬라이더
min_year = df['연도'].min()
max_year = df['연도'].max()
years = st.slider("분석할 연도 범위 선택", min_value=min_year, max_value=max_year, value=(min_year, max_year))

# 📌 데이터 필터링
filtered_df = df[(df['연도'] >= years[0]) & (df['연도'] <= years[1])].copy()

# 🔻 시계열 정렬을 위한 처리
filtered_df['년월'] = pd.to_datetime(filtered_df['년월'], format="%Y.%m")
filtered_df = filtered_df.sort_values('년월')

# 📊 그래프
st.subheader("📅 월 단위 실업률 추이 (성별)")

fig, ax = plt.subplots(figsize=(10, 5))
for gender in filtered_df['성별'].unique():
    subset = filtered_df[filtered_df['성별'] == gender]
    ax.plot(subset['년월'], subset['실업률'], label=gender, marker='o', markersize=3)

ax.set_xlabel("연-월", fontsize=11)
ax.set_ylabel("실업률 (%)", fontsize=11)
ax.legend(title="성별")
ax.grid(True, linestyle='--', alpha=0.4)
fig.tight_layout()

st.pyplot(fig)

# 📋 데이터 테이블
st.subheader("📋 월별 실업률 데이터")
st.dataframe(filtered_df[['년월', '성별', '실업률']].reset_index(drop=True))
