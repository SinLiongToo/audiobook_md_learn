---
name: audiobook-to-markdown
description: >-
  Transcribe and format audiobooks (.mp3, .m4a, .m4b, .wav) into structured,
  time-anchored Markdown study notes and transcripts using faster-whisper.
  Features low-memory streaming audio chunking (safely handles 5 to 30+ hour
  audiobooks without RAM overflow), smart path resolution (auto-extension and
  library keyword fuzzy matching), and Google Colab GPU batch processing workflows.
---

# Audiobook to Markdown Transcriber

## Overview
This skill converts long audiobook audio files into structured, readable, and searchable Markdown (`.md`) files. It solves the critical memory allocation bottleneck inherent in raw Whisper models by implementing a streaming PyAV audio chunker (keeping memory under 150 MB regardless of audio length) and generates clean, human-friendly notes with chapter navigation anchors and timestamps.

## Dependencies
Ensure the following Python packages are installed:
```bash
pip install faster-whisper av tqdm numpy
```

## Quick Start

### 1. Transcribe Single Audiobook by Keyword or Path
```bash
python scripts/transcribe.py --input "Die With Zero" --model base.en
```
*Note: The script automatically searches the local audiobook directory and resolves filenames, even if `.mp3` is omitted.*

### 2. Transcribe Entire Folder of Audiobooks
```bash
python scripts/transcribe.py --input "C:/path/to/audiobooks" --output "./output" --model base.en
```

### 3. Prime with Title/Author Prompt for Enhanced Accuracy
```bash
python scripts/transcribe.py --input "Discipline Equals Freedom" --model base.en --prompt "Discipline Equals Freedom by Jocko Willink"
```

## Utility Scripts

The companion script `scripts/transcribe.py` provides the complete streaming transcription pipeline:

### Arguments:
- `--input`, `-i`: Path to an audio file, folder of audio files, or book title keyword.
- `--output`, `-o`: Directory to save the generated `.md` files (default: `./output`).
- `--model`, `-m`: Model name (`tiny.en`, `base.en`, `small.en`, `medium.en`). Default: `base.en`.
- `--device`, `-d`: Compute device (`cpu` or `cuda`). Default: `cpu`.
- `--compute_type`, `-c`: Quantization precision (`int8` for CPU, `float16` for GPU). Default: `int8`.
- `--interval`: Section interval in minutes for grouping readable paragraphs (default: `5`).
- `--prompt`, `-p`: Initial prompt providing book title, author, or proper nouns to prevent intro hallucinations.
- `--max_duration`: Maximum seconds to transcribe (useful for quick 60-second test runs).

## Workflow

### Step 1: Assess Audio Volume and Device
- Check whether the task is a single book (run locally with `base.en` or `small.en`) or a huge batch of 50+ books.
- For massive batches (>50 hours of audio), recommend executing on **Google Colab (free T4 GPU)** using `colab_transcribe.ipynb` to achieve 10x~20x speedup and protect local CPU thermals.

### Step 2: Resolve Audio File
- Accept either full paths, paths without extensions, or bare book titles.
- The path resolver will auto-append common audio extensions (`.mp3`, `.m4a`, `.m4b`, `.wav`) and fuzzy-match against the user's audiobook library.

### Step 3: Stream and Transcribe in 15-Minute Chunks
- Never decode an entire multi-hour audio file into a single NumPy array at once!
- Stream through PyAV in 15-minute (`900s`) chunks to ensure memory stays strictly under 150 MB.
- Offset each chunk's timestamps by `chunk_offset` so the final output maintains continuous global timestamps.

### Step 4: Output Formatted Markdown
Each output Markdown file contains:
1. **YAML Frontmatter**: Title, original file, audio duration, model used, timestamp.
2. **Table of Contents (ToC)**: Anchor links for each 5-minute section (`[00:00:00 - 00:05:00](#sec-000000)`).
3. **Structured Transcript Sections**: Grouped paragraphs with clean prose and subtle timestamp headers.

### Step 5: Render Standalone HTML eBooks & Bookshelf
- Execute `python build_ebooks.py` to compile all `.md` transcripts in `audiobook_md/` into standalone, single-file HTML eBook readers in `ebooks/`.
- Features include:
  - Sticky / collapsible Table of Contents with section search & active scroll-spy
  - Light ☀️ / Sepia 📜 / Dark 🌙 reading themes with local storage persistence
  - Dynamic font sizing (A- / A+) and serif/sans-serif font switcher
  - Top reading progress bar and floating quick-jump buttons
  - A master digital bookshelf index (`ebooks/index.html`) cataloging all books with real-time title search


## Common Mistakes & Solutions

| Pitfall | Root Cause | Solution |
| :--- | :--- | :--- |
| **`ArrayMemoryError: Unable to allocate 5.5 GiB`** | Faster-Whisper/STFT tries to compute spectrogram on 5+ hour audios at once. | **Always use 15-minute streaming chunk generator** via PyAV. |
| **Missing `.mp3` extension in CLI** | Users copy folder display names without file extensions. | Path auto-resolver checks `.mp3`, `.m4a`, `.m4b` automatically. |
| **First 5 seconds mishearing** | Loud intro music or deep voice before speech starts. | Pass `--prompt "<Book Title> by <Author>"` to prime the decoder. |
| **Local CPU overheating on 80+ books** | Laptops throttling under 100+ hours of continuous CPU load. | Use `colab_transcribe.ipynb` on Google Colab with free T4 GPU. |
