#!/usr/bin/env python3
"""toshin-web-tools のハブページ群を再生成する(データ駆動、rev3 デザイン強化版)。

入力:
    data/chapters.json        ← 章節構造のシングルソース(章名・英語サブタイ・色・説明・節リスト)
出力:
    ../index.html              (ルート: ヒーロー + Field 01 章 1-9 大カード + 章 10-12 roadmap + Field 02 preview + フッター)
    ../calculus/index.html     (微分積分編 詳細: 各章 + 章内全節を 1 ページで)
    ../calculus/lesson-NN/index.html (12 章分のサブハブ: 章カラー継承)

rev3 適用:
- 全 user-controllable string に html.escape を適用(href, class 含む)
- color は whitelist 検証(class injection 対策)
- hero に薄い数学装飾 SVG(関数曲線 + 等高線)
- hero stats 「N tools / N calculus lessons / 1 preview field」
- hero CTA 「START CALCULUS」
- coming 章 (10-12) は compact roadmap で別表示(通常カードと同サイズで並べない)
- status 表記「4 LIVE」「+1 PREP」に変更
- linear preview を 2 カラム(説明 + カード)で孤立感解消
- field-head に「VIEW ALL TOOLS →」リンクを追加可能に
"""

import json
import html
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data/chapters.json"

ALLOWED_COLORS = {
    "indigo", "coral", "navy", "teal", "purple",
    "amber", "cyan", "emerald", "rose", "gray",
}


def safe_color(c: str) -> str:
    """color が whitelist にあることを保証(class injection 対策)。"""
    return c if c in ALLOWED_COLORS else "gray"


def load_data() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def total_published(data: dict, field: str = "calculus") -> int:
    n = 0
    field_obj = data.get(field, {})
    for chap_obj in field_obj.get("chapters", {}).values():
        for s in chap_obj.get("sections", []):
            if s.get("file"):
                n += 1
    return n


FONT_LINK = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Zen+Old+Mincho:wght@500;700;900&family=Zen+Kaku+Gothic+New:wght@300;400;500;700&family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,800;1,9..144,400;1,9..144,600&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">"""

HERO_DECO_SVG = """<div class="hero-deco" aria-hidden="true">
  <svg viewBox="0 0 1200 800" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="curveGrad" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="#2e5cd6" stop-opacity="0"/>
        <stop offset="50%" stop-color="#2e5cd6" stop-opacity="0.5"/>
        <stop offset="100%" stop-color="#2e5cd6" stop-opacity="0"/>
      </linearGradient>
    </defs>
    <!-- 等高線の楕円 -->
    <ellipse cx="600" cy="400" rx="540" ry="280" fill="none" stroke="#1e3a8a" stroke-opacity="0.05" stroke-width="1"/>
    <ellipse cx="600" cy="400" rx="440" ry="220" fill="none" stroke="#1e3a8a" stroke-opacity="0.06" stroke-width="1"/>
    <ellipse cx="600" cy="400" rx="340" ry="170" fill="none" stroke="#1e3a8a" stroke-opacity="0.07" stroke-width="1"/>
    <ellipse cx="600" cy="400" rx="240" ry="120" fill="none" stroke="#1e3a8a" stroke-opacity="0.08" stroke-width="1"/>
    <ellipse cx="600" cy="400" rx="140" ry="70"  fill="none" stroke="#1e3a8a" stroke-opacity="0.10" stroke-width="1"/>
    <!-- sin 曲線 -->
    <path d="M 0 400 Q 150 250, 300 400 T 600 400 T 900 400 T 1200 400" fill="none" stroke="url(#curveGrad)" stroke-width="1.5"/>
    <!-- 微分ベクトル(矢印 4 個) -->
    <g stroke="#d9451c" stroke-opacity="0.18" stroke-width="1" fill="none">
      <path d="M 200 380 L 240 350" marker-end="url(#arrowhead)"/>
      <path d="M 500 320 L 540 305"/>
      <path d="M 800 380 L 840 410"/>
      <path d="M 1050 460 L 1080 440"/>
    </g>
    <!-- 積分の塗りつぶし(右下に小さく) -->
    <path d="M 850 600 Q 950 500, 1050 580 L 1050 650 L 850 650 Z" fill="#0f766e" fill-opacity="0.04"/>
  </svg>
</div>"""


