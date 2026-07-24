from html import escape


def render_report_html(snapshot: dict) -> str:
    name = escape(snapshot.get("name") or "Terreno analisado")
    area = f"{snapshot['area_m2']:,.0f}".replace(",", " ")

    admin_items = snapshot.get("administrative", [])
    admin = (
        "".join(
            f"<li><strong>{escape(x['parish_name'])}</strong>, "
            f"{escape(x['municipality_name'])} — {x['percentage']:.1f}%</li>"
            for x in admin_items
        )
        or "<li>Sem dados administrativos disponíveis.</li>"
    )

    def classes(title: str, items: list[dict]) -> str:
        rows = (
            "".join(
                f"<tr><td>{escape(x['label'])}</td><td>{x['area_m2']:,.0f} m²</td>"
                f"<td>{x['percentage']:.1f}%</td></tr>"
                for x in items
            )
            or "<tr><td colspan='3'>Sem dados disponíveis.</td></tr>"
        )
        return (
            f"<h2>{escape(title)}</h2>"
            "<table><thead><tr><th>Classe</th><th>Área</th><th>%</th></tr></thead>"
            f"<tbody>{rows}</tbody></table>"
        )

    provenance = "".join(
        "<li>"
        f"<strong>{escape(x['authority'])}</strong> — {escape(x['dataset'])} "
        f"({escape(x['version'])}); {escape(x['method'])}; "
        f"confiança: {escape(x['confidence'])}"
        + (
            f"; obtido em {escape(str(x['acquired_at']))}"
            if x.get("acquired_at")
            else ""
        )
        + (
            f"; SHA-256 {escape(x['checksum_sha256'])}"
            if x.get("checksum_sha256")
            else ""
        )
        + "</li>"
        for x in snapshot.get("provenance", [])
    )
    limitations = "".join(
        f"<li>{escape(x)}</li>" for x in snapshot.get("limitations", [])
    )
    water = (
        "".join(
            f"<li>{escape(x['label'])}: "
            f"{'interseta o polígono' if x['intersects'] else str(x['distance_m']) + ' m'}</li>"
            for x in snapshot.get("water", [])
        )
        or "<li>Sem dados disponíveis.</li>"
    )

    return """<!doctype html>
<html lang="pt">
<head>
<meta charset="utf-8">
<title>QuintaWise — {name}</title>
<style>
body{{font-family:Arial,sans-serif;color:#17271d;max-width:900px;margin:40px auto;padding:0 24px}}
h1{{font-size:48px;line-height:1;margin-bottom:8px}} h2{{margin-top:34px}}
.meta{{color:#526157}} table{{width:100%;border-collapse:collapse}}
th,td{{text-align:left;padding:10px;border-bottom:1px solid #d9dedb}}
.notice{{background:#f2efe6;padding:18px;border-radius:12px;margin:24px 0}}
@media print{{body{{margin:0;max-width:none}}}}
</style>
</head>
<body>
<p>QuintaWise · Public Land Intelligence</p>
<h1>{name}</h1>
<p class="meta">Área analisada: <strong>{area} m²</strong></p>
<div class="notice">Este relatório organiza observações provenientes de dados públicos. Não constitui parecer jurídico, urbanístico, cadastral ou técnico.</div>
<h2>Localização administrativa</h2><ul>{admin}</ul>
{land_cover}
{fire_hazard}
<h2>Água superficial cartografada</h2><ul>{water}</ul>
<h2>Fontes e métodos</h2><ul>{provenance}</ul>
<h2>Limitações</h2><ul>{limitations}</ul>
</body></html>""".format(
        name=name,
        area=area,
        admin=admin,
        land_cover=classes("Uso e ocupação do solo", snapshot.get("land_cover", [])),
        fire_hazard=classes("Perigosidade estrutural", snapshot.get("fire_hazard", [])),
        water=water,
        provenance=provenance,
        limitations=limitations,
    )
