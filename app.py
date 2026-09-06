import os
import tempfile

import cv2
import numpy as np
import streamlit as st

from src.pipeline import run_pipeline, DEFAULT_CONFIG
from src.features import extract
from src.matching import match
from src.geometry import extract_match_points
from src.metrics import format_metrics


st.set_page_config(page_title="LunarMatch", layout="wide")

st.title("LUNARMATCH")
st.markdown("**Multi-Modal Lunar Image Correspondence & Registration**")
st.caption("SIH 2026 • PS 26166")

# --- Sidebar config ---
st.sidebar.header("Configuration")

preprocess_normalize = st.sidebar.checkbox("Normalize intensity", value=True)
preprocess_clahe = st.sidebar.checkbox("Contrast enhancement (CLAHE)", value=True)
preprocess_denoise = st.sidebar.checkbox("Denoise", value=False)

geo_model = st.sidebar.radio("Geometric model", ["affine", "homography"])
spatial_enabled = st.sidebar.checkbox("Spatial balancing", value=True)
ratio_thresh = st.sidebar.slider("Ratio test threshold", 0.5, 0.95, 0.75, 0.05)

# --- Input panel ---
col_ref, col_mov = st.columns(2)

with col_ref:
    st.subheader("Reference Image")
    ref_file = st.file_uploader("Upload reference", type=["png", "jpg", "jpeg", "tif", "tiff"], key="ref")
    ref_sensor = st.selectbox("Reference sensor", ["OHRC", "TMC", "TMC-2", "IIRS", "LRO NAC", "SELENE", "Other"], key="ref_sensor")

with col_mov:
    st.subheader("Moving Image")
    mov_file = st.file_uploader("Upload moving", type=["png", "jpg", "jpeg", "tif", "tiff"], key="mov")
    mov_sensor = st.selectbox("Moving sensor", ["OHRC", "TMC", "TMC-2", "IIRS", "LRO NAC", "SELENE", "Other"], key="mov_sensor")

run_button = st.button("Run LunarMatch", type="primary", use_container_width=True)

if run_button and ref_file and mov_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        ref_path = os.path.join(tmpdir, "ref" + os.path.splitext(ref_file.name)[1])
        mov_path = os.path.join(tmpdir, "mov" + os.path.splitext(mov_file.name)[1])

        with open(ref_path, "wb") as f:
            f.write(ref_file.getbuffer())
        with open(mov_path, "wb") as f:
            f.write(mov_file.getbuffer())

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

        # --- Pipeline status ---
        if result["status"] == "success":
            st.success("Pipeline completed successfully")
        else:
            st.error(f"Pipeline failed: {result.get('reason', 'Unknown error')}")
            if "kp_ref" in result:
                st.write(f"Keypoints detected — reference: {len(result.get('kp_ref', []))}, moving: {len(result.get('kp_mov', []))}")
            if "good_matches" in result:
                st.write(f"Good matches: {len(result.get('good_matches', []))}")
            st.info("Suggested actions: try another image pair, enable stronger preprocessing, or adjust the ratio threshold.")

        # --- Metrics ---
        if result.get("metrics"):
            st.subheader("Metrics")
            metrics = result["metrics"]
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Inlier Count", metrics.get("inlier_count", "N/A"))
            m2.metric("Inlier Ratio", f"{metrics['inlier_ratio']:.3f}" if metrics.get("inlier_ratio") is not None else "N/A")
            m3.metric("RMSE", f"{metrics['rmse']:.4f}" if metrics.get("rmse") is not None else "N/A")
            m4.metric("Spatial Coverage", f"{metrics['spatial_coverage']:.2%}" if metrics.get("spatial_coverage") is not None else "N/A")

            with st.expander("Full metrics"):
                st.text(format_metrics(metrics))

        # --- Visual outputs ---
        if result["status"] == "success":
            tab_kp, tab_corr, tab_reg = st.tabs(["Keypoints", "Correspondences", "Registration"])

            with tab_kp:
                ref_kp_img = cv2.drawKeypoints(
                    result["ref_processed"], result["kp_ref"], None,
                    color=(0, 255, 0), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
                )
                mov_kp_img = cv2.drawKeypoints(
                    result["mov_processed"], result["kp_mov"], None,
                    color=(0, 255, 0), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
                )
                c1, c2 = st.columns(2)
                c1.image(cv2.cvtColor(ref_kp_img, cv2.COLOR_BGR2RGB), caption=f"Reference — {len(result['kp_ref'])} keypoints")
                c2.image(cv2.cvtColor(mov_kp_img, cv2.COLOR_BGR2RGB), caption=f"Moving — {len(result['kp_mov'])} keypoints")

            with tab_corr:
                good = result["good_matches"]
                match_img = cv2.drawMatches(
                    result["ref_processed"], result["kp_ref"],
                    result["mov_processed"], result["kp_mov"],
                    good, None,
                    matchColor=(0, 255, 0),
                    flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
                )
                st.image(cv2.cvtColor(match_img, cv2.COLOR_BGR2RGB), caption=f"{len(good)} correspondences")

                if result.get("spatial_indices") is not None and len(result["spatial_indices"]) > 0:
                    spatial_matches = [good[i] for i in result["spatial_indices"] if i < len(good)]
                    spatial_img = cv2.drawMatches(
                        result["ref_processed"], result["kp_ref"],
                        result["mov_processed"], result["kp_mov"],
                        spatial_matches, None,
                        matchColor=(255, 200, 0),
                        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
                    )
                    st.image(cv2.cvtColor(spatial_img, cv2.COLOR_BGR2RGB), caption=f"{len(spatial_matches)} spatially balanced correspondences")

            with tab_reg:
                r1, r2 = st.columns(2)
                ref_display = result["ref_processed"]
                if ref_display.ndim == 2:
                    ref_display = cv2.cvtColor(ref_display, cv2.COLOR_GRAY2RGB)
                else:
                    ref_display = cv2.cvtColor(ref_display, cv2.COLOR_BGR2RGB)

                reg_display = result["registered_image"]
                if reg_display.ndim == 2:
                    reg_display = cv2.cvtColor(reg_display, cv2.COLOR_GRAY2RGB)
                else:
                    reg_display = cv2.cvtColor(reg_display, cv2.COLOR_BGR2RGB)

                r1.image(ref_display, caption="Reference")
                r2.image(reg_display, caption="Registered moving image")

                overlay = result["overlay"]
                if overlay.ndim == 2:
                    overlay = cv2.cvtColor(overlay, cv2.COLOR_GRAY2RGB)
                else:
                    overlay = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)
                st.image(overlay, caption="Alpha overlay")

                diff = result["difference"]
                st.image(diff, caption="Difference image")

elif run_button:
    st.warning("Please upload both reference and moving images.")
