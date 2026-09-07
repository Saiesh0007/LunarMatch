COMMON_CSS = """
<style>
    :root {
        --lm-accent: #0EA5E9;
        --lm-accent-muted: rgba(14, 165, 233, 0.12);
        --lm-accent-border: rgba(14, 165, 233, 0.35);
        --lm-bg: #0B0B14;
        --lm-card-bg: #111120;
        --lm-sidebar-bg: #0D0D1A;
        --lm-border: #1C1C30;
        --lm-border-subtle: #151525;
        --lm-text: #E8E8F0;
        --lm-text-muted: #8888A0;
        --lm-text-dim: #5E5E70;
        --lm-success: #22C55E;
        --lm-success-muted: rgba(34, 197, 94, 0.15);
        --lm-success-border: rgba(34, 197, 94, 0.3);
        --lm-danger: #EF4444;
        --lm-warning: #F59E0B;
        --lm-badge-planned-bg: rgba(136, 136, 160, 0.15);
        --lm-badge-planned-border: rgba(136, 136, 160, 0.3);
        --lm-status-bg: rgba(34, 197, 94, 0.08);
    }

    .sih-badge {
        display: inline-block;
        background: var(--lm-accent-muted);
        border: 1px solid var(--lm-accent-border);
        color: var(--lm-accent);
        padding: 6px 20px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    .sih-badge-container {
        text-align: center;
        margin-bottom: 1rem;
    }
    .feature-card {
        background: var(--lm-card-bg);
        border: 1px solid var(--lm-border);
        border-radius: 12px;
        padding: 24px;
        height: 100%;
        transition: border-color 0.2s;
    }
    .feature-card:hover {
        border-color: var(--lm-accent);
    }
    .feature-card-title {
        color: var(--lm-accent);
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }
    .feature-card-desc {
        color: var(--lm-text);
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 8px;
    }
    .feature-card-detail {
        color: var(--lm-text-muted);
        font-size: 0.82rem;
    }
    .status-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 10px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .status-badge-implemented {
        background: var(--lm-success-muted);
        color: var(--lm-success);
        border: 1px solid var(--lm-success-border);
    }
    .status-badge-planned {
        background: var(--lm-badge-planned-bg);
        color: var(--lm-text-muted);
        border: 1px solid var(--lm-badge-planned-border);
    }
    .step-pass {
        color: var(--lm-success);
    }
    .step-fail {
        color: var(--lm-danger);
    }
    .step-skip {
        color: var(--lm-text-muted);
    }
    .info-table {
        width: 100%;
        border-collapse: collapse;
    }
    .info-table th {
        text-align: left;
        color: var(--lm-text-muted);
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 10px 16px;
        border-bottom: 1px solid var(--lm-border);
    }
    .info-table td {
        padding: 12px 16px;
        border-bottom: 1px solid var(--lm-border-subtle);
        color: var(--lm-text);
        font-size: 0.9rem;
    }
    .info-table td:first-child {
        color: var(--lm-text-muted);
    }
    .info-table .status-pill {
        border: 1px solid var(--lm-border);
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.85rem;
        color: var(--lm-text);
    }
    .info-table .status-success {
        color: var(--lm-success);
        font-weight: 600;
    }
    .info-table .status-failed {
        color: var(--lm-danger);
        font-weight: 600;
    }
    .section-title {
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: var(--lm-text);
        margin-bottom: 16px;
    }
    .theme-toggle-btn {
        background: var(--lm-card-bg);
        border: 1px solid var(--lm-border);
        color: var(--lm-text-muted);
        padding: 6px 12px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 1rem;
        transition: border-color 0.2s;
    }
    .theme-toggle-btn:hover {
        border-color: var(--lm-accent);
    }
</style>
"""

HOME_CSS = """
<style>
    section[data-testid="stSidebar"] { display: none; }
    .hero-title {
        text-align: center;
        font-size: 3.2rem;
        font-weight: 800;
        letter-spacing: 6px;
        color: var(--lm-text);
        margin-bottom: 0;
        line-height: 1.2;
    }
    .hero-subtitle {
        text-align: center;
        font-size: 1.3rem;
        font-weight: 400;
        color: var(--lm-text-muted);
        margin-top: 8px;
        margin-bottom: 8px;
    }
    .hero-desc {
        text-align: center;
        font-size: 0.95rem;
        color: var(--lm-text-dim);
        max-width: 700px;
        margin: 0 auto 2rem auto;
        line-height: 1.6;
    }
    .demo-box {
        background: var(--lm-card-bg);
        border: 1px solid var(--lm-border);
        border-radius: 12px;
        padding: 24px 32px;
        margin-top: 2rem;
    }
    .demo-box-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--lm-text);
        margin-bottom: 6px;
    }
    .demo-box-desc {
        font-size: 0.88rem;
        color: var(--lm-text-muted);
    }
    .footer-text {
        text-align: center;
        color: var(--lm-text-dim);
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid var(--lm-border);
    }
</style>
"""

