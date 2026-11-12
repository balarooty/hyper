import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { SHADOW, useColors, useFonts, useScale } from "./theme";

/** Words land one by one (spring), emphasised words in the accent colour. */
export function KineticText({ text, emphasis = [], staggerFrames = 3, fontSize = 110, color, align = "center", background, uppercase = true }: {
  text: string;
  emphasis?: string[];
  staggerFrames?: number;
  fontSize?: number;
  color?: string;
  align?: "center" | "top" | "bottom";
  background?: string;
  uppercase?: boolean;
}) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = useScale();
  const C = useColors();
  const F = useFonts();
  const emph = new Set(emphasis.map((w) => w.toLowerCase()));
  const words = text.split(/\s+/).filter(Boolean);
  return (
    <AbsoluteFill style={{ background, justifyContent: align === "center" ? "center" : align === "top" ? "flex-start" : "flex-end", alignItems: "center", padding: "12% 8%" }}>
      <div style={{ textAlign: "center", fontFamily: F.display, fontSize: fontSize * scale, lineHeight: 1.05, textTransform: uppercase ? "uppercase" : "none", textShadow: SHADOW }}>
        {words.map((w, i) => {
          const s = spring({ frame: frame - i * staggerFrames, fps, config: { damping: 14, stiffness: 160 } });
          const key = w.toLowerCase().replace(/[^\p{L}\p{N}]/gu, "");
          return (
            <span key={i} style={{ display: "inline-block", marginRight: "0.25em", color: emph.has(key) ? C.accent : color ?? C.ink, opacity: Math.min(1, s), translate: `0 ${(1 - s) * 40 * scale}px`, scale: String(0.8 + 0.2 * s) }}>
              {w}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
}
