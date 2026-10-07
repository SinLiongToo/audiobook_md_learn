# 📚 有聲書轉 Markdown (Audiobook to Markdown) 工具

> 🌐 **線上數位圖書館 (GitHub Pages)**：[https://sinliongtoo.github.io/audiobook_md_learn/](https://sinliongtoo.github.io/audiobook_md_learn/)  
> 包含 83 本有聲書完整逐字稿、時間軸導航、深淺護眼主題與離線閱讀體驗。

這是一套將有聲書音訊（`.mp3`, `.m4a`, `.m4b`, `.wav` 等）高準確度轉換為結構化學習筆記與逐字稿 Markdown (`.md`) 的工具。


核心採用 **faster-whisper**（OpenAI Whisper 的 CTranslate2 高效最佳化版本），具備高辨識率、低記憶體佔用與時間軸標記。

---

## 目錄
- [1. 本機快速開始 (Windows)](#1-本機快速開始-windows)
  - [安裝環境](#安裝環境)
  - [執行轉換指令](#執行轉換指令)
  - [參數說明](#參數說明)
- [2. Google Colab 免費 GPU 極速批次轉換指南](#2-google-colab-免費-gpu-極速批次轉換指南)
  - [為什麼推薦使用 Colab？](#為什麼推薦使用-colab)
  - [Colab 逐步操作教學](#colab-逐步操作教學)
- [3. 輸出 Markdown 格式範例](#3-輸出-markdown-格式範例)
- [4. 模型選擇建議](#4-模型選擇建議)
- [5. 一鍵渲染為 HTML 電子書與數位書架](#5-一鍵渲染為-html-電子書與數位書架)

---

## 1. 本機快速開始 (Windows)

### 安裝環境
確保已安裝 Python 3.10+，並在終端機執行：
```powershell
pip install -r requirements.txt
```

### 執行轉換指令

#### 轉換單本有聲書（以 Jocko Willink - Discipline Equals Freedom 為例）：
```powershell
python transcribe.py --input "C:\Users\tu-hs\OneDrive\文件\2022_0308_MASA\2022-0708\audiobook\Discipline Equals Freedom Audiobook by Jocko Willink [ ezmp3.cc ].mp3" --model base.en --interval 5
```

#### 批次轉換整個資料夾內的音檔：
```powershell
python transcribe.py --input "C:\Users\tu-hs\OneDrive\文件\2022_0308_MASA\2022-0708\audiobook" --output "./output" --model base.en
```

### 常用參數說明
| 參數 | 縮寫 | 預設值 | 說明 |
| :--- | :--- | :--- | :--- |
| `--input` | `-i` | (必填) | 音訊檔案路徑，或包含多個音檔的資料夾路徑 |
| `--output` | `-o` | `./output` | 輸出的 Markdown 檔案存放資料夾 |
| `--model` | `-m` | `base.en` | 模型大小（可選 `tiny.en`, `base.en`, `small.en`, `medium.en`） |
| `--device` | `-d` | `cpu` | 運算裝置（本機預設 `cpu`；若在有顯卡環境可設 `cuda`） |
| `--compute_type` | `-c` | `int8` | 精度模式（CPU 建議 `int8`，GPU 建議 `float16`） |
| `--interval` | | `5` | 每隔幾分鐘聚合為一個獨立小節標題與時間標籤（預設每 5 分鐘） |
| `--language` | `-l` | `None` | 指定語言代碼（如 `en`、`zh`；若不設定則自動辨識） |

---

## 2. Google Colab 免費 GPU 極速批次轉換指南

如果您想要**一口氣把數十本有聲書轉完**，強烈推薦使用 Google Colab 免費提供的 **NVIDIA T4 GPU**。

### 為什麼推薦使用 Colab？
- **速度提升 10~20 倍**：8 小時的有聲書，本機 CPU 需 3~6 小時；在 Colab T4 GPU 上只需 **15~25 分鐘**！
- **保護筆電散熱**：不消耗本機 CPU 與電力，筆電不會發熱風扇狂轉。
- **免費使用**：Google Colab 提供每日免費 GPU 額度。

---

### Colab 逐步操作教學

#### 步驟 1：開啟 Google Colab
1. 在瀏覽器中開啟 [Google Colab](https://colab.research.google.com/)。
2. 點擊「新增筆記本 (New notebook)」，或將本專案內的 `colab_transcribe.ipynb` 直接上傳。

#### 步驟 2：切換至免費 GPU 運算資源
1. 在 Colab 頂部選單點選：**執行階段 (Runtime)** ➔ **變更執行階段類型 (Change runtime type)**。
2. 在「硬體加速器 (Hardware accelerator)」下拉選單選擇 **T4 GPU**。
3. 點選「儲存 (Save)」。

#### 步驟 3：掛載 Google 雲端硬碟（方便讀取與儲存）
在 Colab 程式碼儲存格輸入並執行：
```python
from google.colab import drive
drive.mount('/content/drive')
```
> 將您想轉的有聲書 MP3 丟到 Google Drive（例如 `我的雲端硬碟/audiobooks/`），轉錄完成的 `.md` 也會直接儲存在 Google Drive 中！

#### 步驟 4：安裝極速轉錄套件
```bash
!pip install faster-whisper tqdm
```

#### 步驟 5：在 Colab 執行 GPU 高速轉錄
在儲存格中貼上並執行以下 Python 代碼：

```python
import os
from pathlib import Path
from datetime import timedelta, datetime
from faster_whisper import WhisperModel
from tqdm.auto import tqdm

# === 參數設定 ===
AUDIO_DIR = "/content/drive/MyDrive/audiobooks"      # 放置有聲書的資料夾
OUTPUT_DIR = "/content/drive/MyDrive/audiobook_md"   # 輸出 md 的資料夾
MODEL_NAME = "small.en"                              # GPU 速度極快，推薦直上 small.en 甚至 medium.en！
DEVICE = "cuda"
COMPUTE_TYPE = "float16"                             # GPU 專用高效精度
INTERVAL_MINS = 5                                    # 每 5 分鐘切一段

os.makedirs(OUTPUT_DIR, exist_ok=True)
audio_files = list(Path(AUDIO_DIR).glob("*.mp3")) + list(Path(AUDIO_DIR).glob("*.m4a"))
print(f"找到 {len(audio_files)} 本有聲書，準備使用 GPU ({MODEL_NAME}) 開始高速轉錄！")

model = WhisperModel(MODEL_NAME, device=DEVICE, compute_type=COMPUTE_TYPE)

def fmt_time(seconds):
    td = timedelta(seconds=int(seconds))
    s = int(td.total_seconds())
    return f"{s//3600:02d}:{(s%3600)//60:02d}:{s%60:02d}"

for audio_path in audio_files:
    title = audio_path.stem
    print(f"\n🎧 正在轉錄: {title}")
    segments, info = model.transcribe(str(audio_path), beam_size=5, vad_filter=True)
    
    total_dur = info.duration
    sections = []
    curr_start = 0.0
    curr_texts = []
    
    with tqdm(total=int(total_dur), unit="s", desc=title[:25]) as pbar:
        last_t = 0.0
        for seg in segments:
            pbar.update(max(0, int(seg.end - last_t)))
            last_t = seg.end
            if seg.start >= curr_start + (INTERVAL_MINS * 60) and curr_texts:
                sections.append({"start": curr_start, "end": seg.start, "text": " ".join(curr_texts)})
                curr_start = seg.start
                curr_texts = [seg.text.strip()]
            else:
                curr_texts.append(seg.text.strip())
        if curr_texts:
            sections.append({"start": curr_start, "end": total_dur, "text": " ".join(curr_texts)})
            
    out_md = Path(OUTPUT_DIR) / f"{title}.md"
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(f"> **時長**：`{fmt_time(total_dur)}` | **模型**：`{MODEL_NAME}` | **日期**：`{datetime.now().strftime('%Y-%m-%d')}`\n\n")
        f.write("## 目錄\n\n")
        for s in sections:
            f.write(f"- [{fmt_time(s['start'])} - {fmt_time(s['end'])}](#sec-{fmt_time(s['start']).replace(':', '')})\n")
        f.write("\n---\n\n## 逐字稿與筆記\n\n")
        for s in sections:
            f.write(f'<a id="sec-{fmt_time(s["start"]).replace(":", "")}"></a>\n')
            f.write(f"### ⏱️ [{fmt_time(s['start'])} - {fmt_time(s['end'])}]\n\n{s['text']}\n\n")
            
    print(f"✅ 完成！已儲存至: {out_md}")
```

---

## 3. 輸出 Markdown 格式範例

產生的 Markdown 會具備：
1. **YAML Frontmatter**：包含書名、時長、模型、產生日期。
2. **錨點目錄 (Table of Contents)**：可點擊時間軸跳轉到相應章節。
3. **時間軸區塊**：預設每 5 分鐘一個段落區塊，兼具易讀性與回聽對照功能。

```markdown
---
title: "Discipline Equals Freedom Audiobook by Jocko Willink"
duration: "02:45:10"
model: "base.en"
---

# Discipline Equals Freedom Audiobook by Jocko Willink

> **音檔長度**：`02:45:10` | **模型**：`base.en`

## 目錄 (Table of Contents)
- [00:00:00 - 00:05:00](#sec-000000)
- [00:05:00 - 00:10:00](#sec-000500)

---

## 內文逐字與筆記 (Transcript)

<a id="sec-000000"></a>
### ⏱️ [00:00:00 - 00:05:00]
People look for shortcuts. They look for easy ways to achieve their goals...
```

---

## 4. 模型選擇建議

| 模型 | 參數量 | 本機 CPU 建議 | Google Colab GPU 建議 | 適合情境 |
| :--- | :--- | :--- | :--- | :--- |
| `tiny.en` | 39M | 速度最快 | 幾分鐘可轉完一本 | 快速試閱、粗看結構 |
| `base.en` | 74M | **本機最佳平衡** | 極快 | 本機一般轉錄、內容好讀 |
| `small.en` | 244M | 需較多時間 | **Colab 最推薦首選** | 專業有聲書、極高準確率 |
| `medium.en` | 769M | 不建議純 CPU 跑 | 準確率巔峰 | 需要最完美的專有名詞轉錄 |

---

## 5. 一鍵渲染為 HTML 電子書與數位書架

已將所有轉錄好的 Markdown 筆記升級為現代化、支援離線瀏覽的單檔 HTML 電子書：

```powershell
python build_ebooks.py
```

### 核心功能特點：
1. **獨立單檔 HTML (Single-File)**：無須任何外部依賴或聯網，雙擊即可在任何瀏覽器（手機、平板、電腦）以電子書閱讀體驗開啟。
2. **目錄導航 (TOC) & 滾動偵測 (Scroll Spy)**：左側目錄可即時搜尋時間戳記小節，並隨閱讀進度自動高亮目前章節。
3. **三種舒適主題 (Themes)**：支援「☀️ 明亮模式」、「📜 羊皮紙護眼模式」、「🌙 暗黑模式」，並自動記憶閱讀喜好。
4. **字級與字型切換**：可即時調整字級大小（A- / A+）與襯線/無襯線字型切換。
5. **數位書架首頁 (`ebooks/index.html`)**：提供即時關鍵字過濾搜尋，整合所有有聲書與章節統計。

