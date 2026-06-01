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
    hero,
    section_header,
    render_literature_summary,
    render_design_suggestions,
    render_variables,
    render_framework,
    render_generation_schema,
    render_dataset_profile,
    render_validation_report,
    json_expander,
    card,
)


st.set_page_config(
    page_title="Research Design and Synthetic Data Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()
init_state()
hero()

with st.sidebar:
    st.markdown("### Project setup")
    sources = st.multiselect(
        "Literature sources",
        ["Crossref", "PubMed"],
        default=["Crossref"] + (["PubMed"] if config.NCBI_EMAIL else []),
        help="Crossref is general-purpose. PubMed is best for biomedical and public-health topics.",
    )
    max_results = st.slider("Max results per source", 3, 20, config.LITERATURE_MAX_RESULTS)

    st.divider()
    st.markdown("### AI status")
    st.text_input("Groq model", value=config.GROQ_MODEL, disabled=True)

    if config.GROQ_API_KEY:
        st.success("Groq API key detected")
    else:
        st.warning("GROQ_API_KEY missing. Fallback mode may be used.")

    if "PubMed" in sources and not config.NCBI_EMAIL:
        st.warning("PubMed needs NCBI_EMAIL in Streamlit secrets or .env.")

    st.divider()
    st.markdown("### Progress")
    progress_items = [
        ("Literature", bool(st.session_state.literature_summary)),
        ("Sample", bool(st.session_state.sample_size)),
        ("Design", bool(st.session_state.selected_design)),
        ("Variables", bool(st.session_state.variables)),
        ("Framework", bool(st.session_state.framework)),
        ("Dataset", st.session_state.dataset is not None),
        ("Validation", bool(st.session_state.validation_report)),
    ]

    for label, done in progress_items:
        st.markdown(f"{'✅' if done else '⬜'} {label}")

    st.divider()
    if st.button("Reset project", use_container_width=True):
        reset_project()
        st.rerun()


intro_cols = st.columns(4)

with intro_cols[0]:
    card("1. Evidence", "Search similar literature and convert JSON into a readable evidence brief.")

with intro_cols[1]:
    card("2. Design", "Select a suitable research design and sampling approach.")

with intro_cols[2]:
    card("3. Codebook", "Build variables, roles, definitions, ranges, categories and coding.")

with intro_cols[3]:
    card("4. Dataset", "Generate, validate and export synthetic research data.")


tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "1. Topic + Literature",
        "2. Sample + Population",
        "3. Design",
        "4. Variables + Codebook",
        "5. Framework + Hypotheses",
        "6. Generate Data",
        "7. Validate + Export",
    ]
)


with tab1:
    section_header(
        "Step 1",
        "Research topic and similar literature",
        "Enter a topic. The assistant will retrieve similar literature and show a readable research brief instead of raw JSON.",
    )

    st.session_state.topic = st.text_area(
        "Research topic / study title",
        value=st.session_state.topic,
        placeholder="Example: Effect of social media use on sleep quality among undergraduate students",
        height=90,
    )

    st.session_state.domain = st.text_input(
        "Domain / discipline",
        value=st.session_state.domain,
        placeholder="Example: public health, education, psychology, management, nursing",
    )

    col_a, col_b = st.columns([1, 2])

    with col_a:
        run_lit = st.button(
            "Search literature and summarize",
            type="primary",
            use_container_width=True,
        )

    with col_b:
        st.caption(
            "Tip: start with Crossref only for broad topics; add PubMed for biomedical/public-health topics."
        )

    if run_lit:
        if not st.session_state.topic.strip():
            st.error("Enter a research topic first.")
        else:
            with st.spinner("Searching literature and preparing evidence brief..."):
                st.session_state.literature_summary = research_literature(
                    topic=st.session_state.topic,
                    domain=st.session_state.domain,
                    sources=sources,
                    max_results=max_results,
                )

    if st.session_state.literature_summary:
        render_literature_summary(st.session_state.literature_summary)
        json_expander("Developer view: raw literature JSON", st.session_state.literature_summary)