def render_footer(prefix: str = "") -> str:
    return f"""<footer class="footer">
  <div class="footer-mark">toshin<span class="dot">.</span>web-tools</div>
  <div class="footer-tag">受験数学のWebツール集</div>
  <div class="footer-meta">© 2026 mikikof — MIT License</div>
  <div class="footer-link">
    <a href="{html.escape(prefix, quote=True)}">home</a>
    <a href="https://github.com/mikikof/toshin-web-tools">github / source</a>
    <a href="https://github.com/mikikof/toshin-web-tools/blob/main/LICENSE">license</a>
  </div>
</footer>"""


def chapter_card_root(field: str, chap_num: int, chap_obj: dict) -> str:
    """ルート用の章カード(`live` のみ。coming は別途 roadmap で扱う)。"""
    sections = chap_obj.get("sections", [])
    published = sum(1 for s in sections if s.get("file"))
    coming = sum(1 for s in sections if not s.get("file"))
    name = html.escape(chap_obj.get("name", f"第 {chap_num} 回"))
    name_en = html.escape(chap_obj.get("name_en", ""))
    description = html.escape(chap_obj.get("description", ""))
    color = safe_color(chap_obj.get("color", "gray"))
    field_safe = html.escape(field, quote=True)

    # status 表記改善: 「4 LIVE / +1 PREP」風
    if published > 0:
        status_label = f"{published} LIVE"
        if coming > 0:
            status_label += f" / +{coming} PREP"
        status_class = "live"
        cta = "OPEN CHAPTER →"
    else:
        # ここに来るのは正規ではない(coming は roadmap で扱う)。安全のため fallback
        status_label = "COMING"
        status_class = "coming"
        cta = "PREPARING …"

    href = f"{field_safe}/lesson-{chap_num:02d}/"
    return f"""    <a href="{href}" class="chapter-card chap-{color}">
      <div class="chapter-meta">
        <span class="chapter-num">{chap_num:02d}</span>
        <span class="chapter-status {status_class}">{html.escape(status_label)}</span>
      </div>
      <div class="chapter-name">{name}</div>
      <div class="chapter-en">{name_en}</div>
      <p class="chapter-desc">{description}</p>
      <div class="chapter-cta">{cta}</div>
    </a>"""


def coming_roadmap(coming_chaps: list) -> str:
    """章 10-12 の coming 章を compact な roadmap で表示。"""
    if not coming_chaps:
        return ""
    items = []
    for chap_num, chap_obj in coming_chaps:
        name = html.escape(chap_obj.get("name", "(準備中)"))
        items.append(
            f'<span class="coming-roadmap-item"><span class="num">{chap_num:02d}</span>{name}</span>'
        )
    items_html = "\n          ".join(items)
    return f"""  <div class="coming-roadmap" aria-label="準備中の章">
    <div class="coming-roadmap-head">
      <span class="coming-roadmap-title">Coming Next</span>
      <span class="coming-roadmap-meta">{len(coming_chaps)} CHAPTERS IN PREPARATION</span>
    </div>
    <div class="coming-roadmap-list">
      {items_html}
    </div>
  </div>"""


