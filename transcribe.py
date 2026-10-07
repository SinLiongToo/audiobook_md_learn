"""
Audiobook to Markdown Transcriber using faster-whisper.
Converts long audiobook files (mp3, m4b, m4a, wav, etc.) into structured Markdown files.
Optimized with streaming chunk processing to support arbitrarily long audiobooks (5~30+ hours)
without running out of memory.
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime, timedelta

try:
    import av
    import numpy as np
    from faster_whisper import WhisperModel
    from tqdm import tqdm
except ImportError:
    print("請先安裝必要套件：pip install -r requirements.txt")
    sys.exit(1)


def format_timestamp(seconds: float) -> str:
    """Format seconds into HH:MM:SS format."""
    td = timedelta(seconds=int(seconds))
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def get_audio_duration(file_path: Path) -> float:
    """Get exact audio duration in seconds using PyAV."""
    with av.open(str(file_path)) as container:
        if container.duration:
            return float(container.duration) / av.time_base
        for stream in container.streams.audio:
            if stream.duration and stream.time_base:
                return float(stream.duration * stream.time_base)
    return 0.0


def stream_audio_chunks(file_path: Path, chunk_duration_sec: float = 900.0, sample_rate: int = 16000, max_duration_secs: float = None):
    """
    Stream audio in manageable chunks (default 15 minutes = 900s) to avoid
    huge memory allocations on long multi-hour audiobooks.
    Yields (offset_seconds, 1D float32 numpy array, chunk_duration_seconds).
    """
    container = av.open(str(file_path))
    resampler = av.audio.resampler.AudioResampler(format="s16", layout="mono", rate=sample_rate)
    effective_chunk_sec = min(chunk_duration_sec, max_duration_secs) if max_duration_secs else chunk_duration_sec
    chunk_samples = int(effective_chunk_sec * sample_rate)
    buffer = []
    current_count = 0
    total_time = 0.0

    for frame in container.decode(audio=0):
        for rframe in resampler.resample(frame):
            arr = rframe.to_ndarray().flatten()
            buffer.append(arr)
            current_count += len(arr)
            if current_count >= chunk_samples:
                full_arr = np.concatenate(buffer)
                chunk = full_arr[:chunk_samples].astype(np.float32) / 32768.0
                actual_chunk_len = len(chunk) / sample_rate
                yield total_time, chunk, actual_chunk_len
                total_time += actual_chunk_len
                buffer = [full_arr[chunk_samples:]]
                current_count = len(buffer[0])

                if max_duration_secs and total_time >= max_duration_secs:
                    return

    if buffer and current_count > 0:
        full_arr = np.concatenate(buffer).astype(np.float32) / 32768.0
        actual_chunk_len = len(full_arr) / sample_rate
        if max_duration_secs and (total_time + actual_chunk_len) > max_duration_secs:
            cutoff = int((max_duration_secs - total_time) * sample_rate)
            if cutoff > 0:
                full_arr = full_arr[:cutoff]
                actual_chunk_len = len(full_arr) / sample_rate
                yield total_time, full_arr, actual_chunk_len
        else:
            yield total_time, full_arr, actual_chunk_len


def transcribe_audio(
    audio_path: str,
    output_dir: str = "./output",
    model_size: str = "base.en",
    device: str = "cpu",
    compute_type: str = "int8",
    section_interval_mins: int = 5,
    vad_filter: bool = True,
    language: str = None,
    max_duration_secs: float = None,
    initial_prompt: str = None
):
    audio_file = Path(audio_path).resolve()
    if not audio_file.exists():
        raise FileNotFoundError(f"找不到音訊檔案: {audio_file}")

    output_path = Path(output_dir).resolve()
    output_path.mkdir(parents=True, exist_ok=True)

    clean_name = audio_file.stem
    display_title = clean_name
    for noise in ["[ ezmp3.cc ]", "[ ezmp3.co ]", "_ ezmp3.cc", "(ezmp3.cc)"]:
        display_title = display_title.replace(noise, "").strip()

    md_file_path = output_path / f"{clean_name}.md"

    print(f"\n==========================================")
    print(f" 正在準備轉錄音檔: {audio_file.name}")
    print(f" 模型: {model_size} | 運算裝置: {device} ({compute_type})")
    print(f" 輸出路徑: {md_file_path}")
    print(f"==========================================\n")

    total_duration = get_audio_duration(audio_file)
    effective_duration = min(total_duration, max_duration_secs) if max_duration_secs else total_duration
    print(f"音訊總長度: {format_timestamp(total_duration)} ({total_duration:.1f} 秒)")

    start_load = time.time()
    print("正在載入語音辨識模型...")
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    print(f"模型載入完成，耗時: {time.time() - start_load:.1f} 秒\n")

    print("正在以低記憶體串流分塊模式進行轉錄...")
    start_transcribe = time.time()

    sections = []
    current_section_start = 0.0
    current_section_texts = []
    section_interval_secs = section_interval_mins * 60.0

    # Stream in 15-minute chunks to keep RAM usage under 150MB
    chunk_stream = stream_audio_chunks(
        audio_file,
        chunk_duration_sec=900.0,
        sample_rate=16000,
        max_duration_secs=max_duration_secs
    )

    with tqdm(total=int(effective_duration), unit="s", desc="轉錄進度", dynamic_ncols=True) as pbar:
        last_global_time = 0.0

        for chunk_offset, chunk_audio, chunk_len in chunk_stream:
            # Transcribe current chunk
            segments, info = model.transcribe(
                chunk_audio,
                beam_size=5,
                vad_filter=vad_filter,
                language=language,
                initial_prompt=initial_prompt
            )

            for segment in segments:
                abs_start = chunk_offset + segment.start
                abs_end = chunk_offset + segment.end
                seg_text = segment.text.strip()

                if not seg_text:
                    continue

                # Progress bar update
                advance = max(0, int(abs_end - last_global_time))
                if advance > 0:
                    pbar.update(advance)
                    last_global_time = abs_end

                # Group into section intervals
                if abs_start >= current_section_start + section_interval_secs and current_section_texts:
                    sections.append({
                        "start": current_section_start,
                        "end": abs_start,
                        "text": " ".join(current_section_texts)
                    })
                    current_section_start = abs_start
                    current_section_texts = [seg_text]
                else:
                    current_section_texts.append(seg_text)

        # Make sure progress bar reaches total
        if effective_duration > last_global_time:
            pbar.update(int(effective_duration - last_global_time))

        # Append final section
        if current_section_texts:
            sections.append({
                "start": current_section_start,
                "end": effective_duration,
                "text": " ".join(current_section_texts)
            })

    elapsed_time = time.time() - start_transcribe
    rtf = elapsed_time / effective_duration if effective_duration > 0 else 0
    print(f"\n轉錄完成！共耗時: {timedelta(seconds=int(elapsed_time))} (RTF: {rtf:.2f}x)")

    print(f"正在排版並寫入 Markdown 檔案...")
    with open(md_file_path, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f"title: \"{display_title}\"\n")
        f.write(f"source_file: \"{audio_file.name}\"\n")
        f.write(f"duration: \"{format_timestamp(total_duration)}\"\n")
        f.write(f"transcribed_at: \"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\"\n")
        f.write(f"model: \"{model_size}\"\n")
        f.write(f"device: \"{device} ({compute_type})\"\n")
        f.write("---\n\n")

        f.write(f"# {display_title}\n\n")
        f.write(f"> **音檔長度**：`{format_timestamp(total_duration)}` | ")
        f.write(f"**轉錄耗時**：`{format_timestamp(elapsed_time)}` | ")
        f.write(f"**模型**：`{model_size}`\n\n")

        f.write("## 目錄 (Table of Contents)\n\n")
        for idx, sec in enumerate(sections, 1):
            start_str = format_timestamp(sec["start"])
            end_str = format_timestamp(sec["end"])
            anchor_id = f"sec-{start_str.replace(':', '')}"
            f.write(f"- [{start_str} - {end_str}](#{anchor_id})\n")
        f.write("\n---\n\n")

        f.write("## 內文逐字與筆記 (Transcript)\n\n")
        for idx, sec in enumerate(sections, 1):
            start_str = format_timestamp(sec["start"])
            end_str = format_timestamp(sec["end"])
            anchor_id = f"sec-{start_str.replace(':', '')}"

            f.write(f'<a id="{anchor_id}"></a>\n')
            f.write(f"### ⏱️ [{start_str} - {end_str}]\n\n")
            f.write(f"{sec['text']}\n\n")

    print(f"成功產出 Markdown 文件: {md_file_path}\n")
    return md_file_path


def resolve_audio_inputs(input_arg: str):
    """Smart path resolution with auto-extension detection and fuzzy matching."""
    input_str = input_arg.strip().strip('"').strip("'")
    input_target = Path(input_str).resolve()
    audio_exts = {".mp3", ".m4a", ".m4b", ".wav", ".aac", ".flac", ".ogg"}

    # 1. Direct file
    if input_target.is_file():
        return [input_target]

    # 2. Directory
    if input_target.is_dir():
        files = [f for f in input_target.iterdir() if f.suffix.lower() in audio_exts]
        return files

    # 3. Auto append extension
    for ext in audio_exts:
        candidate = Path(str(input_target) + ext)
        if candidate.is_file():
            print(f"[提示] 自動補上附檔名: {candidate.name}")
            return [candidate]

    # 4. Fuzzy match in parent directory
    if input_target.parent.exists() and input_target.parent.is_dir():
        search_name = input_target.name.lower()
        candidates = [
            f for f in input_target.parent.iterdir()
            if f.is_file() and f.suffix.lower() in audio_exts and search_name in f.name.lower()
        ]
        if candidates:
            print(f"[提示] 自動比對到相符音檔: {candidates[0].name}")
            return [candidates[0]]

    # 5. Fuzzy match in default audiobook library
    default_dir = Path(r"C:\Users\tu-hs\OneDrive\文件\2022_0308_MASA\2022-0708\audiobook")
    if default_dir.exists():
        kw = Path(input_str).name.lower()
        candidates = [
            f for f in default_dir.iterdir()
            if f.is_file() and f.suffix.lower() in audio_exts and kw in f.name.lower()
        ]
        if candidates:
            print(f"[提示] 在有聲書庫中找到相符檔案: {candidates[0].name}")
            return [candidates[0]]

    return []


def main():
    parser = argparse.ArgumentParser(description="有聲書音檔轉錄為 Markdown 檔案工具")
    parser.add_argument("--input", "-i", type=str, required=True, help="音訊檔案路徑、資料夾路徑，或書名關鍵字")
    parser.add_argument("--output", "-o", type=str, default="./output", help="Markdown 輸出資料夾 (預設: ./output)")
    parser.add_argument("--model", "-m", type=str, default="base.en", help="faster-whisper 模型名稱 (例如: tiny.en, base.en, small.en, medium.en)")
    parser.add_argument("--device", "-d", type=str, default="cpu", choices=["cpu", "cuda"], help="運算裝置 (cpu 或 cuda)")
    parser.add_argument("--compute_type", "-c", type=str, default="int8", help="運算精度 (CPU 建議 int8，GPU 建議 float16)")
    parser.add_argument("--interval", type=int, default=5, help="每幾分鐘聚合為一個章節區塊 (預設: 5 分鐘)")
    parser.add_argument("--language", "-l", type=str, default=None, help="指定音訊語言 (例如 en, zh，預設自動偵測)")
    parser.add_argument("--max_duration", type=float, default=None, help="最大轉錄時長（秒），用於快速測試")
    parser.add_argument("--prompt", "-p", type=str, default=None, help="提供給模型的引導提示詞 (例如書名或作者名，提升專有名詞辨識率)")

    args = parser.parse_args()

    audio_files = resolve_audio_inputs(args.input)
    if not audio_files:
        print(f"找不到路徑或相符的音訊檔案: {args.input}")
        print("提示：請確認是否漏打了附檔名（如 .mp3），或是檔案名稱是否正確。")
        return

    print(f"找到 {len(audio_files)} 個待轉錄音檔。")

    for audio_file in audio_files:
        try:
            transcribe_audio(
                audio_path=str(audio_file),
                output_dir=args.output,
                model_size=args.model,
                device=args.device,
                compute_type=args.compute_type,
                section_interval_mins=args.interval,
                language=args.language,
                max_duration_secs=args.max_duration,
                initial_prompt=args.prompt
            )
        except Exception as e:
            print(f"[錯誤] 轉錄 {audio_file.name} 失敗: {e}")


if __name__ == "__main__":
    main()
