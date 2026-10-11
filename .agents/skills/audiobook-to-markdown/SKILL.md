---
name: audiobook-to-markdown
description: >-
  Transcribe, format, and publish audiobooks (.mp3, .m4a, .m4b, .wav) into structured
  Markdown study notes and standalone interactive HTML eBook web readers with
  in-page search, mobile-responsive multi-color highlighting, global corpus search,
  and interactive knowledge connection graphs (D3.js force-directed). Features
  low-memory PyAV streaming chunking and GitHub Pages publishing.
---

# Audiobook to Markdown & Interactive Digital Library System

## Overview
This skill provides an end-to-end pipeline to:
1. **Transcribe** long audiobooks (5 to 30+ hours) into clean, time-anchored Markdown study transcripts without RAM overflow (streaming PyAV chunking kept under 150 MB).
2. **Compile** Markdown files into standalone, responsive, single-file HTML eBook web readers deployed to GitHub Pages (`docs/`).
3. **Equip readers with modern learning features**:
   - 🔍 **In-page full-text content search** (`Ctrl+F` modal / floating button) with instant hit counting, jump navigation, and yellow hit highlighting.
   - 🖍️ **Mobile-optimized multi-color highlighting** (Yellow 🟡, Green 🟢, Blue 🔵, Pink 🔴) with automatic text selection popups, paragraph position tracking, LocalStorage persistence, a notes drawer, and finger-friendly `🗑️ 刪除` touch targets with dual touch (`touchend` + `click`) event bindings.
   - 🕸️ **Interactive Knowledge Connection Graph (知識關聯圖譜)** powered by D3.js force simulation, supporting canvas panning/zooming, category filtering, responsive mobile pinch/touch handling, and viewport auto-fit.
   - 🔎 **Global full-text search index** (`search_index.json`) across the entire multi-book library with snippet previews and category tags.

---

## Dependencies
Ensure the required Python environment is ready:
```bash
pip install faster-whisper av tqdm numpy
```

---

## CLI & Pipeline Workflows

### 1. Transcribe Audiobooks to Markdown
Convert audio files to structured Markdown in `audiobook_md/`:

```bash
# Transcribe single audiobook by title keyword or path
python scripts/transcribe.py --input "Atomic Habits" --model base.en

# Transcribe entire audiobook folder
python scripts/transcribe.py --input "C:/path/to/audiobooks" --output "./audiobook_md" --model base.en

# Prime with title and author prompt for maximum accuracy
python scripts/transcribe.py --input "Discipline Equals Freedom" --model base.en --prompt "Discipline Equals Freedom by Jocko Willink"
```

#### Key Transcriber Arguments:
- `--input`, `-i`: Path to audio file, directory of audiobooks, or keyword (auto-resolved).
- `--output`, `-o`: Directory to save markdown files (default: `./audiobook_md` or `./output`).
- `--model`, `-m`: Whisper model size (`tiny.en`, `base.en`, `small.en`, `medium.en`). Default: `base.en`.
- `--device`, `-d`: `cpu` or `cuda`. Default: `cpu`.
- `--compute_type`, `-c`: `int8` (CPU) or `float16` (GPU).
- `--interval`: Section interval in minutes for grouping paragraphs (default: `5`).
- `--prompt`, `-p`: Initial prompt for proper nouns and book title.

---

### 2. Build Interactive HTML eBooks & Digital Library
Compile all `.md` files into standalone readers and generate the master portal with search index and knowledge graph:

```bash
python build_ebooks.py
```

This generates:
- `docs/*.html`: Individual standalone eBook readers with built-in in-page search and highlighting.
- `docs/index.html`: The 3-tab digital library portal:
  1. 📚 **數位書架 (Bookshelf)**: Category cards, cover art, reading time, and real-time title search.
  2. 🕸️ **知識關聯圖譜 (Connection Graph)**: D3.js force-directed network showing thematic relations across books.
  3. 🔍 **全庫全文檢索 (Global Search)**: Client-side full-text search across all books with snippet highlighting.
- `docs/search_index.json`: Minified JSON search index for fast instant search.

---

### 3. Deploy to GitHub Pages
To publish or update the live library on GitHub Pages:
```bash
git add build_ebooks.py docs/*.html docs/search_index.json docs/index.html
git commit -m "feat: update audiobooks and library features"
git push origin main
```

---

## Architectural Guidelines & Standards

