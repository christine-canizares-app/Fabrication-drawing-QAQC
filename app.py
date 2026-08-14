import streamlit as st
from pdf_handler import pdf_page_to_image
from audit_engine import run_drawing_audit

st.set_page_config(layout="wide", page_title="Fabrication Drawing Checker")
st.title("📐 Automated Fabrication Drawing QA/QC")

api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

col1, col2 = st.columns(2)
with col1:
    fab_file = st.file_uploader("Upload Fabrication Drawing (PDF)", type=["pdf"])
with col2:
    setting_file = st.file_uploader("Upload Setting-Out / Tagging Plan (PDF)", type=["pdf"])

if fab_file and setting_file and api_key:
    fab_img = pdf_page_to_image(fab_file.read())
    setting_img = pdf_page_to_image(setting_file.read())

    st.subheader("Drawing Preview")
    p_col1, p_col2 = st.columns(2)
    p_col1.image(fab_img, caption="Fabrication Drawing", use_container_width=True)
    p_col2.image(setting_img, caption="Setting-Out Drawing", use_container_width=True)

    if st.button("Run Audit", type="primary"):
        with st.spinner("Analyzing drawings for missing dimensions and mismatches..."):
            try:
                report = run_drawing_audit(fab_img, setting_img, api_key)
                
                if report.passed and not report.issues:
                    st.success("✅ No issues found! Fabrication drawing is cleared.")
                else:
                    st.error(f"⚠️ Found {len(report.issues)} issue(s) needing revision:")
                    st.json([issue.model_dump() for issue in report.issues])
            except Exception as e:
                st.error(f"An error occurred during the audit: {e}")