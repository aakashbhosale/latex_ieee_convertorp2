"""Conservative LaTeX structure inspection and IEEE/ACM class conversion.

This educational tool is intentionally transparent: it does not claim to fully
rewrite all publisher-specific commands. It preserves source content where
possible and reports transformations and items that need human review.
"""
from dataclasses import dataclass
from typing import List, Tuple
import re

@dataclass
class LatexNode:
    kind: str
    command: str
    start: int
    end: int
    raw: str

# Recognize major commands/environments without pretending to fully parse TeX.
TOKEN_RE = re.compile(
    r"\\documentclass(?:\s*\[[^\]]*\])?\s*\{[^}]*\}"
    r"|\\begin\s*\{[^}]+\}|\\end\s*\{[^}]+\}"
    r"|\\(?:title|author|section|subsection|subsubsection|chapter|"
    r"abstract|maketitle|bibliography|bibliographystyle|includegraphics|"
    r"input|include|cite|citep|citet|label|ref|eqref)\*?"
)

def parse_latex_structure(source: str) -> List[LatexNode]:
    """Return a lightweight token sequence for common LaTeX structures."""
    nodes = []
    for match in TOKEN_RE.finditer(source):
        raw = match.group(0)
        if raw.startswith(r"\documentclass"):
            kind, command = "documentclass", "documentclass"
        elif raw.startswith(r"\begin"):
            kind, command = "environment_begin", raw
        elif raw.startswith(r"\end"):
            kind, command = "environment_end", raw
        else:
            kind = "command"
            command = raw.split("{", 1)[0].rstrip("*")
        nodes.append(LatexNode(kind, command, match.start(), match.end(), raw))
    return nodes

def _find_balanced_brace(source: str, open_pos: int):
    """Find closing brace while accounting for nested braces and escaped chars."""
    if open_pos >= len(source) or source[open_pos] != "{":
        return None
    depth = 0
    escaped = False
    for i in range(open_pos, len(source)):
        ch = source[i]
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
    return None

def _extract_command_argument(source: str, command: str):
    match = re.search(r"\\" + re.escape(command) + r"\*?(?:\s*\[[^\]]*\])?\s*\{", source)
    if not match:
        return ""
    open_pos = source.find("{", match.start())
    close_pos = _find_balanced_brace(source, open_pos)
    if close_pos is None:
        return ""
    return source[open_pos + 1:close_pos].strip()

def summarize_structure(source: str):
    sections = re.findall(r"\\(?:section|subsection|subsubsection|chapter)\*?\s*\{", source)
    figures = len(re.findall(r"\\begin\s*\{figure\*?\}", source))
    tables = len(re.findall(r"\\begin\s*\{table\*?\}", source))
    elements = []
    for name, pattern in [
        ("Abstract", r"\\begin\s*\{abstract\}"),
        ("Equations", r"\\begin\s*\{(?:equation\*?|align\*?|gather\*?)\}"),
        ("Citations", r"\\(?:cite|citep|citet)\w*\s*[\[{]"),
        ("References", r"\\bibliography\s*\{|\\begin\s*\{thebibliography\}"),
        ("Figures", r"\\begin\s*\{figure\*?\}"),
        ("Tables", r"\\begin\s*\{table\*?\}"),
    ]:
        if re.search(pattern, source):
            elements.append(name)
    title = _extract_command_argument(source, "title")
    authors = _extract_command_argument(source, "author")
    return {
        "sections": len(sections), "figures": figures, "tables": tables,
        "title": re.sub(r"\s+", " ", title)[:180],
        "authors": re.sub(r"\s+", " ", authors)[:180],
        "elements": elements,
    }