with tab2:
    section_header(
        "Step 2",
        "Sample size and population",
        "Define the target sample and population frame. These values guide the generation schema.",
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.session_state.sample_size = st.number_input(
            "Sample size N",
            min_value=1,
            max_value=1_000_000,
            value=int(st.session_state.sample_size),
            step=10,
        )

    with col2:
        st.session_state.population = st.text_area(
            "Population, setting, inclusion/exclusion notes",
            value=st.session_state.population,
            placeholder=(
                "Example: Undergraduate students aged 18-25 years enrolled in urban colleges. "
                "Exclude students with diagnosed sleep disorders."
            ),
            height=115,
        )

    sample_check = validate_sample_size(int(st.session_state.sample_size))

    if sample_check["ok"]:
        st.success(sample_check["message"])
    else:
        st.error(sample_check["message"])


with tab3:
    section_header(
        "Step 3",
        "Research design selection",
        "Get ranked design options and select the final design for the synthetic research dataset.",
    )

    if st.button("Suggest research designs", type="primary"):
        with st.spinner("Suggesting research designs..."):
            st.session_state.design_suggestions = suggest_research_designs(
                topic=st.session_state.topic,
                literature_summary=st.session_state.literature_summary or {},
                population=st.session_state.population,
            )

    if st.session_state.design_suggestions:
        render_design_suggestions(st.session_state.design_suggestions)

        options = [
            item.get("design", "")
            for item in st.session_state.design_suggestions.get("suggested_designs", [])
            if item.get("design")
        ]

        if not options:
            options = ["cross-sectional", "cohort", "case-control", "RCT", "mixed-methods"]

        recommended = st.session_state.design_suggestions.get("recommended_design")
        default_index = options.index(recommended) if recommended in options else 0

        st.session_state.selected_design = st.selectbox(
            "Select final design",
            options=options,
            index=default_index,
        )

        json_expander("Developer view: raw design JSON", st.session_state.design_suggestions)

    else:
        st.session_state.selected_design = st.selectbox(
            "Select final design",
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


with tab4:
    section_header(
        "Step 4",
        "Variables and codebook",
        "Add variables one by one. Review AI suggestions before adding anything to the codebook.",
    )

    col_a, col_b = st.columns([2, 1])

    with col_a:
        new_var = st.text_input("Variable name", placeholder="Example: sleep_quality_score")

    with col_b:
        suggest_clicked = st.button(
            "Suggest metadata",
            type="primary",
            use_container_width=True,
        )

    if suggest_clicked:
        if not new_var.strip():
            st.error("Enter a variable name.")
        else:
            with st.spinner("Suggesting variable metadata..."):
                st.session_state["pending_variable"] = suggest_variable(
                    variable_name=new_var,
                    topic=st.session_state.topic,
                    study_design=st.session_state.selected_design,
                    literature_summary=st.session_state.literature_summary,
                    existing_variables=st.session_state.variables,
                )

    pending = st.session_state.get("pending_variable")

    if pending:
        st.markdown("### Review suggested variable")
        card(
            pending.get("label") or pending.get("name", "Variable"),
            pending.get("definition", ""),
            f"Role: {pending.get('role', '')} • Type: {pending.get('variable_type', '')}",
        )

        with st.form("variable_form"):
            c1, c2 = st.columns(2)

            with c1:
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

                role = st.selectbox(
                    "Role",
                    role_options,
                    index=role_options.index(pending.get("role", "covariate"))
                    if pending.get("role", "covariate") in role_options
                    else 3,
                )

                variable_type = st.selectbox(
                    "Variable type",
                    type_options,
                    index=type_options.index(pending.get("variable_type", "continuous"))
                    if pending.get("variable_type", "continuous") in type_options
                    else 0,
                )

                unit = st.text_input("Unit", value=pending.get("unit", ""))
                missing_rate = st.slider(
                    "Missing rate",
                    0.0,
                    0.8,
                    float(pending.get("missing_rate", 0.0)),
                    0.01,
                )

            with c2:
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
                    value=float(pending["min_value"])
                    if pending.get("min_value") is not None
                    else 0.0,
                )
                use_min = st.checkbox(
                    "Use min value",
                    value=pending.get("min_value") is not None,
                )

                max_value = st.number_input(
                    "Max value",
                    value=float(pending["max_value"])
                    if pending.get("max_value") is not None
                    else 100.0,
                )
                use_max = st.checkbox(
                    "Use max value",
                    value=pending.get("max_value") is not None,
                )

                distribution = st.selectbox(
                    "Distribution",
                    dist_options,
                    index=dist_options.index(pending.get("distribution", "normal"))
                    if pending.get("distribution", "normal") in dist_options
                    else 0,
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
                var = {
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

                st.session_state.variables.append(var)
                st.session_state["pending_variable"] = None
                st.success(f"Added variable: {name}")
                st.rerun()

    render_variables(st.session_state.variables)

    if st.session_state.variables:
        if st.button("Build codebook", type="primary"):
            st.session_state.codebook = build_codebook(st.session_state.variables)

        if st.session_state.codebook:
            st.markdown("### Codebook")
            st.dataframe(pd.DataFrame(st.session_state.codebook), use_container_width=True)


with tab5:
    section_header(
        "Step 5",
        "Conceptual framework and hypotheses",
        "Convert expected associations into hypotheses, framework structure and relationship constraints for generation.",
    )

    expected_text = st.text_area(
        "Expected results / hypotheses / associations to test",
        placeholder=(
            "Example: Higher social media use is expected to be associated with poorer sleep quality "
            "after adjusting for age and gender."
        ),
        height=125,
    )

    if st.button("Build conceptual framework and hypotheses", type="primary"):
        if not st.session_state.variables:
            st.error("Add variables first.")
        else:
            with st.spinner("Building framework and hypotheses..."):
                st.session_state.framework = build_framework_and_hypotheses(
                    topic=st.session_state.topic,
                    study_design=st.session_state.selected_design,
                    variables=st.session_state.variables,
                    expected_results_text=expected_text,
                    literature_summary=st.session_state.literature_summary,
                )

    if st.session_state.framework:
        render_framework(st.session_state.framework)
        json_expander("Developer view: raw framework JSON", st.session_state.framework)


with tab6:
    section_header(
        "Step 6",
        "Generate synthetic dataset",
        "Build the generation schema, create the synthetic dataset and review a quick data profile.",
    )

    seed = st.number_input("Random seed", min_value=0, max_value=999999, value=42)

    if st.button("Build schema and generate data", type="primary"):
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

    if st.session_state.generation_schema:
        st.markdown("### Generation schema summary")
        render_generation_schema(st.session_state.generation_schema)
        json_expander("Developer view: raw generation schema", st.session_state.generation_schema)

    if st.session_state.dataset is not None:
        render_dataset_profile(st.session_state.dataset)
        st.download_button(
            "Download CSV",
            data=st.session_state.dataset.to_csv(index=False).encode("utf-8"),
            file_name="synthetic_dataset.csv",
            mime="text/csv",
        )


with tab7:
    section_header(
        "Step 7",
        "Validate and export",
        "Run mathematical validation, optional Groq plausibility review, and export the complete research bundle.",
    )

    run_ai_review = st.checkbox(
        "Run Groq AI plausibility review",
        value=bool(config.GROQ_API_KEY),
    )

    if st.button("Validate dataset", type="primary"):
        if st.session_state.dataset is None or st.session_state.generation_schema is None:
            st.error("Generate data first.")
        else:
            with st.spinner("Validating dataset..."):
                st.session_state.validation_report = validate_dataset(
                    st.session_state.dataset,
                    st.session_state.generation_schema,
                    run_ai_review=run_ai_review,
                )

    if st.session_state.validation_report:
        render_validation_report(st.session_state.validation_report)
        json_expander("Developer view: raw validation JSON", st.session_state.validation_report)

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
