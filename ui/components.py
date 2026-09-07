import streamlit as st


def render_sih_badge():
    st.markdown(
        '<div class="sih-badge-container">'
        '<span class="sih-badge">Smart India Hackathon 2026 &middot; Problem 26166 &middot; ISRO</span>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_feature_card(title, status, description, detail):
    badge_class = "status-badge-implemented" if status == "IMPLEMENTED" else "status-badge-planned"
    st.markdown(
        f'<div class="feature-card">'
        f'<div class="feature-card-title">{title}</div>'
        f'<span class="status-badge {badge_class}">{status}</span>'
        f'<div class="feature-card-desc">{description}</div>'
        f'<div class="feature-card-detail">{detail}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_status_indicator(status):
    labels = {
        "ready": ("ready", "System Ready"),
        "success": ("success", "Results Available"),
        "failed": ("failed", "Pipeline Failed"),
    }
    dot_class, text = labels.get(status, ("ready", "System Ready"))
    st.sidebar.markdown(
        f'<div class="status-indicator">'
        f'<span class="status-dot status-dot-{dot_class}"></span>'
        f'<span class="status-text">{text}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_theme_toggle():
    current = st.session_state.get("theme", "dark")
    icon = "☀️" if current == "dark" else "\U0001F319"
    label = "Light Mode" if current == "dark" else "Dark Mode"
    if st.button(f"{icon} {label}", key="theme_toggle", use_container_width=True):
        st.session_state.theme = "light" if current == "dark" else "dark"
        st.rerun()


def render_metric_cards(metrics):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Inlier Count", metrics.get("inlier_count", "N/A"))
    m2.metric(
        "Inlier Ratio",
        f"{metrics['inlier_ratio']:.3f}" if metrics.get("inlier_ratio") is not None else "N/A",
    )
    m3.metric(
        "RMSE",
        f"{metrics['rmse']:.4f}" if metrics.get("rmse") is not None else "N/A",
    )
    m4.metric(
        "Spatial Coverage",
        f"{metrics['spatial_coverage']:.1%}" if metrics.get("spatial_coverage") is not None else "N/A",
    )


def render_pipeline_checklist(result):
    stages = []

    stages.append(("Input Validation", True, None))
    stages.append(("Preprocessing", True, None))

    kp_ref = result.get("kp_ref")
    kp_mov = result.get("kp_mov")
    if kp_ref is not None:
        kp_ok = len(kp_ref) >= 4 and (kp_mov is None or len(kp_mov) >= 4)
        detail = f"{len(kp_ref)} ref / {len(kp_mov) if kp_mov else 0} mov keypoints"
        stages.append(("Feature Extraction", kp_ok, detail))
    else:
        stages.append(("Feature Extraction", False, "No keypoints detected"))

    good = result.get("good_matches")
    if good is not None:
        stages.append(("Descriptor Matching", len(good) >= 4, f"{len(good)} good matches"))
    elif kp_ref is not None:
        stages.append(("Descriptor Matching", False, "Matching failed"))

    transform = result.get("transform")
    if transform is not None:
        inlier_count = result.get("metrics", {}).get("inlier_count", "?")
        stages.append(("Geometric Verification", True, f"{inlier_count} inliers"))
    elif good is not None and len(good) >= 4:
        stages.append(("Geometric Verification", False, "RANSAC failed"))

    spatial = result.get("spatial_indices")
    if spatial is not None:
        coverage = result.get("spatial_coverage")
        cov_str = f"{coverage:.1%}" if coverage else "N/A"
        stages.append(("Spatial Balancing", True, f"{len(spatial)} selected, {cov_str} coverage"))
    elif result.get("config", {}).get("spatial", {}).get("enabled"):
        stages.append(("Spatial Balancing", False, None))

    if result.get("registered_image") is not None:
        stages.append(("Registration", True, None))

    lines = []
    for name, passed, detail in stages:
        icon = "✓" if passed else "✗"
        css_class = "step-pass" if passed else "step-fail"
        detail_str = f" — {detail}" if detail else ""
        lines.append(f'<div><span class="{css_class}">{icon}</span> {name}{detail_str}</div>')

    st.markdown("".join(lines), unsafe_allow_html=True)


def render_system_info_table(pipeline_status):
    status_display = {
        "ready": '<span class="status-pill">Ready (Awaiting Image Pair)</span>',
        "success": '<span class="status-success">Completed Successfully</span>',
        "failed": '<span class="status-failed">Failed</span>',
    }
    status_html = status_display.get(pipeline_status, status_display["ready"])

    st.markdown(
        f"""
        <div class="section-title">System Information</div>
        <table class="info-table">
            <tr><th>Parameter</th><th>Value</th></tr>
            <tr><td>Supported Sensors</td><td>Chandrayaan-2 OHRC, TMC, TMC-2, IIRS</td></tr>
            <tr><td>Reference Datasets</td><td>LRO NAC, SELENE, or any optical raster</td></tr>
            <tr><td>Feature Extraction</td><td>SIFT (IMPLEMENTED) &middot; RIFT, SuperPoint (PLANNED)</td></tr>
            <tr><td>Matching</td><td>BF / FLANN + Ratio Test (IMPLEMENTED) &middot; LightGlue (PLANNED)</td></tr>
            <tr><td>Geometric Models</td><td>Affine, Homography (IMPLEMENTED)</td></tr>
            <tr><td>Pipeline Status</td><td>{status_html}</td></tr>
        </table>
        """,
        unsafe_allow_html=True,
    )