### A. Markdown Transcript Specifications
Each transcript `.md` file must contain:
1. **YAML Frontmatter**: Title, source audio filename, audio duration, Whisper model, creation date.
2. **Table of Contents (ToC)**: Anchor links for 5-minute sections (`[00:00:00 - 00:05:00](#sec-000000)`).
3. **Structured Prose**: Punctuation-normalized sentences grouped into coherent reading paragraphs under time headings.

### B. In-Page Reader Features
Each generated HTML eBook reader must include:
- **Sticky / Collapsible Table of Contents** with active scroll-spy.
- **Reading Themes**: Light ☀️, Sepia 📜, Dark 🌙 (saved to `localStorage`).
- **Typography Controls**: Font size increment/decrement (A- / A+) and serif/sans-serif font switch.
- **Reading Progress Bar**: Dynamic top indicator tracking viewport scroll percentage.
- **In-Page Full-Text Search**:
  - Modal triggered via Floating Button or `Ctrl+F` / `Cmd+F`.
  - Incremental hit counter (`[1/14]`) with Up/Down jump navigation and yellow `<mark class="search-hl">` tags.
- **User Highlighting System (Mobile & Desktop)**:
  - 4 highlighter colors: 🟡 Yellow (`#fef08a`), 🟢 Green (`#bbf7d0`), 🔵 Blue (`#bfdbfe`), 🔴 Pink (`#fbcfe8`).
  - Selection floating popup clamped within viewport bounds to prevent off-screen clipping on mobile screens.
  - Highlights saved in `localStorage` under `audiobook_hl_<doc_title>` with paragraph index and character offsets.
  - Notes Drawer displaying all highlights with jump links, color badges, and timestamps.

### C. Mobile Touch & Interaction Best Practices (Crucial for Phones)
When writing or updating JavaScript/CSS for readers and graphs:
1. **Touch Targets**:
   - All interactive touch buttons (e.g., delete buttons, color selectors, drawer toggles) MUST have minimum touch dimensions of $\ge 36\text{px}$ with generous padding (`padding: 6px 12px` or similar).
   - Use clear text and emoji labels like `🗑️ 刪除` rather than tiny single-character `✕` links to avoid misclicking neighboring cards.
2. **Dual Event Handlers (`touchend` + `click`)**:
   - Mobile browsers (iOS Safari and Android Chrome) often delay `click` events by ~300ms or dismiss selection overlays before the click registers.
   - Always bind both `touchend` and `click` to deletion and interactive control buttons:
     ```javascript
     function handleAction(e) {
       e.preventDefault();
       e.stopPropagation();
       // perform action
     }
     btn.addEventListener('click', handleAction);
     btn.addEventListener('touchend', handleAction);
     ```
3. **DOM Initialization Sequence**:
   - Ensure DOM-dependent structures (such as `rawParagraphs` and paragraph maps) are fully initialized before invoking functions like `applyAllHighlightsToDOM()` to prevent `ReferenceError` on fast mobile page loads.
4. **SVG & Canvas Responsiveness**:
   - In graph visualizations (e.g., D3.js force graphs), explicitly set `viewBox` and bind resize listeners to accommodate narrow mobile screen widths ($360\text{px} \sim 430\text{px}$).

---

## Common Pitfalls & Solutions

| Pitfall | Root Cause | Solution |
| :--- | :--- | :--- |
| **`ArrayMemoryError: Unable to allocate 5.5 GiB`** | Faster-Whisper tries to load entire multi-hour WAV into memory. | Use streaming 15-minute PyAV chunks in `scripts/transcribe.py`. |
| **Highlight delete fails on mobile phones** | Touch clicks miss tiny 13px buttons or dismiss prematurely. | Use `🗑️ 刪除` button ($\ge 36\text{px}$) with dual `touchend` + `click` and `e.stopPropagation()`. |
| **`rawParagraphs is not defined` error** | Highlighting code executed before paragraph DOM parsing. | Declare and parse `rawParagraphs` before initializing the highlight system. |
| **Popup off-screen on phone edges** | Popup positioned strictly by selection coordinates without clamping. | Clamp `popupX` between `10px` and `window.innerWidth - popupWidth - 10px`. |
| **Graph out of view or unresponsive on mobile** | SVG lacking responsive `viewBox` or transform center offset. | Add automatic fit-to-screen (`zoom.transform`) and touch gesture support. |
| **GitHub Pages 404 on generated readers** | Whitespace or special characters unencoded in URLs. | Always use `urllib.parse.quote` for HTML file links in `index.html`. |
