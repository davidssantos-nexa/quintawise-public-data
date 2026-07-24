"use client";

import { useEffect, useRef, useState } from "react";
import maplibregl from "maplibre-gl";
import MapboxDraw from "@mapbox/mapbox-gl-draw";

const labels = {
  administrative: "Localização",
  land_cover: "Uso do solo",
  fire_hazard: "Incêndio",
  water: "Água superficial",
  terrain: "Terreno"
};

const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(
  /\/$/,
  ""
);

function ModuleBadge({ name, module }) {
  return (
    <div className={`module ${module.status}`}>
      <strong>{labels[name]}</strong>
      <span>{module.status}</span>
      {module.message && <small>{module.message}</small>}
    </div>
  );
}

function ClassList({ title, items }) {
  if (!items?.length) return null;
  return (
    <section className="resultBlock">
      <h3>{title}</h3>
      {items.map((item) => (
        <div className="barRow" key={`${item.code}-${item.label}`}>
          <div><strong>{item.label}</strong><span>{item.percentage}%</span></div>
          <div className="bar"><i style={{width: `${Math.min(item.percentage, 100)}%`}} /></div>
        </div>
      ))}
    </section>
  );
}

export default function Home() {
  const mapNode = useRef(null);
  const mapRef = useRef(null);
  const drawRef = useRef(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (mapRef.current) return;
    const map = new maplibregl.Map({
      container: mapNode.current,
      style: {
        version: 8,
        sources: {
          osm: {
            type: "raster",
            tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
            tileSize: 256,
            attribution: "© OpenStreetMap contributors"
          }
        },
        layers: [{ id: "osm", type: "raster", source: "osm" }]
      },
      center: [-8.0, 39.5],
      zoom: 6.3
    });
    map.addControl(new maplibregl.NavigationControl(), "top-right");
    const draw = new MapboxDraw({
      displayControlsDefault: false,
      controls: { polygon: true, trash: true },
      defaultMode: "draw_polygon"
    });
    map.addControl(draw, "top-left");
    mapRef.current = map;
    drawRef.current = draw;
    return () => map.remove();
  }, []);

  async function analyse() {
    setError("");
    setResult(null);
    const feature = drawRef.current?.getAll()?.features?.find(
      (item) => item.geometry?.type === "Polygon"
    );
    if (!feature) {
      setError("Desenha primeiro um polígono no mapa.");
      return;
    }
    setBusy(true);
    try {
      const response = await fetch(`${API_URL}/analyses`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ geometry: feature.geometry })
      });
      const contentType = response.headers.get("content-type") || "";
      const payload = contentType.includes("application/json")
        ? await response.json()
        : null;
      if (!response.ok) throw new Error(payload?.detail || "Falha na análise.");
      setResult(payload);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main>
      <header className="hero">
        <p className="eyebrow">QuintaWise · Public Land Intelligence</p>
        <h1>Informação pública. Terrenos mais claros.</h1>
        <p className="intro">
          QuintaWise transforma informação territorial pública portuguesa num
          retrato factual, rastreável e comparável de terrenos e propriedades
          rurais.
        </p>
      </header>

      <section className="mapShell">
        <div ref={mapNode} className="map" />
        <div className="mapActions">
          <button onClick={analyse} disabled={busy}>
            {busy ? "A analisar…" : "Analisar terreno"}
          </button>
          <span>Usa o ícone de polígono no mapa.</span>
        </div>
      </section>

      {error && <section className="error">{error}</section>}

      {result && (
        <>
          <section className="moduleGrid">
            {Object.entries(result.modules).map(([name, module]) => (
              <ModuleBadge key={name} name={name} module={module} />
            ))}
          </section>

          <section className="results">
            <div>
              <p className="eyebrow">Área analisada</p>
              <h2>{result.area_m2.toLocaleString("pt-PT")} m²</h2>
              <a
                className="reportLink"
                href={`${API_URL}/analyses/${result.id}/report`}
                target="_blank"
                rel="noreferrer"
              >
                Abrir relatório imprimível
              </a>
              {result.administrative.map((item) => (
                <p key={`${item.parish_code}-${item.parish_name}`}>
                  <strong>{item.parish_name}</strong>, {item.municipality_name}
                  {item.district_name ? `, ${item.district_name}` : ""}
                  {" · "}{item.percentage}%
                </p>
              ))}
              <ClassList title="Uso e ocupação do solo" items={result.land_cover} />
              <ClassList title="Perigosidade estrutural" items={result.fire_hazard} />
              {result.water.map((item) => (
                <p key={item.label}>
                  <strong>{item.label}</strong>: {item.intersects ? "interseta o polígono" : `${item.distance_m} m`}
                </p>
              ))}
              {result.terrain && (
                <p>
                  Elevação: {result.terrain.elevation_min_m}–{result.terrain.elevation_max_m} m
                  · média {result.terrain.elevation_mean_m} m
                </p>
              )}
            </div>
            <div className="evidence">
              <h3>Fontes e métodos</h3>
              {result.provenance.map((item) => (
                <div key={`${item.authority}-${item.dataset}-${item.version}`}>
                  <strong>{item.authority}</strong>
                  <p>{item.dataset} · {item.version}</p>
                  <small>
                    {item.method} · confiança {item.confidence}
                    {item.acquired_at
                      ? ` · obtido em ${new Date(item.acquired_at).toLocaleDateString("pt-PT")}`
                      : ""}
                  </small>
                  {item.checksum_sha256 && (
                    <code title={item.checksum_sha256}>
                      SHA-256 {item.checksum_sha256.slice(0, 12)}…
                    </code>
                  )}
                  {item.limitations?.map((limitation) => (
                    <small key={limitation}>{limitation}</small>
                  ))}
                </div>
              ))}
              <h3>Limitações</h3>
              <ul>{result.limitations.map((item) => <li key={item}>{item}</li>)}</ul>
            </div>
          </section>
        </>
      )}
    </main>
  );
}
