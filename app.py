import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

st.set_page_config(
    page_title="LunarMatch",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="collapsed",
)

defaults = {
    "current_step": "overview",
    "ref_image_bytes": None,
    "mov_image_bytes": None,
    "ref_sensor": "OHRC",
    "mov_sensor": "OHRC",
    "images_loaded": False,
    "pipeline_result": None,
    "pipeline_status": "ready",
    "load_examples": False,
    "theme": "dark",
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

home = st.Page("pages/home.py", title="Home", icon="🌙", default=True, url_path="home")
workbench = st.Page("pages/workbench.py", title="Workbench", icon="🔬", url_path="workbench")

pg = st.navigation([home, workbench], position="hidden")
pg.run()
