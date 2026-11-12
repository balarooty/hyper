import { geoNaturalEarth1, geoPath, type GeoPermissibleObjects } from "d3-geo";
import { useMemo } from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { feature } from "topojson-client";
import type { GeometryCollection, Topology } from "topojson-specification";
import world from "world-atlas/countries-50m.json";
import { useColors } from "./theme";

type Country = { type: "Feature"; id?: string | number; properties: { name: string }; geometry: GeoPermissibleObjects };

const COUNTRIES = (() => {
  const topo = world as unknown as Topology<{ countries: GeometryCollection<{ name: string }> }>;
  return (feature(topo, topo.objects.countries) as unknown as { features: Country[] }).features;
})();

function largestPart(geometry: { type: string; coordinates: unknown[] }, p: ReturnType<typeof geoPath>) {
  if (geometry.type !== "MultiPolygon") return geometry;
  const parts = geometry.coordinates.map((coordinates) => ({ type: "Polygon", coordinates }));
  return parts.reduce((best, part) => (p.area(part as never) > p.area(best as never) ? part : best));
}

/** Natural Earth names as in world-atlas ("United States of America", "India", "Germany"…). */
export const COUNTRY_NAMES = COUNTRIES.map((c) => c.properties.name);

/**
 * No national borders are needed for most films: pass `colors.border` equal to `colors.land` to hide them, and keep
 * disputed areas out of frame.
 * World map that zooms from the whole world to `focus` and lights up `highlight` countries in order.
 * Names must match Natural Earth names (see COUNTRY_NAMES); unknown names throw so mistakes surface in Studio.
 */
export function MapReveal({
  highlight,
  focus,
  zoomFrames = 40,
  staggerFrames = 10,
  colors: given,
}: {
  highlight: string[];
  focus?: string;
  zoomFrames?: number;
  staggerFrames?: number;
  colors?: { land: string; border: string; hit: string; sea: string };
}) {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const C = useColors();
  const colors = given ?? { land: `${C.muted}55`, border: C.bg, hit: C.accent, sea: C.bg };
  for (const name of [...highlight, ...(focus ? [focus] : [])]) {
    if (!COUNTRY_NAMES.includes(name)) throw new Error(`MapReveal: unknown country '${name}'`);
  }
  const { path, start, end } = useMemo(() => {
    const projection = geoNaturalEarth1().fitSize([width, height], { type: "FeatureCollection", features: COUNTRIES } as never);
    const p = geoPath(projection);
    const target = COUNTRIES.find((c) => c.properties.name === focus);
    // Zoom to the largest landmass (mainland USA, not Alaska + Hawaii).
    const main = target ? largestPart(target.geometry as never, p) : null;
    const [[x0, y0], [x1, y1]] = main ? p.bounds(main as never) : [[0, 0], [width, height]];
    const k = target ? Math.min(8, 0.6 / Math.max((x1 - x0) / width, (y1 - y0) / height)) : 1;
    return { path: p, start: { k: 1, x: width / 2, y: height / 2 }, end: { k, x: (x0 + x1) / 2, y: (y0 + y1) / 2 } };
  }, [focus, width, height]);
  const t = interpolate(frame, [0, zoomFrames], [0, 1], { extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
  const k = start.k + (end.k - start.k) * t;
  const cx = start.x + (end.x - start.x) * t;
  const cy = start.y + (end.y - start.y) * t;
  return (
    <AbsoluteFill style={{ background: colors.sea }}>
      <svg width={width} height={height}>
        <g transform={`translate(${width / 2} ${height / 2}) scale(${k}) translate(${-cx} ${-cy})`}>
          {COUNTRIES.map((c, i) => {
            const order = highlight.indexOf(c.properties.name);
            const lit = order < 0 ? 0 : interpolate(frame - zoomFrames * 0.6 - order * staggerFrames, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            return <path key={i} d={path(c.geometry) ?? undefined} fill={lit > 0 ? colors.hit : colors.land} fillOpacity={lit > 0 ? 0.35 + 0.65 * lit : 1} stroke={colors.border} strokeWidth={0.6 / k} />;
          })}
        </g>
      </svg>
    </AbsoluteFill>
  );
}
