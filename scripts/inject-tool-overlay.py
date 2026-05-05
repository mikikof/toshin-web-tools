#!/usr/bin/env python3
"""既存 33 ツール本体に toshin-web-tools Editorial オーバーレイを注入する(rev2)。

各ツール本体(tools/<field>/N-N.html)に対して以下を **冪等に** 挿入:

1. <html> に `class="journal-mode chap-COLOR"` を追加(または既存 class に追記)
2. <head> 末尾に `<link rel="stylesheet" href="../../assets/tool-overlay.css" data-toshin-overlay>` を追加
3. <body> 直後に上部 Editorial nav(kicker + brand + context + back)を挿入
4. </body> 直前に下部 Editorial footer(rule + mark + tag + links + meta)を挿入

冪等性: `data-toshin-overlay` 属性の有無で判定、既に注入済みのファイルはスキップ。
更新時は `--force` で再注入(古い注入を削除 → 最新版で再注入)。

Usage:
    python3 scripts/inject-tool-overlay.py            # 全ツールに注入
    python3 scripts/inject-tool-overlay.py --force    # 既存注入を更新
    python3 scripts/inject-tool-overlay.py --remove   # オーバーレイ削除
"""

import argparse
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

OVERLAY_LINK_TAG = '<link rel="stylesheet" href="../../assets/tool-overlay.css" data-toshin-overlay>'
OVERLAY_NAV_BEGIN = "<!-- TOSHIN_OVERLAY_NAV -->"
OVERLAY_NAV_END = "<!-- /TOSHIN_OVERLAY_NAV -->"
OVERLAY_FOOTER_BEGIN = "<!-- TOSHIN_OVERLAY_FOOTER -->"
OVERLAY_FOOTER_END = "<!-- /TOSHIN_OVERLAY_FOOTER -->"
OVERLAY_HTML_CLASS_MARK = "data-toshin-html"

ALLOWED_COLORS = {"indigo", "coral", "navy", "teal", "purple", "amber", "cyan", "emerald", "rose", "gray"}


def safe_color(c):
    return c if c in ALLOWED_COLORS else "gray"


def render_nav(home, back, back_label, chap_num, chap_name, chap_name_en):
    """Editorial 風 上部 nav."""
    if chap_num and chap_name:
        context = f"""    <div class="toshin-overlay-context">
      <div class="toshin-overlay-context-label">Lesson {chap_num:02d}</div>
      <div class="toshin-overlay-context-title">{chap_name} — {chap_name_en}</div>
    </div>"""
    else:
        context = '    <div class="toshin-overlay-context"></div>'
    return f"""{OVERLAY_NAV_BEGIN}
<nav class="toshin-overlay-nav" aria-label="toshin-web-tools navigation">
  <div class="toshin-overlay-nav-inner">
    <a href="{home}" class="toshin-overlay-brand-block">
      <span class="toshin-overlay-kicker">toshin · web-tools</span>
      <span class="toshin-overlay-brand">toshin<span class="dot">.</span>web-tools</span>
    </a>
{context}
    <a href="{back}" class="toshin-overlay-back">← {back_label}</a>
  </div>
</nav>
{OVERLAY_NAV_END}"""


def render_footer(home, back, back_label, chap_num):
    """Editorial 風 下部 footer."""
    chap_link = f'<a href="{back}">第 {chap_num} 回</a>' if chap_num else f'<a href="{back}">{back_label}</a>'
    return f"""{OVERLAY_FOOTER_BEGIN}
<footer class="toshin-overlay-footer">
  <div class="toshin-overlay-footer-mark">toshin<span class="dot">.</span>web-tools</div>
  <div class="toshin-overlay-footer-tag">受験数学のWebツール集 — Mathematics, made visible.</div>
  <div class="toshin-overlay-footer-link">
    <a href="{home}">home</a>
    {chap_link}
    <a href="{home}calculus/">all calculus</a>
    <a href="https://github.com/mikikof/toshin-web-tools">github</a>
  </div>
  <div class="toshin-overlay-footer-meta">© 2026 mikikof · MIT License · built with care for learners</div>
</footer>
{OVERLAY_FOOTER_END}"""


def remove_overlay(content):
    """注入された overlay を取り除く(冪等)。"""
    # link 行
    content = re.sub(
        r"^[ \t]*<link[^>]*data-toshin-overlay[^>]*>[ \t]*\n?",
        "",
        content,
        flags=re.MULTILINE,
    )
    # nav ブロック
    content = re.sub(
        re.escape(OVERLAY_NAV_BEGIN) + r".*?" + re.escape(OVERLAY_NAV_END) + r"\n?",
        "",
        content,
        flags=re.DOTALL,
    )
    # footer ブロック
    content = re.sub(
        re.escape(OVERLAY_FOOTER_BEGIN) + r".*?" + re.escape(OVERLAY_FOOTER_END) + r"\n?",
        "",
        content,
        flags=re.DOTALL,
    )
    # <html ... data-toshin-html="..."> の data-toshin-html と journal-mode 系 class を削除
    content = re.sub(
        r'(<html[^>]*?)\s*class="journal-mode chap-\w+"',
        r"\1",
        content,
    )
    content = re.sub(
        r'(<html[^>]*?)\s*data-toshin-html="[^"]*"',
        r"\1",
        content,
    )
    return content


