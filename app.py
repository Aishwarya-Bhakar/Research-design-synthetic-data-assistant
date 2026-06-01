from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

import config
from session_state import init_state, reset_project
from step1_literature import research_literature
from step2_sample_size import validate_sample_size
from step3_design import suggest_research_designs
from step4_variables import suggest_variable
from step5_framework_hypotheses import build_framework_and_hypotheses
from step6_codebook import build_codebook, build_generation_schema
from step7_generator import generate_dataset
from step8_validator import validate_dataset
from exporter import export_bundle


st.set_page_config(
    page_title="Research Design and Synthetic Data Assistant",
    page_icon="📚",
    layout="wide",
)

init_state()

st.title("📚 Research Design and Synthetic Data Assistant")
st.caption("Literature search + Groq AI + research design + conceptual framework + codebook + synthetic data generation.")

with st.sidebar:
    st.header("Settings")
    sources = st.multiselect(
        "Literature sources",
        ["Crossref", "PubMed"],
        default=["Crossref"] + (["PubMed"] if config.NCBI_EMAIL else []),
    )
    max_results = st.slider("Max results per source", 3, 20, config.LITERATURE_MAX_RESULTS)
    st.text_input("Groq model", value=config.GROQ_MODEL, disabled=True)
    st.caption("Set GROQ_MODEL in .env to change model.")
    if not config.GROQ_API_KEY:
        st.warning("GROQ_API_KEY missing. Heuristic fallback will be used if enabled.")
    if "PubMed" in sources and not config.NCBI_EMAIL:
        st.warning("PubMed needs NCBI_EMAIL in .env.")
    if st.button("Reset project"):
        reset_project()
        st.rerun()

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "1. Topic + Literature",
    "2. Sample + Population",
    "3. Design",
    "4. Variables + Codebook",
    "5. Framework + Hypotheses",
    "6. Generate Data",
    "7. Validate + Export",
])

with tab1:
    st.subheader("Step 1: Research topic and similar literature")
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

    if st.button("Search literature and summarize", type="primary"):
        if not st.session_state.topic.strip():
            st.error("Enter a research topic first.")
        else:
            with st.spinner("Searching literature and preparing research brief..."):
                st.session_state.literature_summary = research_literature(
                    topic=st.session_state.topic,
                    domain=st.session_state.domain,
                    sources=sources,
                    max_results=max_results,
                )

    if st.session_state.literature_summary:
        st.json(st.session_state.literature_summary, expanded=False)
        papers = st.session_state.literature_summary.get("papers", [])
        if papers:
            st.markdown("### Retrieved / summarized papers")
            st.dataframe(pd.DataFrame(papers), use_container_width=True)

with tab2:
    st.subheader("Step 2: Sample size and population")
    st.session_state.sample_size = st.number_input(
        "Sample size N",
        min_value=1,
        max_value=1_000_000,
        value=int(st.session_state.sample_size),
        step=10,
    )
    st.session_state.population = st.text_area(
        "Population, setting, inclusion/exclusion notes",
        value=st.session_state.population,
        placeholder="Example: Undergraduate students aged 18-25 years enrolled in urban colleges.",
        height=100,
    )
    sample_check = validate_sample_size(int(st.session_state.sample_size))
    if sample_check["ok"]:
        st.success(sample_check["message"])
    else:
        st.error(sample_check["message"])

with tab3:
    st.subheader("Step 3: Research design selection")
    if st.button("Suggest research designs"):
        with st.spinner("Suggesting research designs..."):
            st.session_state.design_suggestions = suggest_research_designs(
                topic=st.session_state.topic,
                literature_summary=st.session_state.literature_summary or {},
                population=st.session_state.population,
            )

    if st.session_state.design_suggestions:
        st.json(st.session_state.design_suggestions, expanded=False)
        options = [
            item.get("design", "")
            for item in st.session_state.design_suggestions.get("suggested_designs", [])
            if item.get("design")
        ]
        if not options:
            options = ["cross-sectional", "cohort", "case-control", "RCT", "mixed-methods"]
        st.session_state.selected_design = st.selectbox(
            "Select final design",
            options=options,
            index=0,
        )
    else:
        st.session_state.selected_design = st.selectbox(
            "Select final design",
            ["cross-sectional", "cohort", "case-control", "RCT", "quasi-experimental", "diagnostic accuracy", "qualitative", "mixed-methods"],
            index=0,
        )

