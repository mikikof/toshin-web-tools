# toshin-web-tools — 設計の聖典(Claude 向け)

このリポは、東進・大学受験生向けの **数学 Web ツール集** を量産するための場所です。
Claude が「テーマ X を Web ツールにして」と依頼されたとき、**このファイルを最初に読んで設計判断を行います**。

> 関連: 東進モード(`.company/education/CLAUDE.md`)が適用される範囲です。
> Opus 4.7 [1M] 維持、毎ターン extended thinking、品質優先。

---

## 1. このリポの目的

- 数学の概念を「**動かして・触って**」体感させる単発 Web ツールを量産する
- 受験生(高校 3 年〜浪人)が**スマホでもサクッと**触れることを最優先に
- 各ツールは「**1 概念 = 1 ツール**」の原則。複合ツールは分割する
- 教科書の引き写しは作らない。「**学習者が自分で気づく**」設計に徹底する

---

## 2. ディレクトリ構造(意図つき)

```
toshin-web-tools/
├── CLAUDE.md                  ← 設計の聖典(このファイル)
├── README.md                  ← 公開向け紹介
├── index.html                 ← ハブ(分野別ブロック)── build-hub.py が生成
├── calculus/                  ← 微分積分編
│   ├── index.html             ← 第 1〜12 回 一覧 ── build-hub.py が生成
│   └── lesson-NN/index.html   ← 章サブハブ ── build-hub.py が生成
├── tools/                     ← ツール本体(ここを編集する)
│   ├── calculus/N-N.html      ← 微分積分編 32 ツール
│   └── linear/N-N.html        ← 線形代数編
├── _source/                   ← Cocoa HTML Writer 形式の正本(参考用、編集しない)
├── _template/                 ← 新規ツール雛形(4 種)+ チェックリスト + 例題早見表
├── assets/                    ← サイト全体共通の CSS/JS
│   ├── style.css              ← ハブ用(field-card, lesson-card)
│   ├── tool-style.css         ← ツール本体用(tool-* prefix)
│   └── tool-helpers.js        ← ツール本体用 JS(window.toshin namespace)
├── data/
│   └── chapters.json          ← 章節データのシングルソース
├── scripts/
│   ├── decode-cocoa-html.py   ← Cocoa HTML Writer → 真の HTML 変換
│   ├── build-hub.py           ← chapters.json → ハブ HTML 群を生成
│   └── new-tool.py            ← 新規ツール初期化(雛形 copy + dict 追記 + ハブ再生成)
└── .claude/
    └── skills/
        └── toshin-tool/SKILL.md  ← /toshin-tool スキル定義
```

**役割の分離が肝**:
- `tools/` を編集してツール本体を作る
- `data/chapters.json` を編集して構成を変える(ハブが追従)
- `_template/` は雛形、`assets/` は再利用パーツ、`scripts/` は機械化

---

## 3. 命名規則

| 対象 | 規則 | 例 |
|---|---|---|
| ツールファイル | `<chapter>-<section>.html` | `tools/calculus/4-5.html` |
| 章サブハブ | `lesson-NN/index.html` | `calculus/lesson-04/index.html` |
| 短縮表示名(ハブで出る) | 12〜18 字程度、副題は外す | 「逆関数の微分」(× 「逆関数の微分 可視化ツール」) |
| `<title>` | 「<タイトル> | toshin-web-tools」 | `テイラー展開 | toshin-web-tools` |
| CSS class(ツール本体) | `tool-` prefix | `.tool-card`, `.tool-btn-primary` |
| CSS class(ハブ) | prefix なし | `.field-card`, `.lesson-card` |

**ID 命名**: 短く意味が伝わる(`eta`, `n`, `R` 等の数学記号 OK)。`btn` プレフィックスをボタンに(`btnPlay`, `btnReset`)。

---

## 4. デザイン方針(SaaS 風モダン、統一)

- **配色**: ライト基調 + プリチャージのアクセント(brand=スカイブルー、accent=ティール、pop=コーラル)
- **フォント**: `ui-sans-serif, system-ui` 系。Google Fonts は **基本使わない**(完全オフライン優先)
- **角丸**: 12-20px(`--tool-r-sm/md/lg`)。シャープすぎないが過剰な丸も避ける
- **影**: 微妙(`0 10px 30px rgba(2,6,23,.08)`)、SaaS 的軽やかさ
- **ダーク**: `prefers-color-scheme: dark` で自動切替(共通 CSS が対応済)
- **背景**: `linear-gradient(135deg, var(--tool-bg1), var(--tool-bg2) 35%, var(--tool-bg3))` で奥行きを出す

