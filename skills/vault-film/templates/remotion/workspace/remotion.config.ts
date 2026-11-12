import { Config } from "@remotion/cli/config";

// vault-film chapters are rendered silent (scripts/mix.py owns the sound) and joined by scripts/assemble.py.
Config.setVideoImageFormat("jpeg");
Config.setJpegQuality(95);
Config.setOverwriteOutput(true);
Config.setColorSpace("bt709");
Config.setMuted(true);
// chrome-headless-shell aborts on recent macOS (ICU data); the full Chrome for Testing build renders fine.
Config.setChromeMode("chrome-for-testing");
