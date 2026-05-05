#!/usr/bin/env python3
"""新規ツールの初期化スクリプト。

Usage:
    python3 scripts/new-tool.py 4-5 "逆関数の挙動" --template canvas
    python3 scripts/new-tool.py 9-2 "勾配場の可視化" --template three
    python3 scripts/new-tool.py 3-6 "極限の収束" --template offline --back-lesson 3

動作:
    1. _template/saas-<template>.html を tools/<field>/<chapter>-<section>.html にコピー
    2. <!-- TOOL_TITLE -->, <!-- TOOL_DESCRIPTION -->, lesson-XX を置換
       (title は HTML エスケープしてから埋め込む = XSS 対策)
    3. data/chapters.json の該当章 sections に新規節を追記、節番号で昇順ソート
    4. scripts/build-hub.py を呼び出してハブ再生成
    5. ハブ HTML 内に該当ツールへのリンクが含まれることを検証

雛形の TODO コメント(タイトル以外、絵文字・MathML・本文)は残る(中身を書くのは利用者の作業)。

オプション:
    --field      calculus(default) | linear (※ 現状 calculus のみ完全対応、linear は将来拡張)
    --template   offline(default) | canvas | d3 | three
    --back-lesson 戻るリンクの lesson 番号(省略時は <chapter> と同じ)
"""

import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path

TEMPLATES = ("offline", "canvas", "d3", "three")
SUPPORTED_FIELDS = ("calculus",)  # build-hub.py が完全対応している分野
BASE = Path(__file__).resolve().parent.parent


def parse_section(s: str) -> tuple[int, int]:
    m = re.match(r"^(\d+)-(\d+)$", s)
    if not m:
        raise SystemExit(f"Invalid section format: {s} (expected like '4-5')")
    return int(m.group(1)), int(m.group(2))


def section_sort_key(s: dict) -> tuple[int, int]:
    """data/chapters.json の section エントリを節番号で昇順ソートするキー。
    file が None(RTF placeholder)は最後に、numeric な節は昇順に並べる。
    """
    f = s.get("file")
    if not f:
        return (1, 9999)  # placeholder は末尾
    m = re.match(r"^(\d+)-(\d+)\.html$", f)
    if not m:
        return (1, 9998)
    return (0, int(m.group(2)))


def update_chapters_json(field: str, chap: int, file_name: str, title: str) -> None:
    """data/chapters.json の該当章 sections に新規節を追記。

    新スキーマ:
        chapters[str(chap)] = {
            "name": "...", "name_en": "...", "color": "...",
            "description": "...", "sections": [...]
        }
    """
    json_path = BASE / "data/chapters.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    field_obj = data.setdefault(field, {
        "title": "新分野",
        "title_en": "New field",
        "chapter_count": chap,
        "chapters": {},
    })
    chap_count = field_obj.get("chapter_count", chap)
    if chap > chap_count:
        field_obj["chapter_count"] = chap
    chapters = field_obj["chapters"]

    # 新スキーマ: 章は {name, name_en, color, description, sections} の dict
    chap_obj = chapters.setdefault(str(chap), {
        "name": f"第 {chap} 回",
        "name_en": f"Lesson {chap:02d}",
        "color": "gray",
        "description": "(章テーマ未設定 — chapters.json で編集)",
        "sections": [],
    })
    # 既存章が古スキーマ([list] 直接)なら新スキーマに移行
    if isinstance(chap_obj, list):
        chap_obj = {
            "name": f"第 {chap} 回",
            "name_en": f"Lesson {chap:02d}",
            "color": "gray",
            "description": "(章テーマ未設定)",
            "sections": chap_obj,
        }
        chapters[str(chap)] = chap_obj
    sec_list = chap_obj.setdefault("sections", [])

    # 重複チェック
    for s in sec_list:
        if s.get("file") == file_name:
            print(f"⚠ {file_name} は既に登録済み(スキップ)", file=sys.stderr)
            return
    sec_list.append({"file": file_name, "title": title})
    # 節番号で昇順ソート(3-4 を後から追加しても 3-5 の前に並ぶ)
    sec_list.sort(key=section_sort_key)
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # 書き込み後に再 parse して syntax 検証
    try:
        json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"⚠ data/chapters.json が壊れた可能性: {e}")
    print(f"✓ data/chapters.json に追記 + 節番号ソート + 再 parse 検証 OK")


def write_tool_file(template: str, field: str, file_name: str, title: str, back_lesson: int) -> Path:
    src = BASE / f"_template/saas-{template}.html"
    dst = BASE / f"tools/{field}/{file_name}"
    if dst.exists():
        raise SystemExit(f"Refusing to overwrite existing file: {dst}")
    if not src.exists():
        raise SystemExit(f"Template not found: {src}")
    content = src.read_text(encoding="utf-8")

    # XSS 対策: HTML エスケープしてから埋め込む(<title>, <meta description>, <h1> すべて安全)
    title_escaped = html.escape(title, quote=True)
    description = f"{title_escaped}(toshin-web-tools)。"

    # 雛形の統一プレースホルダを置換
    content = content.replace("<!-- TOOL_TITLE -->", title_escaped)
    content = content.replace("<!-- TOOL_DESCRIPTION -->", description)

    # 戻るリンク
    content = content.replace("lesson-XX", f"lesson-{back_lesson:02d}")
    content = content.replace("第 X 回", f"第 {back_lesson} 回")

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(content, encoding="utf-8")
    return dst


