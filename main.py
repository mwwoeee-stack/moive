from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import altair as alt
import pandas as pd
import requests
import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="어제 박스오피스 순위", page_icon="🎬", layout="wide"
)


# 2. 한국 시간(KST) 기준 '어제' 날짜 계산 함수 (파이썬 기본 내장 zoneinfo 사용)
def get_yesterday_kst():
    # 서버 시간대와 무관하게 서울 시간대를 적용합니다.
    kst = ZoneInfo("Asia/Seoul")
    now_kst = datetime.now(kst)
    yesterday_kst = now_kst - timedelta(days=1)

    # API 요청 규격(YYYYMMDD)과 화면 표시 규격(YYYY-MM-DD)으로 변환
    target_dt = yesterday_kst.strftime("%Y%m%d")
    display_dt = yesterday_kst.strftime("%Y년 %m월 %d일")
    return target_dt, display_dt


# 3. KOBIS API 데이터 수집 함수
def fetch_box_office(api_key, target_dt):
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": api_key, "targetDt": target_dt}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"네트워크 통신 오류가 발생했습니다: {e}"


# --- 앱 화면 구현 ---

target_dt, display_dt = get_yesterday_kst()

st.title("🎬 어제 일별 박스오피스")
st.caption(f"기준 일자: **{display_dt}** (한국 표준시 기준)")

# secrets(비밀 금고)에서 인증키 확인
if "KOBIS_KEY" not in st.secrets:
    st.error(
        """
    **[설정 오류] API 인증키를 찾을 수 없습니다.**  
    Streamlit Cloud 설정(Settings -> Secrets)에서 아래 형식으로 키를 등록해 주세요:
    ```toml
    KOBIS_KEY = "발급받은_KOBIS_인증키"
    ```
    """
    )
    st.stop()

api_key = st.secrets["KOBIS_KEY"]

# API 호출
with st.spinner("박스오피스 데이터를 불러오는 중입니다..."):
    data, net_error = fetch_box_office(api_key, target_dt)

# 예외 처리 1: 통신 실패
if net_error:
    st.error(net_error)
    st.info("💡 인터넷 연결 상태를 확인하거나 잠시 후 다시 시도해 주세요.")
    st.stop()

# 예외 처리 2: API 내부 faultInfo 오류 (키 오류, 제한 초과 등)
if "faultInfo" in data:
    fault = data["faultInfo"]
    st.error(
        f"""
    **[KOBIS API 응답 오류]**  
    - **오류 메시지:** {fault.get('message', '알 수 없는 오류')}  
    - **오류 코드:** {fault.get('errorCode', '코드 없음')}  
    
    💡 **확인 사항:** Streamlit Secrets에 입력한 `KOBIS_KEY` 값이 정확한지, 하루 호출 한도를 초과하지 않았는지 확인하세요.
    """
    )
    st.stop()

# 영화 목록 추출
box_office_result = data.get("boxOfficeResult", {})
movie_list = box_office_result.get("dailyBoxOfficeList", [])

# 예외 처리 3: 목록이 비어 있는 경우
if not movie_list:
    st.warning("조회된 박스오피스 데이터가 비어 있습니다.")
    st.info(
        f"💡 영진위 시스템에 아직 {display_dt} 데이터 집계가 완료되지 않았을 수 있습니다. 잠시 후 다시 확인해 주세요."
    )
    st.stop()

# 4. 데이터 가공 (문자열 -> 숫자 변환)
df = pd.DataFrame(movie_list)

numeric_cols = ["rank", "audiCnt", "audiAcc", "scrnCnt"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# 5. 1위 영화 지표 카드 (Metric Card 3장)
top_movie = df.iloc[0]

st.subheader(f"🥇 1위 영화: {top_movie['movieNm']}")

metric_col1, metric_col2, metric_col3 = st.columns(3)
with metric_col1:
    st.metric(label="당일 관객수", value=f"{int(top_movie['audiCnt']):,}명")
with metric_col2:
    st.metric(label="누적 관객수", value=f"{int(top_movie['audiAcc']):,}명")
with metric_col3:
    st.metric(label="확보 스크린수", value=f"{int(top_movie['scrnCnt']):,}개")

st.divider()

# 6. 상위 5편 관객수 막대그래프
st.subheader("📊 일일 관객수 TOP 5")
top_5_df = df.head(5).copy()

chart = (
    alt.Chart(top_5_df)
    .mark_bar(cornerRadiusTopRight=5, cornerRadiusBottomRight=5)
    .encode(
        x=alt.X("audiCnt:Q", title="일일 관객수 (명)"),
        y=alt.Y("movieNm:N", sort="-x", title="영화명"),
        color=alt.Color("audiCnt:Q", legend=None, scale=alt.Scale(scheme="blues")),
        tooltip=[
            alt.Tooltip("rank:Q", title="순위"),
            alt.Tooltip("movieNm:N", title="영화명"),
            alt.Tooltip("audiCnt:Q", title="당일 관객수", format=","),
            alt.Tooltip("audiAcc:Q", title="누적 관객수", format=","),
        ],
    )
    .properties(height=280)
)

st.altair_chart(chart, use_container_width=True)

# 7. 전체 순위 표 출력
st.subheader("📋 전체 순위표")

display_table = df[
    ["rank", "movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]
].copy()
display_table.columns = [
    "순위",
    "영화명",
    "개봉일",
    "당일 관객수",
    "누적 관객수",
    "스크린수",
]

st.dataframe(
    display_table.style.format(
        {"당일 관객수": "{:,.0f}명", "누적 관객수": "{:,.0f}명", "스크린수": "{:,.0f}개"}
    ),
    use_container_width=True,
    hide_index=True,
)