def linear_preview_block(linear_obj: dict) -> str:
    """線形代数編 preview を 2 カラム(説明 + カード)で表示(孤立感を解消)。"""
    chapters = linear_obj.get("chapters", {})
    title = html.escape(linear_obj.get("title", "線形代数学編"))
    title_en = html.escape(linear_obj.get("title_en", "Linear Algebra"))
    tagline = html.escape(linear_obj.get("tagline", ""))

    # preview card
    if chapters:
        first_chap = next(iter(chapters.values()))
        chap_name = html.escape(first_chap.get("name", title))
        chap_name_en = html.escape(first_chap.get("name_en", title_en))
        chap_desc = html.escape(first_chap.get("description", ""))
        color = safe_color(first_chap.get("color", "purple"))
        sections = first_chap.get("sections", [])
        first_section = next((s for s in sections if s.get("file")), None)
        if first_section:
            file_safe = html.escape(first_section["file"], quote=True)
            href = f"tools/linear/{file_safe}"
            target_attr = ' target="_blank" rel="noopener"'
            cta = "↗ OPEN PREVIEW"
        else:
            href = "#"
            target_attr = ""
            cta = "PREPARING …"
        card = f"""<a href="{href}" class="chapter-card chap-{color}"{target_attr}>
        <div class="chapter-meta">
          <span class="chapter-num">PREVIEW</span>
          <span class="chapter-status live">1 LIVE</span>
        </div>
        <div class="chapter-name">{chap_name}</div>
        <div class="chapter-en">{chap_name_en}</div>
        <p class="chapter-desc">{chap_desc}</p>
        <div class="chapter-cta">{cta}</div>
      </a>"""
    else:
        card = f"""<div class="chapter-card chap-gray coming">
        <div class="chapter-meta"><span class="chapter-num">02</span><span class="chapter-status coming">COMING</span></div>
        <div class="chapter-name">{title}</div>
        <div class="chapter-en">{title_en}</div>
        <p class="chapter-desc">{tagline}</p>
        <div class="chapter-cta">PREPARING …</div>
      </div>"""

    return f"""  <div class="preview-layout">
    <div class="preview-blurb">
      <h3>線形代数学編は preview 中</h3>
      <p>{tagline}</p>
      <ul>
        <li>学習ノート(submodule: <code>toshin/線形代数</code>)は別途公開中</li>
        <li>Web ツール版は React UMD のサンプル 1 件のみ</li>
        <li>受験生・大学生からのフィードバックを集めて 2026 年中に拡充予定</li>
      </ul>
    </div>
    <div>
      {card}
    </div>
  </div>"""


def render_root(data: dict) -> str:
    calc_total = total_published(data, "calculus")
    linear_total = total_published(data, "linear")
    grand_total = calc_total + linear_total

    calc = data["calculus"]
    chap_count = calc.get("chapter_count", 12)
    chapters = calc["chapters"]

    # 章 1-9 (live + prep を含む) と章 10-12 (空 = roadmap 行き) を分離
    main_chaps = []
    coming_chaps = []
    for n in range(1, chap_count + 1):
        chap_obj = chapters.get(str(n))
        if not chap_obj:
            continue
        sections = chap_obj.get("sections", [])
        if any(s.get("file") for s in sections):
            main_chaps.append((n, chap_obj))
        else:
            coming_chaps.append((n, chap_obj))

    main_html = "\n".join(chapter_card_root("calculus", n, c) for n, c in main_chaps)
    roadmap_html = coming_roadmap(coming_chaps)
    linear_block = linear_preview_block(data.get("linear", {}))

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>toshin-web-tools — 受験数学の Web ツール集</title>
<meta name="description" content="受験数学の Web ツール集。微分積分学編 全 {calc_total} ツール公開中。動かして・触って理解する数学。">
{FONT_LINK}
<link rel="stylesheet" href="assets/style.css">
</head>
<body>

<!-- ==================== HERO ==================== -->
<section class="hero">
  {HERO_DECO_SVG}
  <div class="hero-kicker">toshin · web-tools</div>
  <h1 class="hero-title">toshin<span class="dot">.</span>web-tools</h1>
  <div class="hero-sub-jp">受験数学のWebツール集</div>
  <p class="hero-lede">
    数学の概念は、<strong>動かして・触って</strong>理解するほど深く根付く。
    微分積分・線形代数の単元ごとに、ブラウザで直接動かせる Web ツールを公開。
  </p>
  <div class="hero-stats">
    <div class="hero-stat">
      <div class="hero-stat-num">{grand_total}</div>
      <div class="hero-stat-label">tools</div>
    </div>
    <div class="hero-stat">
      <div class="hero-stat-num">{calc.get("chapter_count", 12)}</div>
      <div class="hero-stat-label">calculus lessons</div>
    </div>
    <div class="hero-stat">
      <div class="hero-stat-num">1</div>
      <div class="hero-stat-label">preview field</div>
    </div>
  </div>
  <a href="#field-calculus" class="hero-cta">
    Start Calculus
    <span class="hero-cta-arrow">→</span>
  </a>
