#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audiobook Markdown to Standalone HTML eBook Reader Generator
Transforms transcribed markdown study notes into beautiful, responsive, offline-ready HTML eBooks.
Features:
- In-page full-text content search inside every audiobook reader
- Global full-text search across all 83 audiobooks with snippet highlighting
- Interactive Knowledge Connection Graph (知識關聯圖譜)
- 7 Thematic categories with real-time filtering
"""

import os
import re
import html
import json
import sys
from pathlib import Path

# Fix Windows console UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ==========================================
# 1. CATEGORIES & KNOWLEDGE CONNECTION RULES
# ==========================================
CATEGORIES = {
    "wealth": {
        "name": "財富與投資",
        "name_en": "Wealth & Investing",
        "icon": "💰",
        "color": "#10b981",
        "keywords": [
            "psychology of money", "poor charlie", "munger", "warren buffett",
            "die with zero", "think and grow rich", "your money or your life",
            "most important thing", "naval ravikant", "same as ever"
        ]
    },
    "habits": {
        "name": "習慣與生產力",
        "name_en": "Habits & Productivity",
        "icon": "⚡",
        "color": "#3b82f6",
        "keywords": [
            "atomic habits", "deep work", "second brain", "essentialism",
            "effortless", "eat that frog", "master your time", "do it today",
            "compound effect", "power of consistency", "art of laziness",
            "one small step", "power of writing it down"
        ]
    },
    "grit": {
        "name": "意志與心態",
        "name_en": "Grit & Mindset",
        "icon": "🔥",
        "color": "#f97316",
        "keywords": [
            "can_t hurt me", "goggins", "discipline equals freedom", "jocko",
            "make your bed", "nobody cares, work harder", "mindset",
            "motivational", "denzel washington", "awaken the giant",
            "insane race", "let the man be born"
        ]
    },
    "philosophy": {
        "name": "哲學與思辨",
        "name_en": "Philosophy & Psychology",
        "icon": "🧠",
        "color": "#8b5cf6",
        "keywords": [
            "meditations", "marcus aurelius", "antifragile", "taleb",
            "power of now", "zen mind", "freedom from the known", "krishnamurti",
            "courage to be disliked", "12 rules for life", "jordan b. peterson",
            "don_t believe everything you think", "master your emotions",
            "good vibes", "nobody told me this before", "let them theory",
            "four thousand weeks", "art of thinking clearly", "thinking, fast & slow",
            "think again"
        ]
    },
    "leadership": {
        "name": "領導與策略",
        "name_en": "Strategy & Leadership",
        "icon": "🎯",
        "color": "#06b6d4",
        "keywords": [
            "start with why", "simon sinek", "infinite game", "7 habits",
            "covey", "next five moves", "art of the deal", "art of war",
            "win friends and influence", "how to talk to anyone",
            "talk like ted", "public speaking", "how will you measure your life",
            "factfulness", "21 lesson", "harari", "stay ahead of 99"
        ]
    },
    "classics": {
        "name": "文學與經典",
        "name_en": "Literature & Classics",
        "icon": "📖",
        "color": "#ec4899",
        "keywords": [
            "nineteen eighty-four", "1984", "tuesdays with morrie",
            "notes from the underground", "haruki murakami", "dostoyevsky"
        ]
    },
    "taiwan": {
        "name": "台灣念歌與本土",
        "name_en": "Taiwanese Folk & Culture",
        "icon": "🇹🇼",
        "color": "#eab308",
        "keywords": [
            "十殿閻君", "呂柳仙", "勸世歌", "閩南語", "有魂無體"
        ]
    }
}

CROSS_THEMATIC_LINKS = [
    ("複利成長與微習慣", ["Atomic Habits", "Power of Consistency"]),
    ("專注深度與減法工作", ["Atomic Habits", "Deep work"]),
    ("精準本質主義", ["Essentialism", "Effortless"]),
    ("個人知識與第二大腦", ["Deep work", "Second Brain"]),
    ("克服拖延與行動力", ["Eat That Frog", "Do It Today"]),
    ("克服拖延與行動力", ["Do It Today", "The Art Of Laziness"]),
    ("人性行為與金錢心理", ["Psychology of Money", "Poor Charlie"]),
    ("價值投資核心哲學", ["Poor Charlie", "Warren Buffett Portfolio"]),
    ("長期主義與不變真理", ["Psychology of Money", "Same As Ever"]),
    ("投資決策與風險意識", ["Most Important Thing", "Psychology of Money"]),
    ("金錢與生命能量", ["Your Money Or Your Life", "Die With Zero"]),
    ("創富與思考致富", ["Think And Grow Rich", "Almanack of Naval Ravikant"]),
    ("極限自律與心智鍛造", ["Can_t Hurt Me", "Discipline Equals Freedom"]),
    ("堅毅不拔與硬核行動", ["Nobody Cares, Work Harder", "Discipline Equals Freedom"]),
    ("軍事自律與生活整潔", ["MAKE YOUR BED", "Discipline Equals Freedom"]),
    ("成長型思維與突破極限", ["Mindset", "Can_t Hurt Me"]),
    ("激發潛能與內在巨人", ["Awaken the Giant", "Mindset"]),
    ("反脆弱與斯多葛哲學", ["Antifragile", "Meditations"]),
    ("抗挫力與人生韌性", ["Antifragile", "11 Rules For Life"]),
    ("認知偏誤與雙系統思維", ["Thinking, Fast & Slow", "The Art of Thinking Clearly"]),
    ("重新思考與認知重塑", ["Thinking, Fast & Slow", "Think Again"]),
    ("活在當下與心靈覺知", ["The Power of Now", "Zen Mind, Beginner"]),
    ("超越已知與內在自由", ["Freedom From The Known", "The Power of Now"]),
    ("阿德勒心理學與自主人生", ["Courage to be Disliked", "12 Rules for Life"]),
    ("情緒掌控與內在平靜", ["Master Your Emotions", "Don_t Believe Everything You Think"]),
    ("放手哲學與關係界線", ["The Let Them Theory", "Courage to be Disliked"]),
    ("黃金圈法則與無限賽局", ["Start with WHY", "The Infinite Game"]),
    ("以終為始與高效能習慣", ["7 HABITS", "Start with WHY"]),
    ("商業戰略與五步推演", ["Your Next Five Moves", "The Art of War"]),
    ("人際影響力與深度溝通", ["HOW TO WIN FRIENDS", "How to Talk to Anyone"]),
    ("公眾演說與TED魅力", ["Talk Like TED", "The Art of Public Speaking"]),
    ("生命意義與人生衡量", ["How Will You Measure Your Life", "Tuesdays with Morrie"]),
    ("反烏托邦與未來省思", ["Nineteen Eighty-Four", "21 Lesson"]),
    ("長跑耐力與自律修煉", ["What I Talk About When I Talk About Running", "Can_t Hurt Me"]),
    ("台灣說唱與念歌藝術", ["十殿閻君", "懷古勸世歌"]),
    ("念歌曲藝與民間諷喻", ["懷古勸世歌", "有魂無體"]),
]

def categorize_book(title: str) -> str:
    t_lower = title.lower()
    for cat_id, meta in CATEGORIES.items():
        for kw in meta["keywords"]:
            if kw.lower() in t_lower:
                return cat_id
    return "philosophy"

# ==========================================
# 2. HTML EBOOK TEMPLATE (WITH IN-PAGE SEARCH)
# ==========================================
HTML_EBOOK_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-Hant" data-theme="light" data-p-style="indent" data-line-height="normal">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{book_title} - 有聲書學習電子書</title>
  <style>
    :root {{
      --font-body: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif;
      --font-serif: "Iansui", "芫荽", Georgia, "Songti TC", "Noto Serif TC", serif;
      --font-family: var(--font-body);
      --font-size: 18px;
      --line-height: 1.88;
      --content-max-width: 820px;
      --sidebar-width: 320px;
      --bg-primary: #fcfcfd;
      --bg-surface: #ffffff;
      --bg-sidebar: #f8f9fa;
      --bg-header: rgba(255, 255, 255, 0.94);
      --text-primary: #1f2328;
      --text-secondary: #57606a;
      --text-muted: #8c959f;
      --border-color: #e1e4e8;
      --accent-color: #2563eb;
      --accent-hover: #1d4ed8;
      --accent-light: #eff6ff;
      --badge-bg: #e0f2fe;
      --badge-text: #0369a1;
      --subhead-bg: #f1f5f9;
      --card-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03);
    }}

    [data-theme="sepia"] {{
      --bg-primary: #fbf0d9;
      --bg-surface: #f4e8cf;
      --bg-sidebar: #efe3c7;
      --bg-header: rgba(244, 232, 207, 0.95);
      --text-primary: #433422;
      --text-secondary: #6e583f;
      --text-muted: #957d60;
      --border-color: #e3d3b4;
      --accent-color: #92400e;
      --accent-hover: #78350f;
      --accent-light: #fbeacf;
      --badge-bg: #ead8b8;
      --badge-text: #6b4012;
      --subhead-bg: #ecdcb9;
      --card-shadow: 0 1px 3px rgba(67, 52, 34, 0.08);
    }}

    [data-theme="dark"] {{
      --bg-primary: #0f172a;
      --bg-surface: #1e293b;
      --bg-sidebar: #131c31;
      --bg-header: rgba(30, 41, 59, 0.94);
      --text-primary: #f1f5f9;
      --text-secondary: #94a3b8;
      --text-muted: #64748b;
      --border-color: #334155;
      --accent-color: #38bdf8;
      --accent-hover: #7dd3fc;
      --accent-light: #1e3a5f;
      --badge-bg: #1e293b;
      --badge-text: #38bdf8;
      --subhead-bg: #1e293b;
      --card-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
    }}

    [data-line-height="compact"] {{ --line-height: 1.68; }}
    [data-line-height="normal"] {{ --line-height: 1.88; }}
    [data-line-height="loose"] {{ --line-height: 2.12; }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      font-family: var(--font-family);
      font-size: var(--font-size);
      line-height: var(--line-height);
      color: var(--text-primary);
      background-color: var(--bg-primary);
      transition: background-color 0.25s ease, color 0.25s ease;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}

    /* Top Reading Progress Bar */
    #progress-bar {{
      position: fixed;
      top: 0;
      left: 0;
      height: 3px;
      background: linear-gradient(90deg, var(--accent-color), #818cf8);
      width: 0%;
      z-index: 1000;
      transition: width 0.1s linear;
    }}

    /* Top Navigation Header */
    .top-header {{
      position: sticky;
      top: 0;
      z-index: 900;
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 18px;
      background-color: var(--bg-header);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      border-bottom: 1px solid var(--border-color);
    }}

    .header-left, .header-right {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: nowrap;
    }}

    .btn-icon {{
      background: none;
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      cursor: pointer;
      font-size: 13.5px;
      padding: 6px 10px;
      border-radius: 8px;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      transition: all 0.2s;
      white-space: nowrap;
      user-select: none;
      text-decoration: none;
    }}
    .btn-icon:hover {{
      background-color: var(--accent-light);
      border-color: var(--accent-color);
      color: var(--accent-color);
    }}

    .home-link {{
      text-decoration: none;
      color: var(--text-primary);
      font-weight: 600;
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 5px;
    }}
    .home-link:hover {{ color: var(--accent-color); }}

    /* In-Page Search Bar Dropdown */
    .inpage-search-bar {{
      position: sticky;
      top: 60px;
      z-index: 890;
      background-color: var(--bg-surface);
      border-bottom: 1px solid var(--border-color);
      padding: 10px 18px;
      display: none;
      align-items: center;
      gap: 12px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }}
    .inpage-search-bar.active {{ display: flex; }}

    .inpage-search-input-wrapper {{
      flex: 1;
      position: relative;
      display: flex;
      align-items: center;
    }}
    .inpage-search-input {{
      width: 100%;
      padding: 8px 36px 8px 12px;
      border: 1px solid var(--border-color);
      border-radius: 6px;
      background-color: var(--bg-primary);
      color: var(--text-primary);
      font-size: 14px;
    }}
    .inpage-search-input:focus {{ outline: 2px solid var(--accent-color); }}

    .inpage-search-clear {{
      position: absolute;
      right: 10px;
      background: none;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 16px;
    }}

    .inpage-search-count {{
      font-size: 13px;
      color: var(--text-secondary);
      font-family: monospace;
      white-space: nowrap;
    }}
    .search-nav-btns {{ display: flex; gap: 6px; }}

    /* In-Page Search Results Drawer */
    .inpage-search-drawer {{
      position: fixed;
      right: 20px;
      top: 120px;
      width: 360px;
      max-height: calc(100vh - 160px);
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.18);
      z-index: 895;
      display: none;
      flex-direction: column;
      overflow: hidden;
    }}
    .inpage-search-drawer.active {{ display: flex; }}
    .inpage-search-drawer-header {{
      padding: 12px 16px;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 600;
      font-size: 14px;
    }}
    .inpage-search-drawer-list {{
      overflow-y: auto;
      padding: 8px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .search-result-item {{
      padding: 10px 12px;
      border-radius: 8px;
      border: 1px solid var(--border-color);
      background: var(--bg-primary);
      cursor: pointer;
      font-size: 13px;
      transition: all 0.15s;
    }}
    .search-result-item:hover, .search-result-item.active {{
      border-color: var(--accent-color);
      background: var(--accent-light);
    }}
    .search-result-time {{
      font-weight: 700;
      color: var(--accent-color);
      font-family: monospace;
      margin-bottom: 4px;
    }}
    .search-result-snippet {{
      color: var(--text-primary);
      line-height: 1.5;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}

    /* Highlight mark */
    mark.search-highlight {{
      background-color: #fef08a;
      color: #1f2937;
      padding: 1px 3px;
      border-radius: 3px;
    }}
    mark.search-highlight.active-match {{
      background-color: #f97316;
      color: #ffffff;
      outline: 2px solid #ea580c;
    }}

    /* Layout Wrapper */
    .layout {{
      display: flex;
      flex: 1;
      width: 100%;
      position: relative;
    }}

    /* Sidebar / TOC */
    .sidebar {{
      width: var(--sidebar-width);
      position: sticky;
      top: 60px;
      height: calc(100vh - 60px);
      background-color: var(--bg-sidebar);
      border-right: 1px solid var(--border-color);
      overflow-y: auto;
      padding: 20px 16px;
      flex-shrink: 0;
      transition: transform 0.3s ease;
    }}

    .sidebar-title {{
      font-size: 14px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-secondary);
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .toc-search {{
      width: 100%;
      padding: 8px 12px;
      border: 1px solid var(--border-color);
      border-radius: 6px;
      background: var(--bg-surface);
      color: var(--text-primary);
      font-size: 13px;
      margin-bottom: 14px;
    }}
    .toc-search:focus {{ outline: 2px solid var(--accent-color); }}

    .toc-list {{
      list-style: none;
      padding: 0;
      display: flex;
      flex-direction: column;
      gap: 3px;
    }}

    .toc-item a {{
      display: block;
      padding: 7px 10px;
      border-radius: 6px;
      color: var(--text-secondary);
      text-decoration: none;
      font-size: 13.5px;
      font-family: monospace;
      transition: all 0.15s ease;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .toc-item a:hover {{
      background-color: var(--accent-light);
      color: var(--accent-color);
    }}
    .toc-item.active a {{
      background-color: var(--accent-color);
      color: #ffffff;
      font-weight: 600;
    }}

    /* Main Reader Content */
    .main-content {{
      flex: 1;
      min-width: 0;
      padding: 40px 24px 80px 24px;
      display: flex;
      justify-content: center;
    }}
    .reader-container {{
      width: 100%;
      max-width: var(--content-max-width);
    }}

    /* Book Hero */
    .book-hero {{
      margin-bottom: 40px;
      padding-bottom: 24px;
      border-bottom: 2px solid var(--border-color);
    }}
    .book-hero h1 {{
      font-size: 2.1em;
      line-height: 1.35;
      margin-bottom: 16px;
      color: var(--text-primary);
      font-weight: 800;
      letter-spacing: -0.01em;
    }}

    .book-meta-chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 14px;
    }}
    .meta-chip {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 5px 12px;
      border-radius: 20px;
      background-color: var(--badge-bg);
      color: var(--badge-text);
      font-size: 13px;
      font-weight: 500;
    }}
    .meta-chip.cat-badge {{
      background-color: {cat_color}22;
      color: {cat_color};
      font-weight: 600;
    }}

    /* Content Typography */
    .transcript-section {{
      margin-bottom: 50px;
      scroll-margin-top: 80px;
      padding-top: 12px;
    }}

    .section-header {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 20px;
      padding: 9px 14px;
      border-radius: 8px;
      background-color: var(--bg-surface);
      border-left: 4px solid var(--accent-color);
      box-shadow: var(--card-shadow);
    }}

    .section-time {{
      font-size: 1.1em;
      font-weight: 700;
      color: var(--accent-color);
      font-family: monospace;
    }}

    .section-badge {{
      font-size: 12px;
      color: var(--text-muted);
    }}

    .section-subhead {{
      font-size: 1.22em;
      font-weight: 700;
      margin: 1.8em 0 1em 0;
      padding: 7px 14px;
      border-left: 4px solid var(--accent-color);
      background: var(--subhead-bg);
      border-radius: 4px;
      letter-spacing: 0.02em;
      color: var(--text-primary);
    }}

    .section-body {{
      text-align: justify;
      text-justify: inter-ideograph;
      word-break: break-word;
      hyphens: auto;
      letter-spacing: 0.015em;
    }}

    /* Indented paragraph style */
    [data-p-style="indent"] .section-body p {{
      text-indent: 2em;
      margin-bottom: 1.15em;
      line-height: var(--line-height);
    }}

    /* Block paragraph style */
    [data-p-style="block"] .section-body p {{
      text-indent: 0;
      margin-bottom: 1.55em;
      line-height: var(--line-height);
    }}
    .section-body p:last-child {{ margin-bottom: 0; }}

    /* Floating Tools */
    .floating-tools {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      z-index: 800;
    }}
    .float-btn {{
      width: 44px;
      height: 44px;
      border-radius: 50%;
      background-color: var(--bg-surface);
      color: var(--text-primary);
      border: 1px solid var(--border-color);
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      transition: transform 0.2s, background-color 0.2s;
    }}
    .float-btn:hover {{
      transform: translateY(-2px);
      background-color: var(--accent-light);
      color: var(--accent-color);
    }}

    .backdrop {{
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.4);
      z-index: 850;
    }}

    /* Responsive */
    @media (max-width: 992px) {{
      .sidebar {{
        position: fixed;
        left: 0;
        top: 60px;
        bottom: 0;
        z-index: 860;
        transform: translateX(-100%);
        box-shadow: 4px 0 16px rgba(0,0,0,0.15);
      }}
      .sidebar.open {{ transform: translateX(0); }}
      .backdrop.open {{ display: block; }}
      .inpage-search-drawer {{
        left: 20px;
        right: 20px;
        width: auto;
      }}
    }}

    @media (max-width: 640px) {{
      :root {{ --font-size: 17px; }}
      .main-content {{ padding: 24px 16px 60px 16px; }}
      .book-hero h1 {{ font-size: 1.55em; }}
      .top-header {{ padding: 0 10px; }}
      .btn-icon {{ padding: 5px 7px; font-size: 12.5px; }}
      [data-p-style="indent"] .section-body p {{ text-indent: 1.5em; }}
    }}
  </style>
</head>
<body>
  <div id="progress-bar"></div>

  <!-- Top Navigation -->
  <header class="top-header">
    <div class="header-left">
      <button class="btn-icon" id="toggle-sidebar-btn" title="切換章節目錄">
        📑 目錄
      </button>
      <a href="index.html" class="home-link" title="返回書架">
        🏠 書架
      </a>
      <!-- Search Inside Book Button -->
      <button class="btn-icon" id="search-toggle-btn" title="搜尋本書內文 (Ctrl+F)">
        🔍 <span>搜尋內文</span>
      </button>
      <!-- Global Search Link -->
      <a href="index.html?tab=search" class="btn-icon" title="前往全書庫全文檢索">
        🌐 <span>全庫搜尋</span>
      </a>
    </div>

    <div class="header-right">
      <!-- Paragraph Style Toggle -->
      <button class="btn-icon" id="p-style-btn" title="切換段落格式 (縮排 / 間距)">
        ¶ <span id="p-style-label">縮排</span>
      </button>

      <!-- Line Height Toggle -->
      <button class="btn-icon" id="line-height-btn" title="切換行距 (舒適 / 寬鬆 / 緊湊)">
        ↕ <span id="line-height-label">行距</span>
      </button>

      <!-- Font Style Switcher -->
      <button class="btn-icon" id="font-family-btn" title="切換黑體 / 明體">
        🔤
      </button>

      <!-- Theme Switcher -->
      <button class="btn-icon" id="theme-btn" title="切換外觀 (明亮 / 護眼 / 暗黑)">
        🎨 <span id="theme-label">明亮</span>
      </button>

      <!-- Font Size Adjuster -->
      <button class="btn-icon" id="font-dec-btn" title="縮小字級">A-</button>
      <button class="btn-icon" id="font-inc-btn" title="放大字級">A+</button>
    </div>
  </header>

  <!-- In-Page Search Bar Dropdown -->
  <div class="inpage-search-bar" id="inpage-search-bar">
    <div class="inpage-search-input-wrapper">
      <input type="text" id="inpage-search-input" class="inpage-search-input" placeholder="🔍 搜尋本書內文關鍵字 (按 Enter 尋找下一處，Esc 關閉)...">
      <button class="inpage-search-clear" id="inpage-search-clear" title="清空">✕</button>
    </div>
    <span class="inpage-search-count" id="inpage-search-count">0 / 0</span>
    <div class="search-nav-btns">
      <button class="btn-icon" id="inpage-search-prev" title="上一處 (Shift+Enter)">▲</button>
      <button class="btn-icon" id="inpage-search-next" title="下一處 (Enter)">▼</button>
      <button class="btn-icon" id="inpage-search-close" title="關閉搜尋 (Esc)">✕</button>
    </div>
  </div>

  <!-- In-Page Search Results Drawer -->
  <div class="inpage-search-drawer" id="inpage-search-drawer">
    <div class="inpage-search-drawer-header">
      <span>搜尋結果清單</span>
      <button class="btn-icon" id="inpage-drawer-close" style="padding: 2px 6px;">✕</button>
    </div>
    <div class="inpage-search-drawer-list" id="inpage-search-drawer-list"></div>
  </div>

  <div class="backdrop" id="backdrop"></div>

  <div class="layout">
    <!-- Sidebar / TOC -->
    <aside class="sidebar" id="sidebar">
      <div class="sidebar-title">
        <span>章節目錄</span>
        <span style="font-size: 12px; font-weight: normal;">共 {section_count} 節</span>
      </div>
      <input type="text" id="toc-filter" class="toc-search" placeholder="搜尋章節時間...">
      <ul class="toc-list" id="toc-list">
        {toc_html}
      </ul>
    </aside>

    <!-- Main Content Reader -->
    <main class="main-content">
      <article class="reader-container">
        <header class="book-hero">
          <h1>{book_title}</h1>
          <div class="book-meta-chips">
            <span class="meta-chip cat-badge">{cat_icon} {cat_name}</span>
            {meta_chips_html}
          </div>
        </header>

        <!-- Transcript Content -->
        <div class="book-body" id="book-body">
          {content_html}
        </div>
      </article>
    </main>
  </div>

  <!-- Floating Tools -->
  <div class="floating-tools">
    <button class="float-btn" id="scroll-top-btn" title="回到頂部">▲</button>
  </div>

  <script>
    // --- Preferences & Theme Logic ---
    const themes = ['light', 'sepia', 'dark'];
    const themeNames = {{'light': '☀️ 明亮', 'sepia': '📜 護眼', 'dark': '🌙 暗黑'}};
    let currentThemeIdx = themes.indexOf(localStorage.getItem('reader-theme') || 'light');
    if (currentThemeIdx === -1) currentThemeIdx = 0;

    function applyTheme(theme) {{
      document.documentElement.setAttribute('data-theme', theme);
      localStorage.setItem('reader-theme', theme);
      const span = document.getElementById('theme-label');
      if (span) span.textContent = themeNames[theme].split(' ')[1];
    }}
    applyTheme(themes[currentThemeIdx]);

    document.getElementById('theme-btn').addEventListener('click', () => {{
      currentThemeIdx = (currentThemeIdx + 1) % themes.length;
      applyTheme(themes[currentThemeIdx]);
    }});

    // --- Paragraph Style Toggle (Indent vs Block) ---
    const pStyles = ['indent', 'block'];
    const pStyleNames = {{'indent': '縮排', 'block': '留白'}};
    let currentPStyle = localStorage.getItem('reader-p-style') || 'indent';
    if (!pStyles.includes(currentPStyle)) currentPStyle = 'indent';

    function applyPStyle(style) {{
      document.documentElement.setAttribute('data-p-style', style);
      localStorage.setItem('reader-p-style', style);
      const label = document.getElementById('p-style-label');
      if (label) label.textContent = pStyleNames[style];
    }}
    applyPStyle(currentPStyle);

    document.getElementById('p-style-btn').addEventListener('click', () => {{
      currentPStyle = currentPStyle === 'indent' ? 'block' : 'indent';
      applyPStyle(currentPStyle);
    }});

    // --- Line Height Toggle ---
    const lineHeights = ['normal', 'loose', 'compact'];
    const lhNames = {{'normal': '舒適', 'loose': '寬鬆', 'compact': '緊湊'}};
    let currentLH = localStorage.getItem('reader-line-height') || 'normal';
    if (!lineHeights.includes(currentLH)) currentLH = 'normal';

    function applyLineHeight(lh) {{
      document.documentElement.setAttribute('data-line-height', lh);
      localStorage.setItem('reader-line-height', lh);
      const label = document.getElementById('line-height-label');
      if (label) label.textContent = lhNames[lh];
    }}
    applyLineHeight(currentLH);

    document.getElementById('line-height-btn').addEventListener('click', () => {{
      const idx = (lineHeights.indexOf(currentLH) + 1) % lineHeights.length;
      currentLH = lineHeights[idx];
      applyLineHeight(currentLH);
    }});

    // --- Font Family Toggle ---
    let isSerif = localStorage.getItem('reader-serif') === 'true';
    function applyFontFamily(serif) {{
      document.documentElement.style.setProperty('--font-family', serif ? 'var(--font-serif)' : 'var(--font-body)');
      localStorage.setItem('reader-serif', serif);
    }}
    applyFontFamily(isSerif);
    document.getElementById('font-family-btn').addEventListener('click', () => {{
      isSerif = !isSerif;
      applyFontFamily(isSerif);
    }});

    // --- Font Size Adjustment ---
    let currentFontSize = parseInt(localStorage.getItem('reader-font-size') || '18', 10);
    function applyFontSize(size) {{
      size = Math.max(14, Math.min(26, size));
      currentFontSize = size;
      document.documentElement.style.setProperty('--font-size', size + 'px');
      localStorage.setItem('reader-font-size', size);
    }}
    applyFontSize(currentFontSize);

    document.getElementById('font-dec-btn').addEventListener('click', () => applyFontSize(currentFontSize - 1));
    document.getElementById('font-inc-btn').addEventListener('click', () => applyFontSize(currentFontSize + 1));

    // --- Sidebar Drawer & Backdrop ---
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('backdrop');
    const toggleSidebarBtn = document.getElementById('toggle-sidebar-btn');

    function toggleSidebar() {{
      const isOpen = sidebar.classList.toggle('open');
      backdrop.classList.toggle('open', isOpen);
    }}

    toggleSidebarBtn.addEventListener('click', toggleSidebar);
    backdrop.addEventListener('click', () => {{
      sidebar.classList.remove('open');
      backdrop.classList.remove('open');
    }});

    document.querySelectorAll('.toc-item a').forEach(link => {{
      link.addEventListener('click', () => {{
        if (window.innerWidth <= 992) {{
          sidebar.classList.remove('open');
          backdrop.classList.remove('open');
        }}
      }});
    }});

    // --- TOC Search Filter ---
    const tocFilter = document.getElementById('toc-filter');
    const tocItems = document.querySelectorAll('.toc-item');
    tocFilter.addEventListener('input', (e) => {{
      const q = e.target.value.toLowerCase().trim();
      tocItems.forEach(item => {{
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(q) ? '' : 'none';
      }});
    }});

    // --- Reading Progress & Scroll Spy ---
    const progressBar = document.getElementById('progress-bar');
    const sections = Array.from(document.querySelectorAll('.transcript-section'));
    const tocLinkMap = new Map();
    document.querySelectorAll('.toc-item a').forEach(a => {{
      const href = a.getAttribute('href');
      if (href && href.startsWith('#')) {{
        tocLinkMap.set(href.slice(1), a.parentElement);
      }}
    }});

    window.addEventListener('scroll', () => {{
      const winScroll = document.documentElement.scrollTop;
      const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const scrolled = height > 0 ? (winScroll / height) * 100 : 0;
      progressBar.style.width = scrolled + '%';

      let currentSectionId = '';
      for (const sec of sections) {{
        const rect = sec.getBoundingClientRect();
        if (rect.top <= 120) {{
          currentSectionId = sec.id;
        }} else {{
          break;
        }}
      }}

      if (currentSectionId) {{
        document.querySelectorAll('.toc-item.active').forEach(el => el.classList.remove('active'));
        const activeItem = tocLinkMap.get(currentSectionId);
        if (activeItem) {{
          activeItem.classList.add('active');
        }}
      }}
    }}, {{ passive: true }});

    document.getElementById('scroll-top-btn').addEventListener('click', () => {{
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }});

    // ==========================================
    // IN-PAGE CONTENT SEARCH (單書全文搜尋)
    // ==========================================
    const searchBar = document.getElementById('inpage-search-bar');
    const searchInput = document.getElementById('inpage-search-input');
    const searchCount = document.getElementById('inpage-search-count');
    const searchDrawer = document.getElementById('inpage-search-drawer');
    const searchDrawerList = document.getElementById('inpage-search-drawer-list');
    const searchToggleBtn = document.getElementById('search-toggle-btn');
    const searchClearBtn = document.getElementById('inpage-search-clear');
    const searchPrevBtn = document.getElementById('inpage-search-prev');
    const searchNextBtn = document.getElementById('inpage-search-next');
    const searchCloseBtn = document.getElementById('inpage-search-close');
    const drawerCloseBtn = document.getElementById('inpage-drawer-close');

    let searchMatches = [];
    let currentMatchIdx = -1;

    // Cache original innerHTML for clean resets
    const rawParagraphs = Array.from(document.querySelectorAll('.section-body p')).map(p => ({{
      el: p,
      rawHtml: p.innerHTML,
      rawText: p.textContent
    }}));

    function openSearch() {{
      searchBar.classList.add('active');
      searchInput.focus();
      searchInput.select();
      if (searchInput.value.trim()) {{
        performSearch(searchInput.value.trim());
      }}
    }}

    function closeSearch() {{
      searchBar.classList.remove('active');
      searchDrawer.classList.remove('active');
      clearHighlights();
      searchMatches = [];
      currentMatchIdx = -1;
      searchCount.textContent = '0 / 0';
    }}

    function clearHighlights() {{
      rawParagraphs.forEach(item => {{
        item.el.innerHTML = item.rawHtml;
      }});
    }}

    function escapeRegex(str) {{
      return str.replace(/[-\\/\\\\^$*+?.()|[\\]{{}}]/g, '\\\\$&');
    }}

    function escapeHtml(str) {{
      return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }}

    function performSearch(query) {{
      clearHighlights();
      searchMatches = [];
      currentMatchIdx = -1;
      searchDrawerList.innerHTML = '';

      if (!query || query.trim().length === 0) {{
        searchCount.textContent = '0 / 0';
        searchDrawer.classList.remove('active');
        return;
      }}

      query = query.trim();
      const qLower = query.toLowerCase();
      const regex = new RegExp(`(${{escapeRegex(query)}})`, 'gi');

      rawParagraphs.forEach((item, pIdx) => {{
        if (item.rawText.toLowerCase().includes(qLower)) {{
          const sec = item.el.closest('.transcript-section');
          const secTime = sec ? (sec.querySelector('.section-time')?.textContent || '') : '';
          const secId = sec ? sec.id : '';

          // Apply highlight
          item.el.innerHTML = item.rawHtml.replace(regex, '<mark class="search-highlight">$1</mark>');

          const marks = Array.from(item.el.querySelectorAll('mark.search-highlight'));
          marks.forEach(mark => {{
            searchMatches.push({{
              mark,
              el: item.el,
              secTime,
              secId
            }});
          }});

          // Snippet creation
          const matchPos = item.rawText.toLowerCase().indexOf(qLower);
          const start = Math.max(0, matchPos - 30);
          const end = Math.min(item.rawText.length, matchPos + query.length + 50);
          const snippetText = item.rawText.slice(start, end);
          const snippetHtml = escapeHtml(snippetText).replace(regex, '<mark class="search-highlight">$1</mark>');

          const card = document.createElement('div');
          card.className = 'search-result-item';
          card.innerHTML = `
            <div class="search-result-time">${{secTime}}</div>
            <div class="search-result-snippet">...${{snippetHtml}}...</div>
          `;
          card.addEventListener('click', () => {{
            const targetIdx = searchMatches.findIndex(m => m.mark === marks[0]);
            if (targetIdx >= 0) goToMatch(targetIdx);
          }});
          searchDrawerList.appendChild(card);
        }}
      }});

      if (searchMatches.length > 0) {{
        searchDrawer.classList.add('active');
        goToMatch(0);
      }} else {{
        searchCount.textContent = '0 / 0';
        searchDrawer.classList.remove('active');
      }}
    }}

    function goToMatch(idx) {{
      if (idx < 0 || idx >= searchMatches.length) return;
      if (currentMatchIdx >= 0 && searchMatches[currentMatchIdx]) {{
        searchMatches[currentMatchIdx].mark.classList.remove('active-match');
      }}
      currentMatchIdx = idx;
      const target = searchMatches[currentMatchIdx];
      target.mark.classList.add('active-match');
      searchCount.textContent = `${{currentMatchIdx + 1}} / ${{searchMatches.length}}`;

      // Highlight active drawer item
      const drawerItems = searchDrawerList.querySelectorAll('.search-result-item');
      drawerItems.forEach(di => di.classList.remove('active'));

      target.mark.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
    }}

    searchToggleBtn.addEventListener('click', () => {{
      if (searchBar.classList.contains('active')) {{
        closeSearch();
      }} else {{
        openSearch();
      }}
    }});

    let debounceTimer;
    searchInput.addEventListener('input', (e) => {{
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {{
        performSearch(e.target.value);
      }}, 200);
    }});

    searchClearBtn.addEventListener('click', () => {{
      searchInput.value = '';
      performSearch('');
      searchInput.focus();
    }});

    searchNextBtn.addEventListener('click', () => {{
      if (searchMatches.length === 0) return;
      const nextIdx = (currentMatchIdx + 1) % searchMatches.length;
      goToMatch(nextIdx);
    }});

    searchPrevBtn.addEventListener('click', () => {{
      if (searchMatches.length === 0) return;
      const prevIdx = (currentMatchIdx - 1 + searchMatches.length) % searchMatches.length;
      goToMatch(prevIdx);
    }});

    searchInput.addEventListener('keydown', (e) => {{
      if (e.key === 'Enter') {{
        e.preventDefault();
        if (e.shiftKey) {{
          searchPrevBtn.click();
        }} else {{
          searchNextBtn.click();
        }}
      }} else if (e.key === 'Escape') {{
        closeSearch();
      }}
    }});

    searchCloseBtn.addEventListener('click', closeSearch);
    drawerCloseBtn.addEventListener('click', () => searchDrawer.classList.remove('active'));

    window.addEventListener('keydown', (e) => {{
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'f') {{
        e.preventDefault();
        openSearch();
      }} else if (e.key === 'Escape') {{
        if (searchBar.classList.contains('active')) closeSearch();
      }}
    }});
  </script>
</body>
</html>
"""

