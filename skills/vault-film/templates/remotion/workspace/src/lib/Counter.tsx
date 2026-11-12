import { Easing, interpolate, useCurrentFrame } from "remotion";
import { SHADOW, useColors, useFonts, useScale } from "./theme";

/** A number counting up to `to` over `durationInFrames`, formatted with separators. */
export function Counter({ to, from = 0, durationInFrames = 30, decimals = 0, prefix = "", suffix = "", fontSize = 160, color }: {
  to: number;
  from?: number;
  durationInFrames?: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  fontSize?: number;
  color?: string;
}) {
  const frame = useCurrentFrame();
  const scale = useScale();
  const C = useColors();
  const F = useFonts();
  const value = interpolate(frame, [0, durationInFrames], [from, to], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const text = value.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
  return <span style={{ fontFamily: F.display, fontSize: fontSize * scale, color: color ?? C.accent, textShadow: SHADOW, fontVariantNumeric: "tabular-nums" }}>{prefix}{text}{suffix}</span>;
}
