import "maplibre-gl/dist/maplibre-gl.css";
import "@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css";
import "./styles.css";

export const metadata = {
  title: "QuintaWise — Public Land Intelligence",
  description:
    "Informação territorial pública portuguesa num retrato factual, rastreável e comparável."
};

export default function RootLayout({ children }) {
  return (
    <html lang="pt">
      <body>{children}</body>
    </html>
  );
}
