"""Label-independent product split and copied-text purging."""
import hashlib
import html
import re
import unicodedata
import pandas as pd


def clean_text(value) -> str:
    if not isinstance(value, str):
        return ""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]*>", " ", unicodedata.normalize("NFKC", html.unescape(value)))).strip()


def product_partition(parent_asin: str, seed: int, train_fraction=0.7, validation_fraction=0.15) -> str:
    number = int(hashlib.sha256(f"{seed}:{parent_asin}".encode()).hexdigest()[:16], 16) / 2**64
    return "train" if number < train_fraction else ("validation" if number < train_fraction+validation_fraction else "test")


def assign_partitions(df: pd.DataFrame, config: dict) -> tuple[pd.DataFrame, dict]:
    data = df.copy()
    split = config["split"]
    data["split"] = data["parent_asin"].map(lambda x: product_partition(x, config["seed"], split["train_fraction"], split["validation_fraction"]))
    priority = {name: i for i, name in enumerate(split["priority"])}
    text = (data["title"].map(clean_text) + " " + data["text"].map(clean_text)).str.strip().str.casefold()
    eligible = text.str.split().str.len() >= split["copied_text_min_words"]
    data["text_signature"] = text.map(lambda value: hashlib.sha256(value.encode()).hexdigest())
    rank = data["split"].map(priority)
    best = rank[eligible].groupby(data.loc[eligible, "text_signature"]).transform("min")
    purge = pd.Series(False, index=data.index)
    purge.loc[eligible] = rank[eligible] > best
    data["split_exclusion"] = ""
    data.loc[purge, "split_exclusion"] = "copied_text_seen_in_earlier_partition"
    # Keep assignments for every record. Exclusion is explicit, not a hidden deletion.
    before = data.groupby("split").size().to_dict()
    kept = data.loc[~purge]
    counts = kept.groupby("split").size().to_dict()
    products = kept.groupby("split")["parent_asin"].nunique().to_dict()
    overlaps, user_overlaps, text_overlaps = {}, {}, {}
    for a, b in [("train", "validation"), ("train", "test"), ("validation", "test")]:
        left, right = kept[kept.split == a], kept[kept.split == b]
        overlaps[f"{a}_{b}"] = len(set(left.parent_asin) & set(right.parent_asin))
        user_overlaps[f"{a}_{b}"] = len(set(left.user_id) & set(right.user_id))
        signatures = data.loc[eligible & ~purge]
        text_overlaps[f"{a}_{b}"] = len(set(signatures.loc[signatures.split == a,"text_signature"]) & set(signatures.loc[signatures.split == b,"text_signature"]))
    assert not any(overlaps.values()), overlaps
    assert not any(text_overlaps.values()), text_overlaps
    return data, {"before_purge_rows": before, "retained_rows": counts, "retained_products": products,
                  "purged_rows": int(purge.sum()), "product_overlap": overlaps,
                  "long_exact_text_overlap_after_purge": text_overlaps, "user_overlap": user_overlaps,
                  "note": "User overlap is permitted for product cold-start. No user identifier or per-user target aggregate is a model input. Near-duplicates remain a limitation."}
