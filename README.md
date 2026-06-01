# Research Design and Synthetic Data Assistant

A Streamlit research assistant that helps a researcher move from a research topic to a defensible synthetic dataset.

It replaces Claude entirely with:

- **Literature retrieval:** PubMed/NCBI E-utilities and Crossref REST API
- **Cloud LLM:** Groq API
- **Data control:** Python/Pydantic/NumPy/Pandas validation and generation

## Pipeline

1. **Research topic / study title**
   - Search similar literature
   - Summarise findings
   - Extract variables and relationships

2. **Sample size and population**
   - User enters N and population notes

3. **Research design**
   - Suggests study design options
   - User selects cross-sectional, cohort, case-control, RCT, qualitative, mixed-methods, etc.
   - Builds conceptual framework draft

4. **Variables and codebook**
   - Suggests independent, dependent, control, mediator, moderator variables
   - Generates type, definition, unit, range, categories, distribution, coding

5. **Hypotheses and relationships**
   - Maps expected findings to statistical constraints
   - Builds conceptual framework text and Mermaid diagram

6. **Synthetic data generation**
   - Builds a generation schema
   - Python generates synthetic dataset

7. **Validation and export**
   - Mathematical validation
   - AI plausibility review
   - Exports CSV, Excel, codebook JSON, literature JSON, validation JSON

## Setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

## Environment

Edit `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

NCBI_EMAIL=your_email@example.com
NCBI_API_KEY=

CROSSREF_MAILTO=your_email@example.com
LITERATURE_MAX_RESULTS=8
ALLOW_HEURISTIC_FALLBACK=true
```

`NCBI_EMAIL` is only required if you enable PubMed. Crossref works without signup, but a `mailto` value is recommended.

## Notes

- The LLM is never treated as the source of citations.
- Papers come from PubMed/Crossref.
- The LLM only summarizes retrieved metadata/abstracts and drafts structured JSON.
- Python validates schema and controls data generation.
- Generated data is synthetic and must not be interpreted as real study data.
