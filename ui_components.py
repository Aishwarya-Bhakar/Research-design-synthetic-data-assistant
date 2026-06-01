from __future__ import annotations

from typing import Any, Callable
import html

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


PRIMARY = "#2563EB"
PRIMARY_DARK = "#1E3A8A"
GREEN = "#22C55E"
TEAL = "#14B8A6"
SKY = "#38BDF8"
BLUE_SOFT = "#DBEAFE"
BG = "#EEF5FF"
CARD = "#FFFFFF"
TEXT = "#111827"
MUTED = "#6B7280"
BORDER = "#E5E7EB"


def _e(value: Any) -> str:
    return html.escape(str(value or ""))


def apply_theme() -> None:
    st.markdown(
        f"""
        <style>
            :root {{
                --primary: {PRIMARY};
                --primary-dark: {PRIMARY_DARK};
                --green: {GREEN};
                --teal: {TEAL};
                --sky: {SKY};
                --bg: {BG};
                --card: {CARD};
                --text: {TEXT};
                --muted: {MUTED};
                --border: {BORDER};
            }}

            html, body, [class*="css"] {{
                font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }}

            .block-container {{
                padding-top: 1rem;
                padding-bottom: 5rem;
                max-width: 1240px;
            }}

            [data-testid="stAppViewContainer"] {{
                background:
                    radial-gradient(circle at 8% 8%, rgba(34, 197, 94, 0.14), transparent 28rem),
                    radial-gradient(circle at 88% 12%, rgba(37, 99, 235, 0.16), transparent 30rem),
                    linear-gradient(180deg, #F8FBFF 0%, #EEF5FF 42%, #EAF2FF 100%);
            }}

            [data-testid="stSidebar"] > div:first-child {{
                background: linear-gradient(180deg, #FFFFFF 0%, #EFF6FF 100%);
                border-right: 1px solid rgba(148, 163, 184, 0.25);
            }}

            h1, h2, h3, h4 {{
                letter-spacing: -0.035em;
                color: var(--text);
            }}

            p {{
                line-height: 1.6;
            }}

            .landing-wrap {{
                max-width: 1180px;
                margin: 0 auto;
                padding: 1.4rem 0 3rem 0;
            }}

            .nav-bar {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 1rem 1.2rem;
                margin-bottom: 1.3rem;
                border-radius: 999px;
                background: rgba(255,255,255,0.72);
                border: 1px solid rgba(255,255,255,0.72);
                box-shadow: 0 18px 55px rgba(15, 23, 42, 0.08);
                backdrop-filter: blur(14px);
            }}

            .brand {{
                display: flex;
                align-items: center;
                gap: 0.7rem;
                font-weight: 900;
                color: #0F172A;
                letter-spacing: 0.02em;
            }}

            .brand-mark {{
                width: 2.35rem;
                height: 2.35rem;
                border-radius: 14px;
                background: linear-gradient(135deg, var(--green), var(--primary));
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: 900;
                box-shadow: 0 12px 24px rgba(37, 99, 235, 0.25);
            }}

            .nav-links {{
                display: flex;
                align-items: center;
                gap: 1.4rem;
                color: #1F2937;
                font-size: 0.95rem;
                font-weight: 650;
            }}

            .hero-panel {{
                position: relative;
                overflow: hidden;
                min-height: 560px;
                border-radius: 34px;
                padding: 3.2rem 3.2rem;
                background:
                    linear-gradient(90deg, rgba(255,255,255,0.92) 0%, rgba(255,255,255,0.72) 42%, rgba(219,234,254,0.52) 100%),
                    radial-gradient(circle at 72% 44%, rgba(20, 184, 166, 0.28), transparent 20rem),
                    radial-gradient(circle at 86% 12%, rgba(251, 191, 36, 0.24), transparent 18rem),
                    linear-gradient(135deg, #FFFFFF 0%, #E0F2FE 45%, #FDECC8 100%);
                border: 1px solid rgba(255,255,255,0.92);
                box-shadow: 0 35px 90px rgba(15, 23, 42, 0.12);
            }}

            .hero-grid {{
                display: grid;
                grid-template-columns: 0.95fr 1.05fr;
                gap: 2rem;
                align-items: center;
            }}

            .hero-eyebrow {{
                color: var(--primary);
                font-weight: 900;
                letter-spacing: 0.12em;
                text-transform: uppercase;
                font-size: 0.78rem;
                margin-bottom: 1rem;
            }}

            .hero-title {{
                font-size: clamp(2.4rem, 5vw, 4.4rem);
                line-height: 1.05;
                font-weight: 950;
                color: #050816;
                margin-bottom: 1.2rem;
            }}

            .hero-subtitle {{
                max-width: 35rem;
                color: #374151;
                font-size: 1.08rem;
                line-height: 1.75;
                margin-bottom: 1.6rem;
            }}

            .hero-actions {{
                display: flex;
                gap: 1rem;
                align-items: center;
                flex-wrap: wrap;
                margin-top: 1.3rem;
            }}

            .hero-badges {{
                display: flex;
                gap: 0.55rem;
                flex-wrap: wrap;
                margin-top: 1.8rem;
            }}

            .hero-badge {{
                background: rgba(255,255,255,0.72);
                border: 1px solid rgba(148, 163, 184, 0.25);
                color: #0F172A;
                border-radius: 999px;
                padding: 0.45rem 0.72rem;
                font-weight: 750;
                font-size: 0.82rem;
                box-shadow: 0 10px 25px rgba(15,23,42,0.06);
            }}

            .visual-stage {{
                min-height: 420px;
                position: relative;
            }}

            .globe {{
                position: absolute;
                right: 3%;
                top: 8%;
                width: 390px;
                height: 390px;
                border-radius: 50%;
                background:
                    radial-gradient(circle at 35% 35%, rgba(255,255,255,0.92), rgba(125,211,252,0.25) 36%, rgba(37,99,235,0.16) 62%, rgba(20,184,166,0.08) 100%);
                border: 1px solid rgba(255,255,255,0.72);
                box-shadow:
                    inset 0 0 48px rgba(255,255,255,0.9),
                    0 35px 70px rgba(37,99,235,0.17);
            }}

            .globe:before {{
                content: "";
                position: absolute;
                inset: 2.2rem;
                border-radius: 50%;
                border: 1px dashed rgba(37,99,235,0.35);
            }}

            .globe:after {{
                content: "";
                position: absolute;
                inset: 4.8rem 2.4rem;
                border-radius: 50%;
                border-left: 1px solid rgba(20,184,166,0.35);
                border-right: 1px solid rgba(20,184,166,0.22);
            }}

            .person-row {{
                position: absolute;
                right: 10%;
                top: 42%;
                display: flex;
                gap: 0.55rem;
                align-items: end;
                z-index: 2;
            }}

            .person {{
                width: 2.15rem;
                height: 5.2rem;
                border-radius: 1.2rem 1.2rem 0.5rem 0.5rem;
                background: linear-gradient(180deg, rgba(255,255,255,0.88), rgba(37,99,235,0.24));
                box-shadow: 0 10px 25px rgba(15,23,42,0.08);
                position: relative;
            }}

            .person:before {{
                content: "";
                position: absolute;
                top: -1.35rem;
                left: 0.35rem;
                width: 1.45rem;
                height: 1.45rem;
                border-radius: 50%;
                background: rgba(255,255,255,0.92);
                border: 1px solid rgba(37,99,235,0.18);
            }}

            .floating-card {{
                position: absolute;
                z-index: 3;
                border-radius: 22px;
                background: rgba(255,255,255,0.78);
                border: 1px solid rgba(255,255,255,0.86);
                box-shadow: 0 22px 55px rgba(15,23,42,0.12);
                backdrop-filter: blur(16px);
                padding: 1rem;
            }}

            .float-one {{
                left: 5%;
                bottom: 10%;
                width: 210px;
            }}

            .float-two {{
                right: 0;
                bottom: 3%;
                width: 230px;
            }}

            .float-three {{
                left: 20%;
                top: 10%;
                width: 190px;
            }}

            .float-title {{
                font-weight: 900;
                color: #0F172A;
                margin-bottom: 0.3rem;
            }}

            .float-text {{
                color: #64748B;
                font-size: 0.82rem;
                line-height: 1.45;
            }}

            .feature-grid {{
                display: grid;
                grid-template-columns: 1.15fr 0.85fr 0.85fr;
                gap: 1.2rem;
                margin-top: 1.5rem;
            }}

            .feature-large, .feature-card {{
                background: rgba(255,255,255,0.82);
                border: 1px solid rgba(255,255,255,0.86);
                border-radius: 26px;
                box-shadow: 0 22px 55px rgba(15, 23, 42, 0.08);
                padding: 1.3rem;
                min-height: 150px;
            }}

            .feature-large {{
                min-height: 320px;
                background:
                    radial-gradient(circle at 35% 30%, rgba(37,99,235,0.13), transparent 12rem),
                    rgba(255,255,255,0.86);
            }}

            .feature-card.blue {{
                background:
                    radial-gradient(circle at 80% 20%, rgba(255,255,255,0.33), transparent 8rem),
                    linear-gradient(135deg, #2563EB, #38BDF8);
                color: white;
            }}

            .feature-card.blue h4,
            .feature-card.blue p {{
                color: white;
            }}

            .feature-icon {{
                width: 3rem;
                height: 3rem;
                border-radius: 18px;
                background: #DBEAFE;
                color: #1D4ED8;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.35rem;
                margin-bottom: 1rem;
            }}

            .feature-card.blue .feature-icon {{
                background: rgba(255,255,255,0.24);
                color: white;
            }}

            .feature-title {{
                font-size: 1.05rem;
                font-weight: 900;
                margin-bottom: 0.35rem;
            }}

            .feature-text {{
                color: #64748B;
                line-height: 1.55;
                font-size: 0.92rem;
            }}

            .workspace-header {{
                border-radius: 28px;
                padding: 1.55rem 1.65rem;
                background:
                    radial-gradient(circle at 96% 10%, rgba(56,189,248,0.28), transparent 18rem),
                    linear-gradient(135deg, #FFFFFF 0%, #EFF6FF 100%);
                border: 1px solid rgba(255,255,255,0.86);
                box-shadow: 0 22px 55px rgba(15, 23, 42, 0.08);
                margin-bottom: 1.15rem;
            }}

            .workspace-title {{
                font-size: 2rem;
                font-weight: 950;
                color: #0F172A;
                margin: 0;
            }}

            .workspace-subtitle {{
                color: #64748B;
                margin-top: 0.45rem;
                line-height: 1.55;
            }}

            .workspace-pill {{
                display: inline-block;
                margin: 0.25rem 0.35rem 0.25rem 0;
                padding: 0.42rem 0.7rem;
                border-radius: 999px;
                background: rgba(37,99,235,0.08);
                border: 1px solid rgba(37,99,235,0.16);
                color: #1E40AF;
                font-weight: 800;
                font-size: 0.82rem;
            }}

            .step-nav {{
                display: grid;
                grid-template-columns: repeat(7, minmax(0, 1fr));
                gap: 0.55rem;
                margin: 1rem 0 1.2rem 0;
            }}

            .step-box {{
                border-radius: 20px;
                padding: 0.86rem 0.75rem;
                background: rgba(255,255,255,0.78);
                border: 1px solid rgba(148,163,184,0.22);
                text-align: center;
                box-shadow: 0 12px 28px rgba(15,23,42,0.05);
            }}

            .step-box.active {{
                background: linear-gradient(135deg, #2563EB, #14B8A6);
                color: white;
                border-color: transparent;
                box-shadow: 0 18px 36px rgba(37,99,235,0.25);
            }}

            .step-box .step-icon {{
                font-size: 1.25rem;
                margin-bottom: 0.2rem;
            }}

            .step-box .step-label {{
                font-size: 0.8rem;
                font-weight: 900;
            }}

            .section-card {{
                border-radius: 26px;
                padding: 1.35rem 1.45rem;
                background: rgba(255,255,255,0.86);
                border: 1px solid rgba(255,255,255,0.9);
                box-shadow: 0 18px 45px rgba(15,23,42,0.07);
                margin-bottom: 1rem;
            }}

            .section-eyebrow {{
                color: var(--primary);
                font-size: 0.76rem;
                font-weight: 950;
                letter-spacing: 0.12em;
                text-transform: uppercase;
                margin-bottom: 0.25rem;
            }}

            .section-title {{
                color: #0F172A;
                font-size: 1.5rem;
                font-weight: 950;
                margin-bottom: 0.25rem;
            }}

            .section-subtitle {{
                color: #64748B;
                line-height: 1.6;
            }}

            .soft-card {{
                border-radius: 24px;
                padding: 1.15rem 1.2rem;
                background: rgba(255,255,255,0.88);
                border: 1px solid rgba(255,255,255,0.92);
                box-shadow: 0 16px 40px rgba(15,23,42,0.07);
                margin-bottom: 0.9rem;
            }}

            .soft-card h4 {{
                margin: 0 0 0.35rem 0;
                font-size: 1.05rem;
                font-weight: 950;
                color: #0F172A;
            }}

            .soft-card p {{
                margin: 0.1rem 0;
                color: #64748B;
                line-height: 1.6;
            }}

            .card-footer {{
                margin-top: 0.8rem;
                padding-top: 0.7rem;
                border-top: 1px solid rgba(148,163,184,0.20);
                color: #64748B;
                font-size: 0.86rem;
                font-weight: 650;
            }}

            .card-icon {{
                display: inline-flex;
                width: 2.35rem;
                height: 2.35rem;
                border-radius: 16px;
                background: #DBEAFE;
                color: #1D4ED8;
                align-items: center;
                justify-content: center;
                font-size: 1.2rem;
                margin-bottom: 0.75rem;
            }}

            .metric-card {{
                border-radius: 22px;
                padding: 1rem 1.1rem;
                background: rgba(255,255,255,0.86);
                border: 1px solid rgba(255,255,255,0.92);
                box-shadow: 0 15px 34px rgba(15,23,42,0.06);
            }}

            .metric-label {{
                color: #64748B;
                font-weight: 850;
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }}

            .metric-value {{
                margin-top: 0.15rem;
                color: #0F172A;
                font-size: 1.55rem;
                font-weight: 950;
            }}

            .metric-help {{
                margin-top: 0.1rem;
                color: #94A3B8;
                font-size: 0.82rem;
            }}

            .chip {{
                display: inline-block;
                margin: 0.16rem;
                padding: 0.36rem 0.68rem;
                border-radius: 999px;
                background: #DBEAFE;
                color: #1D4ED8;
                border: 1px solid #BFDBFE;
                font-weight: 800;
                font-size: 0.82rem;
            }}

            .chip.green {{
                background: #DCFCE7;
                color: #15803D;
                border-color: #BBF7D0;
            }}

            .chip.amber {{
                background: #FEF3C7;
                color: #92400E;
                border-color: #FDE68A;
            }}

            .chip.red {{
                background: #FEE2E2;
                color: #B91C1C;
                border-color: #FECACA;
            }}

            .empty-state {{
                text-align: center;
                padding: 2.5rem 1.5rem;
                border-radius: 28px;
                background: rgba(255,255,255,0.70);
                border: 1px dashed rgba(37,99,235,0.28);
                color: #64748B;
                margin: 1rem 0;
            }}

            .empty-icon {{
                font-size: 2.4rem;
                margin-bottom: 0.65rem;
            }}

            .empty-title {{
                color: #0F172A;
                font-size: 1.2rem;
                font-weight: 950;
                margin-bottom: 0.25rem;
            }}

            .info-strip {{
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 0.6rem;
                margin: 0.7rem 0;
            }}

            .info-item {{
                border-radius: 18px;
                padding: 0.85rem;
                background: rgba(255,255,255,0.72);
                border: 1px solid rgba(148,163,184,0.18);
            }}

            .info-label {{
                color: #64748B;
                font-size: 0.75rem;
                font-weight: 850;
                text-transform: uppercase;
            }}

            .info-value {{
                color: #0F172A;
                font-weight: 900;
                margin-top: 0.15rem;
            }}

            div[data-testid="stDataFrame"] {{
                border-radius: 18px;
                overflow: hidden;
                border: 1px solid rgba(148,163,184,0.22);
            }}

            .stButton > button {{
                border-radius: 999px !important;
                font-weight: 850 !important;
            }}

            .stTextInput input,
            .stTextArea textarea,
            .stNumberInput input {{
                border-radius: 16px !important;
            }}

            @media (max-width: 900px) {{
                .hero-grid {{
                    grid-template-columns: 1fr;
                }}
                .visual-stage {{
                    min-height: 320px;
                }}
                .globe {{
                    width: 280px;
                    height: 280px;
                }}
                .feature-grid {{
                    grid-template-columns: 1fr;
                }}
                .step-nav {{
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                }}
                .nav-links {{
                    display: none;
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_landing_page(on_start: Callable[[], None], on_demo: Callable[[], None]) -> None:
    st.markdown('<div class="landing-wrap">', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="nav-bar">
          <div class="brand">
            <div class="brand-mark">R</div>
            <div>ResearchPath Studio</div>
          </div>
          <div class="nav-links">
            <span>Evidence</span>
            <span>Design</span>
            <span>Codebook</span>
            <span>Data</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-panel">
          <div class="hero-grid">
            <div>
              <div class="hero-eyebrow">AI-assisted research workflow</div>
              <div class="hero-title">Design better research. Generate smarter synthetic data.</div>
              <div class="hero-subtitle">
                Move from research topic to literature brief, research design, variables, hypotheses,
                codebook, synthetic dataset, validation report, and export bundle — in one guided studio.
              </div>
              <div class="hero-badges">
                <span class="hero-badge">Literature-grounded</span>
                <span class="hero-badge">Codebook-ready</span>
                <span class="hero-badge">Validated synthetic data</span>
              </div>
            </div>
            <div class="visual-stage">
              <div class="globe"></div>
              <div class="person-row">
                <div class="person" style="height:4.6rem"></div>
                <div class="person" style="height:5.6rem"></div>
                <div class="person" style="height:6.3rem"></div>
                <div class="person" style="height:5.2rem"></div>
                <div class="person" style="height:4.7rem"></div>
              </div>
              <div class="floating-card float-three">
                <div class="float-title">Evidence Brief</div>
                <div class="float-text">Summarize similar studies and extract gaps, variables, and relationships.</div>
              </div>
              <div class="floating-card float-one">
                <div class="float-title">Research Design</div>
                <div class="float-text">Compare designs and choose the best structure for your study.</div>
              </div>
              <div class="floating-card float-two">
                <div class="float-title">Synthetic Dataset</div>
                <div class="float-text">Generate and validate research-ready synthetic data with a codebook.</div>
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1.05, 0.95, 0.95])

    with col1:
        st.markdown("")

        if st.button("Start New Research Project  →", type="primary", use_container_width=True):
            on_start()

    with col2:
        st.markdown("")

        if st.button("Open Workspace", use_container_width=True):
            on_demo()

    with col3:
        st.markdown("")

        st.caption("No patient data required. Built for synthetic research planning and teaching workflows.")

    st.markdown(
        """
        <div class="feature-grid">
          <div class="feature-large">
            <div class="feature-icon">📋</div>
            <div class="feature-title">Research assistant workflow</div>
            <div class="feature-text">
              Build a complete research plan from scratch: literature brief, variable roles,
              conceptual framework, hypotheses, codebook, synthetic data, validation and export.
            </div>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🔎</div>
            <div class="feature-title">Literature first</div>
            <div class="feature-text">
              Search Crossref and PubMed, then convert AI JSON into readable evidence summaries.
            </div>
          </div>
          <div class="feature-card blue">
            <div class="feature-icon">🧬</div>
            <div class="feature-title">Synthetic data</div>
            <div class="feature-text">
              Generate structured datasets from codebook definitions and relationship constraints.
            </div>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <div class="feature-title">Frameworks</div>
            <div class="feature-text">
              Convert expected associations into hypotheses, mediators, moderators, and analysis plans.
            </div>
          </div>
          <div class="feature-card">
            <div class="feature-icon">✅</div>
            <div class="feature-title">Validation</div>
            <div class="feature-text">
              Check mathematical ranges, categories, missingness, relationships and plausibility.
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


def render_workspace_header(topic: str, design: str, sample_size: int, active_step: int, total_steps: int) -> None:
    topic_text = topic.strip() if topic else "Untitled research project"

    st.markdown(
        f"""
        <div class="workspace-header">
          <div class="workspace-title">Research Workspace</div>
          <div class="workspace-subtitle">
            {_e(topic_text)}
          </div>
          <div style="margin-top:0.8rem">
            <span class="workspace-pill">Step {active_step + 1} of {total_steps}</span>
            <span class="workspace-pill">Design: {_e(design or "Not selected")}</span>
            <span class="workspace-pill">N = {_e(sample_size)}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_status(groq_available: bool, pubmed_available: bool, model: str) -> None:
    st.markdown("### System status")

    if groq_available:
        st.success("Groq AI connected")
    else:
        st.warning("Groq key missing")

    if pubmed_available:
        st.success("PubMed enabled")
    else:
        st.info("PubMed disabled until NCBI_EMAIL is set")

    st.caption(f"Model: {model}")


def render_step_nav(steps: list[dict[str, str]], active_index: int) -> int | None:
    st.markdown('<div class="step-nav">', unsafe_allow_html=True)

    html_blocks = []

    for i, step in enumerate(steps):
        active = " active" if i == active_index else ""
        html_blocks.append(
            f"""
            <div class="step-box{active}">
                <div class="step-icon">{_e(step.get("icon", ""))}</div>
                <div class="step-label">{_e(step.get("label", ""))}</div>
            </div>
            """
        )

    st.markdown("".join(html_blocks), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    cols = st.columns(len(steps))
    selected = None

    for i, step in enumerate(steps):
        with cols[i]:
            if st.button(step["label"], key=f"top_step_{i}", use_container_width=True):
                selected = i

    return selected


def render_section_header(step: str, title: str, subtitle: str, icon: str = "") -> None:
    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-eyebrow">{_e(step)}</div>
            <div class="section-title">{_e(icon)} {_e(title)}</div>
            <div class="section-subtitle">{_e(subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_soft_card(title: str, body: str, footer: str = "", icon: str = "✨") -> None:
    footer_html = f'<div class="card-footer">{_e(footer)}</div>' if footer else ""

    st.markdown(
        f"""
        <div class="soft-card">
            <div class="card-icon">{_e(icon)}</div>
            <h4>{_e(title)}</h4>
            <p>{_e(body)}</p>
            {footer_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(title: str, body: str, icon: str = "📝") -> None:
    st.markdown(
        f"""
        <div class="empty-state">
            <div class="empty-icon">{_e(icon)}</div>
            <div class="empty-title">{_e(title)}</div>
            <div>{_e(body)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_info_strip(items: list[tuple[str, str]]) -> None:
    html_items = []

    for label, value in items:
        html_items.append(
            f"""
            <div class="info-item">
                <div class="info-label">{_e(label)}</div>
                <div class="info-value">{_e(value)}</div>
            </div>
            """
        )

    st.markdown(f'<div class="info-strip">{"".join(html_items)}</div>', unsafe_allow_html=True)


def render_metric_card(label: str, value: Any, help_text: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{_e(label)}</div>
            <div class="metric-value">{_e(value)}</div>
            <div class="metric-help">{_e(help_text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_row(items: list[tuple[str, Any, str]]) -> None:
    cols = st.columns(len(items))

    for col, item in zip(cols, items):
        label, value, help_text = item
        with col:
            render_metric_card(label, value, help_text)


def render_chips(items: list[Any], kind: str = "blue") -> None:
    if not items:
        st.caption("None listed.")
        return

    class_name = "chip"

    if kind == "green":
        class_name = "chip green"
    elif kind == "amber":
        class_name = "chip amber"
    elif kind == "red":
        class_name = "chip red"

    chips_html = "".join(
        f'<span class="{class_name}">{_e(item)}</span>'
        for item in items
        if str(item).strip()
    )

    st.markdown(chips_html, unsafe_allow_html=True)


def render_literature_summary(summary: dict[str, Any]) -> None:
    papers = summary.get("papers", []) or []
    paper_count = summary.get("paper_count") or len(papers)

    render_metric_row(
        [
            ("Evidence records", paper_count, "Retrieved / summarized"),
            ("Candidate IVs", len(summary.get("candidate_independent_variables", []) or []), "Predictors"),
            ("Candidate DVs", len(summary.get("candidate_dependent_variables", []) or []), "Outcomes"),
            ("Relationships", len(summary.get("candidate_relationships", []) or []), "Found or suggested"),
        ]
    )

    st.markdown("### Evidence brief")
    render_soft_card(
        "Readable evidence summary",
        summary.get("evidence_summary") or "No narrative evidence summary returned.",
        icon="📚",
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Candidate independent variables")
        render_chips(summary.get("candidate_independent_variables", []) or [])

        st.markdown("#### Candidate control variables")
        render_chips(summary.get("candidate_control_variables", []) or [], "green")

    with col2:
        st.markdown("#### Candidate dependent variables")
        render_chips(summary.get("candidate_dependent_variables", []) or [])

        st.markdown("#### Candidate mediators / moderators")
        render_chips(
            (summary.get("candidate_mediators", []) or [])
            + (summary.get("candidate_moderators", []) or []),
            "amber",
        )

    relationships = summary.get("candidate_relationships", []) or []

    if relationships:
        st.markdown("#### Candidate relationships")
        for item in relationships[:10]:
            st.markdown(f"- {item}")

    gaps = summary.get("evidence_gaps", []) or []

    if gaps:
        with st.expander("Evidence gaps", expanded=False):
            for gap in gaps:
                st.markdown(f"- {gap}")

    warnings = summary.get("warnings", []) or []

    if warnings:
        with st.expander("Warnings", expanded=True):
            for warning in warnings:
                st.warning(str(warning))

    if papers:
        st.markdown("### Paper cards")

        for paper in papers[:6]:
            title = paper.get("title") or "Untitled paper"
            meta = " • ".join(
                str(x)
                for x in [paper.get("source"), paper.get("year"), paper.get("journal")]
                if x
            )

            body = (
                paper.get("summary")
                or "; ".join(map(str, paper.get("key_findings", []) or []))
                or paper.get("url")
                or "No summary available."
            )

            render_soft_card(title, str(body), footer=meta, icon="📄")

        with st.expander("All papers table", expanded=False):
            st.dataframe(pd.DataFrame(papers), use_container_width=True)


def render_design_suggestions(data: dict[str, Any]) -> None:
    recommended = data.get("recommended_design") or "Not specified"
    reason = data.get("reason_for_recommendation") or "No reason returned."

    render_soft_card("Recommended design", recommended, reason, icon="🧭")

    designs = data.get("suggested_designs", []) or []

    if designs:
        st.markdown("### Design options")

        cols = st.columns(min(3, len(designs)))

        for index, design in enumerate(designs):
            with cols[index % len(cols)]:
                score = design.get("fit_score", "")
                footer = f"Fit score: {score}" if score != "" else ""
                render_soft_card(
                    design.get("design", "Design option"),
                    design.get("reason", ""),
                    footer=footer,
                    icon="📌",
                )

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


def render_variable_dictionary(variables: list[dict[str, Any]]) -> None:
    if not variables:
        render_empty_state(
            "No variables added yet",
            "Add a variable name and ask the assistant to suggest metadata.",
            "📋",
        )
        return

    role_counts = pd.Series([v.get("role", "unspecified") for v in variables]).value_counts().to_dict()

    render_metric_row(
        [
            ("Variables", len(variables), "Total added"),
            ("Predictors", role_counts.get("independent", 0) + role_counts.get("exposure", 0), "IV/exposure"),
            ("Outcomes", role_counts.get("dependent", 0) + role_counts.get("outcome", 0), "DV/outcome"),
            ("Controls", role_counts.get("control", 0) + role_counts.get("covariate", 0), "Adjustment variables"),
        ]
    )

    st.markdown("### Variable dictionary")

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

    render_soft_card(
        "Conceptual framework summary",
        framework.get("summary", "No framework summary returned."),
        icon="🧠",
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Independent variables")
        render_chips(framework.get("independent_variables", []) or [])

        st.markdown("#### Control variables")
        render_chips(framework.get("control_variables", []) or [], "green")

    with col2:
        st.markdown("#### Dependent variables")
        render_chips(framework.get("dependent_variables", []) or [])

        st.markdown("#### Mediators / moderators")
        render_chips(
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
        st.markdown("### Relationship constraints")
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
        height=340,
        scrolling=True,
    )

    with st.expander("Diagram code", expanded=False):
        st.code(code, language="mermaid")


def render_generation_schema(schema: dict[str, Any]) -> None:
    if not schema:
        return

    render_metric_row(
        [
            ("Sample size", schema.get("sample_size", ""), "Rows"),
            ("Variables", len(schema.get("variables", []) or []), "Columns"),
            ("Relationships", len(schema.get("relationships", []) or []), "Constraints"),
            ("Design", schema.get("study_design", ""), "Selected"),
        ]
    )

    variables = schema.get("variables", []) or []

    if variables:
        with st.expander("Generation variable schema", expanded=False):
            st.dataframe(pd.DataFrame(variables), use_container_width=True)

    relationships = schema.get("relationships", []) or []

    if relationships:
        with st.expander("Relationship constraints", expanded=True):
            st.dataframe(pd.DataFrame(relationships), use_container_width=True)


def render_dataset_profile(df: pd.DataFrame) -> None:
    if df is None:
        return

    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    render_metric_row(
        [
            ("Rows", len(df), "Synthetic observations"),
            ("Columns", len(df.columns), "Variables"),
            ("Numeric", len(numeric_cols), "Quantitative variables"),
            ("Missing cells", int(df.isna().sum().sum()), "Total"),
        ]
    )

    st.markdown("### Dataset preview")
    st.dataframe(df.head(50), use_container_width=True)

    if numeric_cols:
        with st.expander("Numeric profile", expanded=False):
            st.dataframe(df[numeric_cols].describe().T, use_container_width=True)


def render_validation_report(report: dict[str, Any]) -> None:
    if not report:
        return

    ok = report.get("ok")
    issues = report.get("issues", []) or []

    if ok:
        st.success("Mathematical validation passed.")
    else:
        st.error("Validation found issues. Review before using the dataset.")

    render_metric_row(
        [
            ("Errors", sum(1 for x in issues if x.get("severity") == "error"), "Must fix"),
            ("Warnings", sum(1 for x in issues if x.get("severity") == "warning"), "Review"),
            ("Info", sum(1 for x in issues if x.get("severity") == "info"), "Notes"),
        ]
    )

    if issues:
        st.markdown("### Validation issues")

        for issue in issues:
            severity = issue.get("severity", "info")
            message = f"**{issue.get('location', 'dataset')}** — {issue.get('message', '')}"

            if severity == "error":
                st.error(message)
            elif severity == "warning":
                st.warning(message)
            else:
                st.info(message)

    ai_review = report.get("ai_plausibility") or {}

    if ai_review:
        st.markdown("### AI plausibility review")

        render_soft_card(
            "Overall plausibility",
            str(ai_review.get("overall_plausibility", "not reviewed")),
            icon="🧬",
        )

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


def render_json_expander(label: str, data: Any, expanded: bool = False) -> None:
    with st.expander(label, expanded=expanded):
        st.json(data, expanded=False)
