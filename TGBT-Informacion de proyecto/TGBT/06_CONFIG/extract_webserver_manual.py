from pathlib import Path
from pypdf import PdfReader

pdf_path = Path(
    r"c:\Users\maria\OneDrive\Desktop\Proyectos PLC TGBT\TGBT-Informacion de proyecto\TGBT\05_MANUALES\S7-1200 Programmable controller - TIA Portal como programar un user defined page web server.pdf"
)

keywords = [
    "web server",
    "webserver",
    "user-defined",
    "user defined",
    "awp",
    "variable",
    "var",
    ":=",
    "start page",
]

reader = PdfReader(str(pdf_path))
print(f"FILE: {pdf_path.name}")
print(f"PAGES: {len(reader.pages)}")


def safe_print(text: str) -> None:
    # Avoid Windows cp1252 terminal encoding crashes from PDF ligatures/symbols.
    print(text.encode("cp1252", errors="replace").decode("cp1252"))

for i, page in enumerate(reader.pages, start=1):
    text = page.extract_text() or ""
    lower = text.lower()
    if not any(k in lower for k in keywords):
        continue

    print(f"\n===== PAGE {i} =====")
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    hits = []
    for idx, line in enumerate(lines):
        line_low = line.lower()
        if any(k in line_low for k in keywords):
            hits.append(idx)

    shown = set()
    for h in hits[:12]:
        a = max(0, h - 1)
        b = min(len(lines), h + 2)
        for j in range(a, b):
            if j not in shown:
                safe_print(lines[j])
                shown.add(j)
        print("---")
