import { GridStage, HoldPush, LineCaptions, LookProvider, Shots, ShotStub, type ChapterData, type Look } from "../../../lib";
import data from "./chapter.json";

// One Remotion chapter of the film. chapter.json (scripts/timeline.py) gives the frames; never type a frame number
// that belongs to the voice: read it from `chapter.shots`, `chapter.lines` or cueFrame(chapter, "beat" | "dry" | "anchor").
// Replace each ShotStub with a scene (a file per shot in ./shots/ once it grows). No audio here: scripts/mix.py owns sound.
const chapter = data as unknown as ChapterData & { look: Look };

export const Chapter = () => (
  <LookProvider look={chapter.look}>
    <GridStage>
      <Shots chapter={chapter} render={(shot) => <HoldPush><ShotStub shot={shot} /></HoldPush>} />
    </GridStage>
    <LineCaptions lines={chapter.lines} />
  </LookProvider>
);
