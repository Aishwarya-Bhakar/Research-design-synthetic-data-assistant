from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

import config
from exporter import export_bundle
from session_state import init_state, reset_project
from step1_literature import research_literature
from step2_sample_size import validate_sample_size
from step3_design import suggest_research_designs
from step4_variables import suggest_variable
from step5_framework_hypotheses import build_framework_and_hypotheses
from step6_codebook import build_codebook, build_generation_schema
from step7_generator import generate_dataset
from step8_validator import validate_dataset
from ui_components import (
    apply_theme,
    render_landing_page,
    render_workspace_header,
    render_sidebar_status,
    render_step_nav,
    render_section_header,
    render_info_strip,
    render_metric_row,
    render_literature_summary,
    render_design_suggestions,
    render_variable_dictionary,
    render_framework,
    render_generation_schema,
    render_dataset_profile,
    render_validation_report,
    render_json_expander,
    render_soft_card,
    render_empty_state,
)


st.set_page_config(
    page_title="Research Design & Synthetic Data Studio",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)


STEPS = [
    {
        "key": "literature",
        "label": "Literature",
        "title": "Topic + Literature",
        "subtitle": "Search similar literature and convert it into a readable evidence brief.",
        "icon": "🔎",
    },
    {
        "key": "sample",
        "label": "Sample",
        "title": "Sample + Population",
        "subtitle": "Define the sample size, population, setting, and eligibility notes.",
        "icon": "👥",
    },
    {
        "key": "design",
        "label": "Design",
        "title": "Research Design",
        "subtitle": "Choose a suitable research design and understand design limitations.",
        "icon": "🧭",
    },
    {
        "key": "variables",
        "label": "Variables",
        "title": "Variables + Codebook",
        "subtitle": "Build variables, roles, definitions, coding, ranges, and distributions.",
        "icon": "📋",
    },
    {
        "key": "framework",
        "label": "Framework",
        "title": "Framework + Hypotheses",
        "subtitle": "Turn expected associations into a framework, hypotheses, and relationships.",
        "icon": "🧠",
    },
    {
        "key": "generate",
        "label": "Generate",
        "title": "Generate Synthetic Data",
        "subtitle": "Build the generation schema and create a synthetic research dataset.",
        "icon": "⚙️",
    },
    {
        "key": "validate",
        "label": "Validate",
        "title": "Validate + Export",
        "subtitle": "Run validation, review plausibility, and export the complete research bundle.",
        "icon": "✅",
    },
]


