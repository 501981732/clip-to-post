#!/usr/bin/env python3
"""
Extract keyframes from a local video file for the clip-to-post skill.

This helper intentionally handles local files only. Web video playback,
logged-in pages, expiring media URLs, and CORS-protected sources should be
handled by the host application with browser or backend media tooling.
"""

import argparse
import base64
import json
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd):
    return subprocess.run(cmd, check=True, text=True, capture_output=True)


def parse_timestamps(value):
    if not value:
        return []
    timestamps = []
    for raw in value.split(","):
        item = raw.strip()
        if not item:
            continue
        try:
            timestamp = float(item)
        except ValueError as exc:
            raise SystemExit(f"Invalid timestamp: {item}") from exc
        if timestamp < 0:
            raise SystemExit(f"Timestamp must be non-negative: {item}")
        timestamps.append(timestamp)
    return sorted(set(timestamps))


def probe_duration(video_path):
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    result = run(cmd)
    try:
        return float(result.stdout.strip())
    except ValueError as exc:
        raise SystemExit("Unable to determine video duration with ffprobe.") from exc


def build_interval_timestamps(duration, every_seconds, max_frames):
    if every_seconds <= 0:
        raise SystemExit("--every-seconds must be greater than 0.")

    timestamps = []
    current = 0.0
    while current <= duration:
        timestamps.append(round(current, 3))
        current += every_seconds
        if max_frames and len(timestamps) >= max_frames:
            break

    if not timestamps and duration > 0:
        timestamps.append(0.0)
    return timestamps


def timestamp_slug(timestamp):
    milliseconds = int(round(timestamp * 1000))
    seconds, ms = divmod(milliseconds, 1000)
    minutes, sec = divmod(seconds, 60)
    hours, minute = divmod(minutes, 60)
    if hours:
        return f"{hours:02d}-{minute:02d}-{sec:02d}_{ms:03d}"
    return f"{minute:02d}-{sec:02d}_{ms:03d}"


def extract_frame(video_path, output_path, timestamp, scale_width, quality):
    filters = []
    if scale_width:
        filters.append(f"scale={scale_width}:-2")

    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-ss",
        f"{timestamp:.3f}",
        "-i",
        str(video_path),
        "-frames:v",
        "1",
        "-q:v",
        str(quality),
    ]
    if filters:
        cmd.extend(["-vf", ",".join(filters)])
    cmd.append(str(output_path))
    run(cmd)


def image_data_url(path):
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def main():
    parser = argparse.ArgumentParser(
        description="Extract local video frames for clip-to-post workflows."
    )
    parser.add_argument("video", help="Path to a local video file.")
    parser.add_argument(
        "--timestamps",
        help="Comma-separated timestamps in seconds, for example: 0,1.5,3.2",
    )
    parser.add_argument(
        "--every-seconds",
        type=float,
        help="Sample one frame every N seconds when --timestamps is omitted.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=12,
        help="Maximum frames for interval sampling. Default: 12.",
    )
    parser.add_argument(
        "--out",
        default="clip-to-post-frames",
        help="Output directory. Default: clip-to-post-frames.",
    )
    parser.add_argument(
        "--scale-width",
        type=int,
        default=1280,
        help="Resize extracted frames to this width. Use 0 to keep source size. Default: 1280.",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=3,
        help="JPEG quality for ffmpeg -q:v, where lower is better. Default: 3.",
    )
    parser.add_argument(
        "--include-base64",
        action="store_true",
        help="Include data:image/jpeg;base64 values in manifest.json.",
    )
    args = parser.parse_args()

    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise SystemExit("ffmpeg and ffprobe are required but were not found on PATH.")

    video_path = Path(args.video).expanduser().resolve()
    if not video_path.exists():
        raise SystemExit(f"Video file not found: {video_path}")
    if not video_path.is_file():
        raise SystemExit(f"Video path is not a file: {video_path}")

    output_dir = Path(args.out).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    duration = probe_duration(video_path)
    timestamps = parse_timestamps(args.timestamps)
    if not timestamps:
        interval = args.every_seconds or max(duration / max(args.max_frames, 1), 1.0)
        timestamps = build_interval_timestamps(duration, interval, args.max_frames)

    scale_width = args.scale_width if args.scale_width and args.scale_width > 0 else None
    frames = []

    for index, timestamp in enumerate(timestamps):
        if timestamp > duration:
            print(
                f"Skipping timestamp {timestamp:.3f}s beyond duration {duration:.3f}s.",
                file=sys.stderr,
            )
            continue

        filename = f"frame_{index + 1:03d}_{timestamp_slug(timestamp)}.jpg"
        output_path = output_dir / filename
        extract_frame(video_path, output_path, timestamp, scale_width, args.quality)

        frame = {
            "tagId": f"frame-{index + 1:03d}",
            "timestamp": timestamp,
            "file": filename,
            "path": str(output_path),
        }
        if args.include_base64:
            frame["data"] = image_data_url(output_path)
        frames.append(frame)

    manifest = {
        "sourceType": "video",
        "source": str(video_path),
        "duration": duration,
        "frameCount": len(frames),
        "frames": frames,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    print(json.dumps({"manifest": str(manifest_path), "frameCount": len(frames)}, indent=2))


if __name__ == "__main__":
    main()
