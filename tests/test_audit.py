import json
import unittest
from pathlib import Path
import math
import pandas as pd
from src.data_io import parse_price, has_image_url, verify_sources
from src.split import clean_text, product_partition, assign_partitions

ROOT = Path(__file__).resolve().parents[1]


class ParsingTests(unittest.TestCase):
    def test_prices(self):
        self.assertEqual(parse_price("$1,299.50"),1299.5)
        for value in [None,"None","Unavailable","$20-$30",True,-1,{},float("inf")]:
            self.assertTrue(math.isnan(parse_price(value)),repr(value))

    def test_url_is_not_pixel_availability(self):
        self.assertTrue(has_image_url([{"large":"https://example.com/a.jpg"}]))
        for value in [None,[],[{}],[{"variant":"MAIN"}]]:
            self.assertFalse(has_image_url(value))

    def test_unicode_and_html(self):
        self.assertEqual(clean_text(" Ａ &amp; B<br>   C "),"A & B C")


class SplitTests(unittest.TestCase):
    def test_group_assignment_is_order_independent(self):
        ids=["B000000001","B000000002","B000000001"]
        assigned=[product_partition(x,401100025) for x in ids]
        self.assertEqual(assigned[0],assigned[2])
        self.assertEqual(assigned,list(reversed([product_partition(x,401100025) for x in reversed(ids)])))

    def test_copied_text_purge_does_not_use_labels(self):
        config=json.loads((ROOT/"configs/phase1.json").read_text(encoding="utf-8"))
        groups={}
        for i in range(1000):
            product=f"B{i:09d}"
            groups.setdefault(product_partition(product,config["seed"]),product)
            if len(groups)==3:break
        data=pd.DataFrame([{"parent_asin":p,"title":"same title","text":"these are five or more repeated words","user_id":str(i),"rating":i+1} for i,p in enumerate(groups.values())])
        first,audit=assign_partitions(data,config)
        data.rating=5-data.rating
        second,_=assign_partitions(data,config)
        self.assertEqual(first.split_exclusion.tolist(),second.split_exclusion.tolist())
        self.assertEqual(audit["purged_rows"],2)
        self.assertFalse(first.loc[first.split.eq("train"),"split_exclusion"].iloc[0])


class DeliveredArtifactsTests(unittest.TestCase):
    def test_sources_are_the_recorded_versions(self):
        self.assertEqual(len(verify_sources(ROOT)),4)

    def test_counts_and_partition_integrity(self):
        s=json.loads((ROOT/"reports/phase1/audit_summary.json").read_text(encoding="utf-8"))
        self.assertEqual(s["quality"]["raw_review_rows"],87713)
        self.assertEqual(sum(s["split"]["before_purge_rows"].values()),87713-s["quality"]["exact_duplicate_excess"]-s["quality"]["quarantined_rows"])
        self.assertEqual(sum(s["split"]["retained_rows"].values())+s["split"]["purged_rows"],sum(s["split"]["before_purge_rows"].values()))
        self.assertTrue(all(v==0 for v in s["split"]["product_overlap"].values()))
        self.assertTrue(all(v==0 for v in s["split"]["long_exact_text_overlap_after_purge"].values()))

    def test_export_has_no_direct_reviewer_id(self):
        columns=pd.read_csv(ROOT/"data/processed/audit_features.csv.gz",nrows=0).columns
        self.assertIn("user_hash",columns)
        self.assertNotIn("user_id",columns)

    def test_metrics_are_training_references(self):
        baseline=json.loads((ROOT/"reports/phase1/audit_summary.json").read_text(encoding="utf-8"))["baseline"]
        self.assertEqual(baseline["majority_negative_recall"],0)
        self.assertAlmostEqual(baseline["majority_training_accuracy"],1-baseline["negative_prevalence"])


if __name__=="__main__":
    unittest.main()
