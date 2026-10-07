#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audiobook Markdown to Standalone HTML eBook Reader Generator
Transforms transcribed markdown study notes into beautiful, responsive, offline-ready HTML eBooks.
"""

import os
import re
import html
import sys
from pathlib import Path

# Fix Windows console UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

HTML_EBOOK_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-Hant" data-theme="light">
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
      --line-height: 1.85;
      --content-max-width: 820px;
      --sidebar-width: 320px;
      --bg-primary: #fcfcfd;
      --bg-surface: #ffffff;
      --bg-sidebar: #f8f9fa;
      --bg-header: rgba(255, 255, 255, 0.92);
      --text-primary: #1f2328;
      --text-secondary: #57606a;
      --text-muted: #8c959f;
      --border-color: #e1e4e8;
      --accent-color: #2563eb;
      --accent-hover: #1d4ed8;
      --accent-light: #eff6ff;
      --badge-bg: #e0f2fe;
      --badge-text: #0369a1;
      --card-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03);
    }}

    [data-theme="sepia"] {{
      --bg-primary: #fbf0d9;
      --bg-surface: #f4e8cf;
      --bg-sidebar: #efe3c7;
      --bg-header: rgba(244, 232, 207, 0.94);
      --text-primary: #433422;
      --text-secondary: #6e583f;
      --text-muted: #957d60;
      --border-color: #e3d3b4;
      --accent-color: #92400e;
      --accent-hover: #78350f;
      --accent-light: #fbeacf;
      --badge-bg: #ead8b8;
      --badge-text: #6b4012;
      --card-shadow: 0 1px 3px rgba(67, 52, 34, 0.08);
    }}

    [data-theme="dark"] {{
      --bg-primary: #0f172a;
      --bg-surface: #1e293b;
      --bg-sidebar: #131c31;
      --bg-header: rgba(30, 41, 59, 0.92);
      --text-primary: #f1f5f9;
      --text-secondary: #94a3b8;
      --text-muted: #64748b;
      --border-color: #334155;
      --accent-color: #38bdf8;
      --accent-hover: #7dd3fc;
      --accent-light: #1e3a5f;
      --badge-bg: #1e293b;
      --badge-text: #38bdf8;
      --card-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    html {{
      scroll-behavior: smooth;
    }}

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
      padding: 0 20px;
      background-color: var(--bg-header);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      border-bottom: 1px solid var(--border-color);
    }}

    .header-left, .header-right {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .btn-icon {{
      background: none;
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      cursor: pointer;
      font-size: 15px;
      padding: 6px 12px;
      border-radius: 8px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
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
      font-size: 15px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .home-link:hover {{
      color: var(--accent-color);
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
    .toc-search:focus {{
      outline: 2px solid var(--accent-color);
    }}

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

    /* Book Hero / Header */
    .book-hero {{
      margin-bottom: 40px;
      padding-bottom: 24px;
      border-bottom: 2px solid var(--border-color);
    }}

    .book-hero h1 {{
      font-size: 2.1em;
      line-height: 1.3;
      margin-bottom: 16px;
      color: var(--text-primary);
      font-weight: 800;
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

    /* Content Typography */
    .transcript-section {{
      margin-bottom: 44px;
      scroll-margin-top: 80px;
      padding-top: 10px;
    }}

    .section-header {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 16px;
      padding: 8px 12px;
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

    .section-body {{
      text-align: justify;
      hyphens: auto;
    }}

    .section-body p {{
      margin-bottom: 1.25em;
      text-indent: 1.75em;
      letter-spacing: 0.01em;
    }}

    /* Floating Navigation Controls */
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

    /* Overlay for mobile drawer */
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

      .sidebar.open {{
        transform: translateX(0);
      }}

      .backdrop.open {{
        display: block;
      }}
    }}

    @media (max-width: 640px) {{
      :root {{
        --font-size: 17px;
      }}
      .main-content {{
        padding: 24px 16px 60px 16px;
      }}
      .book-hero h1 {{
        font-size: 1.6em;
      }}
      .top-header {{
        padding: 0 12px;
      }}
      .section-body p {{
        text-indent: 1.2em;
      }}
    }}
  </style>
</head>
<body>
  <div id="progress-bar"></div>

  <!-- Top Navigation -->
  <header class="top-header">
    <div class="header-left">
      <button class="btn-icon" id="toggle-sidebar-btn" title="切換目錄">
        📑 目錄
      </button>
      <a href="index.html" class="home-link" title="返回書架">
        🏠 書架
      </a>
    </div>

    <div class="header-right">
      <!-- Theme Switcher -->
      <button class="btn-icon" id="theme-btn" title="切換閱讀模式 (明亮/羊皮紙/暗黑)">
        🎨 <span>外觀</span>
      </button>

      <!-- Font Style Switcher -->
      <button class="btn-icon" id="font-family-btn" title="切換黑體/明體">
        🔤
      </button>

      <!-- Font Size Adjuster -->
      <button class="btn-icon" id="font-dec-btn" title="縮小字級">A-</button>
      <button class="btn-icon" id="font-inc-btn" title="放大字級">A+</button>
    </div>
  </header>

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
            {meta_chips_html}
          </div>
        </header>

        <!-- Transcript Content -->
        <div class="book-body">
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
      const span = document.querySelector('#theme-btn span');
      if (span) span.textContent = themeNames[theme].split(' ')[1];
    }}
    applyTheme(themes[currentThemeIdx]);

    document.getElementById('theme-btn').addEventListener('click', () => {{
      currentThemeIdx = (currentThemeIdx + 1) % themes.length;
      applyTheme(themes[currentThemeIdx]);
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

    // Close sidebar on item click (mobile)
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

      // Scroll spy: find current section
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

    // --- Scroll Top Button ---
    document.getElementById('scroll-top-btn').addEventListener('click', () => {{
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }});
  </script>
</body>
</html>
"""

