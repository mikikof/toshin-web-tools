#!/usr/bin/env python3
"""Cocoa HTML Writer 形式の HTML を真の単一 HTML に復元する。

macOS の TextEdit などが出力する Cocoa HTML Writer 形式は、
本来の HTML ソースを <p class="p1"> で行ごとにラップし、
記号を HTML エンティティ(&lt; &gt; &amp; など)でエスケープして保存する。
このスクリプトはその逆変換を行う。

Usage:
    python3 decode-cocoa-html.py INPUT.html > OUTPUT.html
    python3 decode-cocoa-html.py INPUT.html OUTPUT.html

挙動:
    - <p class="p1">...</p>  → 中身を 1 行として抽出
    - <p class="p2"><br></p> → 空行
    - <span class="Apple-converted-space">  </span> → そのままの空白
    - HTML エンティティは Python 標準の HTMLParser が自動デコード
"""

from html.parser import HTMLParser
import sys
from pathlib import Path


class CocoaHTMLDecoder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines: list[str] = []
        self.buffer: list[str] = []
        self.in_p = False
        self.had_content_in_p = False

    def handle_starttag(self, tag, attrs):
        if tag == "p":
            self.in_p = True
            self.buffer = []
            self.had_content_in_p = False
        elif tag == "br" and self.in_p:
            self.had_content_in_p = True

    def handle_endtag(self, tag):
        if tag == "p":
            line = "".join(self.buffer)
            line = line.rstrip("\n")
            if not self.had_content_in_p and not line.strip():
                self.lines.append("")
            else:
                self.lines.append(line)
            self.in_p = False
            self.buffer = []

    def handle_data(self, data):
        if self.in_p:
            self.buffer.append(data)
            if data.strip():
                self.had_content_in_p = True


def decode(content: str) -> str:
    parser = CocoaHTMLDecoder()
    parser.feed(content)
    parser.close()
    return "\n".join(parser.lines)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: decode-cocoa-html.py INPUT.html [OUTPUT.html]", file=sys.stderr)
        return 1
    src = Path(argv[1])
    if not src.exists():
        print(f"Input not found: {src}", file=sys.stderr)
        return 1
    decoded = decode(src.read_text(encoding="utf-8"))
    if len(argv) >= 3:
        Path(argv[2]).write_text(decoded, encoding="utf-8")
    else:
        sys.stdout.write(decoded)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
