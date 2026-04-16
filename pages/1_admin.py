import json
import os
from datetime import datetime
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="관리자 페이지", page_icon="🔧", layout="wide")

DATA_PATH = Path(__file__).parent.parent / "knowledge_base.json"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin1234")


def load_data():
    if DATA_PATH.exists():
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "notice": "공지 없음",
        "last_updated": "",
        "updated_by": "",
    }


def save_data(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if "admin_name" not in st.session_state:
    st.session_state.admin_name = ""

st.title("🔐 관리자 페이지")

if not st.session_state.admin_logged_in:
    admin_name = st.text_input("이름")
    password = st.text_input("비밀번호", type="password")

    if st.button("로그인", use_container_width=True):
        if admin_name.strip() and password == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.session_state.admin_name = admin_name.strip()
            st.rerun()
        elif not admin_name.strip():
            st.error("이름을 입력하세요.")
        else:
            st.error("비밀번호가 올바르지 않습니다.")
    st.stop()

st.success(f"{st.session_state.admin_name} 님 로그인됨")

data = load_data()
notice = st.text_area("홈페이지에 보여줄 공지", value=data.get("notice", ""), height=200)

col1, col2 = st.columns(2)

with col1:
    if st.button("저장", use_container_width=True):
        data["notice"] = notice
        data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        data["updated_by"] = st.session_state.admin_name
        save_data(data)
        st.success("저장되었습니다.")

with col2:
    if st.button("홈으로 이동", use_container_width=True):
        st.switch_page("app.py")

st.divider()
st.write("기본 관리자 비밀번호: `admin1234`")
