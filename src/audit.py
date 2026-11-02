"""Run: python -m src.audit. All value-level EDA uses the training partition."""
from __future__ import annotations
import argparse
import html
import json
import platform
import re
import unicodedata
from pathlib import Path
from collections import Counter
import importlib.metadata
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency, spearmanr
from .data_io import load_jsonl, verify_sources, canonical_hash, parse_price, has_image_url
from .split import assign_partitions, clean_text

ROOT = Path(__file__).resolve().parents[1]
LABELS = {"Magazine_Subscriptions": "Magazines", "Subscription_Boxes": "Subscription boxes"}
COLORS = ["#245C78", "#CD6948"]


def write_table(root, name, records):
    frame = records if isinstance(records, pd.DataFrame) else pd.DataFrame(records)
    frame.to_csv(root / "tables" / f"{name}.csv", index=False, float_format="%.8g")
    return frame


def save_figure(root, name):
    figure = plt.gcf()
    figure.savefig(root / "figures" / f"{name}.pdf", bbox_inches="tight")
    figure.savefig(root / "figures" / f"{name}.png", dpi=180, bbox_inches="tight")
    figure.set_size_inches(9, 3.7)
    for obj in figure.findobj(matplotlib.text.Text):
        obj.set_fontsize(13)
    figure.tight_layout()
    figure.savefig(root / "figures" / f"slide_{name}.pdf", bbox_inches="tight")
    plt.close(figure)


def available_string(x):
    return isinstance(x, str) and bool(x.strip())


def integer_nonnegative(x):
    return type(x) in (int, float) and np.isfinite(x) and x >= 0 and x == int(x)


def cramer_effect(data, field):
    table = pd.crosstab(data["source_category"], data[field]).reindex(columns=[False,True], fill_value=0)
    if table.shape[0] < 2 or (table.sum(axis=0) == 0).any():
        return {"field": field, "cramers_v": None, "status": "degenerate: no variation"}
    chi2 = chi2_contingency(table, correction=False)[0]
    return {"field": field, "cramers_v": float(np.sqrt(chi2 / table.values.sum())),
            "status": "descriptive effect only; no independence or causality claim"}


