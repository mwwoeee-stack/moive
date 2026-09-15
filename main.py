import streamlit as st
import pandas as pd
import altair as alt

# 1. 페이지 설정
st.set_page_config(
    page_title="시네마 애니메이션 전당",
    page_icon="🎬",
    layout="wide"
)

# 2. 사이드바 - 테마 영상 선택 옵션
st.sidebar.markdown("### 📽️ 극장 환경 설정")
bg_option = st.sidebar.radio(
    "영화관 스크린 영상 선택",
    ["1. 클래식 영사실 빔 (추천)", "2. 레트로 필름 카운트다운", "3. 고요한 심야 상영관"]
)

# 선택에 따른 고화질 비디오 URL
video_urls = {
    "1. 클래식 영사실 빔 (추천)": "https://cdn.pixabay.com/video/2020/05/25/40130-424930030_large.mp4",
    "2. 레트로 필름 카운트다운": "https://cdn.pixabay.com/video/2019/04/23/23011-332464733_large.mp4",
    "3. 고요한 심야 상영관": "https://cdn.pixabay.com/video/2020/04/17/36413-410972412_large.mp4"
}
selected_video = video_urls[bg_option]

# 3. 영화관 인테리어 CSS (붉은 벨벳 좌석 실루엣 + 앰비언트 라이트)
theater_style = f"""
<style>
/* 배경 비디오 - 화면 중앙 상단에서 스크린처럼 투사 */
#theater-video {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    object-fit: cover;
    z-index: -3;
    filter: brightness(0.35) contrast(1.2);
}}

/* 영화관 내부 실루엣 오버레이 (비네팅 + 영사실 빔 효과) */
.cinema-environment {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: -2;
    pointer-events: none;
    background: 
        /* 상단 프로젝터 조명 */
        radial-gradient(ellipse at 50% -10%, rgba(255, 230, 150, 0.22) 0%, transparent 60%),
        /* 하단 객석 좌석 어둠 처리 */
        linear-gradient(to top, rgba(10, 2, 4, 0.95) 15%, rgba(10, 2, 4, 0.6) 50%, rgba(0, 0, 0, 0.4) 100%),
        /* 양옆 커튼 비네팅 */
        radial-gradient(circle at center, transparent 40%, rgba(5, 0, 2, 0.85) 95%);
}}

/* 기본 스트림릿 배경 투명화 */
.stApp {{
    background: transparent !important;
}}

/* 메인 스크린 박스 디자인 */
.screen-frame {{
    background: rgba(18, 12, 16, 0.72) !important;
    border: 1px solid rgba(255, 215, 0, 0.25) !important;
    border-radius: 16px !important;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.9), inset 0 1px 1px rgba(255, 255, 255, 0.1) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    padding: 24px;
    margin-bottom: 24px;
}}

/* 텍스트 골드 발광 효과 */
h1 {{
    color: #FFE082 !important;
    font-weight: 900 !important;
    letter-spacing: 1px;
    text-shadow: 0 0 25px rgba(255, 215, 0, 0.5), 0 2px 4px #000 !important;
}}
h2, h3 {{
    color: #F5F5F5 !important;
    text-shadow: 0 2px 5px #000;
}}

/* 지표 카드 커스텀 */
div[data-testid="stMetric"] {{
    background: rgba(28, 18, 24, 0.75) !important;
    border: 1px solid rgba(255, 193, 7, 0.3) !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.6) !important;
}}
div[data-testid="stMetric"] label {{
    color: #CFD8DC !important;
}}
div[data-testid="stMetricValue"] {{
    color: #FFD54F !important;
    font-weight: 800 !important;
}}

/* 사이드바 다크 와인 톤 */
section[data-testid="stSidebar"] {{
    background: rgba(14, 8, 10, 0.92) !important;
    border-right: 1px solid rgba(255, 215, 0, 0.15) !important;
}}
</style>

<video autoplay muted loop id="theater-video" playsinline key="{selected_video}">
    <source src="{selected_video}" type="video/mp4">
</video>
<div class="cinema-environment"></div>
"""

st.markdown(theater_style, unsafe_allow_html=True)

