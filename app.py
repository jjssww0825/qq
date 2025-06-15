import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# 📌 한글 폰트 설정 (Streamlit Cloud에서는 일부 적용 안될 수 있음)
plt.rcParams['font.family'] = 'NanumGothic'

# 📦 연도별 데이터 불러오기
@st.cache_data
def load_summary_data():
    df = pd.read_csv("성_연령별_실업률_20250615233240.csv", encoding="cp949")
    df = df[df['연령계층별'] == '20 - 29세'].copy()
    df = df.melt(id_vars=['성별', '연령계층별'], var_name='년월', value_name='실업률')
    df['연도'] = df['년월'].str.slice(0, 4).astype(int)
    df_summary = df.groupby(['연도', '성별'])['실업률'].mean().reset_index()
    return df_summary

# 📦 월별 데이터 불러오기
@st.cache_data
def load_monthly_data():
    df = pd.read_csv("성_연령별_실업률_20250615233240.csv", encoding="cp949")
    df = df[df['연령계층별'] == '20 - 29세'].copy()
    df = df.melt(id_vars=['성별', '연령계층별'], var_name='년월', value_name='실업률')
    return df

# 데이터 로드
df_summary = load_summary_data()
df_monthly = load_monthly_data()

# 🌟 앱 제목 및 설명
st.title("📈 20–29세 청년 실업률의 성별 비교 (2004–2024)")
st.markdown("이 앱은 2004년부터 2024년까지 **20–29세 청년**의 **성별 실업률** 변화를 시각화합니다.")

# ----------------------------
# 📊 연도별 실업률 분석
# ----------------------------

st.subheader("연도별 평균 실업률 추이 (성별)")

# 연도 범위 선택 슬라이더
min_year = int(df_summary['연도'].min())
max_year = int(df_summary['연도'].max())
years = st.slider("분석할 연도 범위 선택", min_value=min_year, max_value=max_year, value=(min_year, max_year))

# 필터링된 데이터
filtered_df = df_summary[(df_summary['연도'] >= years[0]) & (df_summary['연도'] <= years[1])]

# 그래프
fig, ax = plt.subplots(figsize=(8, 5))
for gender in filtered_df['성별'].unique():
    subset = filtered_df[filtered_df['성별'] == gender]
    ax.plot(subset['연도'], subset['실업률'], label=gender, marker='o')

ax.set_xlabel("연도", fontsize=11)
ax.set_ylabel("평균 실업률 (%)", fontsize=11)
ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
ax.tick_params(axis='both', labelsize=10)
ax.grid(True, linestyle='--', alpha=0.4)
ax.legend(title='성별', fontsize=10, title_fontsize=11)
fig.tight_layout()
st.pyplot(fig)

# 데이터 테이블
st.subheader("📋 연도별 성별 실업률 데이터")
st.dataframe(filtered_df)

# ----------------------------
# 📅 월별 실업률 분석
# ----------------------------

st.subheader("📅 월별 실업률 추이 분석")

# 선택할 연도와 성별
selected_year = st.selectbox("분석할 연도 선택", sorted(df_summary['연도'].unique()))
selected_gender = st.radio("성별 선택", ['남자', '여자'], horizontal=True)

# 선택한 연도/성별로 필터링
monthly_filtered = df_monthly[
    (df_monthly['성별'] == selected_gender) &
    (df_monthly['년월'].str.startswith(str(selected_year)))
].copy()

# 월 숫자 추출
monthly_filtered['월'] = monthly_filtered['년월'].str.slice(5, 7).astype(int)

# 그래프
fig2, ax2 = plt.subplots(figsize=(8, 4))
ax2.plot(monthly_filtered['월'], monthly_filtered['실업률'], marker='o')
ax2.set_title(f"{selected_year}년 {selected_gender} 월별 실업률", fontsize=13)
ax2.set_xlabel("월", fontsize=11)
ax2.set_ylabel("실업률 (%)", fontsize=11)
ax2.set_xticks(range(1, 13))
ax2.grid(True, linestyle='--', alpha=0.3)
fig2.tight_layout()
st.pyplot(fig2)

# 데이터 테이블
st.dataframe(monthly_filtered[['년월', '실업률']].reset_index(drop=True))
