import { createContext, useContext, type ReactNode } from "react";
import { cancelRender, continueRender, delayRender, staticFile, useVideoConfig } from "remotion";

/** look.json: the one palette, font set and caption style every engine of a film draws from. */
export type FontRole = { family: string; weights: number[] };
export type Look = {
  palette: { bg: string; ink: string; accent: string; accent2: string; alert: string; muted: string; [k: string]: string };
  fonts: { display: FontRole; body: FontRole; mono?: FontRole };
  caption?: { style?: "none" | "sentence"; size?: number; position?: "lower" | "center" | "upper"; uppercase?: boolean };
  grain?: number;
};

export const DEFAULT_LOOK: Look = {
  palette: { bg: "#0B0F17", ink: "#E6EDF3", accent: "#38BDF8", accent2: "#F59E0B", alert: "#EF4444", muted: "#8B98A9" },
  fonts: { display: { family: "Anton", weights: [400] }, body: { family: "Inter", weights: [400, 700] } },
};

const Ctx = createContext<Look>(DEFAULT_LOOK);
export const useLook = () => useContext(Ctx);
export const useColors = () => useContext(Ctx).palette;
export function useFonts() {
  const f = useContext(Ctx).fonts;
  return { display: `"${f.display.family}", sans-serif`, body: `"${f.body.family}", sans-serif`, mono: `"${(f.mono ?? f.body).family}", monospace` };
}

export const fontFile = (family: string, weight: number) => `fonts/${family.toLowerCase().replace(/\s+/g, "-")}-${weight}.woff2`;

const loaded = new Set<string>();
/** Loads the look's fonts from <public>/fonts (copied there by new_film.py); the render waits for them. */
function loadFonts(look: Look) {
  if (typeof document === "undefined") return;
  for (const role of [look.fonts.display, look.fonts.body, look.fonts.mono]) {
    if (!role) continue;
    for (const w of role.weights) {
      const key = `${role.family}/${w}`;
      if (loaded.has(key)) continue;
      loaded.add(key);
      const handle = delayRender(`font ${key}`);
      new FontFace(role.family, `url(${staticFile(fontFile(role.family, w))})`, { weight: String(w) })
        .load()
        .then((f) => { document.fonts.add(f); continueRender(handle); })
        .catch((e) => cancelRender(new Error(`font ${key} did not load from public/${fontFile(role.family, w)}: ${e}`)));
    }
  }
}

export function LookProvider({ look, children }: { look?: Partial<Look>; children: ReactNode }) {
  const merged = { ...DEFAULT_LOOK, ...look, palette: { ...DEFAULT_LOOK.palette, ...look?.palette }, fonts: { ...DEFAULT_LOOK.fonts, ...look?.fonts } } as Look;
  loadFonts(merged);
  return <Ctx.Provider value={merged}>{children}</Ctx.Provider>;
}

/** 1 at 1080 px on the short side; size everything by it so 16:9 and 9:16 share code. */
export function useScale(): number {
  const { width, height } = useVideoConfig();
  return Math.min(width, height) / 1080;
}

/** Fractions of the frame to keep text out of: Shorts UI zones in 9:16, title-safe margins in 16:9. */
export function useSafe() {
  const { width, height } = useVideoConfig();
  return height > width ? { top: 0.14, bottom: 0.25, right: 0.12, left: 0.05 } : { top: 0.08, bottom: 0.1, right: 0.08, left: 0.08 };
}

export const SHADOW = "0 6px 24px rgba(0,0,0,0.45)";
