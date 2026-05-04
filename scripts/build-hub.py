#!/usr/bin/env python3
"""toshin-web-tools のハブページ群を再生成する。

入力データは本ファイル中の CHAPTERS dict。
出力:
    - ../index.html              (ルートハブ: 分野ブロック)
    - ../calculus/index.html     (微分積分編: 第1〜12回 章グリッド)
    - ../calculus/lesson-NN/index.html (12 章分のサブハブ)

ツール本体は ../tools/calculus/N-N.html に既に配置済み。
本スクリプトはハブから tools/ 配下のファイルへリンクするだけ。
"""

from pathlib import Path

CHAPTERS: dict[int, list[tuple[str | None, str]]] = {
    1: [
        ("1-1.html", "Adam 最適化の可視化"),
        ("1-2.html", "Adam 最適化の可視化(別版)"),
    ],
    2: [
        ("2-1.html", "逆三角関数 × ロボットアーム"),
    ],
    3: [
        ("3-1.html", "円錐曲線エクスプローラー"),
        ("3-2.html", "双曲線関数と AI"),
        ("3-3.html", "ε-δ 論法 比較"),
        (None,       "(節 3-4 / RTF 移植予定)"),
        ("3-5.html", "データサイエンス × 物理シミュ"),
    ],
    4: [
        ("4-1.html", "逆関数の微分"),
        ("4-2.html", "C² 連続性の重要性"),
        ("4-3.html", "平均値の定理の応用"),
        ("4-4.html", "マクローリン展開"),
    ],
    5: [
        ("5-1.html", "マクローリン展開(別版)"),
        ("5-2.html", "テイラー展開"),
        ("5-3.html", "ランダウ記号 o(x)"),
        ("5-4.html", "コーシー列:狭まる区間"),
        (None,       "(節 5-5 / RTF 移植予定)"),
        (None,       "(節 5-6 / RTF 移植予定)"),
        (None,       "(節 5-7 / RTF 移植予定)"),
        ("5-8.html", "積分の正体 ② 傾きの場"),
    ],
    6: [
        ("6-1.html", "カヴァリエリの原理"),
        (None,       "(節 6-2 / RTF 移植予定)"),
        ("6-3.html", "リーマン積分 vs ルベーグ積分"),
        ("6-4.html", "定積分ビジュアライザー"),
        ("6-5.html", "微分積分 × 車の動き"),
        ("6-6.html", "広義積分"),
    ],
    7: [
        ("7-1.html", "多変数関数イントロ"),
        ("7-2.html", "2 変数関数 学習サイト"),
        ("7-3.html", "2 変数関数 ビジュアライザー"),
        ("7-4.html", "2 変数関数の極限(3D)"),
        ("7-5.html", "f(x,y)=x^y の極限"),
    ],
    8: [
        ("8-1.html", "偏微分ビジュアライザー"),
        ("8-2.html", "連続性と偏微分可能性"),
        ("8-3.html", "時間による偏微分"),
        (None,       "(節 8-4 / RTF 移植予定)"),
        ("8-5.html", "データサイエンスの数理"),
        ("8-6.html", "拡散モデル"),
    ],
    9: [
        ("9-1.html", "楕円放物面の勾配"),
    ],
    10: [],
    11: [],
    12: [],
}

TOTAL_PUBLISHED = sum(1 for c in CHAPTERS.values() for f, _ in c if f)

FONT_LINK = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Zen+Old+Mincho:wght@500;700;900&family=Zen+Kaku+Gothic+New:wght@300;400;500;700&family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,800;1,9..144,400;1,9..144,600&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">"""

FOOTER = """<footer>
  <div>© toshin-web-tools — built with care for learners.</div>
  <div style="margin-top: 0.75rem;">
    <a href="https://github.com/mikikof/toshin-web-tools">GitHub</a>
  </div>
</footer>"""


def render_root() -> str:
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>toshin-web-tools — 受験数学の Web ツール集</title>
<meta name="description" content="受験数学の Web ツール集。微分積分学編 全 {TOTAL_PUBLISHED} ツール公開中。">
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
    <div class="fields-meta">{TOTAL_PUBLISHED} TOOLS PUBLISHED</div>
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
        <span>{TOTAL_PUBLISHED} TOOLS / 12 LESSONS</span>
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


def render_calculus_index() -> str:
    cards = []
    for n in range(1, 13):
        sections = CHAPTERS[n]
        published = [s for s in sections if s[0]]
        coming = [s for s in sections if not s[0]]
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
<meta name="description" content="微分積分学の Web ツール集(全 12 回 / {TOTAL_PUBLISHED} ツール公開中)。極限・微分・積分の基礎から、データサイエンスへの接続まで。">
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
      現在 <strong>{TOTAL_PUBLISHED} ツール</strong> 公開中。
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


def render_lesson(n: int) -> str:
    sections = CHAPTERS[n]
    if not sections:
        body = """  <div class="lesson-placeholder">
    第 {n} 回は準備中です。<br>
    第 1 〜 9 回 のツールは公開中。
  </div>""".format(n=n)
    else:
        items = []
        for filename, short in sections:
            if filename:
                # 章番号で短縮表示
                section_label = filename.replace(".html", "")
                items.append(f"""    <a href="../../tools/calculus/{filename}" class="lesson-card" target="_blank" rel="noopener">
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
    base = Path(__file__).resolve().parent.parent
    (base / "index.html").write_text(render_root(), encoding="utf-8")
    (base / "calculus/index.html").write_text(render_calculus_index(), encoding="utf-8")
    for n in range(1, 13):
        out = base / f"calculus/lesson-{n:02d}/index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_lesson(n), encoding="utf-8")
    print(f"✓ Generated: index.html + calculus/index.html + 12 lesson pages")
    print(f"  Total tools published: {TOTAL_PUBLISHED}")


if __name__ == "__main__":
    main()
