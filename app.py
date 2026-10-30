from pathlib import Path
import streamlit as st
from converter import convert_latex, inspect_latex, summarize_structure

st.set_page_config(page_title="PaperFormat | LaTeX Converter", page_icon="📄", layout="wide")
st.title("📄 PaperFormat")
st.caption("LaTeX research-paper format conversion prototype · IEEE ↔ ACM SIGCONF")

with st.sidebar:
    st.header("Conversion settings")
    target = st.selectbox("Target template", ["IEEE Conference", "ACM SIGCONF"])
    st.markdown("---")
    st.caption("This prototype makes conservative template changes. Always compile and review the output against the official venue template.")

upload = st.file_uploader("Upload a single LaTeX source file (.tex)", type=["tex"])
if not upload:
    st.markdown("### Workflow")
    c1, c2, c3 = st.columns(3)
    c1.info("**1. Upload**\n\nChoose a `.tex` research paper.")
    c2.info("**2. Inspect**\n\nReview detected sections and source warnings.")
    c3.info("**3. Convert**\n\nDownload converted LaTeX and a conversion report.")
    st.download_button(
        "Download sample LaTeX paper",
        data=Path("sample_paper.tex").read_bytes(),
        file_name="sample_paper.tex",
        mime="text/plain"
    )
    st.stop()

try:
    source = upload.getvalue().decode("utf-8-sig")
except UnicodeDecodeError:
    st.error("Could not decode this file as UTF-8. Save it as UTF-8 and upload it again.")
    st.stop()

analysis = inspect_latex(source)
summary = summarize_structure(source)
converted, report = convert_latex(source, target)

st.subheader("Document overview")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Characters", f"{len(source):,}")
m2.metric("Sections detected", summary["sections"])
m3.metric("Figures", summary["figures"])
m4.metric("Tables", summary["tables"])

left, right = st.columns(2)
with left:
    st.markdown("### Source checks")
    for issue in analysis:
        level, message = issue
        if level == "error":
            st.error(message)
        elif level == "warning":
            st.warning(message)
        else:
            st.success(message)

with right:
    st.markdown("### Conversion report")
    for item in report:
        st.write("• " + item)

st.markdown("### Detected structure")
st.write("**Title:** " + (summary["title"] or "Not detected"))
st.write("**Authors:** " + (summary["authors"] or "Not detected"))
st.write("**Major elements:** " + (", ".join(summary["elements"]) or "No common elements detected"))

tab1, tab2 = st.tabs(["Converted source", "Original source"])
with tab1:
    st.code(converted, language="latex", line_numbers=True)
with tab2:
    st.code(source, language="latex", line_numbers=True)

stem = Path(upload.name).stem
target_suffix = "ieee" if target.startswith("IEEE") else "acm_sigconf"
st.download_button(
    "⬇ Download converted .tex",
    data=converted.encode("utf-8"),
    file_name=f"{stem}_{target_suffix}.tex",
    mime="text/plain",
    type="primary"
)
report_text = "PaperFormat conversion report\n" + "=" * 32 + "\n\n" + "\n".join(report) + "\n\nSource checks:\n" + "\n".join(f"[{level.upper()}] {msg}" for level, msg in analysis)
st.download_button(
    "Download conversion report (.txt)",
    data=report_text.encode("utf-8"),
    file_name=f"{stem}_conversion_report.txt",
    mime="text/plain"
)
st.warning("Important: this is not an official IEEE/ACM compliance checker. Multi-file projects, custom macros, complex author metadata, and package conflicts require manual review.")
