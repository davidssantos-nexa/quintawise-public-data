from app.services.reporting import render_report_html


def test_report_escapes_user_supplied_name():
    html = render_report_html(
        {
            "name": "<script>alert(1)</script>",
            "area_m2": 1000,
            "administrative": [],
            "land_cover": [],
            "fire_hazard": [],
            "water": [],
            "provenance": [],
            "limitations": [],
        }
    )
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
