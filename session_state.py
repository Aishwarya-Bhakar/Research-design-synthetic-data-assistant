from __future__ import annotations

import streamlit as st


DEFAULTS = {
    "topic": "",
    "domain": "",
    "population": "",
    "sample_size": 100,
    "literature_summary": None,
    "design_suggestions": None,
    "selected_design": "cross-sectional",
    "variables": [],
    "framework": None,
    "codebook": None,
    "generation_schema": None,
    "dataset": None,
    "validation_report": None,
}


def init_state() -> None:
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_project() -> None:
    for key, value in DEFAULTS.items():
        st.session_state[key] = value
