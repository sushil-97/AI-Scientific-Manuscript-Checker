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
# HELPER FUNCTIONS
# ==========================================================

def format_name(value):
    """Convert internal variable names into readable labels."""
    return str(value).replace("_", " ").title()


def status_icon(status):
    """Return an icon based on screening status."""

    if status is None:
        return "○"

    status = str(status).upper()

    if status in [
        "PASS",
        "PASS_CANDIDATE",
        "CONSISTENT",
        "DETECTED"
    ]:
        return "✅"

    if status in [
        "REVIEW",
        "REVIEW_MISSING",
        "REVIEW_WAIVER",
        "REVIEW_EXEMPTION",
        "REVIEW_ANIMAL_ETHICS",
        "POTENTIAL_DURC",
        "POSSIBLE_RELEVANCE",
        "NOT_TRACEABLE"
    ]:
        return "⚠️"

    if status in [
        "NOT_TRIGGERED",
        "NOT_APPLICABLE",
        "NOT_DETECTED",
        "NOT_ASSESSABLE"
    ]:
        return "○"

    return "ℹ️"


def display_status_card(title, status, reason=None):
    """Display a simple module summary card."""

    icon = status_icon(status)

    st.markdown(
        f"### {icon} {title}"
    )

    st.markdown(
        f"**Status:** `{status}`"
    )

    if reason:
        st.write(reason)
        
def build_editorial_report(
    uploaded_filename,
    manuscript_report,
    overall
):
    """Create a downloadable editorial screening report."""

    lines = []

    lines.append(
        "AI SCIENTIFIC MANUSCRIPT QUALITY & DISCREPANCY CHECKER"
    )
    lines.append("=" * 65)
    lines.append("")

    lines.append(
        f"Manuscript: {uploaded_filename}"
    )

    lines.append(
        f"Overall Decision: {overall['overall_status']}"
    )

    lines.append(
        f"Review Flags: {overall['review_count']}"
    )

    lines.append("")

    # ------------------------------------------------------
    # REVIEW PRIORITIES
    # ------------------------------------------------------

    lines.append("EDITORIAL REVIEW PRIORITIES")
    lines.append("-" * 65)

    if overall["review_items"]:

        for item in overall["review_items"]:

            lines.append(
                f"{item['module']} — {item['status']}"
            )

            lines.append(
                f"Reason: {item['reason']}"
            )

            lines.append("")

    else:

        lines.append(
            "No review-level findings were detected."
        )

        lines.append("")


    # ------------------------------------------------------
    # EDITORIAL SCREENING
    # ------------------------------------------------------

    lines.append("EDITORIAL & POLICY SCREENING")
    lines.append("-" * 65)

    editorial = manuscript_report[
        "editorial_screening"
    ]

    ethics = editorial["ethics_consent"]

    lines.append(
        f"Ethics: {ethics.get('ethics_status', 'UNKNOWN')}"
    )

    lines.append(
        f"Consent: {ethics.get('consent_status', 'UNKNOWN')}"
    )

    lines.append(
        "Ethics Statement Detected: "
        + (
            "Yes"
            if ethics.get("ethics_statement_detected")
            else "No"
        )
    )

    lines.append(
        "Accordance Statement Detected: "
        + (
            "Yes"
            if ethics.get("accordance_statement_detected")
            else "No"
        )
    )

    lines.append("")


    data = editorial["data_availability"]

    lines.append(
        f"Data Availability: {data.get('status', 'UNKNOWN')}"
    )

    lines.append(
        f"Reason: {data.get('reason', 'Not available')}"
    )

    lines.append("")


    center = editorial["center_screening"]

    lines.append(
        f"Center Screening: {center.get('status', 'UNKNOWN')}"
    )

    lines.append(
        f"Classification: "
        f"{center.get('classification', 'UNKNOWN')}"
    )

    lines.append("")


    cam = editorial["cam"]

    lines.append(
        f"CAM: {cam.get('status', 'UNKNOWN')}"
    )

    lines.append("")


    durc = editorial["durc"]

    lines.append(
        f"DURC: {durc.get('status', 'UNKNOWN')}"
    )

    lines.append("")


    # ------------------------------------------------------
    # CONSISTENCY CHECKS
    # ------------------------------------------------------

    lines.append("CONSISTENCY & DISCREPANCY CHECKS")
    lines.append("-" * 65)

    discrepancies = manuscript_report[
        "discrepancy_checks"
    ]

    statistical = discrepancies[
        "statistical_consistency"
    ]

    lines.append(
        f"Statistical Consistency: "
        f"{statistical.get('status', 'UNKNOWN')}"
    )

    lines.append(
        f"Claim Consistency: "
        f"{statistical.get('claim_consistency', 'UNKNOWN')}"
    )

    lines.append(
        f"Numeric Traceability: "
        f"{statistical.get('numeric_traceability', 'UNKNOWN')}"
    )

    lines.append(
        f"Reason: {statistical.get('reason', 'Not available')}"
    )

    lines.append("")


    sample = discrepancies[
        "sample_size_consistency"
    ]

    lines.append(
        f"Sample Size Consistency: "
        f"{sample.get('status', 'UNKNOWN')}"
    )

    lines.append(
        f"Applicability: "
        f"{sample.get('applicability', 'UNKNOWN')}"
    )

    lines.append("")


    # ------------------------------------------------------
    # REPRODUCIBILITY
    # ------------------------------------------------------

    lines.append("REPRODUCIBILITY ASSESSMENT")
    lines.append("-" * 65)

    reproducibility = manuscript_report[
        "reproducibility"
    ]

    lines.append(
        f"Status: {reproducibility.get('status', 'UNKNOWN')}"
    )

    lines.append("")

    lines.append("Reported:")

    for item in reproducibility.get(
        "reported",
        []
    ):
        lines.append(
            f"  - {format_name(item)}"
        )

    lines.append("")

    lines.append("Explicitly Unavailable:")

    for item in reproducibility.get(
        "explicitly_unavailable",
        []
    ):
        lines.append(
            f"  - {format_name(item)}"
        )

    lines.append("")

    lines.append("Not Detected:")

    for item in reproducibility.get(
        "not_detected",
        []
    ):
        lines.append(
            f"  - {format_name(item)}"
        )

    lines.append("")
    lines.append("=" * 65)

    lines.append(
        "Automated screening result — human editorial "
        "verification is required."
    )

    return "\n".join(lines)