with tab4:
    st.subheader("Step 4: Define variables and build codebook")
    st.markdown("Add variables one by one. The assistant suggests role, type, definition, range, categories, distribution, and coding.")

    col_a, col_b = st.columns([2, 1])
    with col_a:
        new_var = st.text_input("Variable name", placeholder="Example: sleep_quality_score")
    with col_b:
        if st.button("Suggest variable metadata"):
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
        with st.form("variable_form"):
            name = st.text_input("Name", value=pending.get("name", ""))
            label = st.text_input("Label", value=pending.get("label", ""))
            role_options = ["independent", "dependent", "control", "covariate", "mediator", "moderator", "exposure", "outcome", "grouping", "identifier"]
            type_options = ["continuous", "integer", "binary", "categorical", "ordinal", "date", "text"]
            dist_options = ["normal", "lognormal", "uniform", "poisson", "bernoulli", "categorical", "ordinal", "date", "text"]
            role = st.selectbox("Role", role_options, index=role_options.index(pending.get("role", "covariate")) if pending.get("role", "covariate") in role_options else 3)
            variable_type = st.selectbox("Variable type", type_options, index=type_options.index(pending.get("variable_type", "continuous")) if pending.get("variable_type", "continuous") in type_options else 0)
            definition = st.text_area("Definition", value=pending.get("definition", ""), height=80)
            unit = st.text_input("Unit", value=pending.get("unit", ""))
            min_value = st.number_input("Min value", value=float(pending["min_value"]) if pending.get("min_value") is not None else 0.0)
            use_min = st.checkbox("Use min value", value=pending.get("min_value") is not None)
            max_value = st.number_input("Max value", value=float(pending["max_value"]) if pending.get("max_value") is not None else 100.0)
            use_max = st.checkbox("Use max value", value=pending.get("max_value") is not None)
            categories_text = st.text_input("Categories, comma-separated", value=", ".join(pending.get("categories", [])))
            distribution = st.selectbox("Distribution", dist_options, index=dist_options.index(pending.get("distribution", "normal")) if pending.get("distribution", "normal") in dist_options else 0)
            mean = st.number_input("Mean", value=float(pending["mean"]) if pending.get("mean") is not None else 50.0)
            use_mean = st.checkbox("Use mean", value=pending.get("mean") is not None)
            sd = st.number_input("SD", value=float(pending["sd"]) if pending.get("sd") is not None else 10.0)
            use_sd = st.checkbox("Use SD", value=pending.get("sd") is not None)
            missing_rate = st.slider("Missing rate", 0.0, 0.8, float(pending.get("missing_rate", 0.0)), 0.01)
            coding = st.text_area("Coding", value=pending.get("coding", ""), height=80)
            notes = st.text_area("Notes", value=pending.get("notes", ""), height=80)

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

    if st.session_state.variables:
        st.markdown("### Current variables")
        st.dataframe(pd.DataFrame(st.session_state.variables), use_container_width=True)
        if st.button("Build codebook"):
            st.session_state.codebook = build_codebook(st.session_state.variables)
        if st.session_state.codebook:
            st.dataframe(pd.DataFrame(st.session_state.codebook), use_container_width=True)

with tab5:
    st.subheader("Step 5: Conceptual framework and hypotheses")
    expected_text = st.text_area(
        "Expected results / hypotheses / associations to test",
        placeholder="Example: Higher social media use is expected to be associated with poorer sleep quality after adjusting for age and gender.",
        height=120,
    )
    if st.button("Build conceptual framework and hypotheses"):
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
        st.json(st.session_state.framework, expanded=False)
        mermaid_code = st.session_state.framework.get("conceptual_framework", {}).get("mermaid")
        if mermaid_code:
            st.code(mermaid_code, language="mermaid")
        hypotheses = st.session_state.framework.get("hypotheses", [])
        if hypotheses:
            st.dataframe(pd.DataFrame(hypotheses), use_container_width=True)

with tab6:
    st.subheader("Step 6: Generate synthetic dataset")
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
                st.session_state.dataset = generate_dataset(st.session_state.generation_schema, seed=int(seed))
                st.success("Dataset generated.")

    if st.session_state.generation_schema:
        st.markdown("### Generation schema")
        st.json(st.session_state.generation_schema, expanded=False)

    if st.session_state.dataset is not None:
        st.markdown("### Synthetic dataset preview")
        st.dataframe(st.session_state.dataset.head(50), use_container_width=True)
        st.download_button(
            "Download CSV",
            data=st.session_state.dataset.to_csv(index=False).encode("utf-8"),
            file_name="synthetic_dataset.csv",
            mime="text/csv",
        )

with tab7:
    st.subheader("Step 7: Validate and export")
    run_ai_review = st.checkbox("Run Groq AI plausibility review", value=bool(config.GROQ_API_KEY))
    if st.button("Validate dataset"):
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
        if st.session_state.validation_report.get("ok"):
            st.success("Mathematical validation passed.")
        else:
            st.error("Validation found errors.")
        st.json(st.session_state.validation_report, expanded=False)

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
