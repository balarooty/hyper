import { evolvePath } from "@remotion/paths";
import type { ReactNode } from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { useColors, useFonts, useScale } from "./theme";

/** The schematic stage of a code-built explainer: the look's background with a faint coordinate grid. */
export function GridStage({ cell = 60, children }: { cell?: number; children?: ReactNode }) {
  const { width, height } = useVideoConfig();
  const scale = useScale();
  const C = useColors();
  const step = cell * scale;
  const xs = Array.from({ length: Math.ceil(width / step) + 1 }, (_, i) => i * step);
  const ys = Array.from({ length: Math.ceil(height / step) + 1 }, (_, i) => i * step);
  return (
    <AbsoluteFill style={{ background: C.bg }}>
      <svg width={width} height={height} style={{ position: "absolute" }}>
        {xs.map((x, i) => <line key={`x${i}`} x1={x} y1={0} x2={x} y2={height} stroke={C.muted} strokeOpacity={i % 4 ? 0.07 : 0.14} strokeWidth={1} />)}
        {ys.map((y, i) => <line key={`y${i}`} x1={0} y1={y} x2={width} y2={y} stroke={C.muted} strokeOpacity={i % 4 ? 0.07 : 0.14} strokeWidth={1} />)}
      </svg>
      {children}
    </AbsoluteFill>
  );
}

/** Every hold creeps: wraps a shot in a slow push-in (rate per frame) so no frame is ever frozen. */
export function HoldPush({ rate = 0.0006, origin = "50% 50%", children }: { rate?: number; origin?: string; children: ReactNode }) {
  const frame = useCurrentFrame();
  return <AbsoluteFill style={{ scale: String(1 + rate * frame), transformOrigin: origin }}>{children}</AbsoluteFill>;
}

/** An SVG path that draws itself from `at` over `dur` frames. Use inside an <svg>. */
export function DrawPath({ d, at = 0, dur = 20, color, width = 4, fill = "none", dash }: { d: string; at?: number; dur?: number; color?: string; width?: number; fill?: string; dash?: string }) {
  const frame = useCurrentFrame();
  const scale = useScale();
  const C = useColors();
  const t = interpolate(frame - at, [0, dur], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const eased = 1 - (1 - t) ** 3;
  const { strokeDasharray, strokeDashoffset } = evolvePath(eased, d);
  return <path d={d} fill={fill} fillOpacity={fill === "none" ? 0 : eased} stroke={color ?? C.accent} strokeWidth={width * scale} strokeLinecap="round" strokeLinejoin="round"
    strokeDasharray={eased >= 1 && dash ? dash : strokeDasharray} strokeDashoffset={eased >= 1 && dash ? 0 : strokeDashoffset} opacity={t > 0 ? 1 : 0} />;
}

/** A part that springs in (critically damped: no bounce on a schematic). Use for components of a cutaway. */
export function PopIn({ at = 0, from = 0.85, children, style }: { at?: number; from?: number; children: ReactNode; style?: React.CSSProperties }) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - at, fps, config: { damping: 20, stiffness: 180 } });
  return <div style={{ position: "absolute", opacity: Math.min(1, s * 1.5), scale: String(from + (1 - from) * s), ...style }}>{children}</div>;
}

/** A label with a leader line to the feature it names: (x, y) is the feature, (lx, ly) the label, in pixels at 1080 scale. */
export function Callout({ x, y, lx, ly, text, at = 0, color }: { x: number; y: number; lx: number; ly: number; text: string; at?: number; color?: string }) {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const scale = useScale();
  const C = useColors();
  const F = useFonts();
  const t = interpolate(frame - at, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const col = color ?? C.accent2;
  const [X, Y, LX, LY] = [x, y, lx, ly].map((v) => v * scale);
  return (
    <AbsoluteFill style={{ opacity: t > 0 ? 1 : 0 }}>
      <svg width={width} height={height} style={{ position: "absolute" }}>
        <circle cx={X} cy={Y} r={7 * scale * t} fill={col} />
        <line x1={X} y1={Y} x2={X + (LX - X) * t} y2={Y + (LY - Y) * t} stroke={col} strokeWidth={2.5 * scale} />
      </svg>
      <div style={{ position: "absolute", left: LX, top: LY, translate: `${LX < X ? "-100%" : "0"} -50%`, padding: `${4 * scale}px ${12 * scale}px`, fontFamily: F.mono, fontSize: 30 * scale, color: col, opacity: interpolate(t, [0.6, 1], [0, 1], { extrapolateLeft: "clamp" }), whiteSpace: "nowrap" }}>{text}</div>
    </AbsoluteFill>
  );
}
