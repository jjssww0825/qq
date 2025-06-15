import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 한글 폰트 설정 (Streamlit Cloud에서는 반영되지 않을 수 있음)
plt.rcParams['font.family'] = 'NanumGothic'

# CSV 파일 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("성_연령별_실업률_20250615233240.csv", encoding="cp949")
    df = df[df['연령계층별'] == '20 - 29세'].copy()
    df = df.melt(id_vars=['성별', '연령계층별'], var_name='년월', value_name='실업률')
    df['연도'] = df['년월'].str.slice(0, 4).astype(int)
    df_summary = df.groupby(['연도', '성별'])['실업률'].mean().reset_index()
    return df_summary

df_summary = load_data()

# 웹앱 제목
st.title("📈 20–29세 청년 실업률의 성별 비교 (2004–2024)")
st.markdown("이 앱은 2004년부터 2024년까지 **20–29세 청년**의 **성별 실업률** 변화를 시각화합니다.")

# 연도 범위 선택
min_year = int(df_summary['연도'].min())
max_year = int(df_summary['연도'].max())
years = st.slider("분석할 연도 범위 선택", min_value=min_year, max_value=max_year, value=(min_year, max_year))

# 필터링
filtered_df = df_summary[(df_summary['연도'] >= years[0]) & (df_summary['연도'] <= years[1])]

# 그래프 그리기
st.subheader("연도별 평균 실업률 추이 (성별)")
fig, ax = plt.subplots()
for gender in filtered_df['성별'].unique():
    subset = filtered_df[filtered_df['성별'] == gender]
    ax.plot(subset['연도'], subset['실업률'], label=gender, marker='o')

ax.set_xlabel("연도")
ax.set_ylabel("평균 실업률 (%)")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# 데이터 테이블
st.subheader("📋 연도별 성별 실업률 데이터")
st.dataframe(filtered_df)

# 요약 코멘트
st.markdown("📝 **해석 예시**: 연도에 따라 남성과 여성의 실업률 차이가 어떻게 변화했는지 시각적으로 확인할 수 있습니다. 특정 시기에 격차가 확대되거나 좁혀진 시점을 주목해 보세요.")
