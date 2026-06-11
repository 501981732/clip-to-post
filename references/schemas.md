# Schemas and Contracts

Use these contracts as a starting point. Adapt names to the host project.

## Input

```ts
type SourceType = 'video' | 'images';
type TargetPlatform =
  | 'xiaohongshu'
  | 'instagram'
  | 'douyin'
  | 'wechat'
  | 'sop'
  | 'custom';

interface ClipToPostInput {
  sourceType: SourceType;
  videoUrl?: string;
  localVideoFile?: File;
  images?: string[];
  tags?: Tag[];
  targetPlatform: TargetPlatform;
  scene?: 'baby' | 'food' | 'fitness' | 'auto' | 'tutorial' | 'travel' | 'general' | 'custom';
  contextDescription?: string;
  customPrompt?: string;
  style?: 'handdrawn' | 'comic' | 'realistic' | 'clean' | 'custom';
  aspectRatio?: '1:1' | '3:4' | '4:3' | '9:16' | '16:9' | string;
  characterImage?: string;
  watermarkText?: string;
  automationMode?: 'interactive' | 'full_auto';
}

interface Tag {
  id: string;
  timestamp: number;
  label?: string;
  createdAt?: number;
}
```

## Frame and Analysis

```ts
interface FrameData {
  tagId?: string;
  timestamp?: number;
  data: string;
}

interface Step {
  id: string;
  indices: number[];
  title?: string;
  description: string;
}

interface StepAnalysisResult {
  steps: Step[];
  flattenedDescriptions: string[];
}
```

## Artifacts

```ts
interface StoryboardResult {
  baseImage?: string;
  characterIntegratedImage?: string;
  finalImage?: string;
}

interface PanelResult {
  id: string;
  index: number;
  stepId?: string;
  image?: string;
  description: string;
  status: NodeStatus;
  error?: string;
}

interface CaptionOption {
  id: string;
  title: string;
  content: string;
  tone?: string;
  hashtags?: string[];
}

interface CoverResult {
  image?: string;
  title?: string;
  captionId?: string;
}
```

## Pipeline State

```ts
type NodeStatus = 'idle' | 'running' | 'done' | 'error' | 'stale';

type PipelineStatus =
  | 'idle'
  | 'extracting_frames'
  | 'analyzing_steps'
  | 'generating_storyboard'
  | 'integrating_character'
  | 'refining_panels'
  | 'generating_captions'
  | 'selecting_caption'
  | 'generating_cover'
  | 'packaging'
  | 'done'
  | 'failed';

interface NodeRunState {
  status: NodeStatus;
  startedAt?: number;
  finishedAt?: number;
  provider?: string;
  model?: string;
  costEstimate?: number;
  retryCount?: number;
  error?: string;
}

interface ClipToPostPipelineState {
  id: string;
  name: string;
  input: ClipToPostInput;
  frames: FrameData[];
  analysis?: StepAnalysisResult;
  storyboard?: StoryboardResult;
  panels: PanelResult[];
  captions: CaptionOption[];
  selectedCaptionId?: string;
  cover?: CoverResult;
  status: PipelineStatus;
  nodes: Record<string, NodeRunState>;
  batchJobId?: string;
  batchStatus?: 'idle' | 'pending' | 'completed' | 'failed';
  lastUpdated: number;
}
```

## Provider Interface

```ts
interface LLMMessage {
  role: 'system' | 'user' | 'assistant';
  content:
    | string
    | Array<
        | { type: 'text'; text: string }
        | { type: 'image_url'; image_url: { url: string } }
      >;
}

interface LLMConfig {
  responseMimeType?: string;
  thinking?: {
    enabled: boolean;
    level?: 'LOW' | 'HIGH';
    includeThoughts?: boolean;
  };
}

interface LLMResponse {
  text: string;
  images?: string[];
  error?: string;
}

interface BatchStatusResponse {
  status: 'validating' | 'in_progress' | 'completed' | 'failed' | 'expired' | 'cancelled' | 'pending';
  results?: LLMResponse[];
  error?: string;
}

interface LLMProvider {
  generateContent(model: string, messages: LLMMessage[], config?: LLMConfig): Promise<LLMResponse>;
  generateContentBatch?(model: string, batchMessages: LLMMessage[][], config?: LLMConfig): Promise<string>;
  getBatchStatus?(jobId: string): Promise<BatchStatusResponse>;
  testConnection?(): Promise<boolean>;
}
```

## Export Package

```ts
interface ClipToPostExport {
  metadata: {
    projectId: string;
    sourceType: SourceType;
    targetPlatform: TargetPlatform;
    aspectRatio: string;
    generatedAt: string;
    provider?: string;
    models?: string[];
  };
  steps: Step[];
  panels: Array<{
    filename: string;
    title?: string;
    description: string;
  }>;
  selectedCaption?: CaptionOption;
  cover?: {
    filename: string;
    title?: string;
  };
}
```

## Rerun Invalidation

Use downstream invalidation to avoid unnecessary regeneration:

- Edit frames or context: mark analysis, storyboard, panels, captions, cover as stale.
- Edit step descriptions: mark storyboard, panels, captions, cover as stale.
- Edit storyboard prompt/style/aspect ratio: mark storyboard, panels, captions, cover as stale.
- Edit character or watermark: mark character integration, panels, captions, cover as stale.
- Edit one panel: mark captions and cover as stale.
- Edit/select caption: mark cover as stale.
