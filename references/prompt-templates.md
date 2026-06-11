# Prompt Templates

Adapt these templates to the provider and platform strategy. Keep prompts narrow and output contracts explicit.

## Step Analysis

```text
Role: content planning assistant.

Analyze these ordered keyframes from a tutorial, process, story, review, memory, or social clip.

Context:
{contextDescription}

Task:
Group consecutive frames that represent the same action, stage, or narrative beat.

Requirements:
1. Cover all frames in order.
2. Merge adjacent frames only when they express the same step.
3. Give each step a concise description suitable for downstream storyboard generation.
4. Use {language}.
5. Output strict JSON only.

Output:
{
  "steps": [
    {
      "indices": [0, 1],
      "title": "Short step title",
      "description": "Concrete visual/action description"
    }
  ]
}
```

## Base Storyboard

```text
Role: visual storyboard designer.

Create one complete storyboard image for {targetPlatform}.

Source context:
{contextDescription}

User style request:
{customPrompt}

Step plan:
{stepDescriptions}

Requirements:
1. Convert the provided reference frames into a coherent {style} storyboard.
2. Preserve the source subject, key actions, colors, and material details.
3. Give every step its own panel.
4. Keep panel order obvious: {readingOrder}.
5. Use concise, readable step labels in {language}.
6. Avoid unrelated text.
7. Use clean spacing and a consistent visual system.
8. Optimize the full image for aspect ratio {aspectRatio}.

Return one image only.
```

## Character Integration

```text
Role: visual editor.

Inputs:
Image 1: completed storyboard.
Image 2: character/persona/avatar/reference image.

Task:
Redraw the storyboard with the character naturally integrated into the scene.

Requirements:
1. Preserve the original layout, step sequence, labels, and visual style.
2. Do not change the tutorial/story content.
3. Make the character interact differently in each step.
4. Keep the character recognizable from the reference image.
5. Keep the output aspect ratio at {aspectRatio}.
{watermarkInstruction}

Return one image only.
```

Watermark instruction:

```text
Add the watermark text "{watermarkText}" near the subject or in a subtle corner. Keep it legible without covering important content.
```

## Panel Refinement

```text
Role: panel refinement artist.

Inputs:
Image 1: full storyboard/final art.
{optionalOriginalFrameLine}
{optionalCharacterLine}

Task:
Extract and refine panel {panelIndexOneBased} of {totalPanels}.

Step description:
{stepDescription}

Context:
{contextDescription}

Requirements:
1. Output only this one panel.
2. Use aspect ratio {aspectRatio}.
3. Center the main subject with safe margins.
4. Preserve relevant step text.
5. Preserve visual details from the storyboard and source frame.
6. Improve clarity, line quality, legibility, and composition.
{watermarkInstruction}

Return one image only.
```

Optional lines:

```text
Image 2: original reference frame for this step.
Image 3: character reference that must remain present and recognizable.
```

## Caption Generation

```text
Role: {targetPlatform} content strategist.

Create {count} caption options based on the provided final visuals.

Original title:
{videoTitle}

Context:
{contextDescription}

Platform rules:
{platformCaptionRules}

Character note:
{avatarPresenceInstruction}

Requirements:
1. Match the visible content and do not invent unsupported details.
2. Provide distinct tones, such as emotional, instructional, and punchy.
3. Include hashtags only when native to the platform.
4. Output strict JSON only.

Output:
{
  "captions": [
    {
      "id": "caption-1",
      "title": "Short title",
      "content": "Full post caption",
      "tone": "emotional",
      "hashtags": ["#example"]
    }
  ]
}
```

## Cover Generation

```text
Role: social-media cover art director.

Create a high-quality cover image for {targetPlatform}.

Use these inputs:
- Story/background: {contextDescription}
- Selected title: {selectedCaptionTitle}
- Selected caption mood: {selectedCaptionExcerpt}
- Reference frames: first two and last two frames from the source, deduplicated
{optionalCharacterCoverLine}

Requirements:
1. Optimize for aspect ratio {aspectRatio}.
2. Summarize the video's transformation, result, or strongest visual hook.
3. Render the selected title clearly in the image.
4. Keep title text away from key subject details.
5. Apply the platform's cover style: {platformCoverStyle}
{watermarkInstruction}

Return one image only.
```

## Platform Strategy Seeds

### Xiaohongshu

- Step language: Simplified Chinese.
- Storyboard style: cute hand-drawn tutorial, clear strokes, white background, concise Chinese labels.
- Caption angles: emotional/story, practical tutorial, short recommendation.
- Caption elements: emoji and Chinese hashtags.
- Cover style: realistic or lifestyle poster, warm lighting, "种草" appeal, clear Chinese title.

### Instagram

- Step language: native English.
- Storyboard style: aesthetic doodle or clean illustrated guide.
- Caption angles: emotional, instructional, punchy.
- Caption elements: concise English hashtags and emoji.
- Cover style: cinematic, editorial, Reel-ready typography.

### Internal SOP

- Step language: match team language.
- Storyboard style: clean procedural diagram or annotated screenshot style.
- Caption output: concise summary, prerequisites, step list, warnings.
- Cover output: optional; prefer a title card or process overview.
