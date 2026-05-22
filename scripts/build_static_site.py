import shutil
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SITE_DIR = ROOT_DIR / "site"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "output"
DEFAULT_DIST_DIR = ROOT_DIR / "dist"


def build_static_site(
    site_dir: Path = DEFAULT_SITE_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    dist_dir: Path = DEFAULT_DIST_DIR,
) -> Path:
    if not site_dir.exists():
        raise FileNotFoundError(f"Site directory not found: {site_dir}")

    report_json = output_dir / "latest-report.json"
    if not report_json.exists():
        raise FileNotFoundError(
            f"Latest report data not found: {report_json}. Run main.py first."
        )

    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    shutil.copytree(site_dir, dist_dir)

    data_dir = dist_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(report_json, data_dir / "latest-report.json")

    return dist_dir


if __name__ == "__main__":
    path = build_static_site()
    print(f"Static site built at {path}")
