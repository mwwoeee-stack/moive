import streamlit as st
import pandas as pd
import altair as alt

# 1. 페이지 설정
st.set_page_config(
    page_title="역대 애니메이션 영화 흥행 순위",
    page_icon="🎬",
    layout="wide"
)

# 2. 역대 대표 애니메이션 영화 흥행 데이터셋 (영화진흥위원회 KOBIS 공식 통계 기반)
@st.cache_data
def load_animation_data():
    raw_data = [
        {"순위": 1, "영화명": "겨울왕국 2", "개봉연도": 2019, "국가": "미국", "누적관객수": 13768797, "배급사": "월트디즈니"},
        {"순위": 2, "영화명": "겨울왕국", "개봉연도": 2014, "국가": "미국", "누적관객수": 10329222, "배급사": "월트디즈니"},
        {"순위": 3, "영화명": "인사이드 아웃 2", "개봉연도": 2024, "국가": "미국", "누적관객수": 8799611, "배급사": "월트디즈니"},
        {"순위": 4, "영화명": "엘리멘탈", "개봉연도": 2023, "국가": "미국", "누적관객수": 7241486, "배급사": "월트디즈니"},
        {"순위": 5, "영화명": "스즈메의 문단속", "개봉연도": 2023, "국가": "일본", "누적관객수": 5641721, "배급사": "쇼박스"},
        {"순위": 6, "영화명": "쿵푸팬더 2", "개봉연도": 2011, "국가": "미국", "누적관객수": 5073037, "배급사": "CJ ENM"},
        {"순위": 7, "영화명": "인사이드 아웃", "개봉연도": 2015, "국가": "미국", "누적관객수": 4972640, "배급사": "월트디즈니"},
        {"순위": 8, "영화명": "더 퍼스트 슬램덩크", "개봉연도": 2023, "국가": "일본", "누적관객수": 4921209, "배급사": "NEW"},
        {"순위": 9, "영화명": "쿵푸팬더", "개봉연도": 2008, "국가": "미국", "누적관객수": 4673009, "배급사": "CJ ENM"},
        {"순위": 10, "영화명": "주토피아", "개봉연도": 2016, "국가": "미국", "누적관객수": 4707362, "배급사": "월트디즈니"},
        {"순위": 11, "영화명": "너의 이름은.", "개봉연도": 2017, "국가": "일본", "누적관객수": 3979592, "배급사": "메가박스"},
        {"순위": 12, "영화명": "쿵푸팬더 3", "개봉연도": 2016, "국가": "미국", "누적관객수": 3984814, "배급사": "CJ ENM"},
        {"순위": 13, "영화명": "슈퍼배드 3", "개봉연도": 2017, "국가": "미국", "누적관객수": 3324879, "배급사": "UPI"},
        {"순위": 14, "영화명": "하울의 움직이는 성", "개봉연도": 2004, "국가": "일본", "누적관객수": 3015165, "배급사": "대원미디어"},
        {"순위": 15, "영화명": "마당을 나온 암탉", "개봉연도": 2011, "국가": "한국", "누적관객수": 2223145, "배급사": "롯데엔터테인먼트"},
        {"순위": 16, "영화명": "극장판 귀멸의 칼날: 무한열차편", "개봉연도": 2021, "국가": "일본", "누적관객수": 2221338, "배급사": "워터홀컴퍼니"},
        {"순위": 17, "영화명": "센과 치히로의 행방불명", "개봉연도": 2002, "국가": "일본", "누적관객수": 2167573, "배급사": "브에나비스타"},
        {"순위": 18, "영화명": "그대들은 어떻게 살 것인가", "개봉연도": 2023, "국가": "일본", "누적관객수": 2015965, "배급사": "메가박스"},
        {"순위": 19, "영화명": "사랑의 하츄핑", "개봉연도": 2024, "국가": "한국", "누적관객수": 1259120, "배급사": "쇼박스"},
        {"순위": 20, "영화명": "점박이: 한반도의 공룡 3D", "개봉연도": 2012, "국가": "한국", "누적관객수": 1051710, "배급사": "CJ ENM"},
    ]
    df = pd.DataFrame(raw_data)
    # 누적 관객수 기준 내림차순 정렬 및 순위 재지정
    df = df.sort_values(by="누적관객수", ascending=False).reset_index(drop=True)
    df["순위"] = df.index + 1
    return df