**禁止事項**:
- ❌ ネオン/グラデ多用のゲーム的 UI(別系統 = 没入型ダーク は今のところ採用しない)
- ❌ シャープな直角コーナー(教育系には硬すぎる)
- ❌ 黒一色のテキスト(`var(--tool-ink)` を使う)
- ❌ Tailwind CDN 依存(共通 CSS で代替)

---

## 5. 教育設計の規約(最重要)

新規ツールの**教育的価値**は以下のチェックで担保する。`_template/CHECKLIST.md` と整合。

### 5-1. 段階的な構造(必須)

```
[ ① 押すだけプリセット 3 つ ] → 「あ、こうなるんだ」の即時 feedback
        ↓
[ ② 単一パラメータ操作 ]    → 1 つの軸で挙動を観察
        ↓
[ ③ 複数パラメータ組合せ ]   → 相互作用を体感
        ↓
[ ④ 比較・反例・極端値 ]     → 「気づき」のクライマックス
```

各段階を必ずカバー。プリセットだけ・スライダーだけは NG。

### 5-2. 「気づき」を仕掛ける(2 つ以上)

- **比較**: 「前のパラメータ」vs「いま」の並列表示、または 2 つのアルゴリズム並列
- **反例**: 「これでも収束しそう」を打ち砕く反例の同時提示
- **極端値**: パラメータ MAX/MIN で何が起きるか(発散、特異点など)
- **隠す → 予測**: 「関数を隠す」トグル → ユーザーが先に予測 → 答え合わせ

### 5-3. 教師目線の解説を書きすぎない

- ✅ 「学習者が**動かして発見する**」前提で UI と仕掛けを作る
- ❌ 教科書の引き写し(「テイラー展開とは...」と長文)
- 必要に応じて `<details>` で折り畳む(さらに知りたい人向け)

### 5-4. テーマと無関係な「お友達感」を出さない

- ❌ 過剰な絵文字、過剰な擬人化(「がんばろう!」等)
- ✅ 数学的に正確な用語、適度なカジュアルさ(「触ってみよう」程度)

---

## 6. 数式の規約(必須)

- **MathML を第一**に使う(オフライン、軽量、ブラウザネイティブ)
- 必ず `aria-label` で読み上げテキストを付ける
- 必ず **ASCII / code 表記を併記**(MathML 未対応ブラウザ向け)

```html
<div class="tool-math" aria-label="L equals one half x squared">
  <math display="block">
    <mrow>
      <mi>L</mi><mo>=</mo>
      <mfrac><mn>1</mn><mn>2</mn></mfrac>
      <msup><mi>x</mi><mn>2</mn></msup>
    </mrow>
  </math>
</div>
<div class="tool-small tool-mute">
  (未対応なら) <code class="tool-mono">L = (1/2) x^2</code>
</div>
```

- KaTeX/MathJax は **使わない**(CDN 依存になり、完全オフライン要件を破る)
- 例外: 大量の数式が必要 + CDN 雛形を使う場合のみ MathJax 検討可、CLAUDE.md コメントで明示

---

## 7. 可視化手段の選び方(雛形対応表)

| 用途 | 雛形 | ライブラリ | 例(既存) |
|---|---|---|---|
| 関数のグラフ + パス、loss landscape | `saas-offline` | なし(SVG 手描き) | 1-1 |
| 動的グラフ、関数比較、リアルタイム描画 | `saas-canvas` | なし(Canvas) | 5-2 |
| 領域塗りつぶし、収束/発散、確率分布 | `saas-d3` | D3.js v7(CDN) | 6-6 |
| 3D 曲面、ベクトル場、回転体、円錐曲線 | `saas-three` | Three.js r160+(CDN) | 3-1, 7-1, 9-1 |

**選び方の判断軸**:

```
触らせるのは何?
├─ 値・数値 + 軌跡 → SVG (offline)
├─ 連続関数の形状  → Canvas
├─ 領域・分布      → D3
└─ 立体的な空間    → Three
```

**完全オフライン要件があるなら必ず offline 雛形を選ぶ**(後述)。

---

## 8. 完全オフライン基準

「完全オフライン対応」は **CDN 依存ゼロ** を意味する。以下のときに必須:

- 配布・同梱(USB/メールで配る)を想定する場合
- 学校/予備校の教室 Wi-Fi が不安定な環境向け
- ユーザーが「オフライン版がほしい」と明言した場合

