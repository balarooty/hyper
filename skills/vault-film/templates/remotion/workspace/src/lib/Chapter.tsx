import type { ReactNode } from "react";
import { AbsoluteFill, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { KenBurns } from "./KenBurns";
import { useColors, useFonts, useLook, useSafe, useScale } from "./theme";

/** build/<chapter>/chapter.json, written by scripts/timeline.py. Frames and seconds are chapter-local. */
export type Shot = { id: string; start_f: number; end_f: number; start: number; dur: number; file?: string; move?: string; overlay?: string; era?: string; draw?: string; words?: string; art?: boolean };
export type Line = { id: string; text: string; start_f: number; end_f: number; start: number; end: number; speaker?: string };
export type Cue = { type: string; frame: number; t: number; action?: string; line?: string };
export type ChapterData = { id: string; title: string; frames: number; fps: number; width: number; height: number; shots: Shot[]; lines: Line[]; cues: Cue[] };

/** One <Sequence> per shot, on the frames the voice set. `render` returns that shot's scene. */
export function Shots({ chapter, render }: { chapter: ChapterData; render: (shot: Shot, index: number) => ReactNode }) {
  return <>{chapter.shots.map((s, i) => <Sequence key={s.id} from={s.start_f} durationInFrames={s.end_f - s.start_f} name={`shot ${s.id}`}>{render(s, i)}</Sequence>)}</>;
}

/** The chapter-local frame of a delivery cue (a beat action, the dry turn, the anchor): land the action on it. */
export function cueFrame(chapter: ChapterData, type: string, nth = 0): number | undefined {
  return chapter.cues.filter((c) => c.type === type)[nth]?.frame;
}

/** Stand-in for a shot nobody has drawn yet: shows its id, plan and frames so timing can be checked in stills. */
export function ShotStub({ shot }: { shot: Shot }) {
  const scale = useScale();
  const C = useColors();
  const F = useFonts();
  if (shot.art && shot.file) return <KenBurns src={staticFile(`art/${shot.file}`)} />;
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: "10%", fontFamily: F.mono, color: C.muted }}>
      <div style={{ fontSize: 34 * scale, color: C.alert }}>PLACEHOLDER · shot {shot.id} · {shot.end_f - shot.start_f} f</div>
      <div style={{ fontSize: 44 * scale, color: C.ink, textAlign: "center", marginTop: 24 * scale, fontFamily: F.body }}>{shot.draw || shot.overlay || shot.words}</div>
      <div style={{ fontSize: 28 * scale, marginTop: 20 * scale }}>{shot.move}</div>
    </AbsoluteFill>
  );
}

/** Sentence captions from the voice lines, in the look's caption style; long lines are split by their word share. */
export function LineCaptions({ lines, maxWords = 8 }: { lines: Line[]; maxWords?: number }) {
  const frame = useCurrentFrame();
  const { height } = useVideoConfig();
  const scale = useScale();
  const C = useColors();
  const F = useFonts();
  const SAFE = useSafe();
  const cap = useLook().caption ?? {};
  if ((cap.style ?? "none") === "none") return null;
  const pages = lines.flatMap((l) => {
    const words = l.text.split(/\s+/).filter(Boolean);
    const n = Math.ceil(words.length / maxWords), per = Math.ceil(words.length / n), span = l.end_f - l.start_f;
    return Array.from({ length: n }, (_, k) => {
      const a = k * per, b = Math.min(words.length, a + per);
      return { text: words.slice(a, b).join(" "), from: l.start_f + Math.round((a / words.length) * span), to: l.start_f + Math.round((b / words.length) * span) };
    });
  });
  const page = pages.findLast((p) => frame >= p.from && frame < p.to + 6);
  if (!page) return null;
  const top = cap.position === "upper" ? height * (SAFE.top + 0.02) : cap.position === "center" ? height * 0.45 : height * (1 - SAFE.bottom) - 90 * scale;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div style={{ position: "absolute", top, left: `${SAFE.left * 100}%`, right: `${SAFE.right * 100}%`, textAlign: "center", fontFamily: F.body, fontWeight: 700, fontSize: (cap.size ?? 46) * scale, lineHeight: 1.2, color: C.ink, textTransform: cap.uppercase ? "uppercase" : "none", WebkitTextStroke: `${5 * scale}px ${C.bg}`, paintOrder: "stroke", opacity: interpolate(frame - page.from, [0, 4], [0, 1], { extrapolateRight: "clamp" }) }}>
        {page.text}
      </div>
    </AbsoluteFill>
  );
}
