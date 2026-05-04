#!/usr/bin/env python3
"""toshin-web-tools のハブページ群を再生成する(データ駆動)。

入力:
    data/chapters.json        ← 章節構造のシングルソース
出力:
    ../index.html              (ルートハブ: 分野ブロック)
    ../calculus/index.html     (微分積分編: 第1〜12回 章グリッド)
    ../calculus/lesson-NN/index.html (12 章分のサブハブ)

ツール本体は ../tools/calculus/N-N.html に配置済み。
本スクリプトはハブから tools/ 配下のファイルへリンクするだけ。

new-tool.py を経由しない手動編集も可:
    1. data/chapters.json を編集
    2. python3 scripts/build-hub.py
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data/chapters.json"


def load_data() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def total_published(data: dict) -> int:
    n = 0
    for field in data.values():
        for chap_sections in field["chapters"].values():
            for s in chap_sections:
                if s.get("file"):
                    n += 1
    return n


FONT_LINK = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Zen+Old+Mincho:wght@500;700;900&family=Zen+Kaku+Gothic+New:wght@300;400;500;700&family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,800;1,9..144,400;1,9..144,600&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">"""

FOOTER = """<footer>
  <div>© toshin-web-tools — built with care for learners.</div>
  <div style="margin-top: 0.75rem;">
    <a href="https://github.com/mikikof/toshin-web-tools">GitHub</a>
  </div>
</footer>"""


def render_root(data: dict, total: int) -> str:
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>toshin-web-tools — 受験数学の Web ツール集</title>
<meta name="description" content="受験数学の Web ツール集。微分積分学編 全 {total} ツール公開中。">
{FONT_LINK}
<link rel="stylesheet" href="assets/style.css">
</head>
<body>

<section class="hero">
  <div class="hero-kicker">Mathematics Web Tools</div>
  <h1 class="hero-title">toshin<span class="dot">.</span>web-tools</h1>
  <div class="hero-sub-jp">受験数学の Web ツール集</div>
  <p class="hero-lede">
    数学の概念は、<strong>動かして・触って</strong>理解するほど深く根付きます。
    このサイトでは、微分積分学をはじめとする受験数学の単元ごとに、
    ブラウザで直接動かせる Web ツールを公開していきます。
  </p>
</section>

<section class="fields">
  <div class="fields-head">
    <h2 class="fields-title">分野<span class="en">Fields</span></h2>
    <div class="fields-meta">{total} TOOLS PUBLISHED</div>
  </div>
  <div class="fields-grid">

    <a href="calculus/" class="field-card calculus">
      <div class="field-tag">Field 01</div>
      <div class="field-name">微分積分学編</div>
      <div class="field-name-en">Calculus</div>
      <p class="field-desc">
        極限・微分・積分の基礎から、データサイエンスへの接続まで。
        全 12 回の単元に沿って、Web ツールで「何に・どのように使われるか」を体感します。
      </p>
      <div class="field-meta">
        <span>{total} TOOLS / 12 LESSONS</span>
        <span>→</span>
      </div>
    </a>

    <div class="field-card linear coming">
      <div class="field-tag">Field 02</div>
      <div class="field-name">線形代数編</div>
      <div class="field-name-en">Linear Algebra</div>
      <p class="field-desc">
        ベクトル・行列・線形写像・固有値。学習ノートは別途公開中。
        Web ツール版を準備しています。
      </p>
      <div class="field-meta">
        <span>COMING SOON</span>
        <span></span>
      </div>
    </div>

  </div>
</section>

{FOOTER}

</body>
</html>
"""


def render_calculus_index(data: dict, total: int) -> str:
    chapters = data["calculus"]["chapters"]
    cards = []
    for n_str in sorted(chapters.keys(), key=int):
        n = int(n_str)
        sections = chapters[n_str]
        published = [s for s in sections if s.get("file")]
        coming = [s for s in sections if not s.get("file")]
        if published:
            count_text = f"{len(published)} TOOL" + ("S" if len(published) > 1 else "")
            if coming:
                count_text += f" / +{len(coming)} 移植予定"
            status_class = ""
        else:
            count_text = "COMING SOON"
            status_class = " placeholder"
        cards.append(f"""    <a href="lesson-{n:02d}/" class="lesson-card{status_class}">
      <div class="lesson-num">Lesson {n:02d}</div>
      <div class="lesson-title">第 {n} 回</div>
      <div class="lesson-status">{count_text}</div>
    </a>""")
    cards_html = "\n".join(cards)

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>微分積分学編 — toshin-web-tools</title>
<meta name="description" content="微分積分学の Web ツール集(全 12 回 / {total} ツール公開中)。">
{FONT_LINK}
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>

<section class="lessons">
  <a href="../" class="lesson-back">← toshin-web-tools</a>

  <div class="lessons-head">
    <div class="lessons-kicker">Field 01</div>
    <h1 class="lessons-title">微分積分学編<span class="en">Calculus</span></h1>
    <p class="lessons-lede">
      極限・微分・積分の基礎から、データサイエンスへの接続まで。
      全 12 回の単元に沿って、Web ツールで「何に・どのように使われるか」を体感します。
      現在 <strong>{total} ツール</strong> 公開中。
    </p>
  </div>

  <div class="lessons-grid">
{cards_html}
  </div>
</section>

{FOOTER}

</body>
</html>
"""


def render_lesson(n: int, sections: list[dict]) -> str:
    if not sections:
        body = f"""  <div class="lesson-placeholder">
    第 {n} 回は準備中です。<br>
    第 1 〜 9 回 のツールは公開中。
  </div>"""
    else:
        items = []
        for s in sections:
            f = s.get("file")
            short = s.get("title", "")
            if f:
                section_label = f.replace(".html", "")
                items.append(f"""    <a href="../../tools/calculus/{f}" class="lesson-card" target="_blank" rel="noopener">
      <div class="lesson-num">{section_label}</div>
      <div class="lesson-title">{short}</div>
      <div class="lesson-status">↗ ツールを開く</div>
    </a>""")
            else:
                items.append(f"""    <div class="lesson-card placeholder">
      <div class="lesson-num">—</div>
      <div class="lesson-title">{short}</div>
      <div class="lesson-status">準備中</div>
    </div>""")
        body = f"""  <div class="lessons-grid">
{chr(10).join(items)}
  </div>"""

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>第 {n} 回 — 微分積分学編 | toshin-web-tools</title>
{FONT_LINK}
<link rel="stylesheet" href="../../assets/style.css">
</head>
<body>

<section class="lessons">
  <a href="../" class="lesson-back">← 微分積分学編</a>

  <div class="lessons-head">
    <div class="lessons-kicker">Lesson {n:02d}</div>
    <h1 class="lessons-title">第 {n} 回<span class="en">Calculus / Lesson {n:02d}</span></h1>
  </div>

{body}
</section>

{FOOTER}

</body>
</html>
"""


def main():
    data = load_data()
    total = total_published(data)
    (BASE / "index.html").write_text(render_root(data, total), encoding="utf-8")
    (BASE / "calculus/index.html").write_text(render_calculus_index(data, total), encoding="utf-8")
    chapters = data["calculus"]["chapters"]
    chap_count = data["calculus"].get("chapter_count", 12)
    for n in range(1, chap_count + 1):
        sections = chapters.get(str(n), [])
        out = BASE / f"calculus/lesson-{n:02d}/index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_lesson(n, sections), encoding="utf-8")
    print(f"✓ Generated: index.html + calculus/index.html + {chap_count} lesson pages")
    print(f"  Total tools published: {total}")


if __name__ == "__main__":
    main()
