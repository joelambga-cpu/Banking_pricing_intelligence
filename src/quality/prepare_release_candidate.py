"""Prepare a reviewable local release candidate; does not publish anything."""
from pathlib import Path
import json
import shutil
import zipfile
import hashlib

ROOT = Path(__file__).resolve().parents[2]
REPORT = Path(r"C:\Users\joela\Downloads\BankingPricingIntelligence_QuattroPagine")
visual_path = REPORT / "bankingpricingintelligence.Report/definition/pages/segmentanalysis202610/visuals/8e835f384ac81785520c/visual.json"
backup = ROOT / "docs/evidence/segment_table_before_release.json"
if not backup.exists():
    shutil.copy2(visual_path, backup)
visual = json.loads(visual_path.read_text(encoding="utf-8-sig"))
specs = [
    ("segment", "Segment", 160, None, "Column"),
    ("Segment Quota clienti in calo", "Customers declining", 235, "0.00%", "Measure"),
    ("Segment Deflusso proxy mln EUR", "Outflow proxy (EUR m)", 255, "0.00", "Measure"),
    ("Segment Deflusso proxy su depositi", "Proxy / deposits", 205, "0.00%", "Measure"),
    ("Clienti Target", "Eligible customers", 210, "#,0", "Measure"),
    ("Segment Depositi target mln EUR", "Eligible deposits (EUR m)", 270, "0.00", "Measure"),
    ("Segment Quota depositi target", "Eligible deposit share", 250, "0.0%", "Measure"),
    ("Segment Costo targeted mila EUR", "Annual cost (EUR k)", 215, "0.0", "Measure"),
]
projections, widths = [], []
for field, label, width, fmt, kind in specs:
    ref = "SegmentAnalysis." + field
    projection = {"field": {kind: {"Expression": {"SourceRef": {"Entity": "SegmentAnalysis"}}, "Property": field}}, "queryRef": ref, "nativeQueryRef": label, "displayName": label}
    if fmt:
        projection["format"] = fmt
    projections.append(projection)
    widths.append({"properties": {"value": {"expr": {"Literal": {"Value": str(width) + "D"}}}}, "selector": {"metadata": ref}})
visual["visual"]["query"]["queryState"]["Values"]["projections"] = projections
visual["visual"]["objects"]["columnWidth"] = widths
visual["visual"]["visualContainerObjects"]["general"][0]["properties"]["altText"]["expr"]["Literal"]["Value"] = "'Segment exposure across all customers and targeted repricing eligibility. Outflow is a synthetic balance-change proxy, not an observed cash flow.'"
visual_path.write_text(json.dumps(visual, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
# Structural checks are deliberately distinct from native Power BI rendering.
model = (REPORT / "bankingpricingintelligence.SemanticModel/definition/tables/SegmentAnalysis.tmdl").read_text(encoding="utf-8")
for field, _, _, _, kind in specs:
    declaration = f"column {field}" if kind == "Column" else f"measure '{field}'"
    if declaration not in model:
        raise ValueError("Missing field: " + declaration)
if sum(row[2] for row in specs) > visual["position"]["width"]:
    raise ValueError("Table columns exceed existing visual width")
for path in (REPORT / "bankingpricingintelligence.Report/definition").rglob("*.json"):
    json.loads(path.read_text(encoding="utf-8-sig"))

release = ROOT / "releases/banking-pricing-intelligence-v1-candidate"
if release.exists():
    raise FileExistsError("Release already exists; inspect before regenerating")
release.mkdir(parents=True)
for folder in ["src", "sql"]:
    shutil.copytree(ROOT / folder, release / folder, ignore=shutil.ignore_patterns("__pycache__", "prepare_release_candidate.py"))
for name in ["README.md", "requirements.txt", "run_pipeline.py", ".gitignore"]:
    shutil.copy2(ROOT / name, release / name)
for folder in ["processed", "simulated", "analytics", "database"]:
    shutil.copytree(ROOT / "data" / folder, release / "data" / folder)
(release / "data/raw").mkdir()
for name in ["italy_household_deposit_rate", "italy_household_mortgage_rate", "ecb_deposit_facility_rate"]:
    source = sorted((ROOT / "data/raw").glob(name + "_*.csv"))[-1]
    shutil.copy2(source, release / "data/raw" / source.name)
(release / "docs/evidence").mkdir(parents=True)
for name in ["CASE_STUDY_EN.md", "RELEASE_NOTES_EN.md", "RISPOSTE_BUSINESS.md"]:
    shutil.copy2(ROOT / "docs" / name, release / "docs" / name)
for name in ["business_answers.json", "release_checks.json", "pipeline_replay.log"]:
    shutil.copy2(ROOT / "docs/evidence" / name, release / "docs/evidence" / name)
log = release / "docs/evidence/pipeline_replay.log"
log.write_text(log.read_text(encoding="utf-8").replace(str(ROOT), "<PROJECT_ROOT>"), encoding="utf-8")
dashboard = release / "dashboard"
dashboard.mkdir()
shutil.copy2(REPORT / "bankingpricingintelligence.pbip", dashboard)
for name in ["bankingpricingintelligence.Report", "bankingpricingintelligence.SemanticModel"]:
    shutil.copytree(REPORT / name, dashboard / name, ignore=shutil.ignore_patterns(".pbi", ".git"))
local_root = str(ROOT)
example_root = r"C:\banking-pricing-intelligence"
for path in (dashboard / "bankingpricingintelligence.SemanticModel").rglob("*.tmdl"):
    content = path.read_text(encoding="utf-8-sig")
    path.write_text(content.replace(local_root, example_root), encoding="utf-8")
readme = (release / "README.md").read_text(encoding="utf-8")
start = readme.find("The authoritative report location confirmed by the user")
if start >= 0:
    end = readme.find("\n\n", start)
    readme = readme[:start] + "The report is included under `dashboard/`. See [release notes](docs/RELEASE_NOTES_EN.md) for local path configuration and outstanding native Power BI checks.\n" + (readme[end:] if end >= 0 else "")
(release / "README.md").write_text(readme, encoding="utf-8")
manifest = {str(p.relative_to(release)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest() for p in release.rglob("*") if p.is_file()}
(release / "MANIFEST_SHA256.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
archive = release.with_suffix(".zip")
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as package:
    for path in release.rglob("*"):
        if path.is_file():
            package.write(path, str(path.relative_to(release.parent)))
with zipfile.ZipFile(archive) as package:
    if package.testzip() is not None:
        raise ValueError("Invalid release ZIP")
print(json.dumps({"archive": str(archive), "files": len(manifest), "segment_table_columns": len(specs), "native_render": "PENDING", "published": False}, indent=2))
