import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# 한글 폰트 설정 (Streamlit Cloud에서는 적용 안 될 수 있음)
plt.rcParams['font.family'] = 'NanumGothic'

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("성_연령별_실업률_20250615233240.csv", encoding="cp949")
    df = df[df['연령계층별'] == '20 - 29세'].copy()
    df = df.melt(id_vars=['성별', '연령계층별'], var_name='년월', value_name='실업률')
    df['년월'] = pd.to_datetime(df['년월'], format='%Y.%m')
    df = df.sort_values('년월')
    return df

df = load_data()

# 앱 제목
st.title("📅 20–29세 청년 실업률: 월 단위 성별 비교 (2004.01–2024.12)")
st.markdown("슬라이더로 분석할 **월 단위 기간**을 선택하세요. 그래프는 남성과 여성의 실업률을 월별로 비교합니다.")

# 슬라이더: 월 범위 선택 (날짜 형식, 포맷 지정)
start_date = df['년월'].min().to_pydatetime()
end_date = df['년월'].max().to_pydatetime()

selected_range = st.slider(
    "분석할 월 범위 선택",
    min_value=start_date,
    max_value=end_date,
    value=(start_date, end_date),
    format="YYYY-MM"  # ✅ 월 형식으로 출력
)

# 데이터 필터링
filtered_df = df[(df['년월'] >= selected_range[0]) & (df['년월'] <= selected_range[1])]

# 그래프
st.subheader("📊 성별 월별 실업률 추이")
fig, ax = plt.subplots(figsize=(10, 5))

for gender in filtered_df['성별'].unique():
    subset = filtered_df[filtered_df['성별'] == gender]
    ax.plot(subset['년월'], subset['실업률'], label=gender, marker='o', markersize=3)

ax.set_xlabel("년월")
ax.set_ylabel("실업률 (%)")
ax.grid(True, linestyle='--', alpha=0.4)
ax.legend(title="성별")
fig.tight_layout()
st.pyplot(fig)

# 데이터 테이블 출력
st.subheader("📋 월별 실업률 데이터")
st.dataframe(filtered_df[['년월', '성별', '실업률']].reset_index(drop=True))
