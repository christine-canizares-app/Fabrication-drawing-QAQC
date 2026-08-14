import streamlit as st
from pdf_handler import pdf_to_images
from audit_engine import audit_single_page

st.set_page_config(layout="wide", page_title="Multi-Page Fabrication Drawing QA/QC")
st.title("📐 Multi-Page Fabrication Drawing QA/QC Checker")

api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

col1, col2 = st.columns(2)
with col1:
    fab_file = st.file_uploader("Upload Fabrication Drawing Set (PDF)", type=["pdf"])
with col2:
    setting_file = st.file_uploader("Upload Setting-Out / Tagging Plan(s) (PDF)", type=["pdf"])

if fab_file and setting_file and api_key:
    fab_pages = pdf_to_images(fab_file.read())
    setting_pages = pdf_to_images(setting_file.read())

    st.subheader(f"📄 Drawing Loaded ({len(fab_pages)} Fabrication Page(s), {len(setting_pages)} Setting-Out Page(s))")
    
    with st.expander("Preview Uploaded Pages", expanded=False):
        prev_col1, prev_col2 = st.columns(2)
        with prev_col1:
            st.markdown("**Fabrication Pages:**")
            for i, page in enumerate(fab_pages, 1):
                st.image(page, caption=f"Fab Page {i}", use_container_width=True)
        with prev_col2:
            st.markdown("**Setting-Out Pages:**")
            for j, page in enumerate(setting_pages, 1):
                st.image(page, caption=f"Setting-Out Page {j}", use_container_width=True)

    if st.button("Run Multi-Page Audit", type="primary"):
        total_issues = 0
        
        for idx, fab_page in enumerate(fab_pages, start=1):
            with st.spinner(f"Auditing Fabrication Page {idx} of {len(fab_pages)}..."):
                try:
                    report, annotated_fab = audit_single_page(
                        fab_page=fab_page,
                        setting_out_images=setting_pages,
                        api_key=api_key,
                        page_num=idx
                    )
                    
                    st.markdown("---")
                    st.subheader(f"🔍 Audit Results: Fabrication Page {idx}")
                    
                    res_col1, res_col2 = st.columns(2)
                    with res_col1:
                        st.image(annotated_fab, caption=f"Fab Page {idx} - Highlighted Errors", use_container_width=True)
                    with res_col2:
                        st.image(setting_pages[0], caption="Setting-Out Reference", use_container_width=True)

                    if report.passed and not report.issues:
                        st.success(f"✅ Page {idx}: No issues found!")
                    else:
                        num_found = len(report.issues)
                        total_issues += num_found
                        st.error(f"⚠️ Page {idx}: Found {num_found} issue(s) needing revision:")
                        
                        for issue_idx, issue in enumerate(report.issues, start=1):
                            st.markdown(f"**#{issue_idx} - Tag {issue.tag_id} ({issue.severity} Severity):**")
                            st.write(f"- **Type:** {issue.issue_type}")
                            st.write(f"- **Description:** {issue.description}")

                except Exception as e:
                    st.error(f"Error auditing Page {idx}: {e}")

        st.markdown("---")
        if total_issues == 0:
            st.balloons()
            st.success("🎉 Complete Drawing Set Passed QA/QC!")
        else:
            st.warning(f"📋 Multi-Page Audit Complete. Total issues found across all pages: {total_issues}")