def run(root=ROOT):
    root=Path(root)
    for d in ["tables", "figures", "data/processed", "data/splits", "reports/phase1"]:
        (root/d).mkdir(parents=True, exist_ok=True)
    config=json.loads((root/"configs/phase1.json").read_text(encoding="utf-8"))
    manifest=verify_sources(root)
    reviews, metadata, schemas, missing, source_rows, raw_records = [], [], [], [], [], {}
    for source in manifest:
        rows, schema, absent = load_jsonl(root/"data/raw"/source["filename"])
        schemas.extend(schema); missing.extend(absent)
        raw_records[source["filename"]]=rows
        source_rows.append({"file":source["filename"],"category":source["category"],"kind":source["kind"],
                            "rows":len(rows),"fields":len(set().union(*(x.keys() for x in rows))),"compressed_bytes":source["bytes"]})
        target=reviews if source["kind"] == "reviews" else metadata
        target.extend([{**r,"source_category":source["category"],"_raw_hash":canonical_hash(r)} for r in rows])
    write_table(root,"source_inventory",source_rows)
    write_table(root,"raw_schema",schemas)
    write_table(root,"raw_missingness",missing)
    df=pd.DataFrame(reviews); meta=pd.DataFrame(metadata)
    raw_count=len(df)
    duplicates=int(df.duplicated("_raw_hash").sum())
    df=df.drop_duplicates("_raw_hash").copy()
    # Business-key conflicts are quarantined, not resolved through a label-based rule.
    business_key=["user_id","parent_asin","timestamp"]
    key_conflict=df.duplicated(business_key,keep=False)
    conflict_count=int(key_conflict.sum())
    invalid_rating=~df.rating.map(lambda x: type(x) in (int,float) and x in (1,2,3,4,5))
    invalid_parent=~df.parent_asin.map(lambda x: isinstance(x,str) and bool(re.fullmatch(r"[A-Z0-9]{10}",x)))
    invalid_asin=~df.asin.map(lambda x: isinstance(x,str) and bool(re.fullmatch(r"[A-Z0-9]{10}",x)))
    invalid_user=~df.user_id.map(available_string)
    df["date"]=pd.to_datetime(df.timestamp,unit="ms",utc=True,errors="coerce")
    invalid_date=df.date.isna() | (df.date<pd.Timestamp(config["valid_timestamp_start"])) | (df.date>=pd.Timestamp(config["valid_timestamp_end_exclusive"]))
    invalid_votes=~df.helpful_vote.map(integer_nonnegative)
    invalid_verified=~df.verified_purchase.map(lambda x:type(x) is bool)
    # Invalid auxiliary fields remain visible as missing; no silent casting of strings to True.
    df.loc[invalid_votes,"helpful_vote"]=np.nan
    if invalid_verified.any():
        df["verified_purchase"] = df["verified_purchase"].astype(object)
        df.loc[invalid_verified,"verified_purchase"]=None
    quarantine=key_conflict | invalid_rating | invalid_parent | invalid_user | invalid_date
    df["quarantined"]=quarantine
    quality={"raw_review_rows":raw_count,"exact_duplicate_excess":duplicates,"business_key_conflict_rows":conflict_count,
             "invalid_rating_rows":int(invalid_rating.sum()),"invalid_parent_id_rows":int(invalid_parent.sum()),
             "invalid_variant_id_rows":int(invalid_asin.sum()),"missing_user_id_rows":int(invalid_user.sum()),
             "invalid_timestamp_rows":int(invalid_date.sum()),"invalid_helpful_vote_rows":int(invalid_votes.sum()),
             "invalid_verified_purchase_rows":int(invalid_verified.sum()),"quarantined_rows":int(quarantine.sum())}
    write_table(root,"quality_issues",[{"issue":k,"count":v} for k,v in quality.items()])
    if quarantine.any():
        df.loc[quarantine,["_raw_hash","source_category"]].to_csv(root/"data/processed/quarantine.csv",index=False)
    df=df.loc[~quarantine].copy()
    meta_duplicates=int(meta.duplicated("_raw_hash").sum())
    meta=meta.drop_duplicates("_raw_hash").copy()
    if meta.parent_asin.duplicated().any():
        raise ValueError("Conflicting metadata parent keys: join would be ambiguous. Resolve explicitly.")
    meta["price_numeric"]=meta.price.map(parse_price)
    meta["has_price"]=meta.price_numeric.notna()
    meta["has_product_image"]=meta.images.map(has_image_url)
    meta["has_product_title"]=meta.title.map(available_string)
    meta["has_description"]=meta.description.map(lambda x:isinstance(x,list) and any(available_string(v) for v in x))
    meta["has_features"]=meta.features.map(lambda x:isinstance(x,list) and any(available_string(v) for v in x))
    meta["has_store"]=meta.store.map(available_string)
    meta["has_categories"]=meta.categories.map(lambda x:isinstance(x,list) and bool(x))
    meta["has_details"]=meta.details.map(lambda x:isinstance(x,dict) and bool(x))
    meta["feature_count"]=meta.features.map(lambda x:len(x) if isinstance(x,list) else 0)
    meta["product_title_words"]=meta.title.map(clean_text).str.split().str.len()
    meta["description_words"]=meta.description.map(lambda x:len(clean_text(" ".join(x)).split()) if isinstance(x,list) else 0)
    join_columns=["parent_asin","price_numeric","has_price","has_product_image","has_product_title","has_description","has_features","has_store","has_categories","has_details","feature_count","product_title_words","description_words"]
    df=df.merge(meta[join_columns],on="parent_asin",how="left",validate="many_to_one",indicator=True)
    df["has_metadata"]=df.pop("_merge").eq("both")
    for col in [c for c in join_columns if c.startswith("has_")]:df[col]=df[col].fillna(False).astype(bool)
    df["body_clean"]=df.text.map(clean_text)
    df["word_count"]=df.body_clean.str.split().str.len()
    df["char_count"]=df.body_clean.str.len()
    df["has_text"]=df.body_clean.str.len()>0
    df["has_review_title"]=df.title.map(available_string)
    df["has_review_image"]=df.images.map(has_image_url)
    df["has_timestamp"]=df.date.notna()
    df["has_interaction"]=df.user_id.map(available_string)&df.parent_asin.map(available_string)
    df["negative"]=df.rating.le(2).astype(int)
    # These are script/encoding flags, NOT a language classifier.
    df["non_ascii"]=df.text.map(lambda s:isinstance(s,str) and any(ord(c)>127 for c in s))
    df["html_markup"]=df.text.map(lambda s:isinstance(s,str) and bool(re.search(r"<[^>]+>|&(?:amp|lt|gt|quot|#\d+);",s)))
    df["replacement_char"]=df.text.map(lambda s:isinstance(s,str) and "\ufffd" in s)
    df["control_char"]=df.text.map(lambda s:isinstance(s,str) and any(unicodedata.category(c)=="Cc" and c not in "\n\r\t" for c in s))
    df["arabic_script"]=df.text.map(lambda s:isinstance(s,str) and bool(re.search(r"[\u0600-\u06ff]",s)))
    df["cjk_script"]=df.text.map(lambda s:isinstance(s,str) and bool(re.search(r"[\u4e00-\u9fff]",s)))
    df["latin_letter_fraction"]=df.body_clean.map(lambda s:sum('LATIN' in unicodedata.name(c,'') for c in s if c.isalpha())/max(1,sum(c.isalpha() for c in s)))
    df["very_short"]=df.word_count.le(config["text"]["very_short_max_words"])
    df["very_long"]=df.word_count.ge(config["text"]["very_long_min_words"])
    df, split_audit=assign_partitions(df,config)
    retained=df[df.split_exclusion.eq("")].copy()
    train=retained[retained.split.eq("train")].copy()
    if len(train)==0:raise ValueError("Empty training EDA partition")
    q1,q3=train.word_count.quantile([.25,.75])
    text_fence=float(q3+1.5*(q3-q1))
    df["long_iqr_outlier"]=df.word_count>text_fence
    train["long_iqr_outlier"]=train.word_count>text_fence
    vq1,vq3=train.helpful_vote.quantile([.25,.75]);vote_fence=float(vq3+1.5*(vq3-vq1))
    train["vote_iqr_outlier"]=train.helpful_vote>vote_fence
    df["user_hash"]=df.user_id.map(lambda x:canonical_hash({"audit_seed":config["seed"],"user_id":x})[:20])
    membership_columns=["_raw_hash","source_category","parent_asin","user_hash","split","split_exclusion"]
    df[membership_columns].rename(columns={"_raw_hash":"row_id"}).to_csv(root/"data/splits/membership.csv.gz",index=False,compression={"method":"gzip","mtime":0})
    feature_columns=["_raw_hash","source_category","parent_asin","user_hash","date","word_count","char_count","rating","negative","helpful_vote","verified_purchase","has_text","has_metadata","has_review_image","has_product_image","has_price","has_description","has_features","feature_count","product_title_words","description_words","non_ascii","html_markup","replacement_char","control_char","latin_letter_fraction","very_short","very_long","split","split_exclusion","long_iqr_outlier"]
    df[feature_columns].rename(columns={"_raw_hash":"row_id"}).to_csv(root/"data/processed/audit_features.csv.gz",index=False,compression={"method":"gzip","mtime":0})
    inventory=[]
    for category,g in df.groupby("source_category"):
        inventory.append({"category":category,"rows":len(g),"unique_users":g.user_id.nunique(),"products":g.parent_asin.nunique(),
                          "variant_asins":g.asin.nunique(),"earliest_utc":g.date.min().isoformat(),"latest_utc":g.date.max().isoformat(),
                          "metadata_join_pct":100*g.has_metadata.mean()})
    write_table(root,"category_inventory",inventory)
    write_table(root,"split_counts",retained.groupby(["split","source_category"]).agg(rows=("_raw_hash","size"),products=("parent_asin","nunique")).reset_index())
    # All-row audit of input availability, two clearly separated denominators.
    modality_rows=[]
    review_modalities=["has_text","has_review_title","has_review_image","has_metadata","has_product_image","has_price","has_timestamp","has_interaction"]
    catalog_modalities=["has_product_title","has_product_image","has_price","has_description","has_features","has_categories","has_details","has_store"]
    for unit,data,columns in [("review",df,review_modalities),("product",meta,catalog_modalities)]:
        for category,g in data.groupby("source_category"):
            for column in columns:
                modality_rows.append({"unit":unit,"category":category,"modality":column,"available":int(g[column].sum()),
                                      "denominator":len(g),"available_pct":100*g[column].mean(),"missing_pct":100*(1-g[column].mean())})
    modality=write_table(root,"modality_availability",modality_rows)
    effects=[{"unit":unit,**cramer_effect(data,column)} for unit,data,columns in [("review",df,review_modalities),("product",meta,catalog_modalities)] for column in columns]
    write_table(root,"missingness_category_association",effects)
    patterns=df.groupby(["source_category","has_text","has_review_image","has_product_image","has_price"]).size().reset_index(name="rows")
    write_table(root,"modality_patterns",patterns)
    summary=[]
    for category,g in train.groupby("source_category"):
        for column in ["word_count","char_count","rating","helpful_vote"]:
            a=g[column]
            summary.append({"category":category,"variable":column,"n":int(a.count()),"mean":a.mean(),"std":a.std(),"min":a.min(),
                            "q25":a.quantile(.25),"median":a.median(),"q75":a.quantile(.75),"p95":a.quantile(.95),"p99":a.quantile(.99),"max":a.max()})
    write_table(root,"train_numeric_summary",summary)
    ratings=train.groupby(["source_category","rating"]).size().reset_index(name="n")
    ratings["pct"]=100*ratings.n/ratings.groupby("source_category").n.transform("sum")
    write_table(root,"train_rating_distribution",ratings)
    flags=["very_short","very_long","non_ascii","html_markup","replacement_char","control_char","arabic_script","cjk_script","has_text","long_iqr_outlier","vote_iqr_outlier"]
    text_rows=[{"category":cat,"flag":flag,"count":int(g[flag].sum()),"denominator":len(g),"pct":100*g[flag].mean()} for cat,g in train.groupby("source_category") for flag in flags]
    write_table(root,"train_text_audit",text_rows)
    correlations=[]
    for cat,g in [("ALL",train),*list(train.groupby("source_category"))]:
        for a,b in [("word_count","rating"),("word_count","helpful_vote")]:
            correlations.append({"category":cat,"x":a,"y":b,"spearman_rho":float(spearmanr(g[a],g[b],nan_policy="omit").statistic)})
    write_table(root,"train_correlations",correlations)
    train["length_bin"]=pd.cut(train.word_count,[-1,3,10,30,100,200,np.inf],labels=["0-3","4-10","11-30","31-100","101-200","201+"])
    length_rates=train.groupby(["source_category","length_bin"],observed=True).agg(n=("negative","size"),negative_n=("negative","sum"),negative_rate=("negative","mean")).reset_index()
    write_table(root,"train_negative_by_length",length_rates)
    verified=train.groupby(["source_category","verified_purchase"],dropna=False).agg(n=("negative","size"),negative_n=("negative","sum"),negative_rate=("negative","mean")).reset_index()
    write_table(root,"train_negative_by_verified",verified)
    image_rates=train.groupby(["source_category","has_review_image"]).agg(n=("negative","size"),negative_n=("negative","sum"),negative_rate=("negative","mean")).reset_index()
    write_table(root,"train_negative_by_review_image",image_rates)
    monthly=train.assign(month=train.date.dt.strftime("%Y-%m")).groupby(["source_category","month"]).agg(n=("negative","size"),negative_rate=("negative","mean")).reset_index()
    write_table(root,"train_monthly",monthly)
    product_counts=train.groupby("parent_asin").size().sort_values(ascending=False)
    top_ten_share=float(product_counts.head(10).sum()/len(train))
    # Training-only reference values. No validation/test labels are evaluated.
    prevalence=float(train.negative.mean()); majority=max(prevalence,1-prevalence)
    baseline={"scope":"training descriptive reference only; not held-out model performance","n":len(train),
              "negative_count":int(train.negative.sum()),"negative_prevalence":prevalence,
              "majority_class":int(prevalence>=.5),"majority_training_accuracy":majority,
              "majority_negative_recall":1.0 if prevalence>=.5 else 0.0,
              "constant_score_average_precision_reference":prevalence,
              "constant_probability_brier_training":prevalence*(1-prevalence),
              "constant_probability_log_loss_training":float(-prevalence*np.log(prevalence)-(1-prevalence)*np.log(1-prevalence))}
    pair=df.groupby(["user_id","parent_asin"]).size()
    full_text=(df.title.map(clean_text)+" "+df.text.map(clean_text)).str.strip().str.casefold()
    long_text=full_text.str.split().str.len().ge(config["split"]["copied_text_min_words"])
    repeated_excess=int(full_text[long_text].duplicated().sum())
    diagnostics={"text_iqr_upper_fence_train":text_fence,"helpful_vote_iqr_upper_fence_train":vote_fence,
                 "top_10_products_train_share":top_ten_share,"repeated_user_product_pairs":int((pair>1).sum()),
                 "normalized_long_text_duplicate_excess":repeated_excess,
                 "metadata_exact_duplicate_excess":meta_duplicates,
                 "raw_json_parse_errors":0,"join_unmatched_reviews":int((~df.has_metadata).sum()),
                 "train_non_ascii_rows":int(train.non_ascii.sum()),"train_missing_body_rows":int((~train.has_text).sum()),
                 "train_very_short_rows":int(train.very_short.sum()),"train_very_long_rows":int(train.very_long.sum()),
                 "valid_numeric_prices":int(meta.has_price.sum()),"raw_nonnull_prices":int(meta.price.notna().sum()),
                 "train_word_count_median":float(train.word_count.median()),"train_word_count_max":int(train.word_count.max())}
    # Plots use plain English labels for portable typography. Persian interpretation is in the report.
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,"axes.spines.top":False,"axes.spines.right":False,"axes.titleweight":"bold","figure.facecolor":"white"})
    fig,ax=plt.subplots(figsize=(8,4.3))
    for j,cat in enumerate(config["categories"]):
        g=ratings[ratings.source_category.eq(cat)].set_index("rating").reindex(range(1,6),fill_value=0)
        ax.bar(np.arange(1,6)+(j-.5)*.34,g.pct,width=.34,color=COLORS[j],label=f"{LABELS[cat]} (n={int(g.n.sum()):,})")
    ax.set(xticks=range(1,6),xlabel="Star rating",ylabel="Share of training reviews (%)",title="Five-star reviews dominate both categories")
    ax.legend(frameon=False);fig.tight_layout();save_figure(root,"01_rating_distribution")
    fig,ax=plt.subplots(figsize=(8,4.3))
    bins=np.r_[0,np.geomspace(1,max(2,train.word_count.max()),45)]
    for j,(cat,g) in enumerate(train.groupby("source_category")):
        ax.hist(g.word_count,bins=bins,weights=np.ones(len(g))*100/len(g),histtype="step",linewidth=2,color=COLORS[j],label=LABELS[cat])
    ax.set(xscale="symlog",xlabel="Body words (log scale above 1)",ylabel="Share within category (%)",title="Review lengths have a long right tail");ax.legend(frameon=False);fig.tight_layout();save_figure(root,"02_text_length")
    names={"has_text":"Body text","has_review_title":"Review title","has_review_image":"Review image URL","has_metadata":"Metadata join","has_product_image":"Product image URL","has_price":"Numeric price","has_timestamp":"Timestamp","has_interaction":"User-product link"}
    fig,ax=plt.subplots(figsize=(8,4.6))
    for j,cat in enumerate(config["categories"]):
        g=modality[(modality.unit=="review")&(modality.category==cat)].set_index("modality").reindex(review_modalities)
        ax.barh(np.arange(len(g))+(j-.5)*.34,g.available_pct,height=.34,color=COLORS[j],label=LABELS[cat])
    ax.set(yticks=np.arange(len(names)),yticklabels=list(names.values()),xlim=(0,105),xlabel="Available at review level (%)",title="Image links and numeric prices differ sharply in availability")
    ax.invert_yaxis();ax.legend(frameon=False,loc="upper center",bbox_to_anchor=(.5,-.15),ncol=2);fig.tight_layout();save_figure(root,"03_modalities")
    fig,ax=plt.subplots(figsize=(8,4.3))
    groups=[train.loc[train.rating.eq(r),"word_count"].values for r in range(1,6)]
    bp=ax.boxplot(groups,tick_labels=range(1,6),showfliers=False,patch_artist=True)
    for box in bp["boxes"]:box.set_facecolor("#C5DCE5")
    ax.set(xlabel="Star rating",ylabel="Body words (outlier points hidden)",title="Text length varies with rating in the training partition");fig.tight_layout();save_figure(root,"04_length_rating")
    fig,ax=plt.subplots(figsize=(8,4.3))
    for j,(cat,g) in enumerate(monthly.groupby("source_category")):
        ax.plot(pd.to_datetime(g.month),g.n,color=COLORS[j],label=LABELS[cat],linewidth=1.6)
    ax.set(yscale="log",xlabel="Review month (UTC)",ylabel="Training reviews per month (log)",title="Category histories cover different time periods");ax.legend(frameon=False);fig.tight_layout();save_figure(root,"05_monthly_activity")
    fig,ax=plt.subplots(figsize=(8,4.3))
    for j,(cat,g) in enumerate(length_rates.groupby("source_category")):
        ax.plot(g.length_bin.astype(str),100*g.negative_rate,marker="o",color=COLORS[j],label=LABELS[cat])
    ax.set(xlabel="Body length (words)",ylabel="One- or two-star share (%)",title="Low-rating prevalence varies across text-length groups")
    ax.legend(frameon=False);fig.tight_layout();save_figure(root,"06_negative_by_length")
    fig,ax=plt.subplots(figsize=(8,4.3))
    cumulative=product_counts.cumsum()/len(train)
    ax.plot(np.arange(1,len(cumulative)+1)/len(cumulative)*100,cumulative*100,color=COLORS[0],linewidth=2)
    ax.plot([0,100],[0,100],"--",color="gray",linewidth=1)
    ax.set(xlabel="Products sorted by review count (%)",ylabel="Cumulative training reviews (%)",title="A small set of products contributes many reviews")
    fig.tight_layout();save_figure(root,"07_product_concentration")
    fig,ax=plt.subplots(figsize=(8,4.3))
    for j,cat in enumerate(config["categories"]):
        g=verified[verified.source_category.eq(cat)].set_index("verified_purchase")
        values=[100*g.loc[v,"negative_rate"] if v in g.index else np.nan for v in [False,True]]
        ax.bar(np.arange(2)+(j-.5)*.34,values,width=.34,color=COLORS[j],label=LABELS[cat])
    ax.set(xticks=[0,1],xticklabels=["Not verified","Verified"],ylabel="One- or two-star share (%)",title="Verification is associated with rating, not a causal treatment")
    ax.legend(frameon=False);fig.tight_layout();save_figure(root,"08_verified_rating")
    results={"identity":{"name":config["student_name"],"student_id":config["student_id"]},
             "quality":quality,"categories":inventory,"split":split_audit,"diagnostics":diagnostics,"baseline":baseline,
             "eda_scope":"Retained training reviews only. Full-data access is restricted to schema, integrity, time-range and input-availability auditing.",
             "software":{"python":platform.python_version(),**{x:importlib.metadata.version(x) for x in ["pandas","numpy","matplotlib","scipy"]}},
             "source_files":manifest}
    (root/"reports/phase1/audit_summary.json").write_text(json.dumps(results,ensure_ascii=False,indent=2,allow_nan=False),encoding="utf-8")
    print(json.dumps({"quality":quality,"split":split_audit,"diagnostics":diagnostics,"baseline":baseline},indent=2))
    return results


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=ROOT)
    run(parser.parse_args().root)
