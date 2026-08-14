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

    st.subheader("Original Drawing Preview")
    p_col1, p_col2 = st.columns(2)
    p_col1.image(fab_img, caption="Fabrication Drawing")
    p_col2.image(setting_img, caption="Setting-Out Drawing")

    if st.button("Run Audit", type="primary"):
        with st.spinner("Analyzing drawings and detecting error locations..."):
            try:
                # Unpack the tuple: report (AuditReport) and annotated_fab_img (Image)
                report, annotated_fab_img = run_drawing_audit(fab_img, setting_img, api_key)
                
                st.markdown("---")
                st.subheader("🔴 Highlighted Audit Results")
                
                res_col1, res_col2 = st.columns(2)
                with res_col1:
                    st.image(annotated_fab_img, caption="Fabrication Drawing (Errors Highlighted)")
                with res_col2:
                    st.image(setting_img, caption="Setting-Out Plan Reference")

                if report.passed and not report.issues:
                    st.success("✅ No issues found! Fabrication drawing is cleared.")
                else:
                    st.error(f"⚠️ Found {len(report.issues)} issue(s) needing revision:")
                    for idx, issue in enumerate(report.issues, start=1):
                        st.markdown(f"**#{idx} - Tag {issue.tag_id} ({issue.severity} Severity):**")
                        st.write(f"- **Type:** {issue.issue_type}")
                        st.write(f"- **Description:** {issue.description}")
            except Exception as e:
                st.error(f"An error occurred during the audit: {e}")
