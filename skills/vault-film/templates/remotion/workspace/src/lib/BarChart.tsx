import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { useColors, useFonts, useScale } from "./theme";

export interface BarRow {
  label: string;
  value: number;
  highlight?: boolean;
}

/** Horizontal ranked bars that grow in order; values count up. Pass rows sorted the way they should read. */
export function BarChart({ rows, title, unit = "", source, growFrames = 18, staggerFrames = 8, decimals = 0 }: {
  rows: BarRow[];
  title?: string;
  unit?: string;
  source?: string;
  growFrames?: number;
  staggerFrames?: number;
  decimals?: number;
}) {
  const frame = useCurrentFrame();
  const scale = useScale();
  const C = useColors();
  const F = useFonts();
  const max = Math.max(...rows.map((r) => r.value));
  return (
    <AbsoluteFill style={{ padding: "10% 8%", fontFamily: F.body, color: C.ink, justifyContent: "center" }}>
      {title && <div style={{ fontFamily: F.display, fontSize: 70 * scale, textTransform: "uppercase", marginBottom: 40 * scale }}>{title}</div>}
      {rows.map((r, i) => {
        const t = interpolate(frame - i * staggerFrames, [0, growFrames], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
        return (
          <div key={r.label} style={{ marginBottom: 26 * scale, opacity: Math.min(1, t * 3) }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 40 * scale, fontWeight: 700, marginBottom: 8 * scale }}>
              <span>{r.label}</span>
              <span style={{ fontVariantNumeric: "tabular-nums" }}>{(r.value * t).toLocaleString("en-US", { maximumFractionDigits: decimals, minimumFractionDigits: decimals })}{unit}</span>
            </div>
            <div style={{ height: 46 * scale, borderRadius: 10 * scale, background: `${C.ink}1F`, overflow: "hidden" }}>
              <div style={{ height: "100%", width: `${(r.value / max) * 100 * t}%`, background: r.highlight ? C.accent : `${C.ink}BF`, borderRadius: 10 * scale }} />
            </div>
          </div>
        );
      })}
      {source && <div style={{ position: "absolute", bottom: "6%", left: "8%", fontSize: 26 * scale, color: C.muted }}>Source: {source}</div>}
    </AbsoluteFill>
  );
}
