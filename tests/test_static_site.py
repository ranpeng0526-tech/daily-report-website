import json

from scripts.build_static_site import build_static_site


def test_build_static_site_copies_assets_and_report_data(tmp_path):
    site_dir = tmp_path / "site"
    output_dir = tmp_path / "output"
    dist_dir = tmp_path / "dist"
    site_dir.mkdir()
    output_dir.mkdir()

    (site_dir / "index.html").write_text("<html></html>", encoding="utf-8")
    (site_dir / "app.js").write_text("console.log('ok')", encoding="utf-8")
    (output_dir / "latest-report.json").write_text(
        json.dumps({"date": "2026-05-20"}),
        encoding="utf-8",
    )

    build_static_site(site_dir=site_dir, output_dir=output_dir, dist_dir=dist_dir)

    assert (dist_dir / "index.html").exists()
    assert (dist_dir / "app.js").exists()
    assert json.loads((dist_dir / "data" / "latest-report.json").read_text()) == {
        "date": "2026-05-20"
    }
