import streamlit as st

from ui.css import inject_home_css
from ui.components import render_sih_badge, render_feature_card, render_theme_toggle

inject_home_css(st.session_state.get("theme", "dark"))

_, toggle_col = st.columns([5, 1])
with toggle_col:
    render_theme_toggle()

render_sih_badge()

st.markdown(
    '<div class="hero-title">LUNARMATCH</div>'
    '<div class="hero-subtitle">Multi-Modal Lunar Image Correspondence &amp; Registration</div>'
    '<div class="hero-desc">'
    "Automatic image correspondence matching and registration between "
    "Chandrayaan-2 optical imagery (OHRC, TMC-2, IIRS) and LRO reference datasets."
    "</div>",
    unsafe_allow_html=True,
)

_, btn_left, btn_right, _ = st.columns([1.5, 1, 1, 1.5])
with btn_left:
    if st.button("Open Workspace  →", type="primary", use_container_width=True):
        st.switch_page("pages/workbench.py")
with btn_right:
    if st.button("View System Overview", use_container_width=True):
        st.session_state.current_step = "overview"
        st.switch_page("pages/workbench.py")

st.markdown("<br>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    render_feature_card(
        "Feature Detection",
        "IMPLEMENTED",
        "SIFT-based multi-scale keypoint extraction with configurable contrast and edge thresholds.",
        "OpenCV SIFT with Lowe's ratio-test filtering",
    )
with c2:
    render_feature_card(
        "Spatial Balancing",
        "IMPLEMENTED",
        "Grid-based correspondence distribution ensuring uniform coverage across the image.",
        "8×8 grid, quality-ranked selection per cell",
    )
with c3:
    render_feature_card(
        "Fail-Safe Pipeline",
        "IMPLEMENTED",
        "Multi-checkpoint verification with detailed failure diagnostics at every pipeline stage.",
        "Keypoint, match, RANSAC, and inlier checkpoints",
    )

st.markdown("<br>", unsafe_allow_html=True)

with st.container():
    st.markdown(
        '<div class="demo-box">'
        '<div class="demo-box-title">Quick Demo</div>'
        '<div class="demo-box-desc">'
        "Load a known-good lunar image pair and open the workspace to run the full registration pipeline."
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    if st.button("Load Example Pair & Open Workspace", use_container_width=True):
        st.session_state.load_examples = True
        st.session_state.current_step = "image_pair"
        st.switch_page("pages/workbench.py")

st.markdown(
    '<div class="footer-text">Team Spectrum &middot; Python &middot; OpenCV &middot; Streamlit</div>',
    unsafe_allow_html=True,
)
