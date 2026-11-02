"""Build and execute the small audit notebook without a notebook-server dependency."""
from __future__ import annotations
import base64
import contextlib
import io
import json
import os
from pathlib import Path
import traceback

ROOT=Path(__file__).resolve().parents[1]


def build(root=ROOT):
    cells=[]
    def md(text):cells.append({"cell_type":"markdown","metadata":{},"source":text.splitlines(keepends=True)})
    def code(text):cells.append({"cell_type":"code","metadata":{},"source":text.splitlines(keepends=True),"execution_count":None,"outputs":[]})
    md("# ممیزی فاز اول، مسیر ب\nمحمدرضا استادعظیم — 401100025\n\nThis notebook displays actual computed outputs. Run `python -m src.audit` to regenerate the source tables and figures. All value-level EDA below is training-only; schema and modality availability audit the complete accepted inputs.")
    code("from pathlib import Path\nimport json, sys\nimport pandas as pd\nROOT = Path.cwd()\nif not (ROOT / 'configs/phase1.json').exists():\n    ROOT = ROOT.parent\nif not (ROOT / 'configs/phase1.json').exists():\n    raise RuntimeError('Open from the project root or notebooks directory')\nsys.path.insert(0, str(ROOT))\nfrom src.data_io import verify_sources\nprint('Verified official input files:', len(verify_sources(ROOT)))\nsummary = json.loads((ROOT / 'reports/phase1/audit_summary.json').read_text(encoding='utf-8'))\nprint('Student:', summary['identity']['name'], summary['identity']['student_id'])")
    md("## 1. Provenance and structure\nThe source hashes are pinned, not recomputed to silently accept changing inputs.")
    code("print(pd.read_csv(ROOT / 'tables/source_inventory.csv').to_string(index=False))\nprint(pd.read_csv(ROOT / 'tables/category_inventory.csv').to_string(index=False))")
    md("## 2. Quality decisions\nExact raw copies are deduplicated. Different rows sharing user/product/time are quarantined together. Original files stay unchanged.")
    code("print(pd.read_csv(ROOT / 'tables/quality_issues.csv').to_string(index=False))\nprint('Diagnostics:', json.dumps(summary['diagnostics'], indent=2))")
    md("## 3. Availability of each modality\nURL presence is not downloaded pixel availability. Product and review denominators are separate.")
    code("print(pd.read_csv(ROOT / 'tables/modality_availability.csv').to_string(index=False))\nprint(pd.read_csv(ROOT / 'tables/missingness_category_association.csv').to_string(index=False))")
    md("## 4. Training-only EDA\nNon-ASCII is an encoding/script flag, not a language prediction. Outliers remain in the audit.")
    code("print(pd.read_csv(ROOT / 'tables/train_numeric_summary.csv').to_string(index=False))\nprint(pd.read_csv(ROOT / 'tables/train_text_audit.csv').to_string(index=False))")
    # display_png is provided by this executor and defined in the cell for normal Jupyter too.
    code("def show_plot(name):\n    from IPython.display import display, Image\n    display(Image(filename=str(ROOT / 'figures' / (name + '.png'))))\nshow_plot('01_rating_distribution')\nshow_plot('02_text_length')\nshow_plot('03_modalities')")
    md("## 5. Multivariable relationships\nAssociations do not identify causal effects. Row counts accompany every subgroup rate.")
    code("print(pd.read_csv(ROOT / 'tables/train_correlations.csv').to_string(index=False))\nprint(pd.read_csv(ROOT / 'tables/train_negative_by_length.csv').to_string(index=False))\nprint(pd.read_csv(ROOT / 'tables/train_negative_by_verified.csv').to_string(index=False))\nshow_plot('04_length_rating')\nshow_plot('06_negative_by_length')\nshow_plot('08_verified_rating')")
    code("show_plot('05_monthly_activity')\nshow_plot('07_product_concentration')")
    md("## 6. Split integrity and baseline references\nProducts never cross partitions. Exact normalized title+body copies with at least five words are purged from lower-priority partitions without consulting ratings. User overlap is allowed for product cold-start, and is disclosed. These baseline values are training references, not held-out predictions.")
    code("print(json.dumps(summary['split'], indent=2))\nprint(json.dumps(summary['baseline'], indent=2))\nassert all(x == 0 for x in summary['split']['product_overlap'].values())\nassert all(x == 0 for x in summary['split']['long_exact_text_overlap_after_purge'].values())\nprint('No predictive model was fitted in phase one.')")
    md("## 7. Next phases and disclosure\nSee PROJECT_CARD.md for the frozen question, three candidate questions, metrics, leakage controls and planned TF-IDF/SVD/clustering. See AI_USAGE.md for substantial AI assistance. Review the report and source code before defending the work.")
    # Execute exactly the delivered cells, capturing actual stdout and displayed PNGs.
    namespace={"__name__":"__main__"}
    previous=os.getcwd();os.chdir(root)
    try:
        import IPython.display as ipd
        original_display=ipd.display
        current_outputs=[]
        def capture_display(obj):
            if hasattr(obj,"_repr_png_"):
                data=obj._repr_png_()
                if isinstance(data,tuple):data=data[0]
                if isinstance(data,bytes):data=base64.b64encode(data).decode()
                current_outputs.append({"output_type":"display_data","metadata":{},"data":{"image/png":data,"text/plain":["<Actual analysis figure>"]}})
            else:print(obj)
        ipd.display=capture_display
        execution_count=0
        for index,cell in enumerate(cells):
            cell["id"]=f"phase1-{index:03d}"
            if cell["cell_type"]!="code":continue
            execution_count+=1;current_outputs=[];stream=io.StringIO()
            with contextlib.redirect_stdout(stream):exec(compile("".join(cell["source"]),f"notebook_cell_{execution_count}","exec"),namespace)
            outputs=[]
            if stream.getvalue():outputs.append({"output_type":"stream","name":"stdout","text":stream.getvalue().splitlines(keepends=True)})
            outputs.extend(current_outputs)
            cell.update(execution_count=execution_count,outputs=outputs)
    finally:
        os.chdir(previous)
        if 'original_display' in locals():ipd.display=original_display
    notebook={"nbformat":4,"nbformat_minor":5,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":summary_python(root)}},"cells":cells}
    (root/"notebooks/phase1_audit.ipynb").write_text(json.dumps(notebook,ensure_ascii=False,indent=1),encoding='utf-8')
    print(f"Built and executed notebook ({execution_count} code cells).")


def summary_python(root):
    return json.loads((root/"reports/phase1/audit_summary.json").read_text(encoding='utf-8'))["software"]["python"]


if __name__=="__main__":build()
