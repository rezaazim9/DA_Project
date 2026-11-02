# LaTeX compilation fix

## Compile

In TeXstudio, open `reports/phase1.tex`, select **XeLaTeX**, and compile twice. Do not compile `common.tex` as a standalone document.

Alternatively, run this from the extracted `DA_Project` folder:

```bash
python -m src.build_documents
```

This command only rebuilds the LaTeX report from the existing results. It does not rerun the data analysis or require pandas. It compiles only document sources present in `reports/`; the uploaded archive does not contain `presentation.tex`.

## What was fixed

- `reports/common.tex`: the unconditional font overrides referenced nonexistent `requirements/XB Niloofar.ttf` and `requirements/XB Yas.ttf`. They are now conditional. Installed XB Niloofar / XB Yas fonts or the corresponding optional local files are preferred; otherwise the bundled DejaVu fonts are used. Times New Roman is also conditional, with a bundled fallback.
- Added explicit fallback bold/italic digit-font shapes, so missing fonts do not turn the report into blank/nullfont text.
- `reports/phase1.tex`: the indicator uses `\mathbf{1}` to display an actual bold numeral 1 rather than the unrelated glyph produced by `\mathbb{1}`. The equation and analysis keep the same meaning.
- `src/build_documents.py`: removed an unused pandas dependency, made generated text explicitly UTF-8, preserved SyncTeX support, skipped missing presentation sources, and preferred the TeX installation's matching Persian packages before using the bundled fallback pair.
- Updated the compiled report, build intermediates and checksum list. All other original archive files, including project data and Git history, are preserved. No commit or remote upload was made.

## Optional requested fonts

The uploaded ZIP does not contain XB Niloofar or XB Yas. If you have those fonts, install them normally in Windows, or place the correctly named `XB Niloofar.ttf` and `XB Yas.ttf` under `reports/requirements/`. Otherwise no additional font download is required. The supplied PDF uses the bundled fallback fonts.

## Verification

The report was compiled twice with XeLaTeX and visually checked: 16 pages, no font errors, missing-character warnings or overfull boxes. The Python builder was also run with Python site packages disabled, confirming that LaTeX compilation does not require the analysis dependencies. Native Windows/MiKTeX execution was not performed in this environment.

## Follow-up: undefined table command

The repeated `\UseMathForPositioningText` errors are a compatibility problem in the installed table/Persian support combination. `reports/latex_compat.tex` now contains:

```latex
\providecommand{\UseMathForPositioningText}{}
```

This keeps an existing implementation when available and supplies the missing command for this untagged report. `reports/phase1.tex` also sets `\captionsetup{hypcap=false}` for the captions outside floats.

Extract `LaTeX_Table_Fix.zip` directly into your `DA_Project` directory and replace the two matching files under `reports/`. Then rebuild `reports/phase1.tex` with XeLaTeX. The ChkTeX dash/spacing messages are editor style warnings; the small overfull-box message is a layout warning, not an undefined-command error.

The local recompile has no undefined commands, missing glyphs, font-shape warnings, overfull boxes or ignored-hypcap warnings. This is not a claim that Windows/MiKTeX was run here. The report wording and data are unchanged.
