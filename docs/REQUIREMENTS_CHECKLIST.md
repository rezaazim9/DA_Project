# Phase-one requirements coverage

Reference: supplied `sources/project_description.pdf`, printed pages 5-7; reproducibility/AI/ethics pages 17-18. This is a phase-one mapping, not a claim that later-phase modeling has been completed.

| Requirement | Delivered evidence |
| --- | --- |
| Concrete real problem and supported decision | PROJECT_CARD items 3-7; report section 1 |
| At least three candidate questions and reason for selection | PROJECT_CARD item 6; report section 1 |
| Source, collection, time range, observational design and limitations | data/README, source manifest, report section 2, official source snapshots |
| Rows, columns, actual types, identifiers, time and relations | tables/source_inventory.csv, raw_schema.csv, category_inventory.csv; report sections 2-3 |
| Quantified missing values and initial decisions | raw_missingness.csv, modality_availability.csv; report sections 4-5 |
| Duplicates, impossible values, type issues and outliers | quality_issues.csv, train_text_audit.csv, audit_summary.json, quarantine.csv; report sections 4, 6-7 |
| Univariate EDA with center/spread/distribution/imbalance | train_numeric_summary.csv, train_rating_distribution.csv; figures 01-02; report sections 6-8 |
| Several multivariable relationships and subgroups | train_correlations.csv, train_negative_by_length/verified/review_image.csv; figures 04,06,08; report sections 9-11 |
| Baseline defined before later modeling | PROJECT_CARD items 8-9; training references in audit_summary.json; report section 13 |
| Leakage risks and suitable split unit | src/split.py, membership.csv.gz, split integrity summary; PROJECT_CARD items 10-11; report section 12 |
| Path ب: availability of text, stars, metadata, images, time, interaction | raw_schema.csv, modality_availability.csv, report sections 3 and 5. Images refer to URLs only. |
| Path ب: modality availability percentages and category-related absence | modality_availability.csv, modality_patterns.csv, missingness_category_association.csv; report section 5 |
| Path ب: text length, very short/long text, script/encoding checks and association with rating | train_text_audit.csv, train_numeric_summary.csv, train_correlations.csv, figures 02/04/06; report sections 6-9. No unsupported language-classifier claim. |
| Path ب: explain optimism of random row split and propose product/user grouping | PROJECT_CARD item 10, report section 12. Product grouping implemented; remaining user overlap disclosed. |
| reports/phase1.pdf | Full Persian report, plus its .tex source and dependencies |
| PROJECT_CARD.md with 14 required fields | All 14 numbered fields included |
| Reproducible loading/auditing code | src/, reproduce.py, requirements.txt, configs/, data/source_manifest.json |
| Updated README.md | Instructions, scope, interpretation, source files and exact build commands |
| phase-1 repository tag | Present in phase1-history.bundle as a local Git tag. A remote GitHub submission has NOT been made. |
| AI_USAGE.md | Tool, purpose/extent, main instruction, protocol, validation and limitations |
| Ethics/privacy/governance | PROJECT_CARD item 14, data/README and report section 14 |
| User request: ZIP with required files and sources | Complete package with raw inputs, official documentation snapshots, assignment, code, notebook, outputs and fonts/TeX support |
| User request: presentation PDF and LaTeX | reports/presentation.pdf and presentation.tex with shared dependencies |
| User identity | محمدرضا استادعظیم, 401100025 in card, report, slides, config and notebook |

External steps still belonging to the student: central topic registration, connecting/pushing to their own GitHub repository, any CW upload required by the current course announcement, independent review and defense. Final-project video requirements are not phase-one deliverables.