def inject_overlay(content, home, back, back_label, chap_num, chap_name, chap_name_en, color):
    """新版オーバーレイを注入(content は既に古い overlay が remove された前提)。"""
    color = safe_color(color)

    # 1. <html> に class 追加
    def add_html_class(m):
        tag = m.group(0)
        # 既存 class があれば追記、なければ新規
        if "class=" in tag:
            tag = re.sub(
                r'class="([^"]*)"',
                lambda mm: f'class="{mm.group(1)} journal-mode chap-{color}"',
                tag,
                count=1,
            )
        else:
            tag = re.sub(
                r"<html",
                f'<html class="journal-mode chap-{color}"',
                tag,
                count=1,
            )
        # data-toshin-html マーカー
        if "data-toshin-html" not in tag:
            tag = tag.replace(">", f' data-toshin-html="{color}">', 1)
        return tag

    new_content, n_html = re.subn(r"<html[^>]*>", add_html_class, content, count=1)
    if n_html == 0:
        return None, "no_html_tag"

    # 2. <head> 末尾に link 追加
    new_content, n_head = re.subn(
        r"(</head>)",
        f"  {OVERLAY_LINK_TAG}\n\\1",
        new_content,
        count=1,
    )
    if n_head == 0:
        return None, "no_head_close"

    # 3. <body> 直後に nav 挿入
    nav_html = render_nav(home, back, back_label, chap_num, chap_name, chap_name_en)
    new_content, n_body = re.subn(
        r"(<body[^>]*>)",
        f"\\1\n{nav_html}",
        new_content,
        count=1,
    )
    if n_body == 0:
        return None, "no_body_open"

    # 4. </body> 直前に footer 挿入
    footer_html = render_footer(home, back, back_label, chap_num)
    new_content, n_close = re.subn(
        r"(</body>)",
        f"{footer_html}\n\\1",
        new_content,
        count=1,
    )
    if n_close == 0:
        return None, "no_body_close"

    return new_content, "ok"


def process_file(path, home, back, back_label, chap_num, chap_name, chap_name_en, color, mode):
    """mode: 'inject' / 'force' / 'remove'."""
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return f"error:{e}"

    has_overlay = "data-toshin-overlay" in content

    if mode == "remove":
        if not has_overlay:
            return "skipped"
        content = remove_overlay(content)
        path.write_text(content, encoding="utf-8")
        return "removed"

    if mode == "inject" and has_overlay:
        return "skipped"

    if mode == "force" and has_overlay:
        # 既存 overlay を一旦削除
        content = remove_overlay(content)

    new_content, status = inject_overlay(content, home, back, back_label, chap_num, chap_name, chap_name_en, color)
    if new_content is None:
        return f"error:{status}"

    path.write_text(new_content, encoding="utf-8")
    return "injected" if mode == "inject" else "updated"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--force", action="store_true", help="既存注入を最新版に更新")
    parser.add_argument("--remove", action="store_true", help="overlay を取り除く")
    args = parser.parse_args()

    if args.remove:
        mode = "remove"
    elif args.force:
        mode = "force"
    else:
        mode = "inject"

    data = json.loads((BASE / "data/chapters.json").read_text(encoding="utf-8"))

    counts = {"injected": 0, "updated": 0, "skipped": 0, "removed": 0}
    errors = []

    for field, field_obj in data.items():
        for chap_str, chap_obj in field_obj.get("chapters", {}).items():
            try:
                chap = int(chap_str)
            except ValueError:
                continue
            chap_name = chap_obj.get("name", f"第 {chap} 回")
            chap_name_en = chap_obj.get("name_en", f"Lesson {chap:02d}")
            color = chap_obj.get("color", "gray")

            for s in chap_obj.get("sections", []):
                fname = s.get("file")
                if not fname:
                    continue
                tool_path = BASE / f"tools/{field}/{fname}"
                if not tool_path.exists():
                    continue

                home = "../../"
                if field == "calculus":
                    back = f"../../calculus/lesson-{chap:02d}/"
                    back_label = f"第 {chap} 回"
                else:
                    back = "../../"
                    back_label = "home"

                result = process_file(
                    tool_path, home, back, back_label,
                    chap, chap_name, chap_name_en, color, mode,
                )
                if result.startswith("error"):
                    errors.append((tool_path.relative_to(BASE), result))
                else:
                    counts[result] = counts.get(result, 0) + 1
                    if result in ("injected", "updated", "removed"):
                        print(f"  ✓ {tool_path.relative_to(BASE)} ({result})")

    print()
    print("=== Summary ===")
    for k, v in counts.items():
        if v > 0:
            print(f"  {k}: {v}")
    if errors:
        print()
        print("=== Errors ===")
        for path, msg in errors:
            print(f"  ✗ {path}: {msg}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
