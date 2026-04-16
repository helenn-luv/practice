import streamlit as st
import anthropic
import json
import os
from datetime import datetime
from pathlib import Path

# ─── 페이지 설정 ───────────────────────────────────────────────
st.set_page_config(
    page_title="결제 도우미 챗봇",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── 공통 함수 ────────────────────────────────────────────────
KB_PATH = Path(__file__).parent / "knowledge_base.json"

def load_kb() -> dict:
    if KB_PATH.exists():
        with open(KB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"manual": {}, "promotions": [], "last_updated": "", "updated_by": ""}

def build_system_prompt(kb: dict) -> str:
    manual_text = ""
    for section, items in kb.get("manual", {}).items():
        manual_text += f"\n### {section}\n"
        for item in items:
            manual_text += f"- {item}\n"

    promo_text = ""
    active_promos = [p for p in kb.get("promotions", []) if p.get("active")]
    if active_promos:
        for p in active_promos:
            promo_text += f"\n**{p['title']}**\n"
            promo_text += f"- 내용: {p['description']}\n"
            promo_text += f"- 조건: {p['condition']}\n"
            promo_text += f"- 기간: {p['period']}\n"
    else:
        promo_text = "\n- 현재 진행 중인 프로모션이 없습니다.\n"

    last_updated = kb.get("last_updated", "")
    updated_by = kb.get("updated_by", "")
    update_note = f"(최종 업데이트: {last_updated[:10] if last_updated else '미상'}, 담당: {updated_by})" if last_updated else ""

    return f"""당신은 결제 서비스 전문 AI 어시스턴트입니다. 매장 직원들이 결제 업무를 정확하고 신속하게 처리할 수 있도록 돕습니다.

## 역할
- 결제 프로세스, 쿠폰/상품권 처리, 환불, 오류 대응에 대한 즉각적인 안내 제공
- 명확하고 단계별로 구조화된 답변 제공
- 불확실한 경우 관리자 확인을 권장

## 지식 베이스 (관리자 업데이트 내용) {update_note}
{manual_text}

## 현재 프로모션 정보
{promo_text}

## 답변 원칙
1. 단계별 번호 목록으로 명확하게 안내
2. 불확실한 정보는 추측하지 않고 관리자 확인 권장
3. 긴급 상황(고객 불만, 시스템 오류)은 즉시 관리자 에스컬레이션 안내
4. 한국어로 답변, 전문 용어는 쉽게 풀어서 설명"""

# ─── 스타일 ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%); }
section[data-testid="stSidebar"] {
    background: rgba(15,23,42,0.95) !important;
    border-right: 1px solid rgba(99,179,237,0.2);
}
.main-header {
    background: linear-gradient(135deg, rgba(30,41,59,0.9), rgba(15,23,42,0.9));
    border: 1px solid rgba(99,179,237,0.3);
    border-radius: 16px; padding: 24px 32px; margin-bottom: 24px;
    box-shadow: 0 4px 32px rgba(0,0,0,0.3);
}
.main-header h1 { color: #e2e8f0; font-size: 1.8rem; font-weight: 700; margin: 0; letter-spacing: -0.5px; }
.main-header p  { color: #94a3b8; font-size: 0.9rem; margin: 6px 0 0 0; }
.msg-user {
    background: linear-gradient(135deg, #1d4ed8, #2563eb); color: white;
    border-radius: 16px 16px 4px 16px; padding: 14px 18px; margin: 8px 0 8px 60px;
    font-size: 0.92rem; line-height: 1.6; box-shadow: 0 2px 12px rgba(37,99,235,0.3);
}
.msg-assistant {
    background: rgba(30,41,59,0.9); border: 1px solid rgba(99,179,237,0.2); color: #e2e8f0;
    border-radius: 16px 16px 16px 4px; padding: 14px 18px; margin: 8px 60px 8px 0;
    font-size: 0.92rem; line-height: 1.7; box-shadow: 0 2px 12px rgba(0,0,0,0.2);
}
.msg-label { font-size: 0.75rem; color: #64748b; margin-bottom: 4px; font-weight: 500; }
.kpi-card {
    background: rgba(30,41,59,0.8); border: 1px solid rgba(99,179,237,0.2);
    border-radius: 12px; padding: 16px; text-align: center; margin-bottom: 8px;
}
.kpi-value { font-size: 1.4rem; font-weight: 700; color: #63b3ed; }
.kpi-label { font-size: 0.78rem; color: #94a3b8; margin-top: 4px; }
.status-badge {
    display: inline-block; background: rgba(16,185,129,0.15);
    border: 1px solid rgba(16,185,129,0.4); color: #6ee7b7;
    border-radius: 20px; padding: 3px 10px; font-size: 0.75rem; font-weight: 500;
}
.update-badge {
    display: inline-block; background: rgba(251,191,36,0.15);
    border: 1px solid rgba(251,191,36,0.4); color: #fbbf24;
    border-radius: 20px; padding: 3px 10px; font-size: 0.72rem; font-weight: 500; margin-left: 6px;
}
.divider { border: none; border-top: 1px solid rgba(99,179,237,0.1); margin: 16px 0; }
.cat-btn {
    display: inline-block; background: rgba(30,41,59,0.8);
    border: 1px solid rgba(99,179,237,0.25); border-radius: 10px;
    padding: 10px 14px; margin: 4px; color: #cbd5e1; font-size: 0.85rem; text-align: center;
}
.stTextInput > div > div > input {
    background: rgba(30,41,59,0.9) !important; color: #e2e8f0 !important;
    border: 1px solid rgba(99,179,237,0.3) !important; border-radius: 12px !important;
}
.stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; font-weight: 500 !important;
}
</style>
""", unsafe_allow_html=True)

# ─── 빠른 질문 목록 ─────────────────────────────────────────────
QUICK_QUESTIONS = {
    "💳 결제": ["카드 결제 절차를 알려주세요", "모바일 결제는 어떻게 처리하나요?", "복합 결제 방법이 궁금해요"],
    "🎟 쿠폰/상품권": ["쿠폰 적용 방법을 알려주세요", "상품권 잔액은 어떻게 확인하나요?", "쿠폰 오류가 발생했어요"],
    "🔄 환불": ["당일 환불 처리 방법", "카드 부분 환불은 어떻게 하나요?", "현금 환불 절차를 알려주세요"],
    "⚠️ 오류": ["카드가 승인 거절됐어요", "단말기가 응답하지 않아요", "영수증이 출력되지 않아요"],
    "🎁 프로모션": ["현재 진행 중인 프로모션을 알려주세요", "할인 쿠폰 적용 조건이 뭔가요?"],
}

# ─── 세션 상태 초기화 ────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0
if "session_start" not in st.session_state:
    st.session_state.session_start = datetime.now()

kb = load_kb()
system_prompt = build_system_prompt(kb)

# ─── 사이드바 ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 💳 결제 도우미")
    if st.button("🔐 관리자 페이지"):
    st.switch_page("pages/1_관리자.py")
    last_upd = kb.get("last_updated", "")
    if last_upd:
        st.markdown(f'<span class="status-badge">● 온라인</span><span class="update-badge">📝 {last_upd[:10]} 업데이트</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge">● 온라인</span>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{st.session_state.total_queries}</div><div class="kpi-label">총 질문</div></div>', unsafe_allow_html=True)
    with col2:
        elapsed = int((datetime.now() - st.session_state.session_start).total_seconds() / 60)
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{elapsed}분</div><div class="kpi-label">사용 시간</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("**⚡ 빠른 질문**")
    for category, questions in QUICK_QUESTIONS.items():
        with st.expander(category, expanded=False):
            for q in questions:
                if st.button(q, key=f"quick_{q}", use_container_width=True):
                    st.session_state["pending_question"] = q

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    active_count = len([p for p in kb.get("promotions", []) if p.get("active")])
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid rgba(99,179,237,0.1);color:#94a3b8;font-size:0.82rem;">
        <span>활성 프로모션</span><span style="color:#63b3ed;font-weight:600;">{active_count}개</span>
    </div>
    <div style="display:flex;justify-content:space-between;padding:6px 0;color:#94a3b8;font-size:0.82rem;">
        <span>매뉴얼 섹션</span><span style="color:#63b3ed;font-weight:600;">{len(kb.get("manual", {}))}개</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    if st.button("🗑 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_queries = 0
        st.session_state.session_start = datetime.now()
        st.rerun()

# ─── 메인 영역 ──────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>💳 결제 서비스 직원 지원 AI</h1>
    <p>결제 · 쿠폰 · 환불 · 오류 대응 · 프로모션 — 무엇이든 물어보세요</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("#### 👋 오늘 어떤 도움이 필요하신가요?")
    cols = st.columns(len(QUICK_QUESTIONS))
    for i, (cat, _) in enumerate(QUICK_QUESTIONS.items()):
        with cols[i]:
            st.markdown(f'<div class="cat-btn">{cat}</div>', unsafe_allow_html=True)
    st.markdown("---")

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-label" style="text-align:right;">직원</div><div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-label">🤖 AI 도우미</div><div class="msg-assistant">{msg["content"]}</div>', unsafe_allow_html=True)

# ─── 입력 영역 ──────────────────────────────────────────────────
st.markdown("---")
pending = st.session_state.pop("pending_question", None)

col_input, col_btn = st.columns([5, 1])
with col_input:
    user_input = st.text_input(
        "질문",
        value=pending or "",
        placeholder="예: 카드 승인 거절 시 어떻게 해야 하나요?",
        label_visibility="collapsed",
        key="chat_input",
    )
with col_btn:
    send = st.button("전송 →", use_container_width=True)

def get_ai_response(messages, sys_prompt):
    client = anthropic.Anthropic()
    api_messages = [{"role": m["role"], "content": m["content"]} for m in messages]
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=sys_prompt,
        messages=api_messages,
    )
    return response.content[0].text

if (send or pending) and user_input.strip():
    question = user_input.strip()
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.total_queries += 1
    with st.spinner("답변을 생성하는 중..."):
        try:
            answer = get_ai_response(st.session_state.messages, system_prompt)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")
    st.rerun()
    
