# AI usage disclosure

**Student:** محمدرضا استادعظیم, 401100025
**Tool:** OpenAI ChatGPT / Codex, used on 2026-11-01. A specific underlying model version was not independently verified and is not asserted here.

## Purpose and extent

The assistant read the supplied assignment, selected a manageable pair of official categories, downloaded the data, designed the audit and split, wrote the Python sources/tests/configuration/notebook, ran the computations, drafted the analysis and documentation, and authored the Persian LaTeX report and presentation.

## Analysis protocol

1. Extract phase-one and common requirements from the attached assignment.
2. Freeze the two-category all-record rule before model fitting; no predictive model is fitted in this phase.
3. Retrieve the official McAuley Lab files and pin exact source checksums.
4. Audit raw schema, types, missingness, duplicates, keys, ranges, modality links and metadata joins.
5. Deduplicate identical records, quarantine ambiguous business keys, make a deterministic parent-product split and purge qualifying copied text across partitions without using labels.
6. Restrict value-level EDA and baseline reference calculations to training data.
7. Generate figures/tables directly from code and bind report numbers to computed outputs.

No LLM/VLM was used to label reviews, infer sentiment, embed text, interpret image content, or generate dataset records. No fabricated/synthetic rows stand in for real data. No API-generated per-review labels or claimed predictive results are included.

## Validation and limitations

Recorded SHA-256 hashes bind inputs to the observed run. Tests cover invalid price parsing, URL-presence semantics, HTML normalization, stable grouping, label-independent copy purging, input hashes, count reconciliation and export privacy. Charts/tables were produced by the delivered code; PDFs were compiled and visually inspected by the assistant. These checks reduce mistakes.
