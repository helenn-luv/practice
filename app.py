
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="결제 서비스 개선 AI 챗봇",
    page_icon="💳",
    layout="wide",
)

# -----------------------------
# Seed data
# -----------------------------
DEFAULT_MANUALS = {
    "결제": {
        "title": "결제 매뉴얼",
        "content": """
1. 고객 결제 수단을 먼저 확인합니다.
2. 쿠폰/프로모션 적용 가능 여부를 확인합니다.
3. 카드/간편결제/복합결제 순서에 따라 결제를 진행합니다.
4. 예외 상황 발생 시 오류 대응 매뉴얼 또는 관리자 문의 기준을 확인합니다.
""",
        "faq": [
            ("쿠폰과 카드 복합결제 방법", "쿠폰 적용 가능 여부를 먼저 확인한 뒤 카드 결제를 진행합니다. 중복 적용 가능 여부는 프로모션 기준을 함께 확인합니다."),
            ("간편결제 오류 시 어떻게 하나요?", "1차 재시도 후 대체 결제수단을 안내하고, 반복 오류 시 오류 대응 기준에 따라 관리자에게 문의합니다."),
        ],
    },
    "쿠폰/프로모션": {
        "title": "쿠폰/프로모션 매뉴얼",
        "content": """
1. 행사 기간, 대상 브랜드, 적용 조건을 확인합니다.
2. 중복 적용 가능 여부를 확인합니다.
3. 카드사 행사와 백화점 행사 동시 적용 여부를 확인합니다.
4. 매주 변경되는 내용은 관리자 업데이트 항목을 우선 확인합니다.
""",
        "faq": [
            ("이 쿠폰이 해당 브랜드에 적용되나요?", "브랜드별 적용 여부는 프로모션 운영 기준을 우선 확인합니다. 임대매장은 별도 기준이 있을 수 있습니다."),
            ("사은행사와 카드 프로모션 동시 적용 가능한가요?", "행사별 조건이 다르므로 프로모션 상세 기준을 확인해야 합니다."),
        ],
    },
    "상품권": {
        "title": "상품권 매뉴얼",
        "content": """
1. 상품권 단독 결제 가능 여부를 확인합니다.
2. 상품권 + 카드 복합결제 가능 여부를 확인합니다.
3. 잔액 처리 기준과 제외 대상 브랜드 여부를 확인합니다.
""",
        "faq": [
            ("상품권과 카드 같이 사용 가능한가요?", "가능 여부는 브랜드 및 결제 유형에 따라 다를 수 있으며, 복합결제 가능 여부를 먼저 확인해야 합니다."),
        ],
    },
    "취소/환불": {
        "title": "취소/환불 매뉴얼",
        "content": """
1. 원결제 수단 기준으로 취소/환불 가능 여부를 확인합니다.
2. 부분 취소 가능 여부를 확인합니다.
3. 쿠폰/프로모션 적용 건은 재계산 기준을 함께 확인합니다.
""",
        "faq": [
            ("쿠폰 적용 건 환불은 어떻게 하나요?", "원결제 수단 기준으로 처리하되, 쿠폰 및 혜택 재계산 기준을 함께 확인해야 합니다."),
        ],
    },
    "오류 대응": {
        "title": "오류 대응 매뉴얼",
        "content": """
1. 결제기/간편결제 오류 여부를 확인합니다.
2. 동일 수단 재시도 후 대체 수단 안내 여부를 판단합니다.
3. 해결 불가 시 관리자 문의 기준을 따릅니다.
""",
        "faq": [
            ("POS 오류가 발생했어요.", "오류 유형 확인 → 재시도 → 대체 결제수단 안내 → 관리자 문의 순서로 진행합니다."),
        ],
    },
}

DEFAULT_PROMOTIONS = [
    {
        "name": "주말 카드 프로모션",
        "period": "매주 금~일",
        "rule": "지정 카드 결제 시 5% 즉시 할인",
        "updated_at": "2026-04-01",
    },
    {
        "name": "앱 쿠폰 행사",
        "period": "4월 한정",
        "rule": "앱 다운로드 고객 대상 쿠폰 적용",
        "updated_at": "2026-04-03",
    },
]

