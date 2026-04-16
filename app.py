import json
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="결제 도우미", page_icon="💳", layout="wide")

DATA_PATH = Path(__file__).parent / "knowledge_base.json"


def load_data():
    if DATA_PATH.exists():
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "notice": "공지 없음",
        "last_updated": "",
        "updated_by": "",
    }


data = load_data()

with st.sidebar:
    st.markdown("### 💳 결제 도우미")
    if st.button("🔐 관리자 페이지", use_container_width=True):
        st.switch_page("pages/1_admin.py")

st.title("🏠 홈페이지")
st.write("여기는 홈페이지입니다.")

st.subheader("현재 공지")
st.info(data.get("notice", "공지 없음"))

col1, col2 = st.columns(2)
col1.metric("최근 수정자", data.get("updated_by", "-") or "-")
col2.metric("최근 수정일", data.get("last_updated", "-") or "-")
