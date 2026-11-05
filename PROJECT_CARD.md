# Project card - Path ب

**Student:** محمدرضا استادعظیم
**Student ID:** 401100025
**Course:** تحلیل داده، پاییز ۱۴۰۵

## 1. Path and selected subset

Path ب, Amazon Reviews'23, McAuley Lab. Use **all** records from the official `Magazine_Subscriptions` and `Subscription_Boxes` review and metadata files. Raw totals are 71,497 + 16,216 reviews and 3,391 + 641 metadata records. Selection is motivated by a shared subscription-service setting and manageable resources, not by observed predictive performance. No star-based sampling or resampling is applied. This two-category study does not represent Amazon as a whole.

## 2. Working title

شناسایی نارضایتی متنی در نقدهای خدمات اشتراکی با ممیزی داده‌های چندوجهی

English: Identifying textual dissatisfaction in subscription-service reviews with an audit of multimodal data availability.

## 3. Real decision

Support a **human review queue** for complaint-like text when a star score is unavailable or deliberately hidden, such as imported feedback. In this benchmark the existing star is hidden from all inputs and used only as a weak reference label. If an authentic star is available in production, it should be used directly; predicting its threshold adds no operational value. The data does not establish refund eligibility, fraud, the truth of a complaint, or a customer's future behavior.

## 4. Units

Observation and prediction: one published review. Product entity and primary split unit: `parent_asin`, not variant `asin`. Join: many reviews to one metadata row on `parent_asin`. User is a pseudonymous analytic ID only. Input-availability summaries use review and product denominators separately.

## 5. Domain and population

Published Amazon reviews in the two chosen categories, 2001-10-26 to 2023-08-30 UTC in the downloaded files. The catalog is a crawl-time snapshot. The intended evaluation is **retrospective generalization to unseen products**, not an estimate of performance on chronologically future data or on new users. Selection, survival, category, language and exposure biases limit external validity.

## 6. Main question and alternatives

1. **Selected:** With stars hidden, can text plus product metadata and review context identify the one-/two-star proxy on held-out products better than constant-score and text-only references?
2. How do short/long reviews and verified purchases differ in low-rating prevalence within each category? Feasible descriptive supporting question, not a causal question.
3. Can helpfulness votes be predicted from review text? Deferred because this snapshot has no common follow-up duration or vote-arrival timestamps. Review age alone cannot recover a fixed exposure horizon.

Question 1 connects the requested text and structured branches to a measurable human-triage task, permits product cold-start evaluation, and enables meaningful modality ablation. Phase 1 establishes feasibility; it does not answer the predictive question with model results.

## 7. Target and availability time

`y = 1[rating <= 2]`; 3-5 stars form the comparison class. This is an imperfect label for dissatisfaction. Later sensitivity analysis will exclude 3-star reviews. Predict after text submission. Eligible context: review body/title, verified status, calendar context and explicitly retrospective product attributes. Exclude `rating`, `average_rating`, `rating_number`, accumulated `helpful_vote`, all raw IDs and any full-data target aggregate from model inputs. Price has no usable values and is excluded. Product metadata timing is unknown, so a prospective deployment would require a timestamped catalog snapshot or a restricted feature set.

## 8. Initial baselines

Define a majority-class rule and a constant training-prevalence score. In the training partition the negative share is 20.3359%, so majority training accuracy is 79.6641% while negative recall is zero. These are **training descriptive references**, not test results. In Phase 3 add TF-IDF + logistic regression as the text-only reference and a small regularized structured-only branch. Fit encoders/vocabulary/thresholds only on training, select with validation, and compare fusion on the same retained rows.

## 9. Proposed evaluation

Primary: average precision (AP, sklearn definition, not trapezoidal PR area). Secondary: macro-F1, negative recall/precision, balanced accuracy, ROC-AUC where both classes exist, Brier score and calibration. Choose any threshold on validation only. Report category and text-length strata with counts. Later obtain uncertainty by 1,000 bootstrap replicates over held-out **products**, not individual reviews. Small categories or image-bearing groups may have wide uncertainty.

## 10. Fixed split

Use `u = int(SHA256('401100025:' + parent_asin)[:16], 16) / 2**64`. Assign train if u < .70, validation if .70 <= u < .85, test otherwise. Proportions refer to products in expectation, not exact review counts. Remove exact raw duplicates and quarantine conflicting business keys before assignment. Purge normalized title+body strings with >=5 whitespace words from lower-priority partitions if they occur in a higher-priority partition, with train > validation > test. The purge never uses stars. All assignments and exclusions are recorded. Final rows: train 59,963; validation 10,912; test 15,669. Product intersections and qualifying exact text intersections are zero. User overlap is permitted, reported, and not described as user cold-start. Generic short and near-duplicate text can remain. Phase-one value-level EDA uses only train. Validation/test labels remain unused for model choice and evaluation.

## 11. Leakage risks

Target scores and product rating aggregates directly disclose the label or include held-out reviews. Snapshot helpfulness, price and edited catalog text can postdate a review. Variant-based or row-random splits can share a parent product. Repeated users and copied text create dependence. Full-data TF-IDF, imputation, normalization, target encoding and data-driven thresholds leak holdout information. Parent grouping, copied-text purging, blocked features and training-only fitting mitigate these risks; they do not prove all leakage absent.

## 12. Proposed unsupervised work

For Phase 2, fit TF-IDF on train, reduce with TruncatedSVD, and cluster normalized vectors with K-means for k in {3,5,8}. Inspect terms and examples for delivery, content mismatch, value and product-quality themes. Choose k using silhouette on a fixed training sample plus stability over seeds/subsamples, not label agreement. Examine rating/category only after clustering. This work is planned, not claimed as executed in Phase 1.

## 13. Path-specific extension

Phase 1 quantifies text, review images, product images, price, metadata, timestamp and user-product links. For later phases compare text-only, structured-only, and fused inputs on identical partitions. Structured content will include category hierarchy when available, verification, calendar context and catalog attributes with explicit missing indicators. Product-image URLs exist for every product, but image bytes have **not** been downloaded or validated and no image model has been run. An optional image branch must first validate pixels and use a documented pretrained encoder. A multimodal bonus is not established merely by this plan or by appending columns.

## 14. Ethics, privacy, bias and governance

Do not identify reviewers. Derived exports contain a salted hash rather than raw `user_id`; this is pseudonymization, not anonymous data. Raw downloaded files retain upstream pseudonyms and text, so they are excluded from Git. Review text may disclose sensitive details; reports show aggregates and do not reproduce full individual reviews. The inspected dataset card does not state a clear redistribution license; public access is not a blanket license grant. Retain attribution, source URLs and checksums, and review upstream rights before public redistribution. Do not infer causation or use predictions to reject complaints automatically. Keep human review, category-specific error checks, and the course-required AI disclosure.