</section>

<!-- ==================== FIELD 01: CALCULUS ==================== -->
<section class="field" id="field-calculus">
  <div class="field-head">
    <h2 class="field-title">{html.escape(calc["title"])} <span class="en">{html.escape(calc.get("title_en", ""))}</span></h2>
    <div class="field-meta">
      <span style="margin-right: 1.5rem;">{calc.get("chapter_count", 12)} LESSONS / {calc_total} TOOLS</span>
      <a href="calculus/" class="field-head-link">VIEW ALL TOOLS <span>→</span></a>
    </div>
  </div>
  <p class="field-tagline">{html.escape(calc.get("tagline", ""))}</p>
  <div class="chapters-grid">
{main_html}
  </div>
{roadmap_html}
</section>

<!-- ==================== FIELD 02: LINEAR ALGEBRA(preview) ==================== -->
<section class="field field-preview" id="field-linear">
  <div class="field-head">
    <h2 class="field-title">{html.escape(data.get("linear", {}).get("title", "線形代数学編"))} <span class="en">{html.escape(data.get("linear", {}).get("title_en", "Linear Algebra"))}</span></h2>
    <div class="field-meta">PREVIEW / {linear_total} TOOL</div>
  </div>
{linear_block}
</section>

{render_footer("./")}

</body>
</html>
"""


def chapter_block_calc(chap_num: int, chap_obj: dict) -> str:
    """calculus/index.html 用の章ブロック(章ヘッダ + 章内全節グリッド)。"""
    sections = chap_obj.get("sections", [])
    name = html.escape(chap_obj.get("name", f"第 {chap_num} 回"))
    name_en = html.escape(chap_obj.get("name_en", ""))
    description = html.escape(chap_obj.get("description", ""))
    color = safe_color(chap_obj.get("color", "gray"))

    section_cards = []
    for s in sections:
        f = s.get("file")
        title = html.escape(s.get("title", ""))
        if f:
            file_safe = html.escape(f, quote=True)
            section_label = html.escape(f.replace(".html", ""))
            section_cards.append(f"""    <a href="../tools/calculus/{file_safe}" class="section-card" target="_blank" rel="noopener">
      <div class="section-num">{section_label}</div>
      <div class="section-title">{title}</div>
      <div class="section-cta">↗ OPEN TOOL</div>
    </a>""")
        else:
            section_cards.append(f"""    <div class="section-card placeholder">
      <div class="section-num">—</div>
      <div class="section-title">{title}</div>
      <div class="section-cta">PREPARING</div>
    </div>""")

    if not section_cards:
        sections_html = '    <div class="lesson-empty">この回は準備中です。</div>'
    else:
        sections_html = "\n".join(section_cards)

    return f"""<section class="lesson-page chap-{color}" style="padding: 2.5rem 0 1rem; max-width: none;">
  <div class="lesson-head" style="padding-bottom: 1.5rem; margin-bottom: 1.5rem;">
    <div class="lesson-kicker">Lesson {chap_num:02d}</div>
    <h2 class="lesson-title" style="font-size: clamp(1.6rem, 3.5vw, 2.2rem);">{name}<span class="en">{name_en}</span></h2>
    <p class="lesson-tagline">{description}</p>
  </div>
  <div class="sections-grid">
{sections_html}
  </div>
