#!/usr/bin/env python3
"""既存 32 ツール本体に toshin-web-tools 共通オーバーレイを注入する。

各ツール本体(tools/<field>/N-N.html)に対して以下を **冪等に** 挿入:

1. <head> 末尾に `<link rel="stylesheet" href="../../assets/tool-overlay.css" data-toshin-overlay>` を追加
2. <body> 直後に上部 nav(toshin.web-tools ロゴ + 戻るリンク)を挿入
3. </body> 直前に下部 footer(ロゴ + ナビ + クレジット)を挿入

冪等性: `data-toshin-overlay` 属性の有無で判定、既に注入済みのファイルはスキップ。

Usage:
    python3 scripts/inject-tool-overlay.py        # 全 32 ツール + linear/2-2 に注入
    python3 scripts/inject-tool-overlay.py --remove  # オーバーレイを取り除く(ロールバック)
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


def render_nav(home: str, back: str, back_label: str) -> str:
    return f"""{OVERLAY_NAV_BEGIN}
<nav class="toshin-overlay-nav" aria-label="toshin-web-tools navigation">
  <a href="{home}" class="toshin-overlay-brand">toshin<span class="dot">.</span>web-tools</a>
  <a href="{back}" class="toshin-overlay-back">← {back_label}</a>
</nav>
{OVERLAY_NAV_END}"""


def render_footer(home: str, back: str, back_label: str) -> str:
    return f"""{OVERLAY_FOOTER_BEGIN}
<footer class="toshin-overlay-footer">
  <div class="toshin-overlay-footer-mark">toshin<span class="dot">.</span>web-tools</div>
  <div class="toshin-overlay-footer-tag">受験数学のWebツール集</div>
  <div class="toshin-overlay-footer-link">
    <a href="{home}">home</a>
    <a href="{back}">{back_label}</a>
    <a href="https://github.com/mikikof/toshin-web-tools">github</a>
  </div>
  <div class="toshin-overlay-footer-meta">© 2026 mikikof — MIT License</div>
</footer>
{OVERLAY_FOOTER_END}"""


def inject_into_file(path: Path, home: str, back: str, back_label: str) -> str:
    """戻り値: 'injected' / 'skipped' / 'error'"""
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ✗ {path.relative_to(BASE)}: read error {e}", file=sys.stderr)
        return "error"

    if "data-toshin-overlay" in content:
        return "skipped"

    nav_html = render_nav(home, back, back_label)
    footer_html = render_footer(home, back, back_label)

    # 1. <head> 末尾に link 追加
    new_content, n_head = re.subn(
        r"(</head>)",
        f"  {OVERLAY_LINK_TAG}\n\\1",
        content,
        count=1,
    )
    if n_head == 0:
        print(f"  ✗ {path.relative_to(BASE)}: </head> not found", file=sys.stderr)
        return "error"

    # 2. <body...> 直後に nav 挿入
    new_content, n_body = re.subn(
        r"(<body[^>]*>)",
        f"\\1\n{nav_html}",
        new_content,
        count=1,
    )
    if n_body == 0:
        print(f"  ✗ {path.relative_to(BASE)}: <body> not found", file=sys.stderr)
        return "error"

    # 3. </body> 直前に footer 挿入
    new_content, n_close = re.subn(
        r"(</body>)",
        f"{footer_html}\n\\1",
        new_content,
        count=1,
    )
    if n_close == 0:
        print(f"  ✗ {path.relative_to(BASE)}: </body> not found", file=sys.stderr)
        return "error"

    path.write_text(new_content, encoding="utf-8")
    return "injected"


def remove_from_file(path: Path) -> str:
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return "error"
    if "data-toshin-overlay" not in content:
        return "skipped"

    # 1. link 行を削除
    content = re.sub(
        r"^\s*<link[^>]*data-toshin-overlay[^>]*>\s*\n",
        "",
        content,
        count=1,
        flags=re.MULTILINE,
    )
    # 2. nav ブロック削除
    content = re.sub(
        re.escape(OVERLAY_NAV_BEGIN) + r".*?" + re.escape(OVERLAY_NAV_END) + r"\n?",
        "",
        content,
        count=1,
        flags=re.DOTALL,
    )
    # 3. footer ブロック削除
    content = re.sub(
        re.escape(OVERLAY_FOOTER_BEGIN) + r".*?" + re.escape(OVERLAY_FOOTER_END) + r"\n?",
        "",
        content,
        count=1,
        flags=re.DOTALL,
    )
    path.write_text(content, encoding="utf-8")
    return "removed"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remove", action="store_true", help="オーバーレイを取り除く(ロールバック)")
    args = parser.parse_args()

    data = json.loads((BASE / "data/chapters.json").read_text(encoding="utf-8"))

    counts = {"injected": 0, "skipped": 0, "removed": 0, "error": 0}
    for field, field_obj in data.items():
        for chap_str, chap_obj in field_obj.get("chapters", {}).items():
            try:
                chap = int(chap_str)
            except ValueError:
                continue
            for s in chap_obj.get("sections", []):
                fname = s.get("file")
                if not fname:
                    continue
                tool_path = BASE / f"tools/{field}/{fname}"
                if not tool_path.exists():
                    print(f"  ⊘ {tool_path.relative_to(BASE)}: file missing", file=sys.stderr)
                    continue

                home = "../../"
                if field == "calculus":
                    back = f"../../calculus/lesson-{chap:02d}/"
                    back_label = f"第 {chap} 回"
                else:
                    back = "../../"
                    back_label = "home"

                if args.remove:
                    result = remove_from_file(tool_path)
                else:
                    result = inject_into_file(tool_path, home, back, back_label)

                counts[result] = counts.get(result, 0) + 1
                if result in ("injected", "removed"):
                    print(f"  ✓ {tool_path.relative_to(BASE)} ({result}, back={back_label})")

    print()
    print("=== Summary ===")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    return 0 if counts["error"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
