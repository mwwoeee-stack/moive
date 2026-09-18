import streamlit as st
from openai import OpenAI

# 1. 페이지 기본 설정
st.set_page_config(page_title="AI 캐릭터 대화방", page_icon="💬")

st.title("💬 캐릭터 챗봇")

# 2. Streamlit secrets에서 Gemini API 키 불러오기
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("API 키를 찾을 수 없습니다. secrets.toml 파일에 GEMINI_API_KEY를 등록해 주세요.")
    st.stop()

# 3. Gemini 호환 OpenAI 클라이언트 객체 생성
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# 4. 캐릭터 기본 프롬프트(성격) 정의
PERSONA_PROMPTS = {
    "권태기 온 6년 사귄 남자친구": (
        "너는 사용자와 6년 동안 사귀어 심한 권태기가 온 남자친구야. "
        "감정의 동요가 거의 없고, 대화를 이어나가려는 의지가 전혀 없어. "
        "질문에는 귀찮은 듯 단답으로 일관하고, 무미건조한 종결어미(~어, ~음, ~함 등)를 써. "
        "말 중간이나 끝에 () 안에 상황에 어울리는 건조한 표정, 덤덤한 말투, 성의 없는 행동을 반드시 묘사해."
    ),
    "카사노바 남사친": (
        "너는 사용자의 남사친이지만 여자를 능글맞게 대하는 카사노바야. "
        "말투는 다소 천박하고 저급하며, 쉴 틈 없이 유혹적인 플러팅을 퍼부어. "
        "자연스럽게 선을 넘나들며, 친구라는 안전한 관계를 방패 삼아 플러팅을 던진 뒤 반응을 보며 장난처럼 능청스럽게 넘기는 여유가 있어. "
        "다정한 애칭이나 호칭을 부르고 칭찬을 툭툭 던지며, 은근한 스킨십이나 시선을 유도하는 말과 여유로운 어조를 사용해. "
        "말 중간이나 끝에 () 안에 알맞은 능글맞은 표정, 끈적한 말투, 대담한 행동을 상세히 묘사해."
    ),
    "나와 정략결혼 한 나의 입덕 부정기 온 재벌 3세 남편": (
        "너는 집안끼리의 정략결혼으로 사용자와 맺어진 재벌 3세 남편이야. "
        "현재 아내(사용자)에게 마음이 흔들리고 빠져들고 있지만 이를 강하게 부정하는 '입덕 부정기'를 겪고 있어. "
        "기본적으로 격식체를 유지하며 거리감을 두려 하고, 사용자를 반드시 '부인'이라고 불러. "
        "그러나 묘하게 말이 길어지며 '사업상', '집안 체면상', '대외적인 이미지 때문에'라는 핑계를 대며 사용자을 살뜰하고 꼼꼼하게 챙겨줘. "
        "사용자가 다른 사람과 엮이거나 관심을 보이면 차갑게 정색하면서도 은근한 독점욕과 질투를 숨기지 못하고 드러내."
    )
}

# 5. 세션 상태 초기화 (대화 기록 및 선택된 성격 관리)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 직전에 선택했던 캐릭터 프리셋을 추적하기 위한 상태값
if "last_selected_preset" not in st.session_state:
    st.session_state.last_selected_preset = "권태기 온 6년 사귄 남자친구"

if "custom_prompt" not in st.session_state:
    st.session_state.custom_prompt = PERSONA_PROMPTS[st.session_state.last_selected_preset]

# 6. 사이드바 UI 구성
with st.sidebar:
    st.header("⚙️ 캐릭터 설정")

    # (1) 말투(캐릭터 프리셋) 선택 라디오 버튼
    preset_choice = st.radio(
        "말투 고르기",
        options=list(PERSONA_PROMPTS.keys()),
        index=list(PERSONA_PROMPTS.keys()).index(st.session_state.last_selected_preset)
    )

    # 선택한 프리셋이 바뀌었을 때 직접 입력 칸 텍스트 자동 동기화
    if preset_choice != st.session_state.last_selected_preset:
        st.session_state.last_selected_preset = preset_choice
        st.session_state.custom_prompt = PERSONA_PROMPTS[preset_choice]

    # (2) 성격 문장 직접 고쳐 쓰기 칸
    current_system_prompt = st.text_area(
        "성격 문장 직접 수정",
        value=st.session_state.custom_prompt,
        height=180,
        help="선택한 말투의 기본 지침입니다. 원하는 대로 직접 문장을 추가하거나 바꿀 수 있습니다."
    )
    # 사용자가 직접 수정한 텍스트를 상태에 반영
    st.session_state.custom_prompt = current_system_prompt

    st.markdown("---")

    # (3) 대화 지우기 버튼
    if st.button("🗑️ 대화 지우기", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 7. 이전 대화 기록 화면에 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 8. 대화 입력 및 응답 생성
if user_input := st.chat_input("메시지를 입력하세요..."):
    # (1) 사용자 메시지 출력 및 기록
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # (2) AI 답변 출력
    with st.chat_message("assistant"):
        # 현재 사이드바에 설정된 프롬프트를 시스템 지침으로 주입 (다음 답부터 즉시 적용)
        active_instruction = {
            "role": "system",
            "content": st.session_state.custom_prompt
        }
        messages_to_send = [active_instruction] + st.session_state.messages

        try:
            stream = client.chat.completions.create(
                model="gemini-3.5-flash-lite",
                messages=messages_to_send,
                stream=True,
            )
            # 실시간 스트리밍 출력
            ai_response = st.write_stream(stream)
            # 대화 기록에 어시스턴트 응답 추가
            st.session_state.messages.append({"role": "assistant", "content": ai_response})

        except Exception:
            # 오류 발생 시 사용자 친화적인 한국어 안내 문구 표시
            st.warning("상대방과 연결하는 중 문제가 생겼어요. 잠시 후 다시 말을 걸어보세요.")
