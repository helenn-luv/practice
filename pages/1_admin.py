import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path

st.set_page_config(
    page_title="관리자 페이지",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── 상수 & 공통 함수 ──────────────────────────────────────────
KB_PATH = Path(__file__).parent.parent / "knowledge_base.json"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin1234")  # 환경변수로 변경 권장

def load_kb() -> dict:
    if KB_PATH.exists():
        with open(KB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"manual": {}, "promotions": [], "last_updated": "", "updated_by": ""}

def save_kb(kb: dict, admin_name: str):
    kb["last_updated"] = datetime.now().isoformat()
    kb["updated_by"] = admin_name
    with open(KB_PATH, "w", encoding="utf-8") as f:
        json.dump(kb, f, ensure_ascii=False, indent=2)

# ─── 스타일 ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.stApp { background: linear-gradient(135deg, #0f172a 0%, #1a2332 50%, #0f172a 100%); }
section[data-testid="stSidebar"] {
    background: rgba(15,23,42,0.95) !important;
    border-right: 1px solid rgba(245,158,11,0.2);
}
.admin-header {
    background: linear-gradient(135deg, rgba(30,41,59,0.95), rgba(15,23,42,0.95));
    border: 1px solid rgba(245,158,11,0.4);
    border-radius: 16px; padding: 24px 32px; margin-bottom: 24px;
    box-shadow: 0 4px 32px rgba(0,0,0,0.4), 0 0 0 1px rgba(245,158,11,0.1);
}
.admin-header h1 { color: #fef3c7; font-size: 1.7rem; font-weight: 700; margin: 0; }
.admin-header p  { color: #92400e; font-size: 0.88rem; margin: 6px 0 0 0; }
.section-card {
    background: rgba(30,41,59,0.8);
    border: 1px solid rgba(245,158,11,0.2);
    border-radius: 14px; padding: 20px 24px; margin-bottom: 16px;
}
.section-title {
    color: #fbbf24; font-size: 1rem; font-weight: 600;
    margin-bottom: 12px; display: flex; align-items: center; gap: 8px;
}
.promo-card {
    background: rgba(15,23,42,0.7);
    border: 1px solid rgba(245,158,11,0.15);
    border-radius: 10px; padding: 14px 16px; margin-bottom: 10px;
}
.promo-title { color: #e2e8f0; font-weight: 600; font-size: 0.95rem; }
.promo-meta  { color: #64748b; font-size: 0.8rem; margin-top: 4px; }
.active-badge {
    display: inline-block; background: rgba(16,185,129,0.15);
    border: 1px solid rgba(16,185,129,0.4); color: #6ee7b7;
    border-radius: 20px; padding: 2px 8px; font-size: 0.72rem; font-weight: 600;
}
.inactive-badge {
    display: inline-block; background: rgba(100,116,139,0.15);
    border: 1px solid rgba(100,116,139,0.4); color: #94a3b8;
    border-radius: 20px; padding: 2px 8px; font-size: 0.72rem; font-weight: 600;
}
.admin-badge {
    display: inline-block; background: rgba(245,158,11,0.15);
    border: 1px solid rgba(245,158,11,0.4); color: #fbbf24;
    border-radius: 20px; padding: 3px 10px; font-size: 0.75rem; font-weight: 500;
}
.login-box {
    max-width: 400px; margin: 80px auto;
    background: rgba(30,41,59,0.9); border: 1px solid rgba(245,158,11,0.3);
    border-radius: 20px; padding: 40px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.4);
}
.divider { border: none; border-top: 1px solid rgba(245,158,11,0.1); margin: 16px 0; }
.stTextInput > div > div > input {
    background: rgba(15,23,42,0.9) !important; color: #e2e8f0 !important;
    border: 1px solid rgba(245,158,11,0.3) !important; border-radius: 10px !important;
}
.stTextArea > div > div > textarea {
    background: rgba(15,23,42,0.9) !important; color: #e2e8f0 !important;
    border: 1px solid rgba(245,158,11,0.2) !important; border-radius: 10px !important;
    font-size: 0.88rem !important;
}
.stButton > button {
    background: linear-gradient(135deg, #d97706, #f59e0b) !important;
    color: #1a1a1a !important; border: none !important;
    border-radius: 10px !important; font-weight: 700 !important;
}
.stButton > button:hover { box-shadow: 0 4px 16px rgba(245,158,11,0.4) !important; }
div[data-testid="stSelectbox"] > div > div {
    background: rgba(15,23,42,0.9) !important;
    border: 1px solid rgba(245,158,11,0.3) !important;
    border-radius: 10px !important; color: #e2e8f0 !important;
}
</style>
""", unsafe_allow_html=True)

# ─── 로그인 상태 관리 ────────────────────────────────────────────
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "admin_name" not in st.session_state:
    st.session_state.admin_name = ""

# ─── 로그인 화면 ─────────────────────────────────────────────────
if not st.session_state.admin_logged_in:
    st.markdown("""
    <div class="login-box">
        <h2 style="color:#fbbf24;text-align:center;margin-bottom:8px;">🔧 관리자 로그인</h2>
        <p style="color:#64748b;text-align:center;font-size:0.85rem;margin-bottom:24px;">
            매뉴얼 및 프로모션 관리 페이지
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        st.markdown("**관리자 이름**")
        name_input = st.text_input("이름", placeholder="홍길동", label_visibility="collapsed")
        st.markdown("**비밀번호**")
        pw_input = st.text_input("비밀번호", type="password", placeholder="관리자 비밀번호 입력", label_visibility="collapsed")
        if st.button("로그인", use_container_width=True):
            if pw_input == ADMIN_PASSWORD and name_input.strip():
                st.session_state.admin_logged_in = True
                st.session_state.admin_name = name_input.strip()
                st.rerun()
            elif not name_input.strip():
                st.error("이름을 입력해주세요.")
            else:
                st.error("비밀번호가 올바르지 않습니다.")
    st.stop()

# ─── 사이드바 (로그인 후) ────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔧 관리자 메뉴")
    st.markdown(f'<span class="admin-badge">👤 {st.session_state.admin_name}</span>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    kb = load_kb()
    last_upd = kb.get("last_updated", "")
    updated_by = kb.get("updated_by", "")
    if last_upd:
        st.markdown(f"""
        <div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);
                    border-radius:10px;padding:12px;font-size:0.8rem;">
            <div style="color:#fbbf24;font-weight:600;">최근 업데이트</div>
            <div style="color:#94a3b8;margin-top:4px;">{last_upd[:16].replace("T"," ")}</div>
            <div style="color:#94a3b8;">담당: {updated_by}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    active_count = len([p for p in kb.get("promotions", []) if p.get("active")])
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;padding:6px 0;
                border-bottom:1px solid rgba(245,158,11,0.1);color:#94a3b8;font-size:0.82rem;">
        <span>활성 프로모션</span><span style="color:#fbbf24;font-weight:600;">{active_count}개</span>
    </div>
    <div style="display:flex;justify-content:space-between;padding:6px 0;color:#94a3b8;font-size:0.82rem;">
        <span>매뉴얼 섹션</span><span style="color:#fbbf24;font-weight:600;">{len(kb.get("manual", {}))}개</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    if st.button("🚪 로그아웃", use_container_width=True):
        st.session_state.admin_logged_in = False
        st.session_state.admin_name = ""
        st.rerun()

# ─── 메인 관리 화면 ──────────────────────────────────────────────
st.markdown(f"""
<div class="admin-header">
    <h1>🔧 지식베이스 관리자 페이지</h1>
    <p>매뉴얼 및 프로모션 정보를 수정하면 챗봇에 즉시 반영됩니다 — 담당자: {st.session_state.admin_name}</p>
</div>
""", unsafe_allow_html=True)

kb = load_kb()
tab1, tab2 = st.tabs(["📋 매뉴얼 관리", "🎁 프로모션 관리"])

# ══════════════════════════════════════════════════════
# TAB 1 : 매뉴얼 관리
# ══════════════════════════════════════════════════════
with tab1:
    st.markdown("### 📋 결제 매뉴얼 섹션 관리")
    st.caption("각 섹션의 항목을 수정하면 챗봇 답변에 즉시 반영됩니다. 항목은 한 줄에 하나씩 입력하세요.")

    manual = kb.get("manual", {})
    updated_manual = {}
    changed = False

    # 기존 섹션 편집
    for section_name, items in manual.items():
        with st.expander(f"📌 {section_name}", expanded=True):
            col_title, col_del = st.columns([5, 1])
            with col_title:
                new_section_name = st.text_input(
                    "섹션명", value=section_name,
                    key=f"sec_name_{section_name}", label_visibility="collapsed"
                )
            with col_del:
                delete_section = st.button("🗑 삭제", key=f"del_sec_{section_name}")

            if delete_section:
                changed = True
                continue  # 이 섹션을 결과에 포함하지 않음

            items_text = st.text_area(
                "항목 (한 줄에 하나씩)",
                value="\n".join(items),
                height=160,
                key=f"items_{section_name}",
                label_visibility="collapsed",
                placeholder="항목을 한 줄에 하나씩 입력하세요..."
            )
            new_items = [line.strip() for line in items_text.split("\n") if line.strip()]
            updated_manual[new_section_name] = new_items

            if new_section_name != section_name or new_items != items:
                changed = True

    # 새 섹션 추가
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("#### ➕ 새 섹션 추가")
    col_new1, col_new2 = st.columns([2, 1])
    with col_new1:
        new_sec = st.text_input("새 섹션 이름", placeholder="예: 포인트 결제", key="new_section_name")
    with col_new2:
        if st.button("섹션 추가", use_container_width=True) and new_sec.strip():
            if new_sec.strip() not in updated_manual:
                updated_manual[new_sec.strip()] = ["새 항목을 입력하세요"]
                kb["manual"] = updated_manual
                save_kb(kb, st.session_state.admin_name)
                st.success(f"'{new_sec}' 섹션이 추가되었습니다.")
                st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    if st.button("💾 매뉴얼 저장", use_container_width=True):
        kb["manual"] = updated_manual
        save_kb(kb, st.session_state.admin_name)
        st.success("✅ 매뉴얼이 저장되었습니다. 챗봇에 즉시 반영됩니다.")
        st.rerun()

# ══════════════════════════════════════════════════════
# TAB 2 : 프로모션 관리
# ══════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🎁 프로모션 관리")
    st.caption("프로모션을 추가·수정·삭제하거나 활성/비활성 상태를 변경하세요.")

    promotions = kb.get("promotions", [])

    # 기존 프로모션 편집
    updated_promos = []
    for i, promo in enumerate(promotions):
        badge = '<span class="active-badge">● 활성</span>' if promo.get("active") else '<span class="inactive-badge">○ 비활성</span>'
        with st.expander(f"{badge} &nbsp; {promo['title']}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                new_title = st.text_input("프로모션명", value=promo["title"], key=f"p_title_{i}")
                new_desc  = st.text_area("내용 설명", value=promo["description"], height=90, key=f"p_desc_{i}")
            with col2:
                new_cond   = st.text_input("적용 조건", value=promo["condition"], key=f"p_cond_{i}")
                new_period = st.text_input("기간", value=promo["period"], key=f"p_period_{i}",
                                           placeholder="예: 2025-06-01 ~ 2025-06-30")
                new_active = st.toggle("활성화", value=promo.get("active", True), key=f"p_active_{i}")

            col_save, col_del = st.columns([3, 1])
            with col_del:
                delete_promo = st.button("🗑 삭제", key=f"del_promo_{i}", use_container_width=True)

            if not delete_promo:
                updated_promos.append({
                    "id": promo["id"],
                    "title": new_title,
                    "description": new_desc,
                    "condition": new_cond,
                    "period": new_period,
                    "active": new_active,
                })

    # 새 프로모션 추가
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("#### ➕ 새 프로모션 추가")
    with st.form("new_promo_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            np_title  = st.text_input("프로모션명 *", placeholder="예: 여름 특별 할인")
            np_desc   = st.text_area("내용 설명 *", height=90, placeholder="프로모션 내용을 입력하세요")
        with col2:
            np_cond   = st.text_input("적용 조건 *", placeholder="예: 5만원 이상 결제 시")
            np_period = st.text_input("기간 *", placeholder="예: 2025-07-01 ~ 2025-07-31")
            np_active = st.toggle("즉시 활성화", value=True)

        submitted = st.form_submit_button("➕ 프로모션 추가", use_container_width=True)
        if submitted:
            if np_title.strip() and np_desc.strip() and np_cond.strip() and np_period.strip():
                new_id = max([p["id"] for p in promotions], default=0) + 1
                updated_promos.append({
                    "id": new_id,
                    "title": np_title.strip(),
                    "description": np_desc.strip(),
                    "condition": np_cond.strip(),
                    "period": np_period.strip(),
                    "active": np_active,
                })
                kb["promotions"] = updated_promos
                save_kb(kb, st.session_state.admin_name)
                st.success(f"✅ '{np_title}' 프로모션이 추가되었습니다.")
                st.rerun()
            else:
                st.warning("모든 필드(*)를 입력해주세요.")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    if st.button("💾 프로모션 저장", use_container_width=True):
        kb["promotions"] = updated_promos
        save_kb(kb, st.session_state.admin_name)
        st.success("✅ 프로모션 정보가 저장되었습니다. 챗봇에 즉시 반영됩니다.")
        st.rerun()
