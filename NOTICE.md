# NOTICE — toshin-web-tools

このリポジトリ全体は **MIT License**(`LICENSE` 参照)で公開されています。
個別のサードパーティ依存とその由来を以下に明記します。

---

## 著作権

- 著者: **Mikio Kofune**(東進衛星予備校「AI・データ分析のための大学数学」シリーズ担当)
- 既存 33 HTML ツール(`_source/caliculus/*.html` = 32 件 + `_source/linear/2-2.html` = 1 件)の作者: **Mikio Kofune**
  - 本文では便宜上「既存 32 ツール」と呼称(微分積分学編 32 件を主とし、線形代数編は 1 件のサンプルのみ)
  - 2025 年〜 2026 年に Google Sites 上で公開された「微分積分学 webサイト」を本リポに取り込み
  - Cocoa HTML Writer 形式の正本を `_source/` に保存、デコード版を `tools/` に配置
- 本リポの `assets/tool-style.css` `assets/tool-helpers.js` `_template/` `scripts/` `data/` `CLAUDE.md` 等のドキュメント・コード: **Mikio Kofune** 著、MIT License

---

## サードパーティ依存(CDN 経由で読み込まれるもの)

### Three.js
- 用途: 3D 雛形(`_template/saas-three.html` 等)が CDN 経由で読み込み
- バージョン pin: `0.160.0`(`https://unpkg.com/three@0.160.0/`、major.minor.patch 完全固定)
- ライセンス: **MIT License**
- 著作権: Copyright © the three.js authors
  (各バージョンの正確な年は upstream LICENSE を参照: https://github.com/mrdoob/three.js/blob/dev/LICENSE)

### D3.js
- 用途: D3 雛形(`_template/saas-d3.html` 等)が CDN 経由で読み込み
- バージョン pin: **`7.8.5`**(`https://cdn.jsdelivr.net/npm/d3@7.8.5/dist/d3.min.js`、patch 固定)
- ライセンス: **ISC License**
- 著作権: Copyright © Mike Bostock
  (上流 LICENSE: https://github.com/d3/d3/blob/main/LICENSE)

### Google Fonts(ハブ + 既存 32 ツールの一部)
- 用途: ハブ HTML(`index.html`、`calculus/index.html`、`lesson-NN/index.html`)で Zen Old Mincho / Zen Kaku Gothic New / Fraunces / DM Sans を読み込み
- 加えて、**既存 32 ツール(`tools/calculus/*.html`)の一部**も Google Fonts(Inter、Noto Sans JP、M PLUS Rounded 1c 等)を CDN 経由で読み込む
- ライセンス: **SIL Open Font License v1.1**
- 注: 新規ツール雛形(`_template/saas-*.html`)は完全オフライン優先方針で system-ui 系のみ(`saas-d3` `saas-three` は CDN 依存ライブラリを別途使用)

---

## CDN 利用と外部接続

D3 / Three.js を使う雛形(`saas-d3.html` `saas-three.html`)はオンライン環境を前提とします。
利用者の IP やブラウザ情報は CDN プロバイダ(unpkg / d3js.org)に記録される可能性があります。

完全オフライン要件がある場合は `saas-offline.html` または `saas-canvas.html` 雛形を使ってください
(これらは外部接続なし、自作の `assets/tool-style.css` `tool-helpers.js` のみを参照)。

---

## 既存 32 ツールの埋め込みライブラリ(参考)

`tools/calculus/*.html` の中身は単一 HTML 完結で、各ファイルが独自に CSS/JS を持ちます。
これらは Phase 1(2026-05-05)で `_source/` から取り込まれた正本のデコード版です。
個別ツール内で外部 CDN を使っているものは以下:

- `1-1.html`(Adam ロボ学習)— 完全オフライン、外部依存なし
- `3-1.html`, `7-1.html` 等の 3D 系 — Three.js を CDN 経由
- `6-6.html`(広義積分)— D3.js v7 を CDN 経由
- 多数の Tailwind 系ツール — Tailwind CSS を CDN 経由

これら既存 32 ツールの再配布も MIT License の範囲で行います。

---

## 改変・再利用について

MIT License により、以下が認められます:

- 本リポの全ファイル(コード・ドキュメント・既存ツール)の自由な改変・再配布
- 商用・非商用問わず使用可能
- ただし著作権表示と本 NOTICE.md(または LICENSE)を含めること

---

## 連絡先

著作権・ライセンスに関する問い合わせ:
- GitHub: https://github.com/mikikof/toshin-web-tools/issues
