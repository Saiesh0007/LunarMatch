import os
import tempfile

import cv2
import numpy as np
import streamlit as st

from ui.css import inject_workbench_css
from ui.components import (
    render_feature_card,
    render_metric_cards,
    render_pipeline_checklist,
    render_status_indicator,
    render_system_info_table,
    render_theme_toggle,
)
from src.pipeline import run_pipeline, DEFAULT_CONFIG
from src.metrics import format_metrics

EXAMPLE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "examples")
REF_EXAMPLE = os.path.join(EXAMPLE_DIR, "ref_sample.png")
MOV_EXAMPLE = os.path.join(EXAMPLE_DIR, "mov_sample.png")

inject_workbench_css(st.session_state.get("theme", "dark"))

# ── Sidebar ──────────────────────────────────────────────────────────────────

st.sidebar.markdown('<div class="sidebar-logo">LUNARMATCH</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-subtitle">SIH Problem #26166</div>', unsafe_allow_html=True)

with st.sidebar:
    render_theme_toggle()

render_status_indicator(st.session_state.pipeline_status)

st.sidebar.markdown('<div class="sidebar-section">Workflow Steps</div>', unsafe_allow_html=True)

STEPS = [
    ("overview", "Overview", False),
    ("image_pair", "1. Image Pair", False),
    ("run_pipeline", "2. Run Pipeline", False),
    ("correspondences", "3. Correspondences", True),
    ("registration", "4. Registration", True),
    ("metrics", "5. Metrics", True),
]

has_results = st.session_state.pipeline_status == "success"

for step_key, label, needs_results in STEPS:
    disabled = needs_results and not has_results
    btn_type = "primary" if st.session_state.current_step == step_key else "secondary"
    if st.sidebar.button(
        label,
        key=f"nav_{step_key}",
        type=btn_type,
        use_container_width=True,
        disabled=disabled,
    ):
        st.session_state.current_step = step_key
        st.rerun()

st.sidebar.divider()
if st.sidebar.button("← Back to Home", use_container_width=True):
    st.switch_page("pages/home.py")


# ── Auto-load examples ───────────────────────────────────────────────────────

if st.session_state.load_examples:
    if os.path.isfile(REF_EXAMPLE) and os.path.isfile(MOV_EXAMPLE):
        with open(REF_EXAMPLE, "rb") as f:
            st.session_state.ref_image_bytes = f.read()
        with open(MOV_EXAMPLE, "rb") as f:
            st.session_state.mov_image_bytes = f.read()
        st.session_state.images_loaded = True
        st.session_state.ref_sensor = "OHRC"
        st.session_state.mov_sensor = "TMC"
    st.session_state.load_examples = False


# ── Helper ────────────────────────────────────────────────────────────────────

def _display_image(img, caption=None):
    if img is None:
        return
    display = img
    if display.ndim == 2:
        display = cv2.cvtColor(display, cv2.COLOR_GRAY2RGB)
    elif display.shape[2] == 3:
        display = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
    st.image(display, caption=caption, use_container_width=True)


# ── Step: Overview ────────────────────────────────────────────────────────────