def ensure_app_state() -> None:
    defaults = {
        "view": "landing",
        "active_step": 0,
        "topic": "",
        "domain": "",
        "sample_size": 50,
        "population": "",
        "literature_summary": None,
        "design_suggestions": None,
        "selected_design": "cross-sectional",
        "variables": [],
        "pending_variable": None,
        "codebook": None,
        "framework": None,
        "generation_schema": None,
        "dataset": None,
        "validation_report": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def current_progress() -> list[tuple[str, bool]]:
    return [
        ("Literature brief", bool(st.session_state.literature_summary)),
        ("Sample defined", bool(st.session_state.sample_size)),
        ("Design selected", bool(st.session_state.selected_design)),
        ("Variables added", bool(st.session_state.variables)),
        ("Framework built", bool(st.session_state.framework)),
        ("Dataset generated", st.session_state.dataset is not None),
        ("Validation complete", bool(st.session_state.validation_report)),
    ]


def go_to_workspace(step: int = 0) -> None:
    st.session_state.view = "workspace"
    st.session_state.active_step = step
    st.rerun()


def go_to_landing() -> None:
    st.session_state.view = "landing"
    st.rerun()


def sidebar_controls() -> tuple[list[str], int]:
    with st.sidebar:
        st.markdown("## Study Studio")
        st.caption("Research design, codebook, synthetic data, and validation in one workflow.")

        st.divider()

        render_sidebar_status(
            groq_available=bool(config.GROQ_API_KEY),
            pubmed_available=bool(config.NCBI_EMAIL),
            model=config.GROQ_MODEL,
        )

        st.divider()

        st.markdown("### Literature sources")
        sources = st.multiselect(
            "Select sources",
            ["Crossref", "PubMed"],
            default=["Crossref"] + (["PubMed"] if config.NCBI_EMAIL else []),
            label_visibility="collapsed",
            help="Crossref is useful for broad research topics. PubMed is best for biomedical/public-health topics.",
        )

        max_results = st.slider(
            "Max results per source",
            min_value=3,
            max_value=20,
            value=int(config.LITERATURE_MAX_RESULTS),
        )

        st.divider()

        st.markdown("### Progress")
        for label, done in current_progress():
            st.markdown(f"{'✅' if done else '⬜'} {label}")

        st.divider()

        st.markdown("### Step navigation")
        for index, step in enumerate(STEPS):
            active = index == st.session_state.active_step
            button_label = f"{step['icon']} {step['label']}"
            if st.button(button_label, key=f"side_step_{index}", use_container_width=True, type="primary" if active else "secondary"):
                st.session_state.active_step = index
                st.rerun()

        st.divider()

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Home", use_container_width=True):
                go_to_landing()
        with c2:
            if st.button("Reset", use_container_width=True):
                reset_project()
                ensure_app_state()
                st.session_state.view = "landing"
                st.rerun()

        return sources, max_results


def render_literature_step(sources: list[str], max_results: int) -> None:
    render_section_header(
        "Step 1",
        "Research topic and similar literature",
        "Search the literature, summarize evidence, and identify candidate variables and relationships.",
        "🔎",
    )

    with st.container():
        col1, col2 = st.columns([1.35, 1])

        with col1:
            st.session_state.topic = st.text_area(
                "Research topic / study title",
                value=st.session_state.topic,
                placeholder="Example: Effect of social media use on sleep quality among undergraduate students",
                height=120,
            )

            st.session_state.domain = st.text_input(
                "Domain / discipline",
                value=st.session_state.domain,
                placeholder="Example: public health, education, psychology, management, nursing",
            )

            if st.button("Search literature and summarize", type="primary", use_container_width=True):
                if not st.session_state.topic.strip():
                    st.error("Enter a research topic first.")
                else:
                    with st.spinner("Searching literature and preparing your evidence brief..."):
                        st.session_state.literature_summary = research_literature(
                            topic=st.session_state.topic,
                            domain=st.session_state.domain,
                            sources=sources,
                            max_results=max_results,
                        )
                    st.success("Evidence brief generated.")

        with col2:
            render_soft_card(
                "What this step does",
                "The app searches similar literature, extracts a readable research brief, and suggests candidate independent, dependent, control, mediator, and moderator variables.",
                footer="Raw AI JSON is kept in Developer View only.",
                icon="📚",
            )

            render_info_strip(
                [
                    ("Sources", ", ".join(sources) if sources else "None selected"),
                    ("Max results", str(max_results)),
                    ("AI mode", "Groq" if config.GROQ_API_KEY else "Fallback"),
                ]
            )

    if st.session_state.literature_summary:
        render_literature_summary(st.session_state.literature_summary)
        render_json_expander("Developer View: Raw literature JSON", st.session_state.literature_summary)
    else:
        render_empty_state(
            "No evidence brief yet",
            "Enter a topic and click Search literature and summarize.",
            "🔎",
        )


def render_sample_step() -> None:
    render_section_header(
        "Step 2",
        "Sample size and population",
        "Define the sample size and describe the target population. These details guide the codebook and data generator.",
        "👥",
    )

    col1, col2 = st.columns([0.9, 1.6])

    with col1:
        st.session_state.sample_size = st.number_input(
            "Sample size N",
            min_value=1,
            max_value=1_000_000,
            value=int(st.session_state.sample_size),
            step=10,
        )

        sample_check = validate_sample_size(int(st.session_state.sample_size))

        if sample_check["ok"]:
            st.success(sample_check["message"])
        else:
            st.error(sample_check["message"])

    with col2:
        st.session_state.population = st.text_area(
            "Population, setting, inclusion/exclusion notes",
            value=st.session_state.population,
            placeholder=(
                "Example: Undergraduate students aged 18–25 years enrolled in urban colleges. "
                "Exclude students with diagnosed sleep disorders or current psychiatric medication use."
            ),
            height=155,
        )

    render_metric_row(
        [
            ("Sample size", st.session_state.sample_size, "Rows to generate"),
            ("Population note", "Added" if st.session_state.population else "Missing", "Eligibility context"),
            ("Current design", st.session_state.selected_design or "Not selected", "Selected in Step 3"),
        ]
    )


def render_design_step() -> None:
    render_section_header(
        "Step 3",
        "Research design selection",
        "Get design suggestions based on your topic, literature brief, and population.",
        "🧭",
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Suggest research designs", type="primary", use_container_width=True):
            with st.spinner("Suggesting suitable research designs..."):
                st.session_state.design_suggestions = suggest_research_designs(
                    topic=st.session_state.topic,
                    literature_summary=st.session_state.literature_summary or {},
                    population=st.session_state.population,
                )
            st.success("Design suggestions ready.")

    with col2:
        render_soft_card(
            "Design guidance",
            "The assistant ranks possible designs such as cross-sectional, cohort, case-control, RCT, quasi-experimental, diagnostic accuracy, qualitative, or mixed-methods.",
            icon="🧭",
        )

    if st.session_state.design_suggestions:
        render_design_suggestions(st.session_state.design_suggestions)

        options = [
            item.get("design", "")
            for item in st.session_state.design_suggestions.get("suggested_designs", [])
            if item.get("design")
        ]

        if not options:
            options = [
                "cross-sectional",
                "cohort",
                "case-control",
                "RCT",
                "quasi-experimental",
                "diagnostic accuracy",
                "qualitative",
                "mixed-methods",
            ]

        recommended = st.session_state.design_suggestions.get("recommended_design")
        default_index = options.index(recommended) if recommended in options else 0

        st.session_state.selected_design = st.selectbox(
            "Select final research design",
            options=options,
            index=default_index,
        )

        render_json_expander("Developer View: Raw design JSON", st.session_state.design_suggestions)

    else:
        st.session_state.selected_design = st.selectbox(
            "Select final research design",
            [
                "cross-sectional",
                "cohort",
                "case-control",
                "RCT",
                "quasi-experimental",
                "diagnostic accuracy",
                "qualitative",
                "mixed-methods",
            ],
            index=0,
        )


def render_variables_step() -> None:
    render_section_header(
        "Step 4",
        "Variables and codebook",
        "Add variables one by one. Review AI suggestions before adding them to the codebook.",
        "📋",
    )

    col1, col2 = st.columns([1.25, 1])

    with col1:
        new_var = st.text_input(
            "Variable name",
            placeholder="Example: daily_social_media_hours, sleep_quality_score, age, gender",
        )

    with col2:
        st.markdown("<div style='height: 1.78rem'></div>", unsafe_allow_html=True)
        if st.button("Suggest variable metadata", type="primary", use_container_width=True):
            if not new_var.strip():
                st.error("Enter a variable name.")
            else:
                with st.spinner("Preparing variable definition and coding suggestion..."):
                    st.session_state.pending_variable = suggest_variable(
                        variable_name=new_var,
                        topic=st.session_state.topic,
                        study_design=st.session_state.selected_design,
                        literature_summary=st.session_state.literature_summary,
                        existing_variables=st.session_state.variables,
                    )

    pending = st.session_state.get("pending_variable")

    if pending:
        st.markdown("### Review suggested variable")
        render_soft_card(
            pending.get("label") or pending.get("name", "Variable"),
            pending.get("definition", "No definition returned."),
            footer=f"Role: {pending.get('role', '')} • Type: {pending.get('variable_type', '')} • Distribution: {pending.get('distribution', '')}",
            icon="🧾",
        )

        with st.form("variable_form"):
            left, right = st.columns(2)

            with left:
                name = st.text_input("Name", value=pending.get("name", ""))
                label = st.text_input("Label", value=pending.get("label", ""))

                role_options = [
                    "independent",
                    "dependent",
                    "control",
                    "covariate",
                    "mediator",
                    "moderator",
                    "exposure",
                    "outcome",
                    "grouping",
                    "identifier",
                ]

                type_options = [
                    "continuous",
                    "integer",
                    "binary",
                    "categorical",
                    "ordinal",
                    "date",
                    "text",
                ]

                role_default = pending.get("role", "covariate")
                role = st.selectbox(
                    "Role",
                    role_options,
                    index=role_options.index(role_default) if role_default in role_options else 3,
                )

                type_default = pending.get("variable_type", "continuous")
                variable_type = st.selectbox(
                    "Variable type",
                    type_options,
                    index=type_options.index(type_default) if type_default in type_options else 0,
                )

                unit = st.text_input("Unit", value=pending.get("unit", ""))
                missing_rate = st.slider(
                    "Missing rate",
                    0.0,
                    0.8,
                    float(pending.get("missing_rate", 0.0)),
                    0.01,
                )

            with right:
                dist_options = [
                    "normal",
                    "lognormal",
                    "uniform",
                    "poisson",
                    "bernoulli",
                    "categorical",
                    "ordinal",
                    "date",
                    "text",
                ]

                min_value = st.number_input(
                    "Min value",
                    value=float(pending["min_value"]) if pending.get("min_value") is not None else 0.0,
                )
                use_min = st.checkbox(
                    "Use min value",
                    value=pending.get("min_value") is not None,
                )

                max_value = st.number_input(
                    "Max value",
                    value=float(pending["max_value"]) if pending.get("max_value") is not None else 100.0,
                )
                use_max = st.checkbox(
                    "Use max value",
                    value=pending.get("max_value") is not None,
                )

                dist_default = pending.get("distribution", "normal")
                distribution = st.selectbox(
                    "Distribution",
                    dist_options,
                    index=dist_options.index(dist_default) if dist_default in dist_options else 0,
                )

                mean = st.number_input(
                    "Mean",
                    value=float(pending["mean"]) if pending.get("mean") is not None else 50.0,
                )
                use_mean = st.checkbox("Use mean", value=pending.get("mean") is not None)

                sd = st.number_input(
                    "SD",
                    value=float(pending["sd"]) if pending.get("sd") is not None else 10.0,
                )
                use_sd = st.checkbox("Use SD", value=pending.get("sd") is not None)

            definition = st.text_area("Definition", value=pending.get("definition", ""), height=80)
            categories_text = st.text_input(
                "Categories, comma-separated",
                value=", ".join(pending.get("categories", [])),
            )
            coding = st.text_area("Coding", value=pending.get("coding", ""), height=70)
            notes = st.text_area("Notes", value=pending.get("notes", ""), height=70)

            submitted = st.form_submit_button("Add variable to codebook")

            if submitted:
                variable = {
                    "name": name,
                    "label": label,
                    "role": role,
                    "variable_type": variable_type,
                    "definition": definition,
                    "unit": unit,
                    "min_value": min_value if use_min else None,
                    "max_value": max_value if use_max else None,
                    "categories": [x.strip() for x in categories_text.split(",") if x.strip()],
                    "distribution": distribution,
                    "mean": mean if use_mean else None,
                    "sd": sd if use_sd else None,
                    "missing_rate": missing_rate,
                    "coding": coding,
                    "notes": notes,
                }

                st.session_state.variables.append(variable)
                st.session_state.pending_variable = None
                st.success(f"Added variable: {name}")
                st.rerun()

    render_variable_dictionary(st.session_state.variables)

    if st.session_state.variables:
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Build codebook", type="primary", use_container_width=True):
                st.session_state.codebook = build_codebook(st.session_state.variables)
                st.success("Codebook built.")
        with col2:
            st.caption("The codebook is used directly by the synthetic data generator.")

        if st.session_state.codebook:
            st.markdown("### Codebook")
            st.dataframe(pd.DataFrame(st.session_state.codebook), use_container_width=True)


def render_framework_step() -> None:
    render_section_header(
        "Step 5",
        "Conceptual framework and hypotheses",
        "Describe expected results. The assistant will create hypotheses and relationship constraints.",
        "🧠",
    )

    expected_text = st.text_area(
        "Expected results / hypotheses / associations to test",
        placeholder=(
            "Example: Higher daily social media use is expected to be associated with poorer sleep quality. "
            "Screen time before bed may mediate the relationship. Age, gender, and caffeine intake should be control variables."
        ),
        height=150,
    )

    if st.button("Build conceptual framework and hypotheses", type="primary"):
        if not st.session_state.variables:
            st.error("Add variables first.")
        else:
            with st.spinner("Building framework, hypotheses, and relationship constraints..."):
                st.session_state.framework = build_framework_and_hypotheses(
                    topic=st.session_state.topic,
                    study_design=st.session_state.selected_design,
                    variables=st.session_state.variables,
                    expected_results_text=expected_text,
                    literature_summary=st.session_state.literature_summary,
                )
            st.success("Framework generated.")

    if st.session_state.framework:
        render_framework(st.session_state.framework)
        render_json_expander("Developer View: Raw framework JSON", st.session_state.framework)
    else:
        render_empty_state(
            "No framework yet",
            "Add variables and describe expected associations to generate hypotheses.",
            "🧠",
        )


def render_generate_step() -> None:
    render_section_header(
        "Step 6",
        "Generate synthetic dataset",
        "Build the generation schema and create a synthetic dataset from the codebook and relationship constraints.",
        "⚙️",
    )

    col1, col2 = st.columns([0.75, 1.25])

    with col1:
        seed = st.number_input("Random seed", min_value=0, max_value=999999, value=42)

        if st.button("Build schema and generate data", type="primary", use_container_width=True):
            if not st.session_state.variables:
                st.error("Add variables first.")
            else:
                with st.spinner("Generating synthetic dataset..."):
                    relationships = []

                    if st.session_state.framework:
                        relationships = st.session_state.framework.get("relationships", [])

                    st.session_state.codebook = build_codebook(st.session_state.variables)
                    st.session_state.generation_schema = build_generation_schema(
                        study_title=st.session_state.topic,
                        sample_size=int(st.session_state.sample_size),
                        study_design=st.session_state.selected_design,
                        population=st.session_state.population,
                        variables=st.session_state.variables,
                        relationships=relationships,
                    )
                    st.session_state.dataset = generate_dataset(
                        st.session_state.generation_schema,
                        seed=int(seed),
                    )
                st.success("Dataset generated.")

    with col2:
        render_soft_card(
            "Generation note",
            "The app uses the current variables, selected design, sample size, and relationship constraints. You can validate and export the result in the next step.",
            icon="⚙️",
        )

    if st.session_state.generation_schema:
        render_generation_schema(st.session_state.generation_schema)
        render_json_expander("Developer View: Raw generation schema", st.session_state.generation_schema)

    if st.session_state.dataset is not None:
        render_dataset_profile(st.session_state.dataset)

        st.download_button(
            "Download CSV",
            data=st.session_state.dataset.to_csv(index=False).encode("utf-8"),
            file_name="synthetic_dataset.csv",
            mime="text/csv",
        )
    else:
        render_empty_state(
            "No dataset generated yet",
            "Add variables and click Build schema and generate data.",
            "⚙️",
        )


def render_validate_step() -> None:
    render_section_header(
        "Step 7",
        "Validate and export",
        "Run mathematical checks, optional Groq plausibility review, and export the research bundle.",
        "✅",
    )

    col1, col2 = st.columns([0.8, 1.2])

    with col1:
        run_ai_review = st.checkbox(
            "Run Groq AI plausibility review",
            value=bool(config.GROQ_API_KEY),
        )

        if st.button("Validate dataset", type="primary", use_container_width=True):
            if st.session_state.dataset is None or st.session_state.generation_schema is None:
                st.error("Generate data first.")
            else:
                with st.spinner("Validating dataset..."):
                    st.session_state.validation_report = validate_dataset(
                        st.session_state.dataset,
                        st.session_state.generation_schema,
                        run_ai_review=run_ai_review,
                    )
                st.success("Validation finished.")

    with col2:
        render_soft_card(
            "Validation checks",
            "The validator checks row count, ranges, categories, missingness, relationship alignment, and optional AI plausibility review.",
            icon="✅",
        )

    if st.session_state.validation_report:
        render_validation_report(st.session_state.validation_report)
        render_json_expander("Developer View: Raw validation JSON", st.session_state.validation_report)
    else:
        render_empty_state(
            "No validation report yet",
            "Generate a dataset first, then click Validate dataset.",
            "✅",
        )

    st.markdown("### Export bundle")

    if st.button("Create export ZIP"):
        if st.session_state.dataset is None:
            st.error("Generate dataset first.")
        else:
            output_dir = Path("outputs")
            zip_path = export_bundle(
                output_dir=output_dir,
                dataset=st.session_state.dataset,
                literature_summary=st.session_state.literature_summary or {},
                codebook=st.session_state.codebook or build_codebook(st.session_state.variables),
                generation_schema=st.session_state.generation_schema or {},
                validation_report=st.session_state.validation_report or {},
            )
            st.success(f"Export created: {zip_path}")
            st.download_button(
                "Download export ZIP",
                data=zip_path.read_bytes(),
                file_name=zip_path.name,
                mime="application/zip",
            )


def render_workspace() -> None:
    sources, max_results = sidebar_controls()

    render_workspace_header(
        topic=st.session_state.topic,
        design=st.session_state.selected_design,
        sample_size=st.session_state.sample_size,
        active_step=st.session_state.active_step,
        total_steps=len(STEPS),
    )

    selected = render_step_nav(STEPS, st.session_state.active_step)

    if selected is not None and selected != st.session_state.active_step:
        st.session_state.active_step = selected
        st.rerun()

    active_key = STEPS[st.session_state.active_step]["key"]

    if active_key == "literature":
        render_literature_step(sources, max_results)
    elif active_key == "sample":
        render_sample_step()
    elif active_key == "design":
        render_design_step()
    elif active_key == "variables":
        render_variables_step()
    elif active_key == "framework":
        render_framework_step()
    elif active_key == "generate":
        render_generate_step()
    elif active_key == "validate":
        render_validate_step()

    st.divider()

    nav_left, nav_mid, nav_right = st.columns([1, 3, 1])

    with nav_left:
        if st.session_state.active_step > 0:
            if st.button("← Previous", use_container_width=True):
                st.session_state.active_step -= 1
                st.rerun()

    with nav_right:
        if st.session_state.active_step < len(STEPS) - 1:
            if st.button("Next →", type="primary", use_container_width=True):
                st.session_state.active_step += 1
                st.rerun()


def main() -> None:
    apply_theme()
    init_state()
    ensure_app_state()

    if st.session_state.view == "landing":
        render_landing_page(
            on_start=lambda: go_to_workspace(0),
            on_demo=lambda: go_to_workspace(0),
        )
    else:
        render_workspace()


if __name__ == "__main__":
    main()
