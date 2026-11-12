import { AbsoluteFill, Easing, Img, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

/** Slow pan/zoom over a still. from/to: zoom and focal point (0-1 of the image). */
export function KenBurns({ src, from = { zoom: 1.05, x: 0.5, y: 0.5 }, to = { zoom: 1.2, x: 0.5, y: 0.45 }, fit = "cover" }: {
  src: string;
  from?: { zoom: number; x: number; y: number };
  to?: { zoom: number; x: number; y: number };
  fit?: "cover" | "contain";
}) {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const t = interpolate(frame, [0, durationInFrames], [0, 1], { extrapolateRight: "clamp", easing: Easing.inOut(Easing.sin) });
  const zoom = from.zoom + (to.zoom - from.zoom) * t;
  const x = from.x + (to.x - from.x) * t;
  const y = from.y + (to.y - from.y) * t;
  return (
    <AbsoluteFill style={{ overflow: "hidden", background: "black" }}>
      <Img src={src} style={{ width: "100%", height: "100%", objectFit: fit, transformOrigin: `${x * 100}% ${y * 100}%`, scale: String(zoom) }} />
    </AbsoluteFill>
  );
}
