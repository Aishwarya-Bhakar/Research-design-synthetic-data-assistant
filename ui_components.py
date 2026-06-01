from __future__ import annotations

from typing import Any
import html

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


ACCENT = "#6d5dfc"
ACCENT_2 = "#15b8a6"
BG = "#f7f7fb"
CARD = "#ffffff"
TEXT = "#111827"
MUTED = "#6b7280"
BORDER = "#e5e7eb"


def apply_theme() -> None:
    st.markdown(
        f"""
        <style>
            :root {{
                --accent: {ACCENT};
                --accent2: {ACCENT_2};
                --bg: {BG};
                --card: {CARD};
                --text: {TEXT};
                --muted: {MUTED};
                --border: {BORDER};
            }}
            .block-container {{
                padding-top: 1.2rem;
                padding-bottom: 4rem;
                max-width: 1220px;
            }}
            [data-testid="stAppViewContainer"] {{
                background:
                    radial-gradient(circle at top left, rgba(109, 93, 252, 0.12), transparent 34rem),
                    radial-gradient(circle at top right, rgba(21, 184, 166, 0.10), transparent 28rem),
                    var(--bg);
            }}
            [data-testid="stSidebar"] > div:first-child {{
                background: linear-gradient(180deg, #ffffff 0%, #f4f5ff 100%);
                border-right: 1px solid var(--border);
            }}
            h1, h2, h3 {{ letter-spacing: -0.025em; }}
            .hero {{
                padding: 1.4rem 1.6rem;
                border-radius: 24px;
                background: linear-gradient(135deg, #111827 0%, #312e81 52%, #0f766e 100%);
                color: white;
                box-shadow: 0 24px 60px rgba(17, 24, 39, 0.18);
                margin-bottom: 1rem;
            }}
            .hero h1 {{
                color: white;
                margin: 0 0 0.35rem 0;
                font-size: 2.1rem;
            }}
            .hero p {{
                color: rgba(255,255,255,0.86);
                margin: 0;
                font-size: 1rem;
                line-height: 1.55;
            }}
            .step-card {{
                background: rgba(255,255,255,0.82);
                border: 1px solid rgba(229,231,235,0.95);
                border-radius: 20px;
                padding: 1.05rem 1.1rem;
                box-shadow: 0 10px 30px rgba(31, 41, 55, 0.06);
                margin: 0.45rem 0 1rem 0;
            }}
            .section-eyebrow {{
                color: var(--accent);
                font-weight: 800;
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                margin-bottom: 0.2rem;
            }}
            .section-title {{
                color: var(--text);
                font-size: 1.35rem;
                font-weight: 800;
                margin-bottom: 0.25rem;
            }}
            .section-subtitle {{
                color: var(--muted);
                font-size: 0.94rem;
                line-height: 1.5;
            }}
            .metric-card {{
                border-radius: 18px;
                background: var(--card);
                border: 1px solid var(--border);
                padding: 1rem;
                box-shadow: 0 8px 24px rgba(31, 41, 55, 0.055);
            }}
            .metric-label {{
                color: var(--muted);
                font-size: 0.75rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.06em;
            }}
            .metric-value {{
                color: var(--text);
                font-size: 1.45rem;
                font-weight: 850;
                margin-top: 0.15rem;
            }}
            .soft-card {{
                border-radius: 18px;
                background: rgba(255,255,255,0.88);
                border: 1px solid var(--border);
                padding: 1rem 1.05rem;
                box-shadow: 0 8px 24px rgba(31, 41, 55, 0.055);
                margin-bottom: 0.8rem;
            }}
            .soft-card h4 {{
                margin: 0 0 0.35rem 0;
                font-size: 1rem;
            }}
            .soft-card p {{
                color: var(--muted);
                line-height: 1.55;
                margin: 0.2rem 0;
            }}
            .chip {{
                display: inline-block;
                padding: 0.32rem 0.58rem;
                margin: 0.14rem;
                border-radius: 999px;
                background: #eef2ff;
                color: #3730a3;
                border: 1px solid #c7d2fe;
                font-size: 0.82rem;
                font-weight: 650;
            }}
            .chip-green {{
                background: #ecfdf5;
                color: #047857;
                border-color: #a7f3d0;
            }}
            .chip-amber {{
                background: #fffbeb;
                color: #92400e;
                border-color: #fde68a;
            }}
            .chip-red {{
                background: #fef2f2;
                color: #b91c1c;
                border-color: #fecaca;
            }}
            .paper-title {{
                font-weight: 800;
                color: var(--text);
                margin-bottom: 0.2rem;
            }}
            .paper-meta {{
                color: var(--muted);
                font-size: 0.85rem;
                margin-bottom: 0.35rem;
            }}
            .divider {{
                height: 1px;
                background: var(--border);
                margin: 0.75rem 0;
            }}
            .small-muted {{ color: var(--muted); font-size: 0.86rem; }}
            .stTabs [data-baseweb="tab-list"] {{
                gap: 0.25rem;
                background: rgba(255,255,255,0.75);
                padding: 0.35rem;
                border-radius: 16px;
                border: 1px solid var(--border);
            }}
            .stTabs [data-baseweb="tab"] {{
                border-radius: 12px;
                padding: 0.55rem 0.8rem;
                font-weight: 700;
            }}
            div[data-testid="stDataFrame"] {{
                border: 1px solid var(--border);
                border-radius: 14px;
                overflow: hidden;
            }}
            .status-dot {{
                width: 0.55rem;
                height: 0.55rem;
                display: inline-block;
                border-radius: 50%;
                margin-right: 0.4rem;
                background: var(--accent2);
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _e(value: Any) -> str:
    return html.escape(str(value or ""))


def hero() -> None:
    st.markdown(
        """
        <div class="hero">
          <h1>Research Design & Synthetic Data Assistant</h1>
          <p>Move from topic → evidence → design → variables → hypotheses → codebook → synthetic dataset with a cleaner, review-friendly workflow.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(step: str, title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="step-card">
          <div class="section-eyebrow">{_e(step)}</div>
          <div class="section-title">{_e(title)}</div>
          <div class="section-subtitle">{_e(subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: Any, help_text: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-label">{_e(label)}</div>
          <div class="metric-value">{_e(value)}</div>
          <div class="small-muted">{_e(help_text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chips(items: list[Any], kind: str = "blue") -> None:
    if not items:
        st.caption("None found yet.")
        return

    cls = {
        "green": "chip chip-green",
        "amber": "chip chip-amber",
        "red": "chip chip-red",
    }.get(kind, "chip")

    html_items = "".join(
        f'<span class="{cls}">{_e(item)}</span>'
        for item in items
        if str(item).strip()
    )
    st.markdown(html_items, unsafe_allow_html=True)


def card(title: str, body: str = "", footer: str = "") -> None:
    st.markdown(
        f"""
        <div class="soft-card">
          <h4>{_e(title)}</h4>
          <p>{_e(body)}</p>
          {f'<div class="divider"></div><div class="small-muted">{_e(footer)}</div>' if footer else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_literature_summary(summary: dict[str, Any]) -> None:
    paper_count = summary.get("paper_count") or len(summary.get("papers", []) or [])

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card("Evidence records", paper_count, "Retrieved and summarized")

    with c2:
        metric_card(
            "Candidate IVs",
            len(summary.get("candidate_independent_variables", []) or []),
            "Suggested exposures / predictors",
        )

    with c3:
        metric_card(
            "Candidate DVs",
            len(summary.get("candidate_dependent_variables", []) or []),
            "Suggested outcomes",
        )

    st.markdown("### Evidence brief")
    card(
        "AI-readable summary converted to review text",
        summary.get("evidence_summary") or "No narrative evidence summary returned yet.",
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Independent / exposure variables")
        chips(summary.get("candidate_independent_variables", []) or [])

        st.markdown("#### Control variables")
        chips(summary.get("candidate_control_variables", []) or [], "green")

    with col2:
        st.markdown("#### Dependent / outcome variables")
        chips(summary.get("candidate_dependent_variables", []) or [])

        st.markdown("#### Mediators / moderators")
        chips(
            (summary.get("candidate_mediators", []) or [])
            + (summary.get("candidate_moderators", []) or []),
            "amber",
        )

    if summary.get("candidate_relationships"):
        st.markdown("#### Candidate relationships")
        for item in summary.get("candidate_relationships", [])[:8]:
            st.markdown(f"- {item}")

    if summary.get("evidence_gaps"):
        with st.expander("Evidence gaps to consider", expanded=False):
            for item in summary.get("evidence_gaps", []):
                st.markdown(f"- {item}")

    if summary.get("warnings"):
        with st.expander("Warnings", expanded=True):
            for item in summary.get("warnings", []):
                st.warning(str(item))

    papers = summary.get("papers", []) or []

    if papers:
        st.markdown("### Retrieved / summarized papers")

        for paper in papers[:6]:
            title = paper.get("title", "Untitled paper")
            meta = " • ".join(
                str(x)
                for x in [paper.get("source"), paper.get("year"), paper.get("journal")]
                if x
            )

            body = (
                paper.get("summary")
                or paper.get("key_findings")
                or paper.get("url")
                or "No paper-level summary available."
            )

            if isinstance(body, list):
                body = "; ".join(map(str, body))

            card(title, str(body), meta)

        with st.expander("Paper table", expanded=False):
            st.dataframe(pd.DataFrame(papers), use_container_width=True)


def render_design_suggestions(data: dict[str, Any]) -> None:
    st.markdown("### Recommended design")

    recommended = data.get("recommended_design") or "Not selected yet"
    reason = data.get("reason_for_recommendation") or "No recommendation reason returned."

    card(str(recommended), str(reason))

    designs = data.get("suggested_designs", []) or []

    if designs:
        st.markdown("### Design options")

        cols = st.columns(min(3, len(designs)))

        for i, design in enumerate(designs):
            with cols[i % len(cols)]:
                score = design.get("fit_score", "")
                score_text = f"Fit score: {score}" if score != "" else ""
                card(design.get("design", "Design option"), design.get("reason", ""), score_text)

        with st.expander("Detailed design table", expanded=False):
            st.dataframe(pd.DataFrame(designs), use_container_width=True)

    if data.get("sampling_strategy_suggestions"):
        st.markdown("### Sampling strategy suggestions")
        for item in data.get("sampling_strategy_suggestions", []):
            st.markdown(f"- {item}")

    if data.get("bias_and_confounding_warnings"):
        with st.expander("Bias and confounding warnings", expanded=True):
            for item in data.get("bias_and_confounding_warnings", []):
                st.warning(str(item))


def render_variables(variables: list[dict[str, Any]]) -> None:
    if not variables:
        st.info("No variables added yet.")
        return

    counts = pd.Series([v.get("role", "unspecified") for v in variables]).value_counts().to_dict()

    cols = st.columns(4)

    with cols[0]:
        metric_card("Variables", len(variables), "Total in codebook")

    with cols[1]:
        metric_card(
            "Outcomes",
            counts.get("dependent", 0) + counts.get("outcome", 0),
            "Dependent variables",
        )

    with cols[2]:
        metric_card(
            "Predictors",
            counts.get("independent", 0) + counts.get("exposure", 0),
            "Independent/exposure",
        )

    with cols[3]:
        metric_card(
            "Controls",
            counts.get("control", 0) + counts.get("covariate", 0),
            "Controls/covariates",
        )

    st.markdown("### Current variable dictionary")

    display_cols = [
        "name",
        "label",
        "role",
        "variable_type",
        "unit",
        "min_value",
        "max_value",
        "categories",
        "distribution",
        "mean",
        "sd",
    ]

    df = pd.DataFrame(variables)
    st.dataframe(df[[c for c in display_cols if c in df.columns]], use_container_width=True)


def render_framework(data: dict[str, Any]) -> None:
    framework = data.get("conceptual_framework", {}) or {}

    st.markdown("### Conceptual framework")
    card("Framework summary", framework.get("summary", "No framework summary returned."))

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Independent variables")
        chips(framework.get("independent_variables", []) or [])

        st.markdown("#### Control variables")
        chips(framework.get("control_variables", []) or [], "green")

    with col2:
        st.markdown("#### Dependent variables")
        chips(framework.get("dependent_variables", []) or [])

        st.markdown("#### Mediators / moderators")
        chips(
            (framework.get("mediators", []) or [])
            + (framework.get("moderators", []) or []),
            "amber",
        )

    mermaid_code = framework.get("mermaid")

    if mermaid_code:
        with st.expander("Conceptual framework diagram", expanded=True):
            render_mermaid(str(mermaid_code))

    hypotheses = data.get("hypotheses", []) or []

    if hypotheses:
        st.markdown("### Hypotheses")
        st.dataframe(pd.DataFrame(hypotheses), use_container_width=True)

    relationships = data.get("relationships", []) or []

    if relationships:
        st.markdown("### Relationship constraints for data generation")
        st.dataframe(pd.DataFrame(relationships), use_container_width=True)

    if data.get("analysis_plan"):
        st.markdown("### Analysis plan")
        for item in data.get("analysis_plan", []):
            st.markdown(f"- {item}")

    if data.get("warnings"):
        with st.expander("Framework warnings", expanded=False):
            for item in data.get("warnings", []):
                st.warning(str(item))


def render_mermaid(code: str) -> None:
    safe_code = html.escape(code)

    components.html(
        f"""
        <div class="mermaid">{safe_code}</div>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
        </script>
        """,
        height=320,
        scrolling=True,
    )

    with st.expander("Diagram code", expanded=False):
        st.code(code, language="mermaid")


def render_generation_schema(schema: dict[str, Any]) -> None:
    if not schema:
        return

    cols = st.columns(4)

    with cols[0]:
        metric_card("Sample size", schema.get("sample_size", ""), "Rows to generate")

    with cols[1]:
        metric_card("Variables", len(schema.get("variables", []) or []), "Columns")

    with cols[2]:
        metric_card("Relationships", len(schema.get("relationships", []) or []), "Constraints")

    with cols[3]:
        metric_card("Design", schema.get("study_design", ""), "Selected design")

    variables = schema.get("variables", []) or []

    if variables:
        with st.expander("Generation variable schema", expanded=False):
            st.dataframe(pd.DataFrame(variables), use_container_width=True)

    rels = schema.get("relationships", []) or []

    if rels:
        with st.expander("Relationship constraints", expanded=True):
            st.dataframe(pd.DataFrame(rels), use_container_width=True)


def render_dataset_profile(df: pd.DataFrame) -> None:
    if df is None:
        return

    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    cols = st.columns(4)

    with cols[0]:
        metric_card("Rows", len(df), "Synthetic observations")

    with cols[1]:
        metric_card("Columns", len(df.columns), "Variables")

    with cols[2]:
        metric_card("Numeric", len(numeric_cols), "Quantitative variables")

    with cols[3]:
        metric_card("Missing cells", int(df.isna().sum().sum()), "Total missing values")

    st.markdown("### Dataset preview")
    st.dataframe(df.head(50), use_container_width=True)

    if numeric_cols:
        with st.expander("Numeric profile", expanded=False):
            st.dataframe(df[numeric_cols].describe().T, use_container_width=True)


def render_validation_report(report: dict[str, Any]) -> None:
    if not report:
        return

    ok = report.get("ok")

    if ok:
        st.success("Mathematical validation passed.")
    else:
        st.error("Validation found issues. Review before using the dataset.")

    issues = report.get("issues", []) or []

    cols = st.columns(3)

    with cols[0]:
        metric_card(
            "Errors",
            sum(1 for x in issues if x.get("severity") == "error"),
            "Must fix",
        )

    with cols[1]:
        metric_card(
            "Warnings",
            sum(1 for x in issues if x.get("severity") == "warning"),
            "Review",
        )

    with cols[2]:
        metric_card(
            "Info",
            sum(1 for x in issues if x.get("severity") == "info"),
            "Notes",
        )

    if issues:
        st.markdown("### Validation issues")
        for issue in issues:
            severity = issue.get("severity", "info")
            msg = f"**{issue.get('location', 'dataset')}** — {issue.get('message', '')}"

            if severity == "error":
                st.error(msg)
            elif severity == "warning":
                st.warning(msg)
            else:
                st.info(msg)

    ai_review = report.get("ai_plausibility") or {}

    if ai_review:
        st.markdown("### AI plausibility review")

        status = ai_review.get("overall_plausibility", "not reviewed")
        card("Overall plausibility", str(status))

        for key, title in [
            ("major_issues", "Major issues"),
            ("minor_issues", "Minor issues"),
            ("recommended_fixes", "Recommended fixes"),
        ]:
            items = ai_review.get(key, []) or []

            if items:
                st.markdown(f"#### {title}")
                for item in items:
                    st.markdown(f"- {item}")

        comments = ai_review.get("variable_specific_comments", []) or []

        if comments:
            st.dataframe(pd.DataFrame(comments), use_container_width=True)


def json_expander(label: str, data: Any, expanded: bool = False) -> None:
    with st.expander(label, expanded=expanded):
        st.json(data, expanded=False)
