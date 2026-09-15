from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import altair as alt
import pandas as pd
import requests
import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="어제 애니메이션 박스오피스",
    page_icon="🎬",
    layout="wide"
)

# 2. 한국 시간(KST) 기준 '어제' 날짜 계산 함수
def get_yesterday_kst():
    kst = ZoneInfo("Asia/Seoul")
    now_kst = datetime.now(kst)
    yesterday_kst = now_kst - timedelta(days=1)
    target_dt = yesterday_kst.strftime("%Y%m%d")
    display_dt = yesterday_kst.strftime("%Y년 %m월 %d일")
    return target_dt, display_dt

# 3. KOBIS 일별 박스오피스 API 호출
def fetch_box_office(api_key, target_dt):
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": api_key, "targetDt": target_dt}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"네트워크 통신 오류가 발생했습니다: {e}"

# 4. 영화 상세정보 API를 통해 '애니메이션' 장르 여부 확인 (캐싱 적용)
@st.cache_data(ttl=3600)  # 동일 영화 정보는 1시간 동안 캐시 유지
def get_movie_genres(api_key, movie_cd):
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json"
    params = {"key": api_key, "movieCd": movie_cd}
    try:
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            movie_info = res.json().get("movieInfoResult", {}).get("movieInfo", {})
            # genres: [{'genreNm': '애니메이션'}, {'genreNm': '모험'}] 형태
            genres = [g.get("genreNm") for g in movie_info.get("genres", [])]
            return genres
    except Exception:
        pass
    return []

# --- 화면 렌더링 시작 ---

target_dt, display_dt = get_yesterday_kst()

st.title("🍿 어제 애니메이션 박스오피스")
st.caption(f"기준 일자: **{display_dt}** (한국 표준시 기준 / 전체 박스오피스 중 '애니메이션' 장르 추출)")

# secrets(비밀 금고) 키 확인
if "KOBIS_KEY" not in st.secrets:
    st.error("""
    **[설정 오류] API 인증키를 찾을 수 없습니다.**  
    Streamlit Cloud 설정(Secrets)에 `KOBIS_KEY`를 등록해 주세요.
    """)
    st.stop()

api_key = st.secrets["KOBIS_KEY"]

# API 호출 및 데이터 로드
with st.spinner("박스오피스 및 장르 정보를 분석하는 중입니다..."):
    data, net_error = fetch_box_office(api_key, target_dt)

# 예외 처리: 통신 실패
if net_error:
    st.error(net_error)
    st.stop()

# 예외 처리: 인증키 에러 등 KOBIS 자체 오류
if "faultInfo" in data:
    fault = data["faultInfo"]
    st.error(f"**[KOBIS API 오류]** {fault.get('message', '알 수 없는 오류')} (코드: {fault.get('errorCode')})")
    st.stop()

movie_list = data.get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])

if not movie_list:
    st.warning("조회된 박스오피스 데이터가 비어 있습니다.")
    st.stop()

# 5. 각 영화별 장르 조회 후 '애니메이션' 필터링
anime_movies = []
for movie in movie_list:
    movie_cd = movie.get("movieCd")
    genres = get_movie_genres(api_key, movie_cd)
    
    # 장르 목록에 '애니메이션'이 포함되어 있는지 확인
    if "애니메이션" in genres:
        movie["genres"] = ", ".join(genres)
        anime_movies.append(movie)

# 애니메이션 영화가 순위에 없을 경우 안내
if not anime_movies:
    st.info(f"💡 {display_dt} 박스오피스 10위권 내에 상영 중인 **애니메이션** 영화가 없습니다.")
    st.stop()

# 6. 데이터프레임 변환 및 숫자형 변환
df = pd.DataFrame(anime_movies)
numeric_cols = ["rank", "audiCnt", "audiAcc", "scrnCnt"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# 애니메이션 전용 순위 부여 (박스오피스 전체 순위와 구분)
df["animeRank"] = range(1, len(df) + 1)

# 7. 애니메이션 1위 영화 지표 카드 (Metric Cards)
top_anime = df.iloc[0]

st.subheader(f"🏆 애니메이션 1위: {top_anime['movieNm']}")
st.caption(f"전체 박스오피스 순위: **{int(top_anime['rank'])}위** | 장르: {top_anime['genres']}")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="당일 관람객수", value=f"{int(top_anime['audiCnt']):,}명")
with col2:
    st.metric(label="누적 관객수", value=f"{int(top_anime['audiAcc']):,}명")
with col3:
    st.metric(label="확보 스크린수", value=f"{int(top_anime['scrnCnt']):,}개")

st.divider()

# 8. 관객수 비교 막대그래프
st.subheader("📊 애니메이션 당일 관람객수 비교")
chart = (
    alt.Chart(df)
    .mark_bar(cornerRadiusTopRight=5, cornerRadiusBottomRight=5)
    .encode(
        x=alt.X("audiCnt:Q", title="당일 관객수 (명)"),
        y=alt.Y("movieNm:N", sort="-x", title="영화명"),
        color=alt.Color("audiCnt:Q", legend=None, scale=alt.Scale(scheme="oranges")),
        tooltip=[
            alt.Tooltip("animeRank:Q", title="애니 순위"),
            alt.Tooltip("rank:Q", title="전체 순위"),
            alt.Tooltip("movieNm:N", title="영화명"),
            alt.Tooltip("audiCnt:Q", title="당일 관객수", format=","),
            alt.Tooltip("audiAcc:Q", title="누적 관객수", format=","),
            alt.Tooltip("scrnCnt:Q", title="스크린수", format=","),
        ],
    )
    .properties(height=max(150, len(df) * 55))
)
st.altair_chart(chart, use_container_width=True)

# 9. 애니메이션 순위표 출력
st.subheader("📋 애니메이션 순위 및 상세 지표")

display_df = df[
    ["animeRank", "rank", "movieNm", "openDt", "genres", "audiCnt", "audiAcc", "scrnCnt"]
].copy()

display_df.columns = [
    "애니 순위",
    "전체 순위",
    "영화명",
    "개봉일",
    "장르",
    "당일 관객수",
    "누적 관객수",
    "확보 스크린수",
]

st.dataframe(
    display_df.style.format({
        "애니 순위": "{:,.0f}위",
        "전체 순위": "{:,.0f}위",
        "당일 관객수": "{:,.0f}명",
        "누적 관객수": "{:,.0f}명",
        "확보 스크린수": "{:,.0f}개",
    }),
    use_container_width=True,
    hide_index=True,
)