KPI_TARGETS = {
    "결제 VOC 감소": "10~15%",
    "응대 오류 감소": "감소 추적",
    "처리 시간 단축": "월별 모니터링",
    "직원 사용률 증가": "사용 로그 확인",
}


# -----------------------------
# Session state
# -----------------------------
if "manuals" not in st.session_state:
    st.session_state.manuals = DEFAULT_MANUALS.copy()

if "promotions" not in st.session_state:
    st.session_state.promotions = DEFAULT_PROMOTIONS.copy()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        ("assistant", "안녕하세요. 결제, 쿠폰, 상품권, 환불, 오류 대응 관련 질문을 입력하거나 왼쪽 메뉴에서 매뉴얼을 선택해주세요.")
    ]


# -----------------------------
# Helpers
# -----------------------------
def find_answer(user_text: str) -> str:
    q = user_text.strip()

    mappings = [
        (["쿠폰", "카드"], "쿠폰/프로모션", "쿠폰 적용 가능 여부를 먼저 확인한 뒤 카드 결제를 진행합니다. 행사별 중복 적용 여부는 최신 프로모션 기준을 확인해주세요."),
        (["상품권"], "상품권", "상품권과 카드 복합결제 가능 여부를 먼저 확인해주세요. 잔액 처리 기준과 제외 브랜드 여부도 함께 확인해야 합니다."),
        (["환불"], "취소/환불", "원결제 수단 기준으로 환불을 진행합니다. 쿠폰 또는 프로모션 적용 건은 재계산 기준을 함께 확인해주세요."),
        (["취소"], "취소/환불", "취소는 원결제 수단 기준으로 처리합니다. 부분 취소 가능 여부를 먼저 확인해주세요."),
        (["오류"], "오류 대응", "오류 유형 확인 → 재시도 → 대체 결제수단 안내 → 관리자 문의 기준 순으로 대응합니다."),
        (["간편결제"], "결제", "간편결제 오류 발생 시 1차 재시도 후 대체 결제수단을 안내합니다. 반복 오류는 오류 대응 매뉴얼을 참고해주세요."),
    ]

    for keywords, menu, answer in mappings:
        if all(k in q for k in keywords):
            return f"[{menu}] {answer}"

    for menu_name, data in st.session_state.manuals.items():
        if menu_name in q or data["title"].replace(" 매뉴얼", "") in q:
            return f"[{menu_name}]\n{data['content'].strip()}"

    return "관련 매뉴얼을 찾지 못했습니다. 왼쪽 메뉴에서 카테고리를 선택하거나 질문을 더 구체적으로 입력해주세요."


def add_chat(role: str, text: str):
    st.session_state.chat_history.append((role, text))


# -----------------------------
# Header
# -----------------------------
st.title("💳 결제 서비스 개선을 위한 직원 지원형 AI 챗봇")
st.caption("질문형 인터페이스로 결제/쿠폰/상품권/환불/오류 대응 정보를 즉시 확인하는 Streamlit 데모")

col1, col2, col3, col4 = st.columns(4)
col1.metric("결제 VOC 감소 목표", KPI_TARGETS["결제 VOC 감소"])
col2.metric("응대 오류", KPI_TARGETS["응대 오류 감소"])
col3.metric("처리 시간", KPI_TARGETS["처리 시간 단축"])
col4.metric("직원 사용률", KPI_TARGETS["직원 사용률 증가"])

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.header("메뉴 구성")
    selected_menu = st.radio(
        "매뉴얼 선택",
        list(st.session_state.manuals.keys()),
        index=0,
        help="직접 매뉴얼을 탐색할 수 있습니다.",
    )

    st.markdown("---")
    st.subheader("자주 찾는 질문")
    quick_questions = [
        "쿠폰과 카드 복합결제 방법",
        "상품권과 카드 같이 사용 가능한가요?",
        "환불 처리 방법 알려줘",
        "간편결제 오류 시 어떻게 하나요?",
    ]
    for q in quick_questions:
        if st.button(q, use_container_width=True):
            add_chat("user", q)
            add_chat("assistant", find_answer(q))

    st.markdown("---")
    st.subheader("운영 포인트")
    st.write("- 프로모션 정보는 관리자 업데이트")
    st.write("- 매뉴얼은 메뉴 + 질문 방식 병행")
    st.write("- 교육만으로 해결이 어려운 구조 보완")


