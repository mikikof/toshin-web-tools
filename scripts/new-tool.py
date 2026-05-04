#!/usr/bin/env python3
"""新規ツールの初期化スクリプト。

Usage:
    python3 scripts/new-tool.py 4-5 "逆関数の挙動" --template canvas
    python3 scripts/new-tool.py 9-2 "勾配場の可視化" --template three
    python3 scripts/new-tool.py 3-6 "極限の収束" --template offline --back-lesson 3

動作:
    1. _template/saas-<template>.html を tools/calculus/<chapter>-<section>.html にコピー
    2. <title>, description, 戻るリンク lesson-NN を簡易置換
    3. data/chapters.json の該当章 sections に新規節を追記(章末に追加、重複は拒否)
    4. scripts/build-hub.py を呼び出してハブ再生成

雛形のうち TODO コメントは残る(中身を書くのは利用者の作業)。

オプション:
    --field      calculus(default) | linear
    --template   offline(default) | canvas | d3 | three
    --back-lesson 戻るリンクの lesson 番号(省略時は <chapter> と同じ)
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

TEMPLATES = ("offline", "canvas", "d3", "three")
BASE = Path(__file__).resolve().parent.parent


def parse_section(s: str) -> tuple[int, int]:
    m = re.match(r"^(\d+)-(\d+)$", s)
    if not m:
        raise SystemExit(f"Invalid section format: {s} (expected like '4-5')")
    return int(m.group(1)), int(m.group(2))


def update_chapters_json(field: str, chap: int, file_name: str, title: str) -> None:
    json_path = BASE / "data/chapters.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    field_obj = data.setdefault(field, {
        "title": "新分野",
        "chapter_count": chap,
        "chapters": {},
    })
    chap_count = field_obj.get("chapter_count", chap)
    if chap > chap_count:
        field_obj["chapter_count"] = chap
    chapters = field_obj["chapters"]
    sec_list = chapters.setdefault(str(chap), [])

    # 重複チェック
    for s in sec_list:
        if s.get("file") == file_name:
            print(f"⚠ {file_name} は既に登録済み(スキップ)", file=sys.stderr)
            return
    sec_list.append({"file": file_name, "title": title})
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"✓ data/chapters.json に追記")


def write_tool_file(template: str, field: str, file_name: str, title: str, back_lesson: int) -> Path:
    src = BASE / f"_template/saas-{template}.html"
    dst = BASE / f"tools/{field}/{file_name}"
    if dst.exists():
        raise SystemExit(f"Refusing to overwrite existing file: {dst}")
    if not src.exists():
        raise SystemExit(f"Template not found: {src}")
    content = src.read_text(encoding="utf-8")

    # 簡易置換
    content = content.replace(
        "<!-- TODO: ツールタイトル -->", title
    )
    content = content.replace(
        '<title><!-- TODO: タイトル --> | toshin-web-tools</title>',
        f'<title>{title} | toshin-web-tools</title>',
    )
    content = content.replace(
        '<title>{} | toshin-web-tools</title>'.format(title) + '\n<meta name="description" content="<!-- TODO: 1〜2 文の説明 -->">',
        f'<title>{title} | toshin-web-tools</title>\n<meta name="description" content="{title}(toshin-web-tools)。">',
    )
    content = content.replace("lesson-XX", f"lesson-{back_lesson:02d}")
    content = content.replace("第 X 回", f"第 {back_lesson} 回")

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(content, encoding="utf-8")
    return dst


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("section", help="章-節 (例: 4-5)")
    parser.add_argument("title", help="ツールタイトル(短い表示名)")
    parser.add_argument("--template", choices=TEMPLATES, default="offline")
    parser.add_argument("--field", default="calculus")
    parser.add_argument("--back-lesson", type=int, default=None,
                        help="戻るリンクの lesson 番号(省略時は章番号)")
    args = parser.parse_args()

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

    print()
    print(f"次のステップ:")
    print(f"  1. {dst.relative_to(BASE)} を開いて TODO コメントを埋める")
    print(f"  2. python3 -m http.server 8765  → http://localhost:8765/tools/{args.field}/{file_name}")
    print(f"  3. _template/CHECKLIST.md でセルフチェック")
    print(f"  4. submodule で commit & push、親リポで参照進めて push")
    return 0


if __name__ == "__main__":
    sys.exit(main())
