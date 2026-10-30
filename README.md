# PaperFormat: Automated LaTeX-to-ACM/IEEE Converter

A Python + Streamlit educational prototype for converting a **single-file** LaTeX research paper between IEEE conference and ACM SIGCONF document classes.

## What's improved in this version
- Cleaner two-column web interface with original/converted source tabs.
- Detects title, author, sections, figures, tables, equations, citations, and bibliography indicators.
- Basic source checks for document boundaries, braces, references, images, and multi-file dependencies.
- Downloads both the converted `.tex` file and a text conversion report.
- Includes unit tests and a sample paper.
- Uses conservative transformations and clearly reports tasks requiring manual review.

## Limitations
This is **not** a complete semantic TeX parser or an official publisher compliance checker. IEEE and ACM formats differ in author metadata, references, packages, accessibility requirements, and layout. The prototype changes the document class and a limited set of bibliography settings while preserving most source text. It does not recursively convert multi-file projects, guarantee all citations/equations/tables compile, or bundle official publisher templates.

## Setup on macOS
```bash
cd latex_ieee_acm_converter_v2
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```
The terminal prints a local URL (usually `http://localhost:8501`). Open it in your browser.

## Run tests
```bash
python -m unittest discover -s tests -v
```

## Try it
Upload `sample_paper.tex`, choose `IEEE Conference` or `ACM SIGCONF`, review warnings, and download the converted source and report.

## Suggested project evaluation
1. Collect a small test set of papers whose reuse is permitted.
2. Test both conversion directions.
3. Compile with the official target class files and venue-specific instructions.
4. Track compilation success, content preservation, and manually observed formatting issues.
5. Report measured results honestly. Do not claim perfect conversion without evidence.

## Suggested research-paper sections
Abstract; Introduction; Related Work; Proposed AST-Based Approach; System Architecture; Implementation; Experimental Setup; Evaluation Metrics; Results and Discussion; Limitations; Future Work; Conclusion; References.
