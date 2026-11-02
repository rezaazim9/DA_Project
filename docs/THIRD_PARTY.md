# Third-party resources and attribution

- Amazon Reviews'23: McAuley Lab, https://amazon-reviews-2023.github.io/ . Four original downloaded files are pinned in data/source_manifest.json. Bibliography: sources/references.bib. Public documentation snapshots were retrieved 2026-11-01. Raw review text and product images are not licensed by this project. The inspected card has no explicit comprehensive redistribution license.
- Supplied course assignment: copied unchanged to sources/project_description.pdf solely as the user's reference source.
- DejaVu Sans / Sans Bold / Sans Mono: bundled font files, upstream license in fonts/LICENSE-DejaVu.txt.
- bidi v39.8 (2023-08-02): Vafa Khalighi and prior bidi-tex contributors. https://ctan.org/pkg/bidi . Unmodified runtime files under texmf/tex/latex/bidi, with LPPL 1.3c notices retained.
- XePersian v25.0 (2023-08-30): Vafa Khalighi and prior bidi-tex contributors. https://ctan.org/pkg/xepersian . Unmodified runtime files under texmf/tex/latex/xepersian, with LPPL 1.3c notices retained.
- reports/latex_compat.tex is a separate small compatibility layer for older LaTeX formats. It does not modify the bundled upstream packages. Base TeX/LaTeX, Beamer, fontspec and common packages remain system dependencies.
- Python packages and exact versions: requirements.txt. Their upstream licenses remain applicable.

The bundled TeX runtime files were extracted unchanged from Ubuntu's texlive-lang-arabic 2023.20240207-1 package at https://archive.ubuntu.com/ubuntu/pool/universe/t/texlive-lang/texlive-lang-arabic_2023.20240207-1_all.deb . The package copyright is preserved in texmf/UPSTREAM_COPYRIGHT.txt. They are included to make the requested LaTeX sources compile consistently without fetching project-specific files. No illustrative/generated imagery is used; all figures are data charts produced by the delivered analysis.