INDEX_SHELF_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-Hant" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>有聲書數位圖書館 (Audiobook Digital Bookshelf)</title>
  <style>
    :root {{
      --bg-primary: #f8fafc;
      --bg-surface: #ffffff;
      --text-primary: #0f172a;
      --text-secondary: #475569;
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
      padding: 30px 20px 60px 20px;
      min-height: 100vh;
    }}

    .container {{
      max-width: 1200px;
      margin: 0 auto;
    }}

    header {{
      margin-bottom: 36px;
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
      font-size: 2.2rem;
      font-weight: 800;
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .theme-toggle {{
      padding: 8px 16px;
      border-radius: 8px;
      border: 1px solid var(--border-color);
      background: var(--bg-surface);
      color: var(--text-primary);
      cursor: pointer;
      font-weight: 500;
    }}

    .stats-bar {{
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
    }}

    .stat-badge {{
      background: var(--accent-light);
      color: var(--accent-color);
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 14px;
      font-weight: 600;
    }}

    /* Search & Filter Bar */
    .controls {{
      display: flex;
      gap: 12px;
      margin-bottom: 30px;
      flex-wrap: wrap;
    }}

    .search-input {{
      flex: 1;
      min-width: 260px;
      padding: 12px 18px;
      border: 1px solid var(--border-color);
      border-radius: 10px;
      font-size: 15px;
      background: var(--bg-surface);
      color: var(--text-primary);
    }}
    .search-input:focus {{
      outline: 2px solid var(--accent-color);
    }}

    /* Books Grid */
    .books-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
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
    }}

    .book-card:hover {{
      transform: translateY(-3px);
      box-shadow: var(--card-hover-shadow);
      border-color: var(--accent-color);
    }}

    .book-card-title {{
      font-size: 1.15rem;
      font-weight: 700;
      line-height: 1.4;
      margin-bottom: 14px;
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
        <span class="stat-badge">📖 書籍總數：<strong id="book-count">{total_books}</strong> 本</span>
        <span class="stat-badge">⏱️ 總章節小節數：<strong>{total_sections}</strong> 節</span>
        <span class="stat-badge">✨ 獨立離線閱讀器 (Single-file HTML)</span>
      </div>
    </header>

    <div class="controls">
      <input type="text" id="search-input" class="search-input" placeholder="🔍 搜尋書名、作者或關鍵字...">
    </div>

    <div class="books-grid" id="books-grid">
      {cards_html}
      <div class="no-results" id="no-results">無符合搜尋條件之書籍</div>
    </div>
  </div>

  <script>
    // Theme logic
    const themeBtn = document.getElementById('theme-btn');
    let isDark = localStorage.getItem('shelf-theme') === 'dark';
    function applyTheme() {{
      document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
      themeBtn.textContent = isDark ? '☀️ 切換淺色' : '🌙 切換深色';
      localStorage.setItem('shelf-theme', isDark ? 'dark' : 'light');
    }}
    applyTheme();
    themeBtn.addEventListener('click', () => {{
      isDark = !isDark;
      applyTheme();
    }});

    // Search filter
    const searchInput = document.getElementById('search-input');
    const cards = document.querySelectorAll('.book-card');
    const noResults = document.getElementById('no-results');
    const countBadge = document.getElementById('book-count');

    searchInput.addEventListener('input', (e) => {{
      const q = e.target.value.toLowerCase().trim();
      let matchCount = 0;
      cards.forEach(card => {{
        const title = card.getAttribute('data-title').toLowerCase();
        if (title.includes(q)) {{
          card.style.display = '';
          matchCount++;
        }} else {{
          card.style.display = 'none';
        }}
      }});
      noResults.style.display = matchCount === 0 ? 'block' : 'none';
      countBadge.textContent = matchCount;
    }});
  </script>
</body>
</html>
"""

def parse_markdown_audiobook(md_path: Path):
    """Parses an audiobook transcript markdown file into structured data."""
    text = md_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    title = md_path.stem
    meta_chips = []
    toc_links = []
    sections = []

    # 1. Extract Title if first header
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("# "):
            title = line[2:].strip()
            i += 1
            break
        i += 1

    # 2. Extract Metadata blockquote (e.g., > **時長**：`...`)
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith(">"):
            # Clean markdown formatting inside blockquote
            raw_meta = line.lstrip("> ").strip()
            # Split by | or find patterns
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
            body_text = "\n\n".join(current_paragraphs).strip()
            sections.append({
                "id": current_sec_id or f"sec-{len(sections):04d}",
                "time": current_sec_time or "段落內容",
                "body": body_text
            })
            current_paragraphs = []
            current_sec_id = ""
            current_sec_time = ""

    in_toc_area = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Check TOC section
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

        # Anchor tag check: <a id="sec-000000"></a>
        m_anchor = re.match(r'<a\s+id="([^"]+)"></a>', stripped)
        if m_anchor:
            commit_section()
            current_sec_id = m_anchor.group(1)
            i += 1
            continue

        # Header check: ### ⏱️ [00:00:00 - 00:05:01]
        m_head = re.match(r'^###\s*(?:⏱️)?\s*\[?([0-9: \-]+)\]?', stripped)
        if m_head:
            if not current_sec_id:
                commit_section()
            current_sec_time = m_head.group(1).strip()
            if not current_sec_id:
                # generate id from time
                clean_digits = re.sub(r'[^0-9]', '', current_sec_time)[:6]
                current_sec_id = f"sec-{clean_digits}" if clean_digits else f"sec-{len(sections):04d}"
            i += 1
            continue

        # Skip separator or main section divider
        if stripped == "---" or stripped.startswith("## 逐字稿與筆記") or stripped.startswith("## "):
            i += 1
            continue

        # Regular paragraph text
        if stripped:
            current_paragraphs.append(stripped)

        i += 1

    commit_section()

    return {
        "title": title,
        "meta_chips": meta_chips,
        "toc_links": toc_links,
        "sections": sections
    }

def render_book_html(book_data: dict) -> str:
    """Renders structured book data into complete self-contained HTML."""
    book_title = html.escape(book_data["title"])
    sections = book_data["sections"]
    section_count = len(sections)

    # 1. TOC HTML
    toc_items_html = []
    for sec in sections:
        sec_id = html.escape(sec["id"])
        sec_time = html.escape(sec["time"])
        toc_items_html.append(
            f'<li class="toc-item"><a href="#{sec_id}">⏱️ {sec_time}</a></li>'
        )
    toc_html = "\n".join(toc_items_html)

    # 2. Meta Chips HTML
    chips_html = []
    for chip in book_data["meta_chips"]:
        chips_html.append(f'<span class="meta-chip">🏷️ {html.escape(chip)}</span>')
    if not chips_html:
        chips_html.append(f'<span class="meta-chip">📑 章節小節：{section_count} 節</span>')
    meta_chips_html = "\n".join(chips_html)

    # 3. Content Sections HTML
    content_parts = []
    for sec in sections:
        sec_id = html.escape(sec["id"])
        sec_time = html.escape(sec["time"])
        paragraphs = sec["body"].split("\n\n")
        p_html = "".join([f"<p>{html.escape(p)}</p>" for p in paragraphs if p.strip()])

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
        toc_html=toc_html,
        meta_chips_html=meta_chips_html,
        content_html=content_html
    )

def main():
    root_dir = Path(__file__).resolve().parent
    input_dir = root_dir / "audiobook_md"
    output_dir = root_dir / "docs"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create .nojekyll for GitHub Pages compatibility
    (output_dir / ".nojekyll").write_text("", encoding="utf-8")

    if not input_dir.exists():
        print(f"錯誤：找不到目錄 {input_dir}")
        return

    md_files = sorted(list(input_dir.glob("*.md")))
    print(f"📚 找到 {len(md_files)} 個 Markdown 檔案，開始轉換為獨立 HTML 電子書至 docs/...")

    books_catalog = []
    total_sections_count = 0

    for idx, md_path in enumerate(md_files, 1):
        try:
            parsed = parse_markdown_audiobook(md_path)
            book_html = render_book_html(parsed)

            # Generate safe html filename
            safe_filename = md_path.stem.strip()
            # replace illegal filename chars
            for char in r'<>:"/\|?*':
                safe_filename = safe_filename.replace(char, "_")
            out_html_path = output_dir / f"{safe_filename}.html"
            out_html_path.write_text(book_html, encoding="utf-8")

            sec_cnt = len(parsed["sections"])
            total_sections_count += sec_cnt

            books_catalog.append({
                "title": parsed["title"],
                "file": out_html_path.name,
                "sections": sec_cnt,
                "meta": parsed["meta_chips"]
            })

            print(f"[{idx:02d}/{len(md_files):02d}] ✅ 成功渲染: {out_html_path.name} ({sec_cnt} 小節)")
        except Exception as e:
            print(f"[{idx:02d}/{len(md_files):02d}] ❌ 渲染失敗 {md_path.name}: {e}")

    # Generate Bookshelf index.html
    cards = []
    for b in books_catalog:
        meta_spans = "".join([f'<span class="card-chip">{html.escape(m)}</span>' for m in b["meta"][:2]])
        card_html = f"""
        <a href="{html.escape(b['file'])}" class="book-card" data-title="{html.escape(b['title'])}">
          <div class="book-card-title">{html.escape(b['title'])}</div>
          <div class="book-card-meta">
            <span class="card-chip">📑 {b['sections']} 節</span>
            {meta_spans}
          </div>
        </a>
        """
        cards.append(card_html)

    shelf_html = INDEX_SHELF_TEMPLATE.format(
        total_books=len(books_catalog),
        total_sections=total_sections_count,
        cards_html="\n".join(cards)
    )

    index_path = output_dir / "index.html"
    index_path.write_text(shelf_html, encoding="utf-8")
    print(f"\n🎉 全數完成！已生成數位書架首頁: {index_path}")

if __name__ == "__main__":
    main()
