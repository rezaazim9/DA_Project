# Data and provenance

The ZIP contains the four original `.jsonl.gz` files under `raw/` for offline academic reproduction. They are excluded from Git by `.gitignore`. `source_manifest.json` pins their official URLs, compressed sizes and SHA-256 values. Do not decompress in place or edit them. The all-record category rule is in `configs/phase1.json` and `PROJECT_CARD.md`.

```bash
# Download only missing inputs, then verify every source hash
python -m src.download
# Full phase-one analysis from the original data
python -m src.audit
```

`processed/audit_features.csv.gz` contains measured audit variables, not a ready-to-train feature matrix. It deliberately retains label-only and audit-only fields such as `rating` and accumulated helpful votes. Do not pass all columns to a predictive model. `splits/membership.csv.gz` records every accepted unique review's row hash, parent product, reviewer hash, partition and explicit copied-text exclusion. `processed/quarantine.csv` lists ambiguous business-key row hashes; corresponding originals remain in `raw/`.

Dates are UTC, parsed as Unix milliseconds. Words are whitespace-separated units after NFKC normalization, HTML entity decoding, tag removal and whitespace collapse. They are not model tokens. `non_ascii` includes ordinary punctuation/emoji and is not a language label. `has_*image` means at least one syntactically HTTP(S) URL, not accessible/valid image pixels.

Metadata is joined many-to-one on `parent_asin`; `asin` denotes a variant. Product-level missingness must use one denominator per product. Prices are at crawl time according to the official dictionary; in this subset none parse to a usable number. All data are observational, self-selected published reviews and a catalog snapshot, not a controlled experiment.

Source: https://amazon-reviews-2023.github.io/ . Preserve the dataset citation in `sources/references.bib`. The inspected dataset card provides no explicit comprehensive redistribution license. No license is granted by this project for underlying review text or product images. Raw files are provided for this private academic workflow, not as a public mirror. Review upstream rights before redistribution. Do not upload raw files, reviewer text or processed row-level data to a public GitHub repository.
