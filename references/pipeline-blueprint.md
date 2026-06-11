# Clip-to-Post Pipeline Blueprint

## Source Pattern

This skill distills the ClipSketch AI pipeline in the current project:

- `utils.ts`: captures selected video timestamps as JPEG base64 frames through `video + canvas`, including CORS proxy handling for direct Bilibili/Instagram media URLs.
- `services/gemini.ts`: orchestrates step analysis, base storyboard generation, character integration, panel refinement, batch refinement status polling, caption generation, and cover generation.
- `services/strategies.ts`: defines platform strategy methods for Xiaohongshu and Instagram.
- `services/llm.ts`: defines a provider abstraction for Google and OpenAI-style calls.
- `services/storage.ts`: persists workflow state in IndexedDB.

Preserve the architectural principle, not the exact project names.

## Core Product Principle

Use a segmented creative pipeline:

```text
video/images
  -> human-selected keyframes or ordered image batch
  -> frame capture/base64 normalization
  -> step analysis
  -> base storyboard
  -> optional character/watermark integration
  -> single-panel refinement
  -> caption generation
  -> human caption selection
  -> cover generation
  -> durable state/export
```

Avoid "one prompt generates everything". Each node should own one decision and produce one inspectable artifact.

## Node Responsibilities

### CaptureFramesNode

Purpose: convert user-selected timestamps or imported images into an ordered `FrameData[]`.

Implementation notes:

- Treat frame extraction as a host capability with three possible implementations:
  - Local file: use `scripts/extract_frames.py`, which wraps `ffmpeg` and writes JPEGs plus `manifest.json`.
  - Browser app: use a real `<video>` element and `canvas.drawImage()` after seeking to selected timestamps.
  - Backend media service: upload or fetch media server-side and return frame URLs/base64 data.
- Do not expect the skill to play arbitrary web videos by itself. Logged-in pages, expiring media URLs, DRM, CORS, and platform-specific player behavior require host application support.
- Sort video tags by timestamp before capture.
- Draw the loaded media into a canvas and export JPEG at about `0.85` quality.
- Store `tagId`, `timestamp`, and `data`.
- For cross-origin direct media, route through a trusted proxy or fetch service before canvas export.
- For image-batch mode, preserve user order and synthesize tags when needed.

Local script example:

```bash
python3 scripts/extract_frames.py ./input.mp4 --timestamps 0,1.5,3 --out ./frames --include-base64
```

Interval sampling example:

```bash
python3 scripts/extract_frames.py ./input.mp4 --every-seconds 2 --max-frames 8 --out ./frames
```

Script output:

```json
{
  "manifest": "/absolute/path/frames/manifest.json",
  "frameCount": 3
}
```

`manifest.json` contains ordered frame metadata and optional data URLs when `--include-base64` is set.

### AnalyzeStepsNode

Purpose: turn raw keyframes into semantic steps.

Input:

- context/background description
- ordered keyframe images
- platform/language strategy

Output:

```json
{
  "steps": [
    {
      "indices": [0, 1],
      "description": "Step description"
    }
  ]
}
```

Validation:

- Every frame index must be covered exactly once unless duplicate coverage is intentionally supported.
- Indices must be in range and should remain ordered.
- Descriptions must be non-empty.
- Store grouped steps and a flattened per-frame description array.

### GenerateStoryboardNode

Purpose: create one base storyboard image from frames and analyzed steps.

Input:

- all keyframe images
- grouped/flattened step descriptions
- user style prompt
- content context
- platform strategy
- aspect ratio

Output:

- `baseArt`: base64 image or hosted image URL

Guidance:

- Ask for a single coherent grid or long-form tutorial board.
- Require panel order, clear spacing, consistent style, and readable labels.
- Preserve the source subject's shape, colors, and key actions.

### IntegrateCharacterNode

Purpose: redraw the storyboard with an avatar, persona, mascot, family member, creator IP, logo-like character, or watermark.

Input:

- `baseArt`
- character/reference image
- watermark text
- aspect ratio

Guidance:

- Preserve layout, steps, and art style.
- Vary the character's interaction in each panel.
- Keep watermark visible but not blocking core content.

### RefinePanelsNode

Purpose: split the big storyboard into clean individual panels.

Input per panel:

- full storyboard/final art
- panel index and total count
- step description
- optional matching original frame
- optional character image
- watermark text
- aspect ratio

Output:

- ordered `PanelResult[]`

Guidance:

- Generate exactly one panel.
- Center the subject with safe margins.
- Preserve the step text when the product requires text in image.
- Use batch jobs when the provider can return a job ID and ordered results.

### GenerateCaptionsNode

Purpose: write platform-native social copy from the final visuals.

Input:

- refined panels if available
- otherwise final storyboard and frames
- original title/content context
- platform strategy
- avatar/character presence

Output:

```json
{
  "captions": [
    {
      "title": "Title",
      "content": "Caption body",
      "tone": "emotional|instructional|punchy"
    }
  ]
}
```

Guidance:

- Generate at least three different angles when the platform benefits from choice.
- Include hashtags and emoji only when appropriate for the platform.
- Avoid unsupported claims not visible in source context.

### SelectCaptionNode

Purpose: bind one caption choice for downstream cover generation and export.

Modes:

- Interactive: ask the human to choose or edit.
- Automatic: rank by platform fit, clarity, specificity, and title-cover compatibility.

### GenerateCoverNode

Purpose: create the publishable cover image.

Input:

- selected caption title and content
- platform cover strategy
- content context
- first two and last two frames, deduplicated
- optional character image
- watermark
- aspect ratio

Guidance:

- Cover style may differ from storyboard style.
- For Xiaohongshu-like feeds, favor realistic/lifestyle/poster aesthetics when that improves click-through.
- Render the title clearly and avoid covering the main subject.

### PersistAndExportNode

Purpose: save intermediate state and package final artifacts.

Persist:

- source metadata
- frames
- steps
- base storyboard
- character-integrated art
- refined panels
- captions
- selected caption
- cover
- workflow step/status
- batch job ID/status
- model/provider metadata
- errors and retry count

Export:

- `cover.*`
- `panel-001.*`, `panel-002.*`, etc.
- `caption.md`
- `metadata.json`
- optional `workflow-state.json`

## Provider Abstraction

Use a provider interface with these capabilities:

```ts
interface LLMProvider {
  generateContent(model: string, messages: LLMMessage[], config?: LLMConfig): Promise<LLMResponse>;
  generateContentBatch?(model: string, batchMessages: LLMMessage[][], config?: LLMConfig): Promise<string>;
  getBatchStatus?(jobId: string): Promise<BatchStatusResponse>;
  testConnection?(): Promise<boolean>;
}
```

Map OpenAI-style messages into the target provider format. For Gemini-like providers, convert image URLs/base64 values into inline image parts. For OpenAI image fallback, account for weaker multi-image edit behavior and degrade gracefully.

## Failure Handling

- Keep node-level status: `idle`, `running`, `done`, `error`.
- Save node errors with provider response snippets where safe.
- Retry idempotent nodes with the same inputs.
- After editing upstream artifacts, mark only downstream artifacts as stale.
- Allow manual override of step analysis and caption selection.