完全オフラインなら:
- 雛形 `saas-offline` または `saas-canvas` を使う
- `<script src="https://...">` `<link href="https://...">` を**書かない**
- フォントは system-ui のみ(Google Fonts もダメ)
- 共通 `assets/tool-style.css` `tool-helpers.js` は OK(同一サイト内)

オンライン前提(D3, Three.js)なら CDN OK。だが**必要なライブラリだけ**(jQuery 等は不要)。

---

## 9. アクセシビリティ規約(妥協しない)

| 対象 | 規約 |
|---|---|
| `<input type="range">` | 必ず `<label>` または `aria-label` |
| `<button>` | 絵文字だけは NG。意味のあるテキスト or `aria-label` |
| SVG / Canvas / 3D ビュー | `role="img"` + `aria-label` で内容を読み上げ可能に |
| キーボード操作 | タブ移動 + 矢印キーで全機能アクセス可能 |
| フォーカス可視性 | 共通 CSS の `:focus-visible` を上書きしない |
| コントラスト | テキスト 4.5:1 以上(WCAG AA)。`var(--tool-ink)` `var(--tool-text)` `var(--tool-mute)` を使えば自動で OK |

---

## 10. モバイル規約

- **タッチ規格**: ボタン min-height 44-48px(共通 CSS で自動)
- **iOS zoom 抑制**: `<input>` の font-size は 16px 以上(共通 CSS で自動)
- **スライダー thumb 拡大**: モバイルで 30px(PC 24px、共通 CSS で自動)
- **横スクロール禁止**: テーブル/グラフは `overflow-x: auto` で囲む
- **ブレイクポイント**: 1024px(PC 2 カラム / それ以下 1 カラム)
- **iPhone 実機**(or DevTools エミュ)で動作確認すること

---

## 11. ファイルサイズ目安

| 雛形 | 想定サイズ |
|---|---|
| saas-offline | 30-60 KB |
| saas-canvas | 40-80 KB |
| saas-d3 | 30-60 KB(D3 本体は CDN なので含まない) |
| saas-three | 30-60 KB(Three.js 本体は CDN なので含まない) |

100 KB を超えたら構造を見直す(複数ツールに分割を検討)。

---

## 12. 量産化フロー(これに従う)

### 12-1. 単一テーマで新規ツールを作る

```bash
# 1. 雛形コピー + dict 追記 + ハブ再生成 を一発
python3 scripts/new-tool.py 4-5 "逆関数の挙動" --template canvas

# 2. tools/calculus/4-5.html を開いて TODO を埋める
#    - <body class="tool-page"> 配下の各 TODO コメント
#    - <script> 内の関数本体・プリセット・state

# 3. ローカル http.server で動作確認
python3 -m http.server 8765
#    → http://localhost:8765/tools/calculus/4-5.html

# 4. _template/CHECKLIST.md でセルフチェック

# 5. submodule 内で commit & push
git add -A
git commit -m "feat: 4-5 逆関数の挙動 (canvas 雛形)"
git push origin main

# 6. 親リポで submodule 参照を進める
cd ../../../..  # my-company root
git add .company/education/toshin/web-tools
git commit -m "education+toshin: web-tools 4-5 逆関数の挙動 — submodule 参照更新"
git push  # ★ 整合性レポート → ユーザー承認 → push
```

### 12-2. /toshin-tool スキル経由(対話で進めたい場合)

ユーザーが `/toshin-tool [テーマ]` と入力 → `.claude/skills/toshin-tool/SKILL.md` のワークフローに従う(対話で章節決定 + 雛形選択 + 教育設計 + カスタマイズ + push)。

### 12-3. 章節構造を変える(タイトル変更、章ごと削除、並び替え)

- `data/chapters.json` を直接編集
- `python3 scripts/build-hub.py` でハブ再生成
- commit & push

### 12-4. RTF 7 ファイルを HTML 化したい

`_source/caliculus/3-4.rtf, 5-3.rtf, 5-5.rtf, 5-6.rtf, 5-7.rtf, 6-2.rtf, 8-4.rtf` を順次 HTML 化:
1. RTF を読んで内容を把握(textutil コマンド: `textutil -convert html input.rtf`)
2. 該当章節の場所に `tools/calculus/3-4.html` 等として新規作成(雛形 4 種から適切なものを選ぶ)
3. `data/chapters.json` の該当節の `"file": null` を `"file": "3-4.html"` に置き換え
4. `python3 scripts/build-hub.py`
5. commit & push

---

## 13. 既存 32 ツールとの関係