def inspect_latex(source: str) -> List[Tuple[str, str]]:
    findings = []
    if not source.strip():
        return [("error", "The uploaded file is empty.")]
    if r"\begin{document}" in source:
        findings.append(("ok", "Found \\begin{document}."))
    else:
        findings.append(("error", "Missing \\begin{document}; this may not be a complete LaTeX document."))
    if r"\end{document}" in source:
        findings.append(("ok", "Found \\end{document}."))
    else:
        findings.append(("error", "Missing \\end{document}."))
    if not re.search(r"\\documentclass(?:\s*\[[^\]]*\])?\s*\{[^}]*\}", source):
        findings.append(("warning", "No \\documentclass declaration found."))
    # Ignore escaped braces and comments for a basic brace-balance check.
    uncommented = "\n".join(line.split("%", 1)[0] for line in source.splitlines())
    stripped = re.sub(r"\\[{}]", "", uncommented)
    if stripped.count("{") == stripped.count("}"):
        findings.append(("ok", "Opening and closing brace counts match (basic check)."))
    else:
        findings.append(("warning", "Opening and closing brace counts differ; inspect nested commands and comments."))
    if not (r"\bibliography{" in source or r"\begin{thebibliography}" in source or r"\printbibliography" in source):
        findings.append(("warning", "No bibliography command/environment detected."))
    if r"\includegraphics" in source:
        findings.append(("warning", "Figure files may be required; keep referenced image assets alongside the source."))
    if r"\input{" in source or r"\include{" in source:
        findings.append(("warning", "This appears to be a multi-file project. Only the uploaded .tex file is processed."))
    if r"\begin{document}" in source and r"\end{document}" in source:
        findings.append(("ok", "Basic document boundaries are present; compile to verify full LaTeX syntax."))
    return findings

def _set_documentclass(source: str, target: str):
    target_class = (r"\documentclass[conference]{IEEEtran}"
                    if target == "IEEE Conference"
                    else r"\documentclass[sigconf]{acmart}")
    pattern = re.compile(r"\\documentclass(?:\s*\[[^\]]*\])?\s*\{[^}]*\}")
    if pattern.search(source):
        return pattern.sub(lambda _: target_class, source, count=1), "Updated document class."
    return target_class + "\n\n" + source, "Inserted a document class because none was found."

def convert_latex(source: str, target: str):
    if target not in {"IEEE Conference", "ACM SIGCONF"}:
        raise ValueError("Unsupported target. Choose IEEE Conference or ACM SIGCONF.")
    nodes = parse_latex_structure(source)
    output, class_message = _set_documentclass(source, target)
    report = [
        f"Detected {len(nodes)} major LaTeX tokens with lightweight structural parsing.",
        class_message,
        "Original body text and most commands were preserved.",
    ]

    if target == "IEEE Conference":
        if re.search(r"\\bibliographystyle\s*\{[^}]*\}", output):
            output = re.sub(r"\\bibliographystyle\s*\{[^}]*\}",
                            r"\\bibliographystyle{IEEEtran}", output, count=1)
            report.append("Set the first explicit bibliography style to IEEEtran.")
        else:
            report.append("No explicit bibliography style found; review reference formatting.")
        if r"\IEEEauthorblockN" not in output and r"\author{" in output:
            report.append("Author metadata may need conversion to IEEE conference author blocks.")
    else:
        if re.search(r"\\bibliographystyle\s*\{[^}]*\}", output):
            output = re.sub(r"\\bibliographystyle\s*\{[^}]*\}\s*", "", output, count=1)
            report.append("Removed the first explicit bibliography style; ACM class commonly controls reference style.")
        if r"\acmConference" not in output:
            report.append("Add correct ACM conference metadata (name, date, venue) before submission.")
        if r"\Description{" not in output and r"\includegraphics" in output:
            report.append("Consider adding accessibility descriptions for figures.")
        if r"\author{" in output and r"\affiliation{" not in output:
            report.append("ACM author names and affiliations may need restructuring for acmart.")
    if r"\begin{abstract}" not in output:
        report.append("No abstract environment detected; verify whether the target venue requires one.")
    if r"\maketitle" not in output:
        report.append("No \\maketitle command detected; verify title rendering.")
    if r"\input{" in output or r"\include{" in output:
        report.append("Multi-file inputs are not converted recursively by this prototype.")
    report.append("Manual compilation and comparison with the official target template are required.")
    return output, report