def quality_check(dst: Path) -> None:
    """生成された HTML を機械的にチェック(SKILL Step 7 の前哨)。"""
    content = dst.read_text(encoding="utf-8")
    todo_count = content.count("TODO")
    cdn_https = sum(1 for line in content.splitlines()
                    if 'src="https://' in line or 'href="https://' in line)
    mathml_count = content.count("<math")
    label_for = content.count('<label for="')
    aria_live = content.count("aria-live")
    placeholder_left = content.count("<!-- TOOL_TITLE -->") + content.count("<!-- TOOL_DESCRIPTION -->")

    print()
    print("--- 自動品質チェック ---")
    print(f"  プレースホルダ残: {placeholder_left} 件 (0 件であるべき)")
    print(f"  TODO 残存:        {todo_count} 件 (雛形の TODO コメント、後で埋める)")
    print(f"  https:// 依存:    {cdn_https} 件 (Three/D3 雛形では正常)")
    print(f"  <math> 数式:      {mathml_count} 件 (0 件なら数式が未実装)")
    print(f"  <label for=...>:  {label_for} 件 (スライダー数だけあるべき)")
    print(f"  aria-live:        {aria_live} 件 (頻繁更新の KPI には付けない)")
    if placeholder_left > 0:
        print(f"  ⚠ プレースホルダが残っている。new-tool.py の置換ロジック確認が必要")


def verify_hub_links(field: str, file_name: str, back_lesson: int) -> bool:
    """ハブ HTML 内に該当ツールへのリンク文字列が含まれるか検証。"""
    lesson_path = BASE / f"{field}/lesson-{back_lesson:02d}/index.html"
    if not lesson_path.exists():
        print(f"⚠ {lesson_path} が存在しない", file=sys.stderr)
        return False
    lesson_content = lesson_path.read_text(encoding="utf-8")
    expected_link = f"tools/{field}/{file_name}"
    if expected_link not in lesson_content:
        print(f"⚠ lesson-{back_lesson:02d}/index.html に '{expected_link}' へのリンクが見つからない", file=sys.stderr)
        return False
    print(f"✓ ハブリンク文字列検証: lesson-{back_lesson:02d} → tools/{field}/{file_name} OK")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("section", help="章-節 (例: 4-5)")
    parser.add_argument("title", help="ツールタイトル(短い表示名)")
    parser.add_argument("--template", choices=TEMPLATES, default="offline")
    parser.add_argument("--field", default="calculus")
    parser.add_argument("--back-lesson", type=int, default=None,
                        help="戻るリンクの lesson 番号(省略時は章番号)")
    args = parser.parse_args()

    # field の対応状況を警告(現状 calculus のみ build-hub.py が完全対応)
    if args.field not in SUPPORTED_FIELDS:
        print(f"⚠ field '{args.field}' は build-hub.py が完全対応していません。現状 'calculus' のみ。",
              file=sys.stderr)
        print(f"   ファイルと chapters.json は書き込まれますが、ハブの該当分野インデックスは生成されない可能性があります。",
              file=sys.stderr)
        # 続行確認なしで進む(明示的に --field 指定したユーザーの判断を尊重)

    chap, sec = parse_section(args.section)
    file_name = f"{chap}-{sec}.html"
    back_lesson = args.back_lesson if args.back_lesson is not None else chap

    dst = write_tool_file(args.template, args.field, file_name, args.title, back_lesson)
    print(f"✓ Created: {dst.relative_to(BASE)}")
    update_chapters_json(args.field, chap, file_name, args.title)

    # build-hub.py 実行
    try:
        subprocess.run([sys.executable, str(BASE / "scripts/build-hub.py")], check=True)
    except subprocess.CalledProcessError as e:
        print(f"⚠ build-hub.py が失敗: {e}", file=sys.stderr)
        return 1

    # ハブからのリンクを物理ファイル + リンクテキスト両方で検証
    expected_paths = [
        BASE / "index.html",
        BASE / f"{args.field}/index.html" if args.field in SUPPORTED_FIELDS else None,
        BASE / f"{args.field}/lesson-{back_lesson:02d}/index.html" if args.field in SUPPORTED_FIELDS else None,
        dst,
    ]
    expected_paths = [p for p in expected_paths if p is not None]
    missing = [p for p in expected_paths if not p.exists()]
    if missing:
        print(f"⚠ 期待されるファイルが存在しない: {missing}", file=sys.stderr)
        return 1
    print(f"✓ ハブ + 章サブハブ + ツール本体 {len(expected_paths)} ファイル 存在確認 OK")

    if args.field in SUPPORTED_FIELDS:
        if not verify_hub_links(args.field, file_name, back_lesson):
            print("⚠ ハブリンクが正しく生成されていない可能性があります", file=sys.stderr)

    # 自動品質チェック
    quality_check(dst)

    print()
    print(f"次のステップ:")
    print(f"  1. {dst.relative_to(BASE)} を開いて TODO コメントを埋める")
    print(f"  2. python3 -m http.server 8765  → http://localhost:8765/tools/{args.field}/{file_name}")
    print(f"  3. _template/CHECKLIST.md でセルフチェック(§3-B 数学的正確性 必須)")
    print(f"  4. submodule で commit & push、親リポで submodule SHA がリモートに存在することを確認 → 親 push")
    return 0


if __name__ == "__main__":
    sys.exit(main())