# -----------------------------
# Main layout tabs
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs(["챗봇", "매뉴얼", "프로모션", "관리자"])

with tab1:
    left, right = st.columns([1.2, 0.8])

    with left:
        st.subheader("챗봇 질의응답")
        chat_container = st.container(border=True)
        with chat_container:
            for role, msg in st.session_state.chat_history:
                with st.chat_message("assistant" if role == "assistant" else "user"):
                    st.write(msg)

        user_prompt = st.chat_input("예: 쿠폰과 카드 복합결제 방법")
        if user_prompt:
            add_chat("user", user_prompt)
            add_chat("assistant", find_answer(user_prompt))
            st.rerun()

    with right:
        st.subheader("선택된 매뉴얼 요약")
        manual = st.session_state.manuals[selected_menu]
        st.info(f"**{manual['title']}**")
        st.write(manual["content"])

        st.subheader("관련 FAQ")
        for q, a in manual["faq"]:
            with st.expander(q):
                st.write(a)

with tab2:
    st.subheader("매뉴얼 직접 탐색")
    c1, c2 = st.columns([0.9, 1.1])

    with c1:
        st.markdown("### 카테고리")
        for key in st.session_state.manuals.keys():
            st.write(f"- {key}")

    with c2:
        manual = st.session_state.manuals[selected_menu]
        st.markdown(f"### {manual['title']}")
        st.write(manual["content"])

        st.markdown("### 업무 흐름")
        st.code("질문 입력 → 즉시 답변 확인 → 추가 매뉴얼 확인", language=None)

with tab3:
    st.subheader("최신 프로모션 정보")
    st.caption("블로그/문서 기반 정보를 관리자 업데이트 방식으로 반영하는 예시")

    if st.session_state.promotions:
        for idx, promo in enumerate(st.session_state.promotions, start=1):
            with st.container(border=True):
                st.markdown(f"**{idx}. {promo['name']}**")
                st.write(f"- 기간: {promo['period']}")
                st.write(f"- 기준: {promo['rule']}")
                st.write(f"- 업데이트: {promo['updated_at']}")
    else:
        st.warning("등록된 프로모션이 없습니다.")

with tab4:
    st.subheader("관리자 업데이트 데모")
    st.caption("실제 운영 시 프로모션/매뉴얼을 주기적으로 업데이트하는 구조를 가정합니다.")

    with st.form("promo_form", clear_on_submit=True):
        st.markdown("#### 프로모션 추가")
        name = st.text_input("프로모션명")
        period = st.text_input("기간", placeholder="예: 4월 한정 / 매주 금~일")
        rule = st.text_area("적용 기준", placeholder="예: 지정 카드 결제 시 5% 할인")
        submitted = st.form_submit_button("추가")
        if submitted and name and period and rule:
            st.session_state.promotions.insert(
                0,
                {
                    "name": name,
                    "period": period,
                    "rule": rule,
                    "updated_at": datetime.now().strftime("%Y-%m-%d"),
                },
            )
            st.success("프로모션이 추가되었습니다.")

    st.markdown("---")
    st.markdown("#### 운영 리스크 및 대응")
    st.write("- 정보 오류 → 관리자 검수")
    st.write("- 사용 저조 → UX 개선 및 교육")
    st.write("- 데이터 업데이트 부담 → 관리자 운영 체계 구축")

st.markdown("---")
st.markdown(
    """
**기획 요약**  
- 결제 단계의 반복적 고객 불편을 해결하기 위해 직원의 정보 접근성을 강화합니다.  
- 블로그/매뉴얼 중심 정보를 질문 기반 구조로 전환합니다.  
- 메뉴형 탐색 + 챗봇형 질의응답 + 관리자 업데이트 구조를 함께 설계합니다.  
"""
)
