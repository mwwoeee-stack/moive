import streamlit as st
import pandas as pd
import altair as alt

# 1. 페이지 기본 설정 (넓은 화면, 다크 테마 느낌)
st.set_page_config(
    page_title="시네마 애니메이션 박스오피스",
    page_icon="🍿",
    layout="wide"
)

# 2. 영화관 배경 영상 및 시네마 스타일 CSS 주입
cinema_css_and_bg = """
<style>
/* 배경 비디오 스타일 */
#bg-video {
    position: fixed;
    right: 0;
    bottom: 0;
    min-width: 100%;
    min-height: 100%;
    width: auto;
    height: auto;
    z-index: -2;
    object-fit: cover;
    filter: brightness(0.28) contrast(1.15) saturate(1.1); /* 텍스트 가독성을 위해 어둡게 처리 */
}

/* 영화관 앰비언트 오버레이 (비네팅 및 극장 분위기) */
.theater-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: radial-gradient(circle at 50% 30%, rgba(255, 215, 0, 0.05) 0%, rgba(5, 5, 10, 0.85) 80%);
    z-index: -1;
    pointer-events: none;
}

/* 스트림릿 기본 배경을 투명화 */
.stApp {
    background: transparent !important;
    color: #F8F9FA !important;
}

/* 헤더 및 텍스트 시네마틱 골드/네온 글로우 효과 */
h1 {
    color: #FFE082 !important;
    font-weight: 800 !important;
    text-shadow: 0 0 20px rgba(255, 215, 0, 0.4), 0 2px 4px rgba(0,0,0,0.8);
    letter-spacing: -0.5px;
}
h2, h3 {
    color: #FFF !important;
    text-shadow: 0 2px 6px rgba(0, 0, 0, 0.7);
}

/* 글래스모피즘(반투명 유리) 카드 컨테이너 */
div[data-testid="stMetric"], .cinema-card {
    background: rgba(20, 20, 30, 0.65) !important;
    border: 1px solid rgba(255, 215, 0, 0.25) !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5) !important;
    backdrop-filter: blur(10px) !important;
    -webkit-backdrop-filter: blur(10px) !important;
    border-radius: 14px !important;
    padding: 16px 20px !important;
}

/* 지표 레이블 및 숫자 색상 */
div[data-testid="stMetric"] label {
    color: #B0BEC5 !important;
    font-size: 0.95rem !important;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #FFD54F !important;
    font-weight: 700 !important;
}

/* 데이터프레임 표 반투명화 및 스타일링 */
div[data-testid="stDataFrame"] {
    background: rgba(15, 15, 25, 0.65) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(8px) !important;
    padding: 10px !important;
}

/* 사이드바 어둡고 은은한 영화관 커튼 느낌 */
section[data-testid="stSidebar"] {
    background: rgba(10, 10, 15, 0.88) !important;
    border-right: 1px solid rgba(255, 215, 0, 0.15) !important;
    backdrop-filter: blur(12px) !important;
}
</style>

<!-- 배경 비디오: 극장/필름 프로젝터 분위기 루프 영상 -->
<video autoplay muted loop id="bg-video" playsinline>
    <source src="https://assets.mixkit.co/videos/preview/mixkit-dust-particles-flying-in-a-dark-room-41584-large.mp4" type="video/mp4">
</video>
<div class="theater-overlay"></div>
"""

st.markdown(cinema_css_and_bg, unsafe_allow_html=True)

# 3. 역대 애니메이션 흥행 데이터셋 로드
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

# 4. 헤더
st.title("🎬 CINEMA THEATER: 역대 애니메이션 명예의 전당")
st.markdown("<p style='color: #CFD8DC; font-size: 1.1rem; margin-top: -10px;'>영사실의 영롱한 빛과 함께 감상하는 한국 극장가 역대 최고 흥행작 통계</p>", unsafe_allow_html=True)
st.write("")

# 5. 사이드바 컨트롤 (영화관 매표소 느낌)
with st.sidebar:
    st.markdown("### 🎟️ 매표소 필터 (TICKET BOX)")
    country_options = ["전체 국가"] + list(df_all["국가"].unique())
    selected_country = st.selectbox("제작 국가 선택", country_options)

    min_audi = st.slider(
        "최소 누적 관객수 (만 명)",
        min_value=50,
        max_value=1300,
        value=100,
        step=50
    ) * 10000

    st.divider()
    st.caption("📽️ Background: Cinema Dust & Projector Ambience")

# 필터링
filtered_df = df_all[df_all["누적관객수"] >= min_audi].copy()
if selected_country != "전체 국가":
    filtered_df = filtered_df[filtered_df["국가"] == selected_country]

filtered_df = filtered_df.reset_index(drop=True)
filtered_df["선택순위"] = filtered_df.index + 1

# 6. 상단 하이라이트 지표 카드 (시네마 카드 형태)
if not filtered_df.empty:
    top_movie = filtered_df.iloc[0]
    total_audience = filtered_df["누적관객수"].sum()
    avg_audience = filtered_df["누적관객수"].mean()

    st.markdown(f"### 🏆 현재 1위 상영작 : <span style='color:#FFE082;'>{top_movie['영화명']}</span> ({top_movie['개봉연도']})", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="🥇 1위 관객수", value=f"{top_movie['누적관객수']:,}명")
    with col2:
        st.metric(label="🎞️ 상영 편수", value=f"{len(filtered_df)}편")
    with col3:
        st.metric(label="📊 평균 동원 관객", value=f"{int(avg_audience):,}명")

    st.write("")
    st.divider()

    # 7. 골드/네온 톤의 누적 관객수 시각화 차트
    st.subheader("📊 스크린 누적 관객수 시각화")
    chart = (
        alt.Chart(filtered_df)
        .mark_bar(cornerRadiusTopRight=5, cornerRadiusBottomRight=5, opacity=0.9)
        .encode(
            x=alt.X("누적관객수:Q", title="누적 관객수 (명)", axis=alt.Axis(labelColor="#FFF", titleColor="#FFE082", gridColor="#333")),
            y=alt.Y("영화명:N", sort="-x", title="영화명", axis=alt.Axis(labelColor="#FFF", titleColor="#FFE082")),
            color=alt.Color("국가:N", scale=alt.Scale(range=["#E50914", "#FFD700", "#00B4D8"]), legend=alt.Legend(title="국가", labelColor="#FFF", titleColor="#FFE082")),
            tooltip=[
                alt.Tooltip("선택순위:Q", title="순위"),
                alt.Tooltip("영화명:N", title="영화명"),
                alt.Tooltip("개봉연도:Q", title="개봉연도"),
                alt.Tooltip("국가:N", title="국가"),
                alt.Tooltip("누적관객수:Q", title="누적 관객수", format=","),
            ]
        )
        .properties(height=max(220, len(filtered_df) * 36))
        .configure_view(strokeOpacity=0)
        .configure(background="transparent")
    )
    st.altair_chart(chart, use_container_width=True)

    st.write("")
    
    # 8. 영화 순위 목록 표
    st.subheader("📋 전체 박스오피스 리스트")
    display_df = filtered_df[["선택순위", "역대순위", "영화명", "개봉연도", "국가", "누적관객수", "배급사"]].copy()
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
    st.warning("선택하신 조건에 해당하는 영화가 없습니다. 사이드바 필터를 조정해 주세요.")