if st.session_state.current_step == "overview":
    st.markdown('<div class="page-header">Dashboard Overview</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subheader">LunarMatch Registration Workbench</div>',
        unsafe_allow_html=True,
    )

    render_system_info_table(st.session_state.pipeline_status)

    st.markdown("<br>", unsafe_allow_html=True)

    col_wf, col_cap = st.columns(2)

    with col_wf:
        st.markdown('<div class="section-title">Processing Workflow</div>', unsafe_allow_html=True)
        steps_html = [
            '<span class="workflow-num">1.</span> <b>Image Ingestion:</b> Load reference &amp; target rasters',
            '<span class="workflow-num">2.</span> <b>Preprocessing:</b> Normalize, CLAHE, denoise',
            '<span class="workflow-num">3.</span> <b>Feature Extraction:</b> SIFT keypoint detection',
            '<span class="workflow-num">4.</span> <b>Descriptor Matching:</b> BF/FLANN + ratio test',
            '<span class="workflow-num">5.</span> <b>Geometric Verification:</b> RANSAC outlier rejection',
            '<span class="workflow-num">6.</span> <b>Spatial Balancing:</b> Grid-based selection',
            '<span class="workflow-num">7.</span> <b>Registration:</b> Affine / Homography warp',
            '<span class="workflow-num">8.</span> <b>Evaluation:</b> RMSE, inlier ratio, coverage',
        ]
        st.markdown("<br>".join(steps_html), unsafe_allow_html=True)

    with col_cap:
        st.markdown('<div class="section-title">Core Capabilities</div>', unsafe_allow_html=True)
        st.markdown(
            "**Multi-Sensor Input**<br>"
            "Handles Chandrayaan-2 OHRC, TMC, TMC-2, IIRS and LRO NAC imagery.<br><br>"
            "**Geometric Verification**<br>"
            "RANSAC-based affine and homography estimation with configurable threshold.<br><br>"
            "**Spatial Coverage**<br>"
            "Grid-based spatial balancing ensures correspondences are uniformly distributed.",
            unsafe_allow_html=True,
        )


# ── Step: Image Pair ──────────────────────────────────────────────────────────

elif st.session_state.current_step == "image_pair":
    st.markdown('<div class="page-header">Image Pair</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subheader">Upload reference and moving images for registration</div>',
        unsafe_allow_html=True,
    )

    col_ref, col_mov = st.columns(2)

    with col_ref:
        st.markdown("**Reference Image**")
        ref_file = st.file_uploader(
            "Upload reference",
            type=["png", "jpg", "jpeg", "tif", "tiff"],
            key="ref_uploader",
            label_visibility="collapsed",
        )
        st.session_state.ref_sensor = st.selectbox(
            "Reference sensor",
            ["OHRC", "TMC", "TMC-2", "IIRS", "LRO NAC", "SELENE", "Other"],
            index=["OHRC", "TMC", "TMC-2", "IIRS", "LRO NAC", "SELENE", "Other"].index(
                st.session_state.ref_sensor
            ),
            key="ref_sensor_sel",
        )
        if ref_file is not None:
            st.session_state.ref_image_bytes = ref_file.getvalue()
            st.session_state.images_loaded = st.session_state.mov_image_bytes is not None

        if st.session_state.ref_image_bytes:
            ref_arr = cv2.imdecode(
                np.frombuffer(st.session_state.ref_image_bytes, np.uint8),
                cv2.IMREAD_UNCHANGED,
            )
            if ref_arr is not None:
                _display_image(ref_arr, f"Reference ({ref_arr.shape[1]}×{ref_arr.shape[0]})")

    with col_mov:
        st.markdown("**Moving Image**")
        mov_file = st.file_uploader(
            "Upload moving",
            type=["png", "jpg", "jpeg", "tif", "tiff"],
            key="mov_uploader",
            label_visibility="collapsed",
        )
        st.session_state.mov_sensor = st.selectbox(
            "Moving sensor",
            ["OHRC", "TMC", "TMC-2", "IIRS", "LRO NAC", "SELENE", "Other"],
            index=["OHRC", "TMC", "TMC-2", "IIRS", "LRO NAC", "SELENE", "Other"].index(
                st.session_state.mov_sensor
            ),
            key="mov_sensor_sel",
        )
        if mov_file is not None:
            st.session_state.mov_image_bytes = mov_file.getvalue()
            st.session_state.images_loaded = st.session_state.ref_image_bytes is not None

        if st.session_state.mov_image_bytes:
            mov_arr = cv2.imdecode(
                np.frombuffer(st.session_state.mov_image_bytes, np.uint8),
                cv2.IMREAD_UNCHANGED,
            )
            if mov_arr is not None:
                _display_image(mov_arr, f"Moving ({mov_arr.shape[1]}×{mov_arr.shape[0]})")

    st.divider()

    if st.button("Load Example Pair", use_container_width=True):
        if os.path.isfile(REF_EXAMPLE) and os.path.isfile(MOV_EXAMPLE):
            with open(REF_EXAMPLE, "rb") as f:
                st.session_state.ref_image_bytes = f.read()
            with open(MOV_EXAMPLE, "rb") as f:
                st.session_state.mov_image_bytes = f.read()
            st.session_state.images_loaded = True
            st.session_state.ref_sensor = "OHRC"
            st.session_state.mov_sensor = "TMC"
            st.rerun()
        else:
            st.warning("Example images not found in data/examples/")


