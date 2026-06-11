---
name: clip-to-post
description: This skill should be used when turning video clips, keyframes, screenshots, or image batches into a structured social-media content package with storyboard panels, platform captions, cover art, and exportable workflow state.
---

# Clip-to-Post

## Overview

Transform raw visual material into a reusable multimodal content workflow: extract or accept keyframes, analyze steps, plan a storyboard, optionally integrate a character or watermark, refine panels, write captions, create a cover, and package the result.

Prefer this skill for productizing a "video/images to post" pipeline, designing an AI workflow demo, or implementing a human-in-the-loop content factory. Keep the core rule: understand first, generate second; generate the whole storyboard first, refine panels later; write copy from final visuals, then make the cover.

## Workflow

1. Normalize input material.
   - Accept a video URL/file, a set of screenshots, or an ordered image batch.
   - For local video files, run `scripts/extract_frames.py` when ffmpeg is available and deterministic local frame extraction is needed.
   - For web video playback, logged-in pages, expiring URLs, or CORS-protected media, require the host application to provide browser/backend frame extraction. This skill describes the contract but does not bypass website access controls.
   - Convert selected video timestamps into image frames and optional base64 data URLs with a browser canvas, backend media tool, or bundled local ffmpeg helper.
   - Preserve `tagId`, `timestamp`, original order, source metadata, and target aspect ratio.

2. Analyze steps before generating art.
   - Send keyframes plus context to a multimodal text model.
   - Group consecutive frames that describe the same action or stage.
   - Require strict JSON and validate that every input frame is covered in order.
   - Store both grouped steps and per-frame flattened step descriptions.

3. Generate the base storyboard.
   - Send all keyframes, grouped step descriptions, context, target platform, user style prompt, and aspect ratio to an image model.
   - Ask for a single coherent storyboard grid with clear panel order, concise step labels, and consistent style.
   - Treat the base storyboard as an intermediate draft, not the final export.

4. Integrate optional character assets.
   - When a persona, avatar, mascot, brand character, or watermark is provided, redraw the storyboard while preserving layout, steps, and visual style.
   - Require the character interaction to vary across steps.
   - Skip this node when no character/brand layer exists.

5. Refine individual panels.
   - For each step, provide the full storyboard, the step description, the matching original reference frame when available, and any character image.
   - Generate one clean panel at the requested aspect ratio.
   - Prefer batch generation when the provider supports asynchronous batch jobs; otherwise run panels sequentially with retry.

6. Generate platform captions.
   - Prefer refined panels as visual context.
   - Fall back to the final storyboard plus original keyframes when refined panels are unavailable.
   - Generate multiple caption options with title, content, tone, and hashtags.
   - Require strict JSON.

7. Select or confirm the caption.
   - Ask for human selection when operating interactively.
   - Choose the strongest caption automatically only when the caller requests full automation.
   - Persist the selected caption ID and text because cover generation depends on it.

8. Generate cover art.
   - Use the selected caption title, context, platform strategy, optional character, watermark, and a small reference set from the first two and last two frames.
   - Do not blindly reuse the storyboard style; choose the cover style that best fits the target platform's click behavior.

9. Save and export.
   - Persist all intermediate artifacts: frames, steps, storyboard, final art, panels, captions, cover, selected caption, batch job ID, node status, errors, and model/provider metadata.
   - Export an asset package containing panel images, cover image, caption text, metadata JSON, and any workflow manifest required by the host platform.

## Decision Rules

- Use keyframes instead of sending complete videos to models unless the available model/tool explicitly supports long-video understanding at acceptable cost.
- Do not claim this skill can play arbitrary web videos by itself. Use `scripts/extract_frames.py` only for local video files; use a host-provided browser or backend extractor for remote/video-page sources.
- Keep every AI node narrow: one node for analysis, one for base storyboard, one for character integration, one for panel refinement, one for captions, one for cover.
- Preserve human edits to steps, prompts, captions, and selected frames across reruns.
- Rerun only the invalidated downstream nodes after a user edits an upstream artifact.
- Favor provider-agnostic message contracts, then map those messages to Gemini, OpenAI, or an internal model gateway.
- Treat JSON parsing as an explicit reliability boundary; extract fenced JSON, validate structure, and surface parse failures as node errors.

## Platform Strategy

Model platform-specific behavior as strategy objects. Include these methods or their equivalent:

- `getStepAnalysisInstruction()`
- `getBaseImagePrompt(context, customPrompt, providerTraits, aspectRatio)`
- `getCaptionPrompt(title, context, avatarPresent)`
- `getCoverPrompt(context, selectedCaption, watermark, avatarPresent, providerTraits, aspectRatio)`

Use strategies for language, visual style, caption tone, hashtag conventions, typography instructions, and cover aesthetics. Add new strategies for domains such as baby memory, food recipe, fitness movement, car review, product tutorial, travel log, internal SOP, or enterprise demo.

## Human-in-the-Loop UX

Expose the pipeline as editable nodes rather than one monolithic generation button.

- Show input and output for every node.
- Allow editing step descriptions before storyboard generation.
- Allow regenerating a single panel without rerunning the full workflow.
- Allow locking approved panels, captions, and cover art.
- Show provider/model, cost, status, and error per node when available.

## Local Frame Extraction Helper

Use `scripts/extract_frames.py` when the input is a local video file and `ffmpeg`/`ffprobe` are installed:

```bash
python3 scripts/extract_frames.py ./demo.mp4 --timestamps 0,2.5,5 --out ./frames --include-base64
```

The script writes JPEG frames and `manifest.json`. Load `manifest.json` as `FrameData[]` input for the rest of the workflow. For web videos, continue to use a host-provided browser/canvas or backend extraction tool.

## References

- Load `references/pipeline-blueprint.md` for the ClipSketch-derived architecture and node responsibilities.
- Load `references/prompt-templates.md` when writing or adapting prompts for a concrete provider or platform.
- Load `references/schemas.md` when implementing state, tool contracts, or export payloads.