# ==========================================================
# TITLE
# ==========================================================

st.title(
    "🔬 AI Scientific Manuscript Quality & Discrepancy Checker"
)

st.write(
    "Automated editorial screening for scientific manuscripts, "
    "including policy checks, discrepancy detection, statistical "
    "consistency, and reproducibility assessment."
)

st.info(
    "This system is designed as an editorial decision-support tool. "
    "All findings should be verified by a human editor."
)


# ==========================================================
# FILE UPLOAD
# ==========================================================

st.header("Upload Manuscript")

uploaded_file = st.file_uploader(
    "Upload a scientific manuscript in PDF format",
    type=["pdf"]
)


# ==========================================================
# ANALYSIS
# ==========================================================

if uploaded_file is not None:

    st.success(
        f"PDF ready for analysis: {uploaded_file.name}"
    )

    if st.button(
        "Analyze Manuscript",
        type="primary",
        use_container_width=True
    ):

        temp_path = None

        try:

            # --------------------------------------------------
            # SAVE TEMPORARY PDF
            # --------------------------------------------------

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as temp_file:

                temp_file.write(
                    uploaded_file.getbuffer()
                )

                temp_path = temp_file.name


            # --------------------------------------------------
            # RUN ANALYSIS
            # --------------------------------------------------

            with st.spinner(
                "Analyzing manuscript..."
            ):

                result = analyze_manuscript(
                    temp_path
                )
                st.write("DEBUG — Accordance phrase test")

                import fitz
                
                debug_doc = fitz.open(temp_path)
                
                debug_text = "\n".join(
                    page.get_text("text")
                    for page in debug_doc
                )
                
                debug_doc.close()
                
                phrase = "in accordance with relevant guidelines and regulations"
                
                st.write(
                    "Phrase found in extracted PDF text:",
                    phrase.lower() in debug_text.lower()
                )
                                
                


            manuscript_report = result[
                "manuscript_report"
            ]

            overall = result[
                "overall_decision"
            ]

            editorial = manuscript_report[
                "editorial_screening"
            ]

            discrepancies = manuscript_report[
                "discrepancy_checks"
            ]

            reproducibility = manuscript_report[
                "reproducibility"
            ]


            # ==================================================
            # OVERALL SUMMARY
            # ==================================================

            st.divider()

            st.header(
                "Manuscript Screening Summary"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Overall Decision",
                    overall["overall_status"]
                )

            with col2:

                st.metric(
                    "Review Flags",
                    overall["review_count"]
                )

            with col3:

                st.metric(
                    "Screening Modules",
                    "8"
                )


            if overall["overall_status"] == "REVIEW":

                st.warning(
                    "One or more findings require editorial review."
                )

            else:

                st.success(
                    "No review-level findings were detected."
                )


            # ==================================================
            # REVIEW PRIORITIES
            # ==================================================

            if overall["review_items"]:

                st.subheader(
                    "⚠️ Editorial Review Priorities"
                )

                for item in overall[
                    "review_items"
                ]:

                    with st.expander(
                        f"{item['module']} — {item['status']}",
                        expanded=True
                    ):

                        st.write(
                            item["reason"]
                        )


            # ==================================================
            # EDITORIAL & POLICY SCREENING
            # ==================================================

            st.divider()

            st.header(
                "Editorial & Policy Screening"
            )


            # --------------------------------------------------
            # ETHICS & CONSENT
            # --------------------------------------------------

            ethics = editorial[
                "ethics_consent"
            ]

            col1, col2 = st.columns(2)

            with col1:

                display_status_card(
                    "Ethics",
                    ethics.get(
                        "ethics_status",
                        "UNKNOWN"
                    )
                )

                st.write(
                    "Ethics statement detected:",
                    "Yes"
                    if ethics.get(
                        "ethics_statement_detected"
                    )
                    else "No"
                )

                st.write(
                    "Accordance statement detected:",
                    "Yes"
                    if ethics.get(
                        "accordance_statement_detected"
                    )
                    else "No"
                )

            with col2:

                display_status_card(
                    "Consent",
                    ethics.get(
                        "consent_status",
                        "UNKNOWN"
                    )
                )

                st.write(
                    "Consent statement detected:",
                    "Yes"
                    if ethics.get(
                        "consent_statement_detected"
                    )
                    else "No"
                )

                st.write(
                    "Consent waiver detected:",
                    "Yes"
                    if ethics.get(
                        "consent_waiver_detected"
                    )
                    else "No"
                )


            # --------------------------------------------------
            # DATA AVAILABILITY
            # --------------------------------------------------

            st.divider()

            data = editorial[
                "data_availability"
            ]

            display_status_card(
                "Data Availability",
                data.get(
                    "status",
                    "UNKNOWN"
                ),
                data.get("reason")
            )

            data_col1, data_col2 = st.columns(2)

            with data_col1:

                st.write(
                    "**Applicability:**",
                    data.get(
                        "applicability",
                        "Unknown"
                    )
                )

                st.write(
                    "**Statement detected:**",
                    "Yes"
                    if data.get(
                        "statement_detected"
                    )
                    else "No"
                )

            with data_col2:

                access_types = data.get(
                    "access_type",
                    []
                )

                st.write(
                    "**Access type:**",
                    ", ".join(access_types)
                    if access_types
                    else "Not identified"
                )

                repositories = data.get(
                    "repositories",
                    []
                )

                st.write(
                    "**Repositories:**",
                    ", ".join(repositories)
                    if repositories
                    else "None detected"
                )


            # --------------------------------------------------
            # CENTER / CAM / DURC
            # --------------------------------------------------

            st.divider()

            col1, col2, col3 = st.columns(3)


            with col1:

                center = editorial[
                    "center_screening"
                ]

                display_status_card(
                    "Center Screening",
                    center.get(
                        "status",
                        "UNKNOWN"
                    ),
                    center.get("reason")
                )

                st.write(
                    "**Classification:**",
                    center.get(
                        "classification",
                        "Unknown"
                    )
                )


            with col2:

                cam = editorial[
                    "cam"
                ]

                display_status_card(
                    "CAM",
                    cam.get(
                        "status",
                        "UNKNOWN"
                    ),
                    cam.get("reason")
                )

                categories = cam.get(
                    "categories",
                    []
                )

                st.write(
                    "**Categories:**",
                    ", ".join(categories)
                    if categories
                    else "None detected"
                )


            with col3:

                durc = editorial[
                    "durc"
                ]

                display_status_card(
                    "DURC",
                    durc.get(
                        "status",
                        "UNKNOWN"
                    ),
                    durc.get("reason")
                )

                st.write(
                    "**Classification:**",
                    durc.get(
                        "classification",
                        "Unknown"
                    )
                )


            # ==================================================
            # DISCREPANCY CHECKS
            # ==================================================

            st.divider()

            st.header(
                "Consistency & Discrepancy Checks"
            )


            # --------------------------------------------------
            # STATISTICAL CONSISTENCY
            # --------------------------------------------------

            statistical = discrepancies[
                "statistical_consistency"
            ]

            display_status_card(
                "Statistical Consistency",
                statistical.get(
                    "status",
                    "UNKNOWN"
                ),
                statistical.get("reason")
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Claim Consistency",
                    statistical.get(
                        "claim_consistency",
                        "Unknown"
                    )
                )

            with col2:

                abstract_pvalues = statistical.get(
                    "abstract_pvalues",
                    []
                )

                st.metric(
                    "Abstract P-values",
                    len(abstract_pvalues)
                )

            with col3:

                st.metric(
                    "Numeric Traceability",
                    statistical.get(
                        "numeric_traceability",
                        "Unknown"
                    )
                )


            if abstract_pvalues:

                st.write(
                    "**Abstract p-values:**",
                    ", ".join(
                        str(value)
                        for value in abstract_pvalues
                    )
                )


            results_pvalues = statistical.get(
                "results_pvalues",
                []
            )

            st.write(
                "**Results p-values:**",
                ", ".join(
                    str(value)
                    for value in results_pvalues
                )
                if results_pvalues
                else "None detected"
            )


            # --------------------------------------------------
            # SAMPLE SIZE
            # --------------------------------------------------

            st.divider()

            sample = discrepancies[
                "sample_size_consistency"
            ]

            display_status_card(
                "Sample Size Consistency",
                sample.get(
                    "status",
                    "UNKNOWN"
                ),
                sample.get("reason")
            )

            st.write(
                "**Applicability:**",
                sample.get(
                    "applicability",
                    "Unknown"
                )
            )


            # ==================================================
            # REPRODUCIBILITY
            # ==================================================

            st.divider()

            st.header(
                "Reproducibility Assessment"
            )

            display_status_card(
                "Reproducibility",
                reproducibility.get(
                    "status",
                    "UNKNOWN"
                ),
                reproducibility.get(
                    "reason"
                )
            )


            reported = reproducibility.get(
                "reported",
                []
            )

            unavailable = reproducibility.get(
                "explicitly_unavailable",
                []
            )

            not_detected = reproducibility.get(
                "not_detected",
                []
            )


            col1, col2, col3 = st.columns(3)


            with col1:

                st.subheader(
                    "✅ Reported"
                )

                if reported:

                    for item in reported:

                        st.write(
                            f"• {format_name(item)}"
                        )

                else:

                    st.write(
                        "None identified"
                    )


            with col2:

                st.subheader(
                    "⚠️ Explicitly Unavailable"
                )

                if unavailable:

                    for item in unavailable:

                        st.write(
                            f"• {format_name(item)}"
                        )

                else:

                    st.write(
                        "None"
                    )


            with col3:

                st.subheader(
                    "○ Not Detected"
                )

                if not_detected:

                    for item in not_detected:

                        st.write(
                            f"• {format_name(item)}"
                        )

                else:

                    st.write(
                        "None"
                    )

            # ==========================================================
            # DOWNLOAD EDITORIAL REPORT
            # ==========================================================
            
            st.divider()
            
            st.header("Download Editorial Report")
            
            editorial_report_text = build_editorial_report(
                uploaded_file.name,
                manuscript_report,
                overall
            )
            
            report_filename = (
                os.path.splitext(uploaded_file.name)[0]
                + "_editorial_report.txt"
            )
            
            st.download_button(
                label="📄 Download Editorial Screening Report",
                data=editorial_report_text,
                file_name=report_filename,
                mime="text/plain",
                use_container_width=True
            )
            # ==================================================
            # TECHNICAL DETAILS
            # ==================================================

            st.divider()

            with st.expander(
                "View Technical Analysis Details"
            ):

                st.write(
                    "### Editorial Screening"
                )

                st.json(
                    manuscript_report[
                        "editorial_screening"
                    ]
                )

                st.write(
                    "### Discrepancy Checks"
                )

                st.json(
                    manuscript_report[
                        "discrepancy_checks"
                    ]
                )

                st.write(
                    "### Reproducibility"
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

            # --------------------------------------------------
            # DELETE TEMPORARY PDF
            # --------------------------------------------------

            if (
                temp_path
                and os.path.exists(temp_path)
            ):

                os.remove(
                    temp_path
                )
