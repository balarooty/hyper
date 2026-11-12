import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { useColors, useFonts, useSafe, useScale } from "./theme";

function useEnter(delay = 0) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: frame - delay, fps, config: { damping: 200 }, durationInFrames: 12 });
}

/** Name / role / year strip in the lower third. */
export function LowerThird({ title, subtitle }: { title: string; subtitle?: string }) {
  const s = useEnter();
  const scale = useScale();
  const C = useColors();
  const F = useFonts();
  const SAFE = useSafe();
  const { height } = useVideoConfig();
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: `${SAFE.left * 100}%`, top: height * (1 - SAFE.bottom) - 190 * scale, translate: `${(1 - s) * -60}px 0`, opacity: s }}>
        <div style={{ background: C.accent, color: C.bg, fontFamily: F.display, fontSize: 54 * scale, padding: `${8 * scale}px ${20 * scale}px`, textTransform: "uppercase", display: "inline-block" }}>{title}</div>
        {subtitle && <div style={{ background: "rgba(0,0,0,0.7)", color: C.ink, fontFamily: F.body, fontSize: 34 * scale, padding: `${6 * scale}px ${20 * scale}px`, display: "table" }}>{subtitle}</div>}
      </div>
    </AbsoluteFill>
  );
}

/** Small source credit for a fact on screen (every number on screen has one in sources.md). */
export function SourceCard({ text }: { text: string }) {
  const s = useEnter(6);
  const scale = useScale();
  const C = useColors();
  const F = useFonts();
  const SAFE = useSafe();
  const { height } = useVideoConfig();
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: `${SAFE.left * 100}%`, top: height * (1 - SAFE.bottom) - 60 * scale, opacity: s * 0.85, color: C.ink, fontFamily: F.body, fontSize: 26 * scale, background: "rgba(0,0,0,0.5)", padding: `${4 * scale}px ${12 * scale}px`, borderRadius: 6 * scale }}>
        Source: {text}
      </div>
    </AbsoluteFill>
  );
}