# ==========================================
# 3. BOOKSHELF INDEX TEMPLATE (3 TABS)
# ==========================================
INDEX_SHELF_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-Hant" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>有聲書數位圖書館 (Audiobook Digital Bookshelf & Knowledge Graph)</title>
  <style>
    :root {{
      --bg-primary: #f8fafc;
      --bg-surface: #ffffff;
      --text-primary: #0f172a;
      --text-secondary: #475569;
      --text-muted: #64748b;
      --border-color: #e2e8f0;
      --accent-color: #2563eb;
      --accent-light: #eff6ff;
      --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
      --card-hover-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
    }}

    [data-theme="dark"] {{
      --bg-primary: #0f172a;
      --bg-surface: #1e293b;
      --text-primary: #f8fafc;
      --text-secondary: #94a3b8;
      --text-muted: #64748b;
      --border-color: #334155;
      --accent-color: #38bdf8;
      --accent-light: #1e3a5f;
      --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
      --card-hover-shadow: 0 10px 20px -3px rgba(0, 0, 0, 0.5);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans TC", sans-serif;
      background-color: var(--bg-primary);
      color: var(--text-primary);
      padding: 24px 20px 60px 20px;
      min-height: 100vh;
    }}

    .container {{
      max-width: 1280px;
      margin: 0 auto;
    }}

    /* Top Header */
    header {{
      margin-bottom: 24px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    .header-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }}

    h1 {{
      font-size: 2.1rem;
      font-weight: 800;
      display: flex;
      align-items: center;
      gap: 12px;
      letter-spacing: -0.01em;
    }}

    .theme-toggle {{
      padding: 8px 16px;
      border-radius: 8px;
      border: 1px solid var(--border-color);
      background: var(--bg-surface);
      color: var(--text-primary);
      cursor: pointer;
      font-weight: 500;
      transition: all 0.2s;
    }}
    .theme-toggle:hover {{ border-color: var(--accent-color); }}

    .stats-bar {{
      display: flex;
      gap: 14px;
      flex-wrap: wrap;
    }}

    .stat-badge {{
      background: var(--accent-light);
      color: var(--accent-color);
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 13.5px;
      font-weight: 600;
    }}

    /* Main Tab Navigation */
    .tab-nav {{
      display: flex;
      gap: 10px;
      border-bottom: 2px solid var(--border-color);
      margin-bottom: 24px;
    }}

    .tab-btn {{
      background: none;
      border: none;
      padding: 12px 20px;
      font-size: 16px;
      font-weight: 700;
      color: var(--text-secondary);
      cursor: pointer;
      position: relative;
      transition: color 0.2s;
      border-bottom: 3px solid transparent;
      margin-bottom: -2px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .tab-btn:hover {{ color: var(--accent-color); }}

    .tab-btn.active {{
      color: var(--accent-color);
      border-bottom-color: var(--accent-color);
    }}

    .tab-pane {{ display: none; }}
    .tab-pane.active {{ display: block; }}

    /* Category Filter Pills */
    .category-pills {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 20px;
    }}

    .cat-pill {{
      padding: 7px 14px;
      border-radius: 20px;
      border: 1px solid var(--border-color);
      background: var(--bg-surface);
      color: var(--text-secondary);
      cursor: pointer;
      font-size: 13.5px;
      font-weight: 600;
      transition: all 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}

    .cat-pill:hover {{
      border-color: var(--accent-color);
      color: var(--accent-color);
      transform: translateY(-1px);
    }}

    .cat-pill.active {{
      background: var(--accent-color);
      color: #ffffff;
      border-color: var(--accent-color);
      box-shadow: 0 2px 6px rgba(37,99,235,0.25);
    }}

    /* Search Input */
    .controls {{
      display: flex;
      gap: 12px;
      margin-bottom: 24px;
      flex-wrap: wrap;
    }}

    .search-input {{
      flex: 1;
      min-width: 280px;
      padding: 12px 18px;
      border: 1px solid var(--border-color);
      border-radius: 10px;
      font-size: 15px;
      background: var(--bg-surface);
      color: var(--text-primary);
    }}
    .search-input:focus {{ outline: 2px solid var(--accent-color); }}

    /* Books Grid */
    .books-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
      gap: 20px;
    }}

    .book-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 22px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-shadow: var(--card-shadow);
      transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
      text-decoration: none;
      color: inherit;
      position: relative;
    }}

    .book-card:hover {{
      transform: translateY(-3px);
      box-shadow: var(--card-hover-shadow);
      border-color: var(--accent-color);
    }}

    .book-card-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
      gap: 8px;
    }}

    .card-cat-badge {{
      font-size: 11.5px;
      font-weight: 700;
      padding: 3px 10px;
      border-radius: 12px;
      white-space: nowrap;
    }}

    .book-card-title {{
      font-size: 1.15rem;
      font-weight: 700;
      line-height: 1.4;
      margin-bottom: 16px;
      color: var(--text-primary);
    }}

    .book-card-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      font-size: 12.5px;
      color: var(--text-secondary);
      margin-top: auto;
    }}

    .card-chip {{
      padding: 3px 8px;
      border-radius: 6px;
      background: var(--bg-primary);
      border: 1px solid var(--border-color);
    }}

    .no-results {{
      text-align: center;
      padding: 60px 20px;
      color: var(--text-secondary);
      font-size: 1.2rem;
      grid-column: 1 / -1;
      display: none;
    }}

    /* ==========================================
       TAB 2: CONNECTION GRAPH (知識關聯圖譜)
       ========================================== */
    .graph-container {{
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      padding: 16px;
      box-shadow: var(--card-shadow);
      position: relative;
      overflow: hidden;
    }}

    .graph-toolbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 14px;
      flex-wrap: wrap;
      gap: 10px;
    }}

    .graph-search-input {{
      padding: 8px 14px;
      border: 1px solid var(--border-color);
      border-radius: 8px;
      background: var(--bg-primary);
      color: var(--text-primary);
      font-size: 13.5px;
      width: 240px;
    }}

    .graph-controls {{
      display: flex;
      gap: 8px;
    }}

    .graph-btn {{
      padding: 6px 12px;
      border: 1px solid var(--border-color);
      border-radius: 6px;
      background: var(--bg-primary);
      color: var(--text-primary);
      cursor: pointer;
      font-size: 13px;
      font-weight: 600;
    }}
    .graph-btn:hover {{ border-color: var(--accent-color); color: var(--accent-color); }}

    #graph-canvas {{
      width: 100%;
      height: 720px;
      border-radius: 10px;
      background: var(--bg-primary);
      cursor: grab;
      display: block;
    }}
    #graph-canvas:active {{ cursor: grabbing; }}

    /* Graph Detail Side Card */
    .graph-info-card {{
      position: absolute;
      top: 80px;
      right: 30px;
      width: 320px;
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 18px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.2);
      display: none;
      flex-direction: column;
      gap: 12px;
      z-index: 100;
    }}
    .graph-info-card.active {{ display: flex; }}
    .graph-info-title {{
      font-size: 1.1rem;
      font-weight: 800;
      color: var(--text-primary);
      line-height: 1.35;
    }}
    .graph-info-cat {{
      display: inline-block;
      font-size: 12px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 8px;
    }}
    .graph-info-links {{
      font-size: 13px;
      color: var(--text-secondary);
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}
    .graph-open-btn {{
      display: inline-flex;
      justify-content: center;
      align-items: center;
      gap: 6px;
      background: var(--accent-color);
      color: #ffffff;
      padding: 10px;
      border-radius: 8px;
      text-decoration: none;
      font-weight: 700;
      font-size: 14px;
      transition: background 0.15s;
    }}
    .graph-open-btn:hover {{ background: var(--accent-hover); }}

    /* ==========================================
       TAB 3: GLOBAL FULL-TEXT SEARCH (全庫搜尋)
       ========================================== */
    .global-search-box {{
      display: flex;
      gap: 12px;
      margin-bottom: 24px;
      flex-wrap: wrap;
    }}
    .global-search-input {{
      flex: 1;
      min-width: 300px;
      padding: 14px 20px;
      border: 2px solid var(--border-color);
      border-radius: 10px;
      font-size: 16px;
      background: var(--bg-surface);
      color: var(--text-primary);
    }}
    .global-search-input:focus {{
      border-color: var(--accent-color);
      outline: none;
    }}

    .search-status-bar {{
      padding: 12px 18px;
      border-radius: 8px;
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      margin-bottom: 20px;
      font-size: 14px;
      color: var(--text-secondary);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .global-results-list {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    .global-book-group {{
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 20px;
      box-shadow: var(--card-shadow);
    }}

    .global-book-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 10px;
    }}

    .global-book-title {{
      font-size: 1.15rem;
      font-weight: 800;
      color: var(--text-primary);
      text-decoration: none;
    }}
    .global-book-title:hover {{ color: var(--accent-color); }}

    .global-snippet-list {{
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}

    .global-snippet-item {{
      background: var(--bg-primary);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 10px 14px;
      font-size: 13.5px;
      text-decoration: none;
      color: inherit;
      display: block;
      transition: all 0.15s;
    }}
    .global-snippet-item:hover {{
      border-color: var(--accent-color);
      background: var(--accent-light);
    }}
    .global-snippet-time {{
      font-size: 12px;
      font-weight: 700;
      color: var(--accent-color);
      font-family: monospace;
      margin-bottom: 4px;
    }}
    .global-snippet-text {{
      line-height: 1.55;
    }}

    mark.global-highlight {{
      background-color: #fef08a;
      color: #1f2937;
      padding: 1px 3px;
      border-radius: 3px;
      font-weight: 600;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="header-top">
        <h1>📚 有聲書數位圖書館</h1>
        <button class="theme-toggle" id="theme-btn">🌓 切換深色</button>
      </div>
      <div class="stats-bar">
        <span class="stat-badge">📖 書籍總數：<strong>{total_books}</strong> 本</span>
        <span class="stat-badge">⏱️ 總章節小節數：<strong>{total_sections}</strong> 節</span>
        <span class="stat-badge">🏷️ 7 大主題分類</span>
        <span class="stat-badge">🕸️ 知識網絡關聯圖譜</span>
        <span class="stat-badge">🔍 單書 / 全庫全文搜尋</span>
      </div>
    </header>

    <!-- Tab Navigation -->
    <nav class="tab-nav">
      <button class="tab-btn active" data-tab="catalog">📚 書庫目錄 (Catalog)</button>
      <button class="tab-btn" data-tab="graph">🕸️ 知識關聯圖譜 (Connection Graph)</button>
      <button class="tab-btn" data-tab="search">🔍 全庫全文檢索 (Global Search)</button>
    </nav>

    <!-- TAB 1: CATALOG -->
    <section class="tab-pane active" id="pane-catalog">
      <!-- Category Filter Pills -->
      <div class="category-pills">
        <button class="cat-pill active" data-cat="all">🌟 全部 ({total_books})</button>
        {category_pills_html}
      </div>

      <div class="controls">
        <input type="text" id="search-input" class="search-input" placeholder="🔍 即時搜尋書名、作者或關鍵字...">
      </div>

      <div class="books-grid" id="books-grid">
        {cards_html}
        <div class="no-results" id="no-results">無符合搜尋條件之書籍</div>
      </div>
    </section>

    <!-- TAB 2: CONNECTION GRAPH -->
    <section class="tab-pane" id="pane-graph">
      <div class="graph-container">
        <div class="graph-toolbar">
          <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">
            <input type="text" id="graph-search" class="graph-search-input" placeholder="🔍 搜尋節點書名...">
            <select id="graph-cat-filter" class="graph-btn">
              <option value="all">🌐 顯示全部分類</option>
              {graph_cat_options_html}
            </select>
          </div>
          <div class="graph-controls">
            <button class="graph-btn" id="graph-fit-all" title="全景適應 (Fit All)" style="background: var(--accent-light); color: var(--accent-color); font-weight: 700;">🎯 全景適應 (Fit All)</button>
            <button class="graph-btn" id="graph-zoom-in" title="放大">➕</button>
            <button class="graph-btn" id="graph-zoom-out" title="縮小">➖</button>
            <button class="graph-btn" id="graph-reset" title="重設視圖">↺ 重設</button>
          </div>
        </div>

        <canvas id="graph-canvas"></canvas>

        <!-- Graph Node Detail Card -->
        <div class="graph-info-card" id="graph-info-card">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="graph-info-cat" id="gic-cat">分類</span>
            <button class="graph-btn" id="gic-close" style="padding: 2px 8px;">✕</button>
          </div>
          <h3 class="graph-info-title" id="gic-title">書籍標題</h3>
          <div style="font-size: 13px; color: var(--text-muted);" id="gic-meta">時長 / 小節數</div>
          <div>
            <div style="font-size: 12px; font-weight: 700; color: var(--text-secondary); margin-bottom: 6px;">關聯主題與書籍：</div>
            <div class="graph-info-links" id="gic-links"></div>
          </div>
          <a href="#" class="graph-open-btn" id="gic-open">📖 開啟電子書 (Open eBook)</a>
        </div>
      </div>
    </section>

    <!-- TAB 3: GLOBAL FULL-TEXT SEARCH -->
    <section class="tab-pane" id="pane-search">
      <div class="global-search-box">
        <input type="text" id="global-search-input" class="global-search-input" placeholder="🔍 輸入關鍵字進行全書庫全文檢索（例：compound interest、習慣、意志力、巴菲特、投資）...">
        <select id="global-cat-select" class="theme-toggle" style="font-size: 15px;">
          <option value="all">全部分類 (83 本)</option>
          {graph_cat_options_html}
        </select>
      </div>

      <div class="search-status-bar" id="search-status-bar">
        <span id="search-status-msg">請輸入關鍵字開始檢索</span>
        <span id="search-status-count"></span>
      </div>

      <div class="global-results-list" id="global-results-list"></div>
    </section>
  </div>

  <script>
    // Embedded Graph Data
    const GRAPH_DATA = {graph_data_json};

    // Helper functions
    function escapeRegex(str) {{
      return (str || '').replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&');
    }}

    function escapeHtml(str) {{
      return (str || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }}

    // --- Preferences & Theme ---
    const themeBtn = document.getElementById('theme-btn');
    let isDark = false;
    try {{
      isDark = localStorage.getItem('shelf-theme') === 'dark';
    }} catch (e) {{}}

    function applyTheme() {{
      document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
      if (themeBtn) themeBtn.textContent = isDark ? '☀️ 切換淺色' : '🌙 切換深色';
      try {{
        localStorage.setItem('shelf-theme', isDark ? 'dark' : 'light');
      }} catch (e) {{}}
    }}
    applyTheme();

    if (themeBtn) {{
      themeBtn.addEventListener('click', () => {{
        isDark = !isDark;
        applyTheme();
        if (graphInitialized) drawGraph();
      }});
    }}

    // ==========================================
    // TAB 1: CATALOG SEARCH & CATEGORY FILTER
    // ==========================================
    const searchInput = document.getElementById('search-input');
    const cards = document.querySelectorAll('.book-card');
    const noResults = document.getElementById('no-results');
    const catPills = document.querySelectorAll('.cat-pill');
    let currentCategory = 'all';

    function filterCatalog() {{
      const q = (searchInput ? searchInput.value : '').toLowerCase().trim();
      let matchCount = 0;
      cards.forEach(card => {{
        const title = (card.getAttribute('data-title') || '').toLowerCase();
        const cat = card.getAttribute('data-cat');
        const matchesCat = currentCategory === 'all' || cat === currentCategory;
        const matchesSearch = !q || title.includes(q);
        if (matchesCat && matchesSearch) {{
          card.style.display = '';
          matchCount++;
        }} else {{
          card.style.display = 'none';
        }}
      }});
      if (noResults) noResults.style.display = matchCount === 0 ? 'block' : 'none';
    }}

    if (searchInput) searchInput.addEventListener('input', filterCatalog);

    catPills.forEach(pill => {{
      pill.addEventListener('click', () => {{
        catPills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        currentCategory = pill.getAttribute('data-cat');
        filterCatalog();
      }});
    }});

    // ==========================================
    // TAB 2: INTERACTIVE KNOWLEDGE CONNECTION GRAPH
    // ==========================================
    const canvas = document.getElementById('graph-canvas');
    const ctx = canvas ? canvas.getContext('2d') : null;
    const gic = document.getElementById('graph-info-card');
    let graphInitialized = false;
    let isAnimationRunning = false;
    let simFrames = 0;
    let nodes = [];
    let edges = [];
    let transform = {{ x: 0, y: 0, scale: 1 }};
    let isDragging = false;
    let dragStart = {{ x: 0, y: 0 }};
    let draggedNode = null;
    let hoveredNode = null;
    let activeFilterCat = 'all';

    function buildGraphNodes(width, height) {{
      const hubList = (GRAPH_DATA.nodes || []).filter(n => n.isHub);
      const hubCount = Math.max(1, hubList.length);
      const hubRadius = 150; // Compact hub core

      nodes = (GRAPH_DATA.nodes || []).map(n => {{
        let x = 0, y = 0;
        if (n.isHub) {{
          const hubIdx = hubList.findIndex(h => h.id === n.id);
          const angle = (hubIdx / hubCount) * Math.PI * 2 - Math.PI / 2;
          x = Math.cos(angle) * hubRadius;
          y = Math.sin(angle) * hubRadius;
        }} else {{
          const parentHubIdx = hubList.findIndex(h => h.cat === n.cat);
          const baseAngle = parentHubIdx >= 0 ? (parentHubIdx / hubCount) * Math.PI * 2 - Math.PI / 2 : Math.random() * Math.PI * 2;
          const r = hubRadius + 35 + Math.random() * 85;
          const a = baseAngle + (Math.random() - 0.5) * 0.9;
          x = Math.cos(a) * r;
          y = Math.sin(a) * r;
        }}
        return {{
          ...n,
          x,
          y,
          vx: 0,
          vy: 0,
          radius: n.isHub ? 24 : 12
        }};
      }});

      edges = (GRAPH_DATA.edges || []).map(e => {{
        const source = nodes.find(n => n.id === e.source);
        const target = nodes.find(n => n.id === e.target);
        return {{ source, target, label: e.label || '', isThematic: e.isThematic || false }};
      }}).filter(e => e.source && e.target);
    }}

    function fitAll() {{
      if (!nodes || nodes.length === 0 || !canvas) return;
      const width = canvas.width / (window.devicePixelRatio || 1);
      const height = canvas.height / (window.devicePixelRatio || 1);

      const visibleNodes = nodes.filter(n => activeFilterCat === 'all' || n.cat === activeFilterCat || (n.isHub && n.cat === activeFilterCat));
      const targetNodes = visibleNodes.length > 0 ? visibleNodes : nodes;

      let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
      targetNodes.forEach(n => {{
        const r = n.radius + 22;
        if (n.x - r < minX) minX = n.x - r;
        if (n.x + r > maxX) maxX = n.x + r;
        if (n.y - r < minY) minY = n.y - r;
        if (n.y + r + 20 > maxY) maxY = n.y + r + 20;
      }});

      const graphW = Math.max(60, maxX - minX);
      const graphH = Math.max(60, maxY - minY);
      const padX = 60;
      const padY = 50;

      const scaleX = (width - padX * 2) / graphW;
      const scaleY = (height - padY * 2) / graphH;
      const newScale = Math.min(1.25, Math.max(0.35, Math.min(scaleX, scaleY)));

      const centerX = (minX + maxX) / 2;
      const centerY = (minY + maxY) / 2;

      transform.scale = newScale;
      transform.x = width / 2 - centerX * newScale;
      transform.y = height / 2 - centerY * newScale;

      drawGraph();
    }}

    function initOrResizeGraph() {{
      if (!canvas || !ctx) return;
      const container = canvas.parentElement;
      if (!container) return;
      const rect = container.getBoundingClientRect();
      const width = Math.max(320, container.clientWidth || rect.width || (window.innerWidth - 64));
      const height = 720;
      const dpr = window.devicePixelRatio || 1;

      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = width + 'px';
      canvas.style.height = height + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      if (!graphInitialized) {{
        buildGraphNodes(width, height);
        graphInitialized = true;
        simFrames = 0;
        fitAll();
      }} else {{
        fitAll();
      }}

      drawGraph();
      wakeAnimation();
    }}

    function wakeAnimation() {{
      if (!isAnimationRunning) {{
        isAnimationRunning = true;
        requestAnimationFrame(animateGraph);
      }}
    }}

    function animateGraph() {{
      if (!graphInitialized) return;

      // Force simulation
      for (let i = 0; i < nodes.length; i++) {{
        const n1 = nodes[i];
        if (n1 === draggedNode) continue;

        // Subtle gravity pull to center
        n1.vx -= n1.x * 0.001;
        n1.vy -= n1.y * 0.001;

        // Node-to-node normalized repulsion
        for (let j = i + 1; j < nodes.length; j++) {{
          const n2 = nodes[j];
          const dx = n2.x - n1.x;
          const dy = n2.y - n1.y;
          const dist = Math.hypot(dx, dy) || 1;
          const minDist = n1.radius + n2.radius + 18;
          if (dist < minDist * 2.2) {{
            const repForce = Math.min(6, (minDist * 2.2 - dist) / (dist * 2));
            const fx = (dx / dist) * repForce;
            const fy = (dy / dist) * repForce;
            n1.vx -= fx;
            n1.vy -= fy;
            n2.vx += fx;
            n2.vy += fy;
          }}
        }}
      }}

      // Edge spring attraction (Hooke's normalized law)
      edges.forEach(e => {{
        const dx = e.target.x - e.source.x;
        const dy = e.target.y - e.source.y;
        const dist = Math.hypot(dx, dy) || 1;
        const targetDist = e.isThematic ? 95 : 65;
        const displacement = dist - targetDist;
        const k = 0.035;
        const fx = (dx / dist) * displacement * k;
        const fy = (dy / dist) * displacement * k;
        if (e.source !== draggedNode) {{ e.source.vx += fx; e.source.vy += fy; }}
        if (e.target !== draggedNode) {{ e.target.vx -= fx; e.target.vy -= fy; }}
      }});

      let maxSpeed = 0;
      nodes.forEach(n => {{
        if (n !== draggedNode) {{
          n.vx = Math.max(-12, Math.min(12, n.vx * 0.8));
          n.vy = Math.max(-12, Math.min(12, n.vy * 0.8));
          n.x += n.vx;
          n.y += n.vy;
          maxSpeed = Math.max(maxSpeed, Math.abs(n.vx), Math.abs(n.vy));
        }}
      }});

      simFrames++;
      // Auto fit-all at frame 25 when initial layout settles
      if (simFrames === 25) {{
        fitAll();
      }}

      drawGraph();

      if ((maxSpeed > 0.05 && simFrames < 150) || isDragging || draggedNode) {{
        requestAnimationFrame(animateGraph);
      }} else {{
        isAnimationRunning = false;
      }}
    }}

    function drawGraph() {{
      if (!ctx || !canvas) return;
      const width = canvas.width / (window.devicePixelRatio || 1);
      const height = canvas.height / (window.devicePixelRatio || 1);
      ctx.clearRect(0, 0, width, height);

      ctx.save();
      ctx.translate(transform.x, transform.y);
      ctx.scale(transform.scale, transform.scale);

      // Draw Edges
      edges.forEach(e => {{
        const isCatMatch = activeFilterCat === 'all' || e.source.cat === activeFilterCat || e.target.cat === activeFilterCat;
        if (!isCatMatch) return;

        const isConnectedToHover = hoveredNode && (e.source === hoveredNode || e.target === hoveredNode);
        ctx.beginPath();
        ctx.moveTo(e.source.x, e.source.y);
        ctx.lineTo(e.target.x, e.target.y);
        if (e.isThematic) {{
          ctx.setLineDash([4, 4]);
          ctx.strokeStyle = isConnectedToHover ? '#f97316' : (isDark ? 'rgba(255,255,255,0.22)' : 'rgba(0,0,0,0.18)');
          ctx.lineWidth = isConnectedToHover ? 2.5 : 1.3;
        }} else {{
          ctx.setLineDash([]);
          ctx.strokeStyle = isConnectedToHover ? e.source.color : (isDark ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.1)');
          ctx.lineWidth = isConnectedToHover ? 2 : 1;
        }}
        ctx.stroke();
        ctx.setLineDash([]);
      }});

      // Draw Nodes
      nodes.forEach(n => {{
        const isCatMatch = activeFilterCat === 'all' || n.cat === activeFilterCat;
        if (!isCatMatch) return;

        const isHovered = n === hoveredNode;
        const isConnected = hoveredNode && edges.some(e => (e.source === hoveredNode && e.target === n) || (e.target === hoveredNode && e.source === n));

        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius + (isHovered ? 4 : 0), 0, Math.PI * 2);
        ctx.fillStyle = n.color;
        ctx.fill();

        if (n.isHub || isHovered || isConnected) {{
          ctx.strokeStyle = isDark ? '#ffffff' : '#0f172a';
          ctx.lineWidth = isHovered ? 3 : (n.isHub ? 2.5 : 1.5);
          ctx.stroke();
        }}

        // Text label
        if (n.isHub || isHovered || transform.scale > 0.85) {{
          ctx.fillStyle = isDark ? '#f8fafc' : '#0f172a';
          ctx.font = n.isHub ? 'bold 13px sans-serif' : (isHovered ? 'bold 12px sans-serif' : '11px sans-serif');
          ctx.textAlign = 'center';
          ctx.fillText(n.shortTitle || n.title, n.x, n.y + n.radius + 14);
        }}
      }});

      ctx.restore();
    }}

    function getMousePos(e) {{
      const rect = canvas.getBoundingClientRect();
      const clientX = e.clientX ?? (e.touches && e.touches[0] ? e.touches[0].clientX : 0);
      const clientY = e.clientY ?? (e.touches && e.touches[0] ? e.touches[0].clientY : 0);
      return {{
        x: (clientX - rect.left - transform.x) / transform.scale,
        y: (clientY - rect.top - transform.y) / transform.scale
      }};
    }}

    function findNodeAt(pos) {{
      for (let i = nodes.length - 1; i >= 0; i--) {{
        const n = nodes[i];
        if (activeFilterCat !== 'all' && n.cat !== activeFilterCat) continue;
        const dist = Math.hypot(n.x - pos.x, n.y - pos.y);
        if (dist <= n.radius + 6) return n;
      }}
      return null;
    }}

    if (canvas) {{
      canvas.addEventListener('mousedown', (e) => {{
        const pos = getMousePos(e);
        const node = findNodeAt(pos);
        if (node) {{
          draggedNode = node;
        }} else {{
          isDragging = true;
          dragStart = {{ x: e.clientX - transform.x, y: e.clientY - transform.y }};
        }}
        wakeAnimation();
      }});

      canvas.addEventListener('mousemove', (e) => {{
        const pos = getMousePos(e);
        if (draggedNode) {{
          draggedNode.x = pos.x;
          draggedNode.y = pos.y;
          draggedNode.vx = 0;
          draggedNode.vy = 0;
          wakeAnimation();
        }} else if (isDragging) {{
          transform.x = e.clientX - dragStart.x;
          transform.y = e.clientY - dragStart.y;
          drawGraph();
        }} else {{
          const prevHover = hoveredNode;
          hoveredNode = findNodeAt(pos);
          if (prevHover !== hoveredNode) {{
            drawGraph();
          }}
        }}
      }});

      window.addEventListener('mouseup', () => {{
        isDragging = false;
        draggedNode = null;
      }});

      // Touch events for mobile/tablet
      canvas.addEventListener('touchstart', (e) => {{
        if (e.touches && e.touches.length === 1) {{
          const touch = e.touches[0];
          const pos = getMousePos(touch);
          const node = findNodeAt(pos);
          if (node) {{
            draggedNode = node;
          }} else {{
            isDragging = true;
            dragStart = {{ x: touch.clientX - transform.x, y: touch.clientY - transform.y }};
          }}
          wakeAnimation();
        }}
      }}, {{ passive: true }});

      canvas.addEventListener('touchmove', (e) => {{
        if (e.touches && e.touches.length === 1) {{
          const touch = e.touches[0];
          const pos = getMousePos(touch);
          if (draggedNode) {{
            draggedNode.x = pos.x;
            draggedNode.y = pos.y;
            draggedNode.vx = 0;
            draggedNode.vy = 0;
            wakeAnimation();
          }} else if (isDragging) {{
            transform.x = touch.clientX - dragStart.x;
            transform.y = touch.clientY - dragStart.y;
            drawGraph();
          }}
        }}
      }}, {{ passive: true }});

      window.addEventListener('touchend', () => {{
        isDragging = false;
        draggedNode = null;
      }});

      canvas.addEventListener('wheel', (e) => {{
        e.preventDefault();
        const zoomFactor = e.deltaY < 0 ? 1.15 : 0.88;
        const rect = canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        transform.x = mouseX - (mouseX - transform.x) * zoomFactor;
        transform.y = mouseY - (mouseY - transform.y) * zoomFactor;
        transform.scale *= zoomFactor;
        transform.scale = Math.max(0.3, Math.min(3.5, transform.scale));
        drawGraph();
      }}, {{ passive: false }});

      canvas.addEventListener('click', (e) => {{
        const pos = getMousePos(e);
        const node = findNodeAt(pos);
        if (node && !node.isHub) {{
          showGraphInfoCard(node);
        }}
      }});
    }}

    function showGraphInfoCard(node) {{
      if (!gic) return;
      const titleEl = document.getElementById('gic-title');
      const catEl = document.getElementById('gic-cat');
      const metaEl = document.getElementById('gic-meta');
      const openEl = document.getElementById('gic-open');
      const linksContainer = document.getElementById('gic-links');

      if (titleEl) titleEl.textContent = node.title;
      if (catEl) {{
        catEl.textContent = node.catName;
        catEl.style.backgroundColor = node.color + '22';
        catEl.style.color = node.color;
      }}
      if (metaEl) metaEl.textContent = `📑 共 ${{node.sections || 0}} 節時間軸`;
      if (openEl) openEl.href = node.file;

      if (linksContainer) {{
        const connectedEdges = edges.filter(e => (e.source === node || e.target === node) && e.isThematic);
        linksContainer.innerHTML = '';
        if (connectedEdges.length === 0) {{
          linksContainer.innerHTML = '<div style="color: var(--text-muted); font-size: 13px;">無特定跨書主題鏈結</div>';
        }} else {{
          connectedEdges.forEach(e => {{
            const other = e.source === node ? e.target : e.source;
            const a = document.createElement('a');
            a.href = other.file;
            a.style.color = 'var(--accent-color)';
            a.style.textDecoration = 'none';
            a.style.display = 'block';
            a.style.marginBottom = '6px';
            a.style.fontSize = '13px';
            a.innerHTML = `🔗 <strong>${{escapeHtml(e.label)}}</strong>：${{escapeHtml(other.title)}}`;
            linksContainer.appendChild(a);
          }});
        }}
      }}

      gic.classList.add('active');
    }}

    const gicClose = document.getElementById('gic-close');
    if (gicClose && gic) gicClose.addEventListener('click', () => gic.classList.remove('active'));

    // Zoom around viewport center
    function zoomBy(factor) {{
      if (!canvas) return;
      const width = canvas.width / (window.devicePixelRatio || 1);
      const height = canvas.height / (window.devicePixelRatio || 1);
      const centerX = width / 2;
      const centerY = height / 2;

      const newScale = Math.max(0.25, Math.min(3.5, transform.scale * factor));
      const actualFactor = newScale / transform.scale;

      transform.x = centerX - (centerX - transform.x) * actualFactor;
      transform.y = centerY - (centerY - transform.y) * actualFactor;
      transform.scale = newScale;

      drawGraph();
    }}

    // Graph toolbar
    const fitAllBtn = document.getElementById('graph-fit-all');
    const zoomInBtn = document.getElementById('graph-zoom-in');
    const zoomOutBtn = document.getElementById('graph-zoom-out');
    const resetBtn = document.getElementById('graph-reset');
    const graphCatFilter = document.getElementById('graph-cat-filter');
    const graphSearch = document.getElementById('graph-search');

    if (fitAllBtn) fitAllBtn.addEventListener('click', () => {{
      fitAll();
    }});
    if (zoomInBtn) zoomInBtn.addEventListener('click', () => {{
      zoomBy(1.25);
    }});
    if (zoomOutBtn) zoomOutBtn.addEventListener('click', () => {{
      zoomBy(0.8);
    }});
    if (resetBtn) resetBtn.addEventListener('click', () => {{
      activeFilterCat = 'all';
      if (graphCatFilter) graphCatFilter.value = 'all';
      if (graphSearch) graphSearch.value = '';
      hoveredNode = null;
      if (gic) gic.classList.remove('active');
      const width = canvas.width / (window.devicePixelRatio || 1);
      const height = canvas.height / (window.devicePixelRatio || 1);
      buildGraphNodes(width, height);
      simFrames = 0;
      fitAll();
      wakeAnimation();
    }});

    if (graphCatFilter) graphCatFilter.addEventListener('change', (e) => {{
      activeFilterCat = e.target.value;
      fitAll();
    }});

    if (graphSearch) graphSearch.addEventListener('input', (e) => {{
      const q = e.target.value.toLowerCase().trim();
      if (!q) return;
      const match = nodes.find(n => !n.isHub && n.title.toLowerCase().includes(q));
      if (match && canvas) {{
        const rect = canvas.parentElement ? canvas.parentElement.getBoundingClientRect() : {{ width: 800 }};
        transform.x = (rect.width || 800) / 2 - match.x * transform.scale;
        transform.y = 340 - match.y * transform.scale;
        hoveredNode = match;
        drawGraph();
        showGraphInfoCard(match);
      }}
    }});

    window.addEventListener('resize', () => {{
      const pane = document.getElementById('pane-graph');
      if (pane && pane.classList.contains('active')) {{
        initOrResizeGraph();
      }}
    }});

    // ==========================================
    // TAB 3: GLOBAL FULL-TEXT SEARCH (全庫搜尋)
    // ==========================================
    let searchIndexData = null;
    let isSearchIndexLoading = false;

    async function loadSearchIndexOnce() {{
      if (searchIndexData) return searchIndexData;
      if (isSearchIndexLoading) return null;
      isSearchIndexLoading = true;
      const statusMsg = document.getElementById('search-status-msg');
      if (statusMsg) statusMsg.textContent = '⏳ 正在載入全書庫全文檢索索引 (83 本有聲書)...';

      try {{
        const res = await fetch('search_index.json');
        if (!res.ok) throw new Error(`HTTP ${{res.status}}`);
        searchIndexData = await res.json();
        if (statusMsg) statusMsg.textContent = '✅ 全書庫索引載入完成！請輸入關鍵字檢索。';
        return searchIndexData;
      }} catch (err) {{
        if (statusMsg) {{
          if (window.location.protocol === 'file:') {{
            statusMsg.textContent = '⚠️ 本地 file:// 協定受瀏覽器跨域安全性限制。請在 GitHub Pages 線上瀏覽或啟用本地伺服器以使用全文檢索。';
          }} else {{
            statusMsg.textContent = '❌ 載入全文索引失敗：' + err.message;
          }}
        }}
        return null;
      }} finally {{
        isSearchIndexLoading = false;
      }}
    }}

    // Preload index in background after page is fully idle
    if (window.location.protocol !== 'file:') {{
      setTimeout(() => {{
        loadSearchIndexOnce();
      }}, 1200);
    }}

    const globalSearchInput = document.getElementById('global-search-input');
    const globalCatSelect = document.getElementById('global-cat-select');
    const globalResultsList = document.getElementById('global-results-list');
    const searchStatusMsg = document.getElementById('search-status-msg');
    const searchStatusCount = document.getElementById('search-status-count');

    let globalSearchDebounce;
    if (globalSearchInput) {{
      globalSearchInput.addEventListener('input', (e) => {{
        clearTimeout(globalSearchDebounce);
        globalSearchDebounce = setTimeout(() => {{
          runGlobalSearch(e.target.value);
        }}, 250);
      }});
    }}
    if (globalCatSelect) {{
      globalCatSelect.addEventListener('change', () => {{
        if (globalSearchInput) runGlobalSearch(globalSearchInput.value);
      }});
    }}

    async function runGlobalSearch(query) {{
      if (!searchIndexData) {{
        const data = await loadSearchIndexOnce();
        if (!data) return;
      }}

      query = (query || '').trim();
      if (!globalResultsList) return;
      globalResultsList.innerHTML = '';

      if (!query) {{
        if (searchStatusMsg) searchStatusMsg.textContent = '請輸入關鍵字開始檢索';
        if (searchStatusCount) searchStatusCount.textContent = '';
        return;
      }}

      const selectedCat = globalCatSelect ? globalCatSelect.value : 'all';
      const qLower = query.toLowerCase();
      const regex = new RegExp(`(${{escapeRegex(query)}})`, 'gi');

      let totalBookMatches = 0;
      let totalSnippetMatches = 0;

      searchIndexData.forEach(book => {{
        if (selectedCat !== 'all' && book.category !== selectedCat) return;

        const matchingSections = [];
        (book.sections || []).forEach(sec => {{
          if (sec.text && sec.text.toLowerCase().includes(qLower)) {{
            matchingSections.push(sec);
          }}
        }});

        if (matchingSections.length > 0) {{
          totalBookMatches++;
          totalSnippetMatches += matchingSections.length;

          const group = document.createElement('div');
          group.className = 'global-book-group';

          const bookHeader = document.createElement('div');
          bookHeader.className = 'global-book-header';
          bookHeader.innerHTML = `
            <a href="${{book.file}}" class="global-book-title">${{escapeHtml(book.title)}}</a>
            <span class="card-cat-badge" style="background: var(--accent-light); color: var(--accent-color);">
              ${{matchingSections.length}} 處相符
            </span>
          `;
          group.appendChild(bookHeader);

          const snippetList = document.createElement('div');
          snippetList.className = 'global-snippet-list';

          matchingSections.slice(0, 5).forEach(sec => {{
            const matchPos = sec.text.toLowerCase().indexOf(qLower);
            const start = Math.max(0, matchPos - 40);
            const end = Math.min(sec.text.length, matchPos + query.length + 80);
            const snippetText = sec.text.slice(start, end);
            const snippetHtml = escapeHtml(snippetText).replace(regex, '<mark class="global-highlight">$1</mark>');

            const item = document.createElement('a');
            item.href = `${{book.file}}#${{sec.id}}`;
            item.className = 'global-snippet-item';
            item.innerHTML = `
              <div class="global-snippet-time">⏱️ ${{escapeHtml(sec.time)}}</div>
              <div class="global-snippet-text">...${{snippetHtml}}...</div>
            `;
            snippetList.appendChild(item);
          }});

          if (matchingSections.length > 5) {{
            const more = document.createElement('div');
            more.style.fontSize = '12px';
            more.style.color = 'var(--text-muted)';
            more.style.padding = '4px 0';
            more.textContent = `還有 ${{matchingSections.length - 5}} 處相符，點擊書名進入閱讀完整內文...`;
            snippetList.appendChild(more);
          }}

          group.appendChild(snippetList);
          globalResultsList.appendChild(group);
        }}
      }});

      if (searchStatusMsg) searchStatusMsg.textContent = `檢索「${{escapeHtml(query)}}」結果：共涵蓋 ${{totalBookMatches}} 本書`;
      if (searchStatusCount) searchStatusCount.textContent = `共找到 ${{totalSnippetMatches}} 處段落`;
    }}

    // ==========================================
    // TAB SWITCHER CONTROLLER (Attached after all components ready)
    // ==========================================
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    function switchTab(tabId) {{
      tabBtns.forEach(btn => btn.classList.toggle('active', btn.getAttribute('data-tab') === tabId));
      tabPanes.forEach(pane => pane.classList.toggle('active', pane.id === 'pane-' + tabId));

      if (tabId === 'graph') {{
        requestAnimationFrame(() => {{
          initOrResizeGraph();
        }});
      }} else if (tabId === 'search') {{
        loadSearchIndexOnce();
        if (globalSearchInput) globalSearchInput.focus();
      }}
    }}

    tabBtns.forEach(btn => {{
      btn.addEventListener('click', () => {{
        const tab = btn.getAttribute('data-tab');
        if (tab) switchTab(tab);
      }});
    }});

    // Check URL params for direct search or tab: ?tab=search&q=keyword
    try {{
      const urlParams = new URLSearchParams(window.location.search);
      const tabParam = urlParams.get('tab');
      if (tabParam === 'search') {{
        switchTab('search');
        const q = urlParams.get('q');
        if (q && globalSearchInput) {{
          globalSearchInput.value = q;
          runGlobalSearch(q);
        }}
      }} else if (tabParam === 'graph') {{
        switchTab('graph');
      }}
    }} catch (e) {{}}
  </script>
</body>
</html>
"""


# ==========================================
# 4. PARSER & ENHANCER LOGIC
# ==========================================
def enhance_transcript_text(raw_text: str) -> list:
    """Cleans punctuation and groups into readable paragraphs."""
    text = raw_text.strip()
    if not text:
        return []

    text = re.sub(r'\s+([,.;:?!])', r'\1', text)

    is_chinese = bool(re.search(r'[\u4e00-\u9fff]', text))
    if is_chinese:
        text = re.sub(r'([\u4e00-\u9fff]),', r'\1，', text)
        text = re.sub(r',([\u4e00-\u9fff])', r'，\1', text)
        text = re.sub(r'([\u4e00-\u9fff])\.', r'\1。', text)
        text = re.sub(r'([\u4e00-\u9fff])\?', r'\1？', text)
        text = re.sub(r'([\u4e00-\u9fff])!', r'\1！', text)
        text = re.sub(r'([\u4e00-\u9fff]):', r'\1：', text)
        text = re.sub(r'([\u4e00-\u9fff]);', r'\1；', text)
        text = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', text)
        text = re.sub(r'(說|道|問|答|喊)[，：]\s*([「"“]?)([^。！？，\n]+[。！？])', r'\1：「\3」', text)
        text = re.sub(r'([\u4e00-\u9fff])([a-zA-Z0-9])', r'\1 \2', text)
        text = re.sub(r'([a-zA-Z0-9])([\u4e00-\u9fff])', r'\1 \2', text)

    text = re.sub(r'([A-Z]{2,}(?:[\s,:\-–—]+[A-Z]{2,})+)\s+([A-Z][a-z]+|\bI\s+[a-z]+)', r'\1.\n\n\2', text)
    text = re.sub(r'([.?!])([A-Z])', r'\1 \2', text)
    text = re.sub(r'\b(said|asked|told him|told her|replied|yelled|whispered|screamed),\s+([A-Z][^\.\?!]+[\.\?!])', r'\1, “\2”', text)
    text = re.sub(r'(?<!<[^>])"([^"\n]+)"', r'“\1”', text)
    text = re.sub(r"([A-Za-z])'([A-Za-z])", r'\1’\2', text)
    text = re.sub(r'\.{3,}', '…', text)
    text = re.sub(r'\s+--\s+|\s+--|--\s+', ' — ', text)

    protected = {}
    abbrs = [
        r'Mr\.', r'Mrs\.', r'Ms\.', r'Dr\.', r'Prof\.', r'Sr\.', r'Jr\.',
        r'vs\.', r'etc\.', r'i\.e\.', r'e\.g\.', r'vol\.', r'no\.',
        r'J\.\s*C\.', r'B\.\s*F\.', r'U\.\s*S\.', r'U\.\s*K\.', r'a\.m\.', r'p\.m\.'
    ]
    for idx, abbr in enumerate(abbrs):
        pattern = re.compile(abbr, re.IGNORECASE)
        for m in pattern.finditer(text):
            tok = f"__ABBR_{idx}_{len(protected)}__"
            protected[tok] = m.group(0)
            text = text.replace(m.group(0), tok, 1)

    def num_replace(m):
        tok = f"__NUM_{len(protected)}__"
        protected[tok] = m.group(0)
        return tok
    text = re.sub(r'\b\d+\.\d+\b', num_replace, text)

    raw_sents = re.split(r'(?<=[.?!…])\s+(?=[A-Z“「])|(?<=[。！？…])(?=[^\s。！？…])', text)

    sentences = []
    for s in raw_sents:
        s = s.strip()
        if not s:
            continue
        for tok, orig in protected.items():
            s = s.replace(tok, orig)
        sentences.append(s)

    paragraphs = []
    current_p = []

    transitions = (
        'however', 'meanwhile', 'furthermore', 'in fact', 'on the other hand',
        'one day', 'years later', 'days later', 'finally', 'suddenly',
        'for example', 'in contrast', 'in other words', 'now,', 'first,', 'second,',
        'the premise of this book', 'the lesson here', 'then he waited', 'the truth is',
        'when i opened my eyes', 'my recovery', 'how i learned', 'how and why',
        'problem number one', 'problem number two', 'problem number three',
        'however,', 'therefore,', 'moreover,', 'consequently,',
        '然而', '但是', '因此', '例如', '有一天', '總之', '事實上', '最後', '第一', '第二'
    )

    for sent in sentences:
        is_subhead = False
        words = [w for w in re.findall(r'[a-zA-Z]+', sent) if len(w) > 1]
        if words and len(words) >= 2 and all(w.isupper() for w in words):
            is_subhead = True
        elif re.match(r'^(?:Chapter|Part|Rule|Introduction)\s+\d+', sent, re.I):
            is_subhead = True

        if is_subhead:
            if current_p:
                paragraphs.append(" ".join(current_p))
                current_p = []
            paragraphs.append(f"###SUBHEAD###{sent}")
            continue

        has_dialogue = '“' in sent or '「' in sent
        sent_lower = sent.lower()
        has_transition = any(sent_lower.startswith(t) for t in transitions)

        should_break = False
        if len(current_p) >= 2 and (has_transition or has_dialogue):
            should_break = True
        elif len(current_p) >= 4:
            should_break = True
        elif sum(len(s.split()) for s in current_p) >= 85:
            should_break = True

        if should_break and current_p:
            paragraphs.append(" ".join(current_p))
            current_p = []

        current_p.append(sent)

    if current_p:
        paragraphs.append(" ".join(current_p))

    return paragraphs

def parse_markdown_audiobook(md_path: Path):
    """Parses an audiobook transcript markdown file into structured data."""
    text = md_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    title = md_path.stem
    meta_chips = []
    toc_links = []
    sections = []

    # 1. Extract Title
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("# "):
            title = line[2:].strip()
            i += 1
            break
        i += 1

    # 2. Extract Metadata blockquote
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith(">"):
            raw_meta = line.lstrip("> ").strip()
            parts = [p.strip() for p in raw_meta.split("|")]
            for p in parts:
                cleaned = re.sub(r'[*`]', '', p)
                if cleaned:
                    meta_chips.append(cleaned)
            i += 1
            break
        elif line.startswith("## ") or line.startswith("<a "):
            break
        i += 1

    # 3. Parse content lines into sections
    current_sec_id = ""
    current_sec_time = ""
    current_paragraphs = []

    def commit_section():
        nonlocal current_sec_id, current_sec_time, current_paragraphs
        if current_sec_id or current_paragraphs:
            raw_body = "\n\n".join(current_paragraphs).strip()
            enhanced_paras = enhance_transcript_text(raw_body)
            sections.append({
                "id": current_sec_id or f"sec-{len(sections):04d}",
                "time": current_sec_time or "段落內容",
                "paragraphs": enhanced_paras,
                "raw_text": raw_body
            })
            current_paragraphs = []
            current_sec_id = ""
            current_sec_time = ""

    in_toc_area = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("## 目錄") or stripped.startswith("## Table of Contents"):
            in_toc_area = True
            i += 1
            continue

        if in_toc_area:
            if stripped == "---" or stripped.startswith("## 逐字稿"):
                in_toc_area = False
                i += 1
                continue
            m_toc = re.match(r'^[-\*]\s+\[(.*?)\]\(#(.*?)\)', stripped)
            if m_toc:
                toc_links.append((m_toc.group(1), m_toc.group(2)))
                i += 1
                continue
            if stripped.startswith("<a id=") or stripped.startswith("### "):
                in_toc_area = False

        m_anchor = re.match(r'<a\s+id="([^"]+)"></a>', stripped)
        if m_anchor:
            commit_section()
            current_sec_id = m_anchor.group(1)
            i += 1
            continue

        m_head = re.match(r'^###\s*(?:⏱️)?\s*\[?([0-9: \-]+)\]?', stripped)
        if m_head:
            if not current_sec_id:
                commit_section()
            current_sec_time = m_head.group(1).strip()
            if not current_sec_id:
                clean_digits = re.sub(r'[^0-9]', '', current_sec_time)[:6]
                current_sec_id = f"sec-{clean_digits}" if clean_digits else f"sec-{len(sections):04d}"
            i += 1
            continue

        if stripped == "---" or stripped.startswith("## 逐字稿與筆記") or stripped.startswith("## "):
            i += 1
            continue

        if stripped:
            current_paragraphs.append(stripped)

        i += 1

    commit_section()

    cat_id = categorize_book(title)

    return {
        "title": title,
        "category": cat_id,
        "meta_chips": meta_chips,
        "toc_links": toc_links,
        "sections": sections
    }

def update_markdown_source(md_path: Path, parsed: dict):
    """Updates original markdown file with cleanly formatted paragraphs and subheads."""
    lines = []
    lines.append(f"# {parsed['title']}\n")
    if parsed["meta_chips"]:
        meta_str = " | ".join([f"**{m}**" for m in parsed["meta_chips"]])
        lines.append(f"> {meta_str}\n")

    lines.append("## 目錄 (Table of Contents)\n")
    for sec in parsed["sections"]:
        lines.append(f"- [{sec['time']}](#{sec['id']})")
    lines.append("\n---\n")

    lines.append("## 逐字稿與筆記\n")
    for sec in parsed["sections"]:
        lines.append(f'<a id="{sec["id"]}"></a>')
        lines.append(f'### ⏱️ [{sec["time"]}]\n')
        for p in sec["paragraphs"]:
            if p.startswith("###SUBHEAD###"):
                sub_title = p[len("###SUBHEAD###"):].strip()
                lines.append(f"#### {sub_title}\n")
            else:
                lines.append(f"{p}\n")
        lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")

def render_book_html(book_data: dict) -> str:
    """Renders structured book data into complete self-contained HTML."""
    book_title = html.escape(book_data["title"])
    sections = book_data["sections"]
    section_count = len(sections)
    cat_id = book_data["category"]
    cat_meta = CATEGORIES[cat_id]

    toc_items_html = []
    for sec in sections:
        sec_id = html.escape(sec["id"])
        sec_time = html.escape(sec["time"])
        toc_items_html.append(
            f'<li class="toc-item"><a href="#{sec_id}">⏱️ {sec_time}</a></li>'
        )
    toc_html = "\n".join(toc_items_html)

    chips_html = []
    for chip in book_data["meta_chips"]:
        chips_html.append(f'<span class="meta-chip">🏷️ {html.escape(chip)}</span>')
    if not chips_html:
        chips_html.append(f'<span class="meta-chip">📑 章節小節：{section_count} 節</span>')
    meta_chips_html = "\n".join(chips_html)

    content_parts = []
    for sec in sections:
        sec_id = html.escape(sec["id"])
        sec_time = html.escape(sec["time"])

        body_elements = []
        for p in sec["paragraphs"]:
            if p.startswith("###SUBHEAD###"):
                sub_title = html.escape(p[len("###SUBHEAD###"):].strip())
                body_elements.append(f'<h4 class="section-subhead">{sub_title}</h4>')
            else:
                p_text = html.escape(p)
                body_elements.append(f'<p class="prose-p">{p_text}</p>')

        p_html = "\n".join(body_elements)

        sec_block = f"""
        <section class="transcript-section" id="{sec_id}">
          <div class="section-header">
            <span class="section-time">⏱️ {sec_time}</span>
            <span class="section-badge">有聲書逐字學習段落</span>
          </div>
          <div class="section-body">
            {p_html}
          </div>
        </section>
        """
        content_parts.append(sec_block)
    content_html = "\n".join(content_parts)

    return HTML_EBOOK_TEMPLATE.format(
        book_title=book_title,
        section_count=section_count,
        cat_icon=cat_meta["icon"],
        cat_name=cat_meta["name"],
        cat_color=cat_meta["color"],
        toc_html=toc_html,
        meta_chips_html=meta_chips_html,
        content_html=content_html
    )

def main():
    root_dir = Path(__file__).resolve().parent
    input_dir = root_dir / "audiobook_md"
    output_dir = root_dir / "docs"
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / ".nojekyll").write_text("", encoding="utf-8")

    if not input_dir.exists():
        print(f"錯誤：找不到目錄 {input_dir}")
        return

    md_files = sorted(list(input_dir.glob("*.md")))
    print(f"📚 找到 {len(md_files)} 個 Markdown 檔案，開始進行段落增強、搜尋索引構建與 HTML 渲染...")

    books_catalog = []
    search_index_data = []
    total_sections_count = 0

    for idx, md_path in enumerate(md_files, 1):
        try:
            parsed = parse_markdown_audiobook(md_path)
            update_markdown_source(md_path, parsed)

            book_html = render_book_html(parsed)

            safe_filename = md_path.stem.strip()
            for char in r'<>:"/\|?*':
                safe_filename = safe_filename.replace(char, "_")
            out_html_path = output_dir / f"{safe_filename}.html"
            out_html_path.write_text(book_html, encoding="utf-8")

            sec_cnt = len(parsed["sections"])
            total_sections_count += sec_cnt
            cat_id = parsed["category"]

            books_catalog.append({
                "id": idx - 1,
                "title": parsed["title"],
                "file": out_html_path.name,
                "category": cat_id,
                "sections": sec_cnt,
                "meta": parsed["meta_chips"]
            })

            # Build search index for this book
            clean_sections = []
            for sec in parsed["sections"]:
                plain_body = " ".join([
                    p[len("###SUBHEAD###"):].strip() if p.startswith("###SUBHEAD###") else p
                    for p in sec["paragraphs"]
                ])
                clean_sections.append({
                    "id": sec["id"],
                    "time": sec["time"],
                    "text": plain_body
                })

            search_index_data.append({
                "file": out_html_path.name,
                "title": parsed["title"],
                "category": cat_id,
                "sections": clean_sections
            })

            print(f"[{idx:02d}/{len(md_files):02d}] ✅ 成功處理: {out_html_path.name} ({sec_cnt} 小節 | {CATEGORIES[cat_id]['name']})")
        except Exception as e:
            print(f"[{idx:02d}/{len(md_files):02d}] ❌ 處理失敗 {md_path.name}: {e}")

    # Write global search index json
    search_index_path = output_dir / "search_index.json"
    search_index_path.write_text(json.dumps(search_index_data, ensure_ascii=False), encoding="utf-8")
    print(f"🔍 全庫全文檢索索引已生成: {search_index_path} ({search_index_path.stat().st_size / (1024*1024):.2f} MB)")

    # Build Graph Data (Nodes + Edges)
    graph_nodes = []
    graph_edges = []

    # 1. Add Category Hub Nodes
    for cat_id, cat_meta in CATEGORIES.items():
        hub_id = f"hub_{cat_id}"
        graph_nodes.append({
            "id": hub_id,
            "title": f"{cat_meta['icon']} {cat_meta['name']}",
            "shortTitle": cat_meta['name'],
            "cat": cat_id,
            "catName": cat_meta['name'],
            "color": cat_meta['color'],
            "isHub": True,
            "file": "#"
        })

    # 2. Add Book Nodes and Link to Category Hubs
    for b in books_catalog:
        node_id = f"book_{b['id']}"
        cat_meta = CATEGORIES[b['category']]
        graph_nodes.append({
            "id": node_id,
            "title": b['title'],
            "shortTitle": b['title'][:16] + ('...' if len(b['title']) > 16 else ''),
            "cat": b['category'],
            "catName": cat_meta['name'],
            "color": cat_meta['color'],
            "isHub": False,
            "file": b['file'],
            "sections": b['sections']
        })
        # Edge to Hub
        graph_edges.append({
            "source": f"hub_{b['category']}",
            "target": node_id,
            "isThematic": False
        })

    # 3. Add Cross-Thematic Knowledge Edges
    for theme_label, book_pair_keywords in CROSS_THEMATIC_LINKS:
        kw1, kw2 = book_pair_keywords[0].lower(), book_pair_keywords[1].lower()
        matched1 = [b for b in books_catalog if kw1 in b['title'].lower()]
        matched2 = [b for b in books_catalog if kw2 in b['title'].lower()]
        for b1 in matched1:
            for b2 in matched2:
                if b1['id'] != b2['id']:
                    graph_edges.append({
                        "source": f"book_{b1['id']}",
                        "target": f"book_{b2['id']}",
                        "label": theme_label,
                        "isThematic": True
                    })

    graph_data_json = json.dumps({"nodes": graph_nodes, "edges": graph_edges}, ensure_ascii=False)

    # Category Pill Buttons HTML for Bookshelf
    cat_pills = []
    for cat_id, cat_meta in CATEGORIES.items():
        count = sum(1 for b in books_catalog if b['category'] == cat_id)
        cat_pills.append(
            f'<button class="cat-pill" data-cat="{cat_id}">{cat_meta["icon"]} {cat_meta["name"]} ({count})</button>'
        )
    category_pills_html = "\n".join(cat_pills)

    # Category options for dropdown
    cat_options = []
    for cat_id, cat_meta in CATEGORIES.items():
        cat_options.append(f'<option value="{cat_id}">{cat_meta["icon"]} {cat_meta["name"]}</option>')
    graph_cat_options_html = "\n".join(cat_options)

    # Book Cards HTML for Catalog
    cards = []
    for b in books_catalog:
        cat_meta = CATEGORIES[b['category']]
        meta_spans = "".join([f'<span class="card-chip">{html.escape(m)}</span>' for m in b["meta"][:2]])
        card_html = f"""
        <a href="{html.escape(b['file'])}" class="book-card" data-title="{html.escape(b['title'])}" data-cat="{b['category']}">
          <div class="book-card-header">
            <span class="card-cat-badge" style="background: {cat_meta['color']}22; color: {cat_meta['color']};">
              {cat_meta['icon']} {cat_meta['name']}
            </span>
            <span class="card-chip">📑 {b['sections']} 節</span>
          </div>
          <div class="book-card-title">{html.escape(b['title'])}</div>
          <div class="book-card-meta">
            {meta_spans}
          </div>
        </a>
        """
        cards.append(card_html)

    shelf_html = INDEX_SHELF_TEMPLATE.format(
        total_books=len(books_catalog),
        total_sections=total_sections_count,
        category_pills_html=category_pills_html,
        graph_cat_options_html=graph_cat_options_html,
        cards_html="\n".join(cards),
        graph_data_json=graph_data_json
    )

    index_path = output_dir / "index.html"
    index_path.write_text(shelf_html, encoding="utf-8")
    print(f"\n🎉 全數完成！已生成包含 3 大頁籤與關聯圖譜之數位書架首頁: {index_path}")

if __name__ == "__main__":
    main()