WORKBENCH_CSS = """
<style>
    section[data-testid="stSidebar"] {
        background-color: var(--lm-sidebar-bg);
    }
    .sidebar-logo {
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: 2px;
        color: var(--lm-text);
        margin-bottom: 2px;
    }
    .sidebar-subtitle {
        font-size: 0.75rem;
        color: var(--lm-text-muted);
        margin-bottom: 16px;
    }
    .sidebar-section {
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: var(--lm-text-dim);
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .status-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        background: var(--lm-status-bg);
        border-radius: 8px;
        margin-bottom: 16px;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
    }
    .status-dot-ready { background: var(--lm-success); }
    .status-dot-success { background: var(--lm-accent); }
    .status-dot-failed { background: var(--lm-danger); }
    .status-text {
        font-size: 0.85rem;
        color: var(--lm-text);
    }
    .page-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--lm-text);
        margin-bottom: 4px;
    }
    .page-subheader {
        font-size: 0.9rem;
        color: var(--lm-text-muted);
        margin-bottom: 24px;
    }
    .workflow-num {
        color: var(--lm-accent);
        font-weight: 700;
    }
</style>
"""

LIGHT_OVERRIDE_CSS = """
<style>
    :root {
        --lm-accent: #0EA5E9;
        --lm-accent-muted: rgba(14, 165, 233, 0.08);
        --lm-accent-border: rgba(14, 165, 233, 0.25);
        --lm-bg: #F8FAFC;
        --lm-card-bg: #FFFFFF;
        --lm-sidebar-bg: #F1F3F5;
        --lm-border: #E2E8F0;
        --lm-border-subtle: #F1F5F9;
        --lm-text: #1A1A2E;
        --lm-text-muted: #64748B;
        --lm-text-dim: #94A3B8;
        --lm-success: #16A34A;
        --lm-success-muted: rgba(22, 163, 74, 0.1);
        --lm-success-border: rgba(22, 163, 74, 0.25);
        --lm-danger: #DC2626;
        --lm-warning: #D97706;
        --lm-badge-planned-bg: rgba(100, 116, 139, 0.1);
        --lm-badge-planned-border: rgba(100, 116, 139, 0.25);
        --lm-status-bg: rgba(22, 163, 74, 0.06);
    }

    /* Streamlit native overrides */
    [data-testid="stAppViewContainer"],
    .main .block-container {
        background-color: #F8FAFC !important;
        color: #1A1A2E !important;
    }
    [data-testid="stHeader"] {
        background-color: #F8FAFC !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #F1F3F5 !important;
    }
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: #1A1A2E !important;
    }
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown td, .stMarkdown th {
        color: #1A1A2E !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #1A1A2E !important;
    }
    .stMetric label {
        color: #64748B !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #1A1A2E !important;
    }
    [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border-color: #E2E8F0 !important;
    }
    [data-testid="stExpander"] summary span {
        color: #1A1A2E !important;
    }
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stMultiselect > div > div {
        background-color: #FFFFFF !important;
        color: #1A1A2E !important;
        border-color: #E2E8F0 !important;
    }
    .stCheckbox label span {
        color: #1A1A2E !important;
    }
    .stRadio label span {
        color: #1A1A2E !important;
    }
    .stSlider label {
        color: #1A1A2E !important;
    }
    [data-testid="stFileUploader"] {
        background-color: #FFFFFF !important;
        border-color: #E2E8F0 !important;
    }
    [data-testid="stFileUploader"] label {
        color: #1A1A2E !important;
    }
    .stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #1A1A2E !important;
        border-color: #E2E8F0 !important;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: #0EA5E9 !important;
        color: #0EA5E9 !important;
    }
    .stDownloadButton > button {
        background-color: #FFFFFF !important;
        color: #1A1A2E !important;
        border-color: #E2E8F0 !important;
    }
    hr {
        border-color: #E2E8F0 !important;
    }
    [data-testid="stDivider"] {
        background-color: #E2E8F0 !important;
    }
    .stAlert {
        color: #1A1A2E !important;
    }
    pre, code {
        background-color: #F1F5F9 !important;
        color: #1A1A2E !important;
    }
</style>
"""


def inject_home_css(theme="dark"):
    import streamlit as st
    css = COMMON_CSS + HOME_CSS
    if theme == "light":
        css += LIGHT_OVERRIDE_CSS
    st.markdown(css, unsafe_allow_html=True)


def inject_workbench_css(theme="dark"):
    import streamlit as st
    css = COMMON_CSS + WORKBENCH_CSS
    if theme == "light":
        css += LIGHT_OVERRIDE_CSS
    st.markdown(css, unsafe_allow_html=True)