# ── Step: Run Pipeline ────────────────────────────────────────────────────────

elif st.session_state.current_step == "run_pipeline":
    st.markdown('<div class="page-header">Run Pipeline</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subheader">Configure parameters and execute the registration pipeline</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.images_loaded:
        st.warning("Upload or load images in Step 1 first.")
    else:
        with st.expander("Pipeline Configuration", expanded=True):
            cfg1, cfg2 = st.columns(2)
            with cfg1:
                st.markdown("**Preprocessing**")
                preprocess_normalize = st.checkbox("Normalize intensity", value=True, key="cfg_norm")
                preprocess_clahe = st.checkbox("Contrast enhancement (CLAHE)", value=True, key="cfg_clahe")
                preprocess_denoise = st.checkbox("Denoise", value=False, key="cfg_denoise")

            with cfg2:
                st.markdown("**Geometry & Matching**")
                geo_model = st.radio(
                    "Geometric model", ["affine", "homography"], key="cfg_geo", horizontal=True
                )
                spatial_enabled = st.checkbox("Spatial balancing", value=True, key="cfg_spatial")
                ratio_thresh = st.slider(
                    "Ratio test threshold", 0.50, 0.95, 0.75, 0.05, key="cfg_ratio"
                )

        if st.button("Run Pipeline", type="primary", use_container_width=True):
            with tempfile.TemporaryDirectory() as tmpdir:
                ref_path = os.path.join(tmpdir, "ref.png")
                mov_path = os.path.join(tmpdir, "mov.png")
                with open(ref_path, "wb") as f:
                    f.write(st.session_state.ref_image_bytes)
                with open(mov_path, "wb") as f:
                    f.write(st.session_state.mov_image_bytes)

                config = {
                    "preprocessing": {
                        "grayscale": True,
                        "normalize": preprocess_normalize,
                        "clahe": preprocess_clahe,
                        "denoise": preprocess_denoise,
                    },
                    "feature": {"method": "sift"},
                    "matching": {"method": "bf", "ratio_thresh": ratio_thresh},
                    "geometry": {"model": geo_model, "ransac_thresh": 5.0},
                    "spatial": {"enabled": spatial_enabled, "grid_size": 8, "max_per_cell": 5},
                }

                with st.spinner("Running LunarMatch pipeline..."):
                    result = run_pipeline(ref_path, mov_path, config)

                st.session_state.pipeline_result = result
                st.session_state.pipeline_status = result["status"]
                st.rerun()

        result = st.session_state.pipeline_result
        if result is not None:
            if result["status"] == "success":
                st.success("Pipeline completed successfully.")
            else:
                st.error(f"Pipeline failed: {result.get('reason', 'Unknown error')}")
                st.info(
                    "Try another image pair, enable stronger preprocessing, "
                    "or adjust the ratio threshold."
                )

            st.markdown("**Pipeline Stages**")
            render_pipeline_checklist(result)


# ── Step: Correspondences ─────────────────────────────────────────────────────

elif st.session_state.current_step == "correspondences":
    st.markdown('<div class="page-header">Correspondences</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subheader">Keypoint detection and feature matching results</div>',
        unsafe_allow_html=True,
    )

    result = st.session_state.pipeline_result
    if result is None or result["status"] != "success":
        st.info("Run the pipeline in Step 2 to see correspondence results.")
    else:
        st.markdown("**Keypoints**")
        c1, c2 = st.columns(2)
        ref_kp_img = cv2.drawKeypoints(
            result["ref_processed"],
            result["kp_ref"],
            None,
            color=(0, 255, 0),
            flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
        )
        mov_kp_img = cv2.drawKeypoints(
            result["mov_processed"],
            result["kp_mov"],
            None,
            color=(0, 255, 0),
            flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
        )
        with c1:
            _display_image(ref_kp_img, f"Reference — {len(result['kp_ref'])} keypoints")
        with c2:
            _display_image(mov_kp_img, f"Moving — {len(result['kp_mov'])} keypoints")

        st.divider()
        st.markdown("**All Correspondences (after ratio test)**")
        good = result["good_matches"]
        match_img = cv2.drawMatches(
            result["ref_processed"],
            result["kp_ref"],
            result["mov_processed"],
            result["kp_mov"],
            good,
            None,
            matchColor=(0, 255, 0),
            flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
        )
        _display_image(match_img, f"{len(good)} correspondences")

        if result.get("spatial_indices") is not None and len(result["spatial_indices"]) > 0:
            st.divider()
            st.markdown("**Spatially Balanced Correspondences**")
            spatial_matches = [good[i] for i in result["spatial_indices"] if i < len(good)]
            spatial_img = cv2.drawMatches(
                result["ref_processed"],
                result["kp_ref"],
                result["mov_processed"],
                result["kp_mov"],
                spatial_matches,
                None,
                matchColor=(255, 200, 0),
                flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
            )
            _display_image(spatial_img, f"{len(spatial_matches)} spatially balanced correspondences")

        st.divider()
        st.markdown("**Match Statistics**")
        metrics = result.get("metrics", {})
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Candidate Matches", metrics.get("candidate_matches", "N/A"))
        s2.metric("Good Matches", metrics.get("good_matches", "N/A"))
        s3.metric("Inliers", metrics.get("inlier_count", "N/A"))
        s4.metric(
            "Inlier Ratio",
            f"{metrics['inlier_ratio']:.3f}" if metrics.get("inlier_ratio") is not None else "N/A",
        )


# ── Step: Registration ────────────────────────────────────────────────────────

elif st.session_state.current_step == "registration":
    st.markdown('<div class="page-header">Registration</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subheader">Image warping and visual comparison</div>',
        unsafe_allow_html=True,
    )

    result = st.session_state.pipeline_result
    if result is None or result["status"] != "success":
        st.info("Run the pipeline in Step 2 to see registration results.")
    else:
        st.markdown("**Reference vs Registered**")
        r1, r2 = st.columns(2)
        with r1:
            _display_image(result["ref_processed"], "Reference")
        with r2:
            _display_image(result["registered_image"], "Registered moving image")

        st.divider()
        st.markdown("**Alpha Overlay**")
        _display_image(result["overlay"], "Alpha blend of reference and registered")

        st.divider()
        st.markdown("**Difference Image**")
        diff = result["difference"]
        st.image(diff, caption="Pixel-wise absolute difference", use_container_width=True)


# ── Step: Metrics ─────────────────────────────────────────────────────────────

elif st.session_state.current_step == "metrics":
    st.markdown('<div class="page-header">Metrics &amp; Evaluation</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subheader">Quantitative registration accuracy assessment</div>',
        unsafe_allow_html=True,
    )

    result = st.session_state.pipeline_result
    if result is None or result["status"] != "success":
        st.info("Run the pipeline in Step 2 to see metrics.")
    else:
        metrics = result["metrics"]
        render_metric_cards(metrics)

        with st.expander("Full Metrics"):
            st.text(format_metrics(metrics))

        st.divider()
        st.markdown("**Export**")
        exp1, exp2 = st.columns(2)

        with exp1:
            csv_lines = ["metric,value"]
            for k, v in metrics.items():
                csv_lines.append(f"{k},{v}")
            csv_data = "\n".join(csv_lines)
            st.download_button(
                "Download Metrics (CSV)",
                data=csv_data,
                file_name="lunarmatch_metrics.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with exp2:
            reg_img = result.get("registered_image")
            if reg_img is not None:
                success, buf = cv2.imencode(".png", reg_img)
                if success:
                    st.download_button(
                        "Download Registered Image (PNG)",
                        data=buf.tobytes(),
                        file_name="lunarmatch_registered.png",
                        mime="image/png",
                        use_container_width=True,
                    )
