# pdf

Professional PDF document generators built with [ReportLab](https://www.reportlab.com/).

## Documents

| File | Generator | Description |
| --- | --- | --- |
| `HALYK_PETROLEUM_SCO.pdf` | `halyk_scope.py` | HALYK PETROLEUM LLP – Approved Official Scope of Work (HP-SCO-2025-001, Rev. 03). 10-page controlled corporate document: cover with full document-control block, auto TOC with page numbers & bookmarks, 12 sections + Appendix A (definitions & abbreviations), signature block. |
| `resume.pdf` | `generate_resume.py` | Two-page professional resume / CV with banded header, skill chips and balanced pagination. |

## Regenerating

```bash
pip install reportlab          # tested with reportlab 5.x
python3 halyk_scope.py         # writes HALYK_PETROLEUM_SCO.pdf
python3 generate_resume.py     # writes resume.pdf
```

All document content lives in the data blocks at the top of each script
(`COMPANY` / `DOC` / `RESUME`); edit those and re-run to regenerate.
The generators embed complete PDF metadata (title, author, subject, keywords),
PDF outline bookmarks, clickable TOC links and "Page X of Y" footers.