- `_source/caliculus/*.html` (33 HTML + 7 RTF) は**正本として保存**(編集しない)
- `tools/calculus/*.html` (32 HTML) は**配信用デコード版**
- 既存 32 ツールは各自が `<style>` を inline で持つ(共通 `tool-style.css` を読まない)。これは **意図的**:
  - 既存ツールは「単一 HTML 完結」が完成している
  - 共通 CSS に切替えると class 名衝突や挙動変化のリスクがある
  - **既存ツールは触らない**。新規ツールから共通 CSS を使う
- ただし、Phase 2 で「既存ツールも共通 CSS に統一する」プロジェクトを実施する可能性あり(その時は別途計画)

---

## 14. commit / push のルール

### 14-1. submodule push 順序(厳守)
1. **submodule(`toshin-web-tools`)** を先に push
2. **親リポ(`my-company`)** で submodule 参照を進めて push

逆順だとリモートで参照切れになる。memory ルール「submodule push 順序の厳守」を参照。

### 14-2. commit メッセージの形式

submodule 側:
```
feat: <chapter>-<section> <短縮タイトル> (<雛形種類>)

(必要なら詳細)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

親リポ側:
```
education+toshin: web-tools <chapter>-<section> <短縮タイトル> — submodule 参照更新

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

### 14-3. push 前の整合性レポート(必須)

`git push` を実行する前に、必ず以下を表で出してユーザー承認を取る:

- submodule SHA(古い → 新しい)
- 公開 URL の HTTP 状態(`https://mikikof.github.io/toshin-web-tools/`)
- 親リポ未コミット変更の一覧
- submodule push が先に完了しているか

これは memory ルール「Auto モードでもリモート push 前は整合性レポートで承認」を遵守するため。

---

## 15. トラブルシューティング(よくあるミス)

### Q. 新規ツールの戻るリンクが lesson-XX のまま
A. `new-tool.py` で `--back-lesson` を渡したか確認。雛形の `lesson-XX` は自動置換される。手動で書き換えてもよい。

### Q. ハブから新規ツールへのリンクが切れている
A. `data/chapters.json` に追記されているか確認 → `python3 scripts/build-hub.py` 再実行。

### Q. ツールがブラウザで真っ白
A. ブラウザの DevTools コンソールを見る。よくある原因:
- `<script>` の path が間違っている(`../../assets/tool-helpers.js` を `../assets/...` 等)
- IIFE で `window.toshin.Slider` を使う前に `<script src=".../tool-helpers.js"></script>` がない
- (Three.js) importmap が対応していないブラウザ(Safari 16.3 以下)→ ブラウザを上げる or Three.js を直接 `<script src>` で読み込む

### Q. MathML が表示されない
A. Firefox は OK。Chrome は 109+ で対応。Safari は 14+ で対応。常に **code フォールバック**を併記する。

### Q. submodule の編集が親リポで反映されない
A. submodule 内で commit & push したら、親リポで `git add .company/education/toshin/web-tools` で参照を進める必要がある(自動では追従しない)。

### Q. `data/chapters.json` を手で編集したらハブが壊れた
A. JSON syntax エラーの可能性。`python3 -c "import json; json.load(open('data/chapters.json'))"` でパース確認。

---

## 16. 「テーマ X」を受けたときの最短手順(Claude 用)

```
1. ユーザーから「テーマ X を Web ツールにして」と言われる
2. /toshin-tool スキルが起動(または手動で以下を実行)
3. このファイル(CLAUDE.md)を最初に読む(設計判断軸を頭に入れる)
4. _template/EXAMPLES.md で類似事例を見つける
5. AskUserQuestion で:
   - 章節番号(例: 4-5)
   - 雛形(offline/canvas/d3/three)
   - 教育意図(プリセット 3 つは何にする?)
   - 完全オフライン要件があるか
6. python3 scripts/new-tool.py <chapter>-<section> "<title>" --template <type>
7. 生成された tools/<field>/<chapter>-<section>.html を編集
   - 数式(MathML + code)
   - プリセット 3 つ(意味のあるシナリオ)
   - スライダー定義
   - 関数本体・可視化ロジック
   - 教育文(導入で何を体感するか、1-2 文)
8. python3 -m http.server で動作確認、curl で 200 確認
9. _template/CHECKLIST.md でセルフチェック(全項目)
10. submodule で commit & push
11. 親リポで submodule 参照進める + 整合性レポート → ユーザー承認 → push
```

---

## 17. 改訂履歴

| 日付 | 改訂内容 |
|---|---|
| 2026-05-05 | 初版。Phase 1(既存 32 ツール取り込み)+ Phase A(量産化体制)で確立 |