</section>"""


def render_calculus_index(data: dict) -> str:
    calc = data["calculus"]
    total = total_published(data, "calculus")

    chapters_html = "\n\n".join(
        chapter_block_calc(n, calc["chapters"][str(n)])
        for n in range(1, calc.get("chapter_count", 12) + 1)
        if str(n) in calc["chapters"]
    )

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(calc["title"])} — 全ツール一覧 | toshin-web-tools</title>
<meta name="description" content="{html.escape(calc["title"])}の Web ツール集(全 {calc.get("chapter_count", 12)} 回 / {total} ツール)。各章の節すべてを 1 ページで一覧。">
{FONT_LINK}
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>

<section class="calc-page">
  <a href="../" class="lesson-back">← toshin.web-tools</a>

  <div class="calc-head">
    <div class="calc-kicker">Field 01 — All Tools</div>
    <h1 class="calc-title">{html.escape(calc["title"])}<span class="en">{html.escape(calc.get("title_en", ""))}</span></h1>
    <p class="calc-tagline">
      {html.escape(calc.get("tagline", ""))}
      現在 <strong>{total} ツール</strong> / 全 <strong>{calc.get("chapter_count", 12)} 回</strong> 公開中。各章の節すべてを 1 ページで横断的に。
    </p>
  </div>

{chapters_html}

</section>

{render_footer("../")}

</body>
</html>
"""


def render_lesson(field: str, chap_num: int, chap_obj: dict) -> str:
    """lesson-NN/index.html: 章サブハブ。"""
    sections = chap_obj.get("sections", [])
    name = html.escape(chap_obj.get("name", f"第 {chap_num} 回"))
    name_en = html.escape(chap_obj.get("name_en", ""))
    description = html.escape(chap_obj.get("description", ""))
    color = safe_color(chap_obj.get("color", "gray"))
    field_safe = html.escape(field, quote=True)

    section_cards = []
    for s in sections:
        f = s.get("file")
        title = html.escape(s.get("title", ""))
        if f:
            file_safe = html.escape(f, quote=True)
            section_label = html.escape(f.replace(".html", ""))
            section_cards.append(f"""    <a href="../../tools/{field_safe}/{file_safe}" class="section-card" target="_blank" rel="noopener">
      <div class="section-num">{section_label}</div>
      <div class="section-title">{title}</div>
      <div class="section-cta">↗ OPEN TOOL</div>
    </a>""")
        else:
            section_cards.append(f"""    <div class="section-card placeholder">
      <div class="section-num">—</div>
      <div class="section-title">{title}</div>
      <div class="section-cta">PREPARING</div>
    </div>""")

    if not section_cards:
        body = f"""  <div class="lesson-empty">
    第 {chap_num} 回は準備中です。<br>
    他の回のツールをお試しください。
  </div>"""
    else:
        body = f"""  <div class="sections-grid">
{chr(10).join(section_cards)}
  </div>"""

    field_title_en = "Calculus" if field == "calculus" else "Linear Algebra"

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>第 {chap_num} 回 {name} — toshin-web-tools</title>
<meta name="description" content="{name}: {description}">
{FONT_LINK}
<link rel="stylesheet" href="../../assets/style.css">
</head>
<body>

<section class="lesson-page chap-{color}">
  <a href="../" class="lesson-back">← {html.escape(field_title_en)}</a>

  <div class="lesson-head">
    <div class="lesson-kicker">Lesson {chap_num:02d}</div>
    <h1 class="lesson-title">{name}<span class="en">{name_en}</span></h1>
    <p class="lesson-tagline"><strong>{name_en}</strong> — {description}</p>
  </div>

{body}
</section>

{render_footer("../../")}

</body>
</html>
"""


def main():
    data = load_data()
    calc_total = total_published(data, "calculus")
    chap_count = data["calculus"].get("chapter_count", 12)

    (BASE / "index.html").write_text(render_root(data), encoding="utf-8")
    (BASE / "calculus/index.html").write_text(render_calculus_index(data), encoding="utf-8")

    chapters = data["calculus"]["chapters"]
    for n in range(1, chap_count + 1):
        chap_obj = chapters.get(str(n), {"sections": []})
        out = BASE / f"calculus/lesson-{n:02d}/index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_lesson("calculus", n, chap_obj), encoding="utf-8")

    print(f"✓ Generated: index.html + calculus/index.html + {chap_count} lesson pages")
    print(f"  Total tools published (calculus): {calc_total}")


if __name__ == "__main__":
    main()
