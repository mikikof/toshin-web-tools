#!/usr/bin/env python3
"""既存 33 ツール本体に toshin-web-tools オーバーレイを注入する(非侵略版 v3)。

各ツール本体(tools/<field>/N-N.html)に対して以下を **冪等に** 挿入:

1. <head> 末尾に `<link rel="stylesheet" href="../../assets/tool-overlay.css" data-toshin-overlay>`
2. <body> タグに `data-toshin-overlay="<color>"` 属性を追加(既存 class/属性は維持)
3. <body> 直後に上部 nav(brand + context + back)を挿入
4. </body> 直前に下部 footer(mark + tag + links + meta)を挿入

旧版にあった <html class="journal-mode chap-COLOR"> による既存 CSS 上書きは **撤去**。
オーバーレイは既存ツールの内部レイアウトに一切触れない設計。

冪等性: `data-toshin-overlay` の有無で判定。`--force` で再注入(削除→注入)。
ロールバック: `--remove`。

Usage:
    python3 scripts/inject-tool-overlay.py            # 全ツールに注入
    python3 scripts/inject-tool-overlay.py --force    # 既存注入を最新版に更新
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

# 章カラー hex 一覧(inline style で渡す)
COLOR_HEX = {
    "indigo":  "#4338ca",
    "coral":   "#dc2626",
    "navy":    "#1e3a8a",
    "teal":    "#0f766e",
    "purple":  "#7c3aed",
    "amber":   "#ca8a04",
    "cyan":    "#0891b2",
    "emerald": "#059669",
    "rose":    "#be185d",
    "gray":    "#64748b",
}


def render_nav(home, back, back_label, chap_num, chap_name, chap_name_en, color_hex):
    if chap_num and chap_name:
        ctx_inner = f'<strong>第 {chap_num} 回 — {chap_name}</strong>'
    else:
        ctx_inner = ''
    return f"""{OVERLAY_NAV_BEGIN}
<nav class="toshin-overlay-nav" style="--toshin-accent: {color_hex};" aria-label="toshin-web-tools navigation">
  <div class="toshin-overlay-nav-inner">
    <a href="{home}" class="toshin-overlay-brand">toshin<span class="dot">.</span>web-tools</a>
    <div class="toshin-overlay-context">{ctx_inner}</div>
    <a href="{back}" class="toshin-overlay-back">← {back_label}</a>
  </div>
</nav>
{OVERLAY_NAV_END}"""


def render_footer(home, back, back_label, chap_num):
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
  <div class="toshin-overlay-footer-meta">© 2026 mikikof · MIT License</div>
</footer>
{OVERLAY_FOOTER_END}"""


def remove_overlay(content):
    """既存の overlay(旧版・新版を問わず)を取り除く。冪等。"""
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
    # 旧版 <html class="journal-mode chap-..."> を撤去
    content = re.sub(
        r'(<html[^>]*?)\s+class="([^"]*?)\s*journal-mode\s+chap-\w+\s*([^"]*?)"',
        lambda m: f'{m.group(1)} class="{m.group(2).strip()}{(" " + m.group(3).strip()) if m.group(3).strip() else ""}"',
        content,
    )
    # 上の置換で class="" になったら削除
    content = re.sub(
        r'(<html[^>]*?)\s+class=""',
        r"\1",
        content,
    )
    # 旧版 data-toshin-html 属性を撤去
    content = re.sub(
        r'(<html[^>]*?)\s+data-toshin-html="[^"]*"',
        r"\1",
        content,
    )
    # 新版 <body data-toshin-overlay="..."> を撤去
    content = re.sub(
        r'(<body[^>]*?)\s+data-toshin-overlay="[^"]*"',
        r"\1",
        content,
    )
    return content


def inject_overlay(content, home, back, back_label, chap_num, chap_name, chap_name_en, color):
    color_hex = COLOR_HEX.get(color, COLOR_HEX["gray"])

    # 1. <head> 末尾に link 追加
    new_content, n_head = re.subn(
        r"(</head>)",
        f"  {OVERLAY_LINK_TAG}\n\\1",
        content,
        count=1,
    )
    if n_head == 0:
        return None, "no_head_close"

    # 2. <body ...> タグに data-toshin-overlay 属性を追加(既存属性は維持)
    def add_body_attr(m):
        tag = m.group(0)
        if "data-toshin-overlay" in tag:
            return tag  # already
        # ">" の直前に attribute を挿入
        return tag[:-1].rstrip() + f' data-toshin-overlay="{color}">'

    new_content, n_body_attr = re.subn(r"<body[^>]*>", add_body_attr, new_content, count=1)
    if n_body_attr == 0:
        return None, "no_body_open"

    # 3. <body> 直後に nav 挿入
    nav_html = render_nav(home, back, back_label, chap_num, chap_name, chap_name_en, color_hex)
    new_content = re.sub(
        r"(<body[^>]*>)",
        f"\\1\n{nav_html}",
        new_content,
        count=1,
    )

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
        content = remove_overlay(content)

    new_content, status = inject_overlay(
        content, home, back, back_label,
        chap_num, chap_name, chap_name_en, color,
    )
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
