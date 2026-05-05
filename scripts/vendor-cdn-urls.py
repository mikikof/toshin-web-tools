#!/usr/bin/env python3
"""全 33 ツールの CDN URL を assets/vendor/<file> へ書き換える(冪等)。

Google Fonts は維持(woff2 へのリンクが入れ子になっており vendoring 困難、
かつフォント未ロードでも text は system font fallback で表示される)。
unpkg.com/lucide@latest も維持(1 件のみ、必要なら別途対処)。
"""

from pathlib import Path
import re
import sys

BASE = Path(__file__).resolve().parent.parent

# CDN URL → assets/vendor/<filename> マッピング
URL_MAP = {
    # Tailwind CDN
    "https://cdn.tailwindcss.com": "../../assets/vendor/tailwindcss.js",
    # KaTeX
    "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js": "../../assets/vendor/katex.min.js",
    "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css": "../../assets/vendor/katex.min.css",
    "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js": "../../assets/vendor/katex-auto-render.min.js",
    # Chart.js
    "https://cdn.jsdelivr.net/npm/chart.js": "../../assets/vendor/chart.js",
    "https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js": "../../assets/vendor/chart.umd.min.js",
    "https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.0.1/dist/chartjs-plugin-annotation.min.js": "../../assets/vendor/chartjs-plugin-annotation.min.js",
    "https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js": "../../assets/vendor/chartjs-adapter-date-fns.bundle.min.js",
    # D3
    "https://d3js.org/d3.v7.min.js": "../../assets/vendor/d3.v7.min.js",
    # Three.js (r128 系)
    "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js": "../../assets/vendor/three.r128.min.js",
    "https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js": "../../assets/vendor/three.r128.OrbitControls.js",
    # Three.js (ESM)
    "https://cdn.jsdelivr.net/npm/three@0.164.1/build/three.module.js": "../../assets/vendor/three.module-0.164.1.js",
    "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js": "../../assets/vendor/three.module-0.160.0.js",
    # es-module-shims (importmap polyfill)
    "https://ga.jspm.io/npm:es-module-shims@1.10.0/dist/es-module-shims.js": "../../assets/vendor/es-module-shims.js",
    # MathJax
    "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js": "../../assets/vendor/mathjax-tex-svg.js",
    # React
    "https://unpkg.com/react@18/umd/react.production.min.js": "../../assets/vendor/react.production.min.js",
    "https://unpkg.com/react-dom@18/umd/react-dom.production.min.js": "../../assets/vendor/react-dom.production.min.js",
    "https://unpkg.com/react@18/umd/react.development.js": "../../assets/vendor/react.development.js",
    "https://unpkg.com/react-dom@18/umd/react-dom.development.js": "../../assets/vendor/react-dom.development.js",
    "https://unpkg.com/@babel/standalone/babel.min.js": "../../assets/vendor/babel.standalone.min.js",
    # GSAP
    "https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js": "../../assets/vendor/gsap.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js": "../../assets/vendor/gsap-ScrollTrigger.min.js",
    # Plotly
    "https://cdn.plot.ly/plotly-2.33.0.min.js": "../../assets/vendor/plotly-2.33.0.min.js",
    # Tone.js
    "https://cdnjs.cloudflare.com/ajax/libs/tone/14.7.77/Tone.js": "../../assets/vendor/tone.js",
}


def rewrite_file(path: Path) -> tuple[int, list[str]]:
    """1 ファイルの URL を書き換え。戻り値: (置換件数, 未対応 URL 一覧)."""
    content = path.read_text(encoding="utf-8")
    orig = content
    count = 0
    for cdn, local in URL_MAP.items():
        if cdn in content:
            content = content.replace(cdn, local)
            count += content.count(local) - orig.count(local)
            orig = content

    # 未対応 URL を検出(残った CDN 風 URL)
    unhandled = []
    for m in re.finditer(r'(?:src|href)="(https://[^"]+)"', content):
        url = m.group(1)
        if url in URL_MAP:
            continue
        # Google Fonts と lucide は意図的にスキップ
        if "fonts.googleapis.com" in url or "fonts.gstatic.com" in url:
            continue
        if "unpkg.com/lucide" in url:
            continue
        unhandled.append(url)
    # importmap 内の URL も
    for m in re.finditer(r'"(https://[^"]+\.js)"', content):
        url = m.group(1)
        if url in URL_MAP:
            continue
        if url not in unhandled:
            unhandled.append(url)

    if content != path.read_text(encoding="utf-8"):
        path.write_text(content, encoding="utf-8")
    return count, unhandled


def main():
    tools_root = BASE / "tools"
    total_changes = 0
    all_unhandled = set()
    for html in sorted(tools_root.rglob("*.html")):
        cnt, unhandled = rewrite_file(html)
        if cnt > 0:
            print(f"  ✓ {html.relative_to(BASE)}: {cnt} URL 置換")
        if unhandled:
            for u in unhandled:
                all_unhandled.add(u)
        total_changes += cnt

    print()
    print(f"=== 合計置換: {total_changes} URL ===")
    if all_unhandled:
        print()
        print("=== 未対応 URL(維持される、意図通り or 別途対処要)===")
        for u in sorted(all_unhandled):
            print(f"  ⊘ {u}")


if __name__ == "__main__":
    main()