df_all = load_animation_data()

# 3. 타이틀 및 대시보드 헤더
st.title("🏆 대한민국 역대 애니메이션 흥행 순위")
st.caption("영화진흥위원회(KOBIS) 통합전산망 공식 누적 관객수 기준 집계 데이터")

# 4. 사이드바 필터링 컨트롤
st.sidebar.header("🔍 필터 옵션")

# 국가 필터
country_options = ["전체"] + list(df_all["국가"].unique())
selected_country = st.sidebar.selectbox("제작 국가 선택", country_options)

# 관객수 필터 (슬라이더)
min_audi = st.sidebar.slider(
    "최소 누적 관객수 (만 명)",
    min_value=50,
    max_value=1300,
    value=100,
    step=50
) * 10000

# 필터 적용
filtered_df = df_all[df_all["누적관객수"] >= min_audi]
if selected_country != "전체":
    filtered_df = filtered_df[filtered_df["국가"] == selected_country]

filtered_df = filtered_df.reset_index(drop=True)
filtered_df["선택조건 순위"] = filtered_df.index + 1

# 5. 핵심 하이라이트 지표 카드
if not filtered_df.empty:
    top_movie = filtered_df.iloc[0]
    total_audience = filtered_df["누적관객수"].sum()
    avg_audience = filtered_df["누적관객수"].mean()

    st.subheader(f"🥇 조건 내 1위: {top_movie['영화명']} ({top_movie['개봉연도']})")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="1위 누적 관객수", value=f"{top_movie['누적관객수']:,}명")
    with col2:
        st.metric(label="조회된 작품 수", value=f"{len(filtered_df)}편")
    with col3:
        st.metric(label="조회 작품 평균 관객수", value=f"{int(avg_audience):,}명")

    st.divider()

    # 6. 관객수 비교 차트
    st.subheader("📊 누적 관객수 비교 시각화")
    chart = (
        alt.Chart(filtered_df)
        .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
        .encode(
            x=alt.X("누적관객수:Q", title="누적 관객수 (명)"),
            y=alt.Y("영화명:N", sort="-x", title="영화명"),
            color=alt.Color("국가:N", legend=alt.Legend(title="국가")),
            tooltip=[
                alt.Tooltip("선택조건 순위:Q", title="순위"),
                alt.Tooltip("영화명:N", title="영화명"),
                alt.Tooltip("개봉연도:Q", title="개봉연도"),
                alt.Tooltip("국가:N", title="국가"),
                alt.Tooltip("누적관객수:Q", title="누적 관객수", format=","),
            ]
        )
        .properties(height=max(200, len(filtered_df) * 35))
    )
    st.altair_chart(chart, use_container_width=True)

    # 7. 전체 상세 표
    st.subheader("📋 순위 목록표")
    
    display_df = filtered_df[["선택조건 순위", "순위", "영화명", "개봉연도", "국가", "누적관객수", "배급사"]].copy()
    display_df.columns = ["조건 순위", "역대 순위", "영화명", "개봉연도", "국가", "누적 관객수", "배급사"]
    
    st.dataframe(
        display_df.style.format({
            "조건 순위": "{:d}위",
            "역대 순위": "{:d}위",
            "개봉연도": "{:d}년",
            "누적 관객수": "{:,.0f}명"
        }),
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("선택하신 조건(국가/관객수)에 맞는 영화 데이터가 없습니다. 사이드바 필터를 조정해 보세요.")