# 4. 애니메이션 역대 박스오피스 데이터
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
    df = df.sort_values(by="누적관객수", ascending=False).reset_index(drop=True)
    df["역대순위"] = df.index + 1
    return df

df_all = load_animation_data()

# 5. 헤더 섹션
st.markdown("<h1>🎟️ THE CINEMA HALL: 역대 애니메이션 박스오피스</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #ECEFF1; font-size: 1.05rem; text-shadow: 0 1px 4px #000;'>극장 대형 스크린 너머로 만나는 대한민국 흥행 명작선</p>", unsafe_allow_html=True)
st.write("")

# 6. 사이드바 필터
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🔍 상영작 검색 필터")
    country_options = ["전체 국가"] + list(df_all["국가"].unique())
    selected_country = st.selectbox("제작 국가", country_options)

    min_audi = st.slider(
        "관객수 컷오프 (만 명 이상)",
        min_value=50,
        max_value=1300,
        value=100,
        step=50
    ) * 10000

# 필터 적용
filtered_df = df_all[df_all["누적관객수"] >= min_audi].copy()
if selected_country != "전체 국가":
    filtered_df = filtered_df[filtered_df["국가"] == selected_country]

filtered_df = filtered_df.reset_index(drop=True)
filtered_df["표시순위"] = filtered_df.index + 1

# 7. 본문 대시보드
if not filtered_df.empty:
    top_movie = filtered_df.iloc[0]
    total_audience = filtered_df["누적관객수"].sum()
    avg_audience = filtered_df["누적관객수"].mean()

    # 상단 하이라이트 지표
    st.markdown(f"### 🌟 조건 내 1위 상영작: <span style='color: #FFE082;'>{top_movie['영화명']}</span> ({top_movie['개봉연도']})", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("1위 동원 관객", f"{top_movie['누적관객수']:,} 명")
    with col2:
        st.metric("선택된 상영작", f"{len(filtered_df)} 편")
    with col3:
        st.metric("편당 평균 관객", f"{int(avg_audience):,} 명")

    st.write("")
    st.divider()

    # 시각화 막대 그래프
    st.subheader("📊 스크린 누적 관객 랭킹")
    chart = (
        alt.Chart(filtered_df)
        .mark_bar(cornerRadiusTopRight=5, cornerRadiusBottomRight=5, opacity=0.92)
        .encode(
            x=alt.X("누적관객수:Q", title="누적 관객수 (명)", axis=alt.Axis(labelColor="#FFF", titleColor="#FFE082", gridColor="rgba(255,255,255,0.1)")),
            y=alt.Y("영화명:N", sort="-x", title="", axis=alt.Axis(labelColor="#FFF")),
            color=alt.Color("국가:N", scale=alt.Scale(range=["#E50914", "#FFC107", "#00BCD4"]), legend=alt.Legend(title="국가", labelColor="#FFF", titleColor="#FFE082")),
            tooltip=[
                alt.Tooltip("표시순위:Q", title="순위"),
                alt.Tooltip("영화명:N", title="영화명"),
                alt.Tooltip("개봉연도:Q", title="개봉연도"),
                alt.Tooltip("국가:N", title="국가"),
                alt.Tooltip("누적관객수:Q", title="누적 관객수", format=","),
            ]
        )
        .properties(height=max(200, len(filtered_df) * 36))
        .configure_view(strokeOpacity=0)
        .configure(background="transparent")
    )
    st.altair_chart(chart, use_container_width=True)

    st.write("")

    # 데이터 테이블
    st.subheader("📋 전체 순위 리스트")
    display_df = filtered_df[["표시순위", "역대순위", "영화명", "개봉연도", "국가", "누적관객수", "배급사"]].copy()
    display_df.columns = ["순위", "역대 순위", "영화명", "개봉연도", "국가", "누적 관객수", "배급사"]

    st.dataframe(
        display_df.style.format({
            "순위": "{:d}위",
            "역대 순위": "{:d}위",
            "개봉연도": "{:d}년",
            "누적 관객수": "{:,.0f}명"
        }),
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("선택하신 조건에 일치하는 영화가 없습니다. 사이드바 필터를 변경해 보세요.")
