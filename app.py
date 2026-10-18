
import streamlit as st
import tempfile
import os

from manuscript_checker import analyze_manuscript


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="AI Scientific Manuscript Checker",
    page_icon="🔬",
    layout="wide"
)


# ==========================================================
# TITLE
# ==========================================================

st.title("🔬 AI Scientific Manuscript Quality & Discrepancy Checker")

st.write(
    "Upload a scientific manuscript in PDF format to perform "
    "automated editorial screening, discrepancy checks, and "
    "reproducibility assessment."
)

st.info(
    "This tool provides automated screening support. "
    "Findings should be reviewed by a human editor."
)


# ==========================================================
# FILE UPLOAD
# ==========================================================

uploaded_file = st.file_uploader(
    "Upload Scientific Manuscript",
    type=["pdf"]
)


# ==========================================================
# ANALYSIS
# ==========================================================

if uploaded_file is not None:

    st.success(
        f"Uploaded: {uploaded_file.name}"
    )

    if st.button(
        "Analyze Manuscript",
        type="primary"
    ):

        temp_path = None

        try:

            # Save uploaded PDF temporarily
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as temp_file:

                temp_file.write(
                    uploaded_file.getbuffer()
                )

                temp_path = temp_file.name


            # Run analysis
            with st.spinner(
                "Analyzing manuscript..."
            ):

                result = analyze_manuscript(
                    temp_path
                )


            manuscript_report = result[
                "manuscript_report"
            ]

            overall = result[
                "overall_decision"
            ]


            # ==================================================
            # OVERALL RESULT
            # ==================================================

            st.divider()

            st.header(
                "Editorial Screening Result"
            )


            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "Overall Status",
                    overall["overall_status"]
                )

            with col2:

                st.metric(
                    "Review Flags",
                    overall["review_count"]
                )


            # ==================================================
            # REVIEW FINDINGS
            # ==================================================

            if overall["review_items"]:

                st.subheader(
                    "⚠️ Items Requiring Editorial Review"
                )

                for item in overall[
                    "review_items"
                ]:

                    with st.expander(
                        f"{item['module']} — "
                        f"{item['status']}"
                    ):

                        st.write(
                            item["reason"]
                        )

            else:

                st.success(
                    "No review-level findings "
                    "were detected."
                )


            # ==================================================
            # DETAILED REPORT
            # ==================================================

            st.divider()

            st.header(
                "Detailed Screening Report"
            )


            # Editorial screening
            st.subheader(
                "Editorial & Policy Screening"
            )

            editorial = manuscript_report[
                "editorial_screening"
            ]

            for module, module_result in editorial.items():

                with st.expander(
                    module.replace(
                        "_", " "
                    ).title()
                ):

                    st.json(
                        module_result
                    )


            # Discrepancy checks
            st.subheader(
                "Discrepancy Checks"
            )

            discrepancies = manuscript_report[
                "discrepancy_checks"
            ]

            for module, module_result in discrepancies.items():

                with st.expander(
                    module.replace(
                        "_", " "
                    ).title()
                ):

                    st.json(
                        module_result
                    )


            # Reproducibility
            st.subheader(
                "Reproducibility"
            )

            st.json(
                manuscript_report[
                    "reproducibility"
                ]
            )


        except Exception as e:

            st.error(
                f"Analysis failed: {e}"
            )


        finally:

            # Remove temporary PDF
            if (
                temp_path
                and os.path.exists(temp_path)
            ):

                os.remove(temp_path)
