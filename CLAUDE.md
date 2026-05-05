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

## 3-1. data/chapters.json スキーマ(v2、2026-05-05)

ハブ生成のシングルソース。`build-hub.py` がこれを読んで全ハブ HTML を生成する。

```json
{
  "calculus": {
    "title": "微分積分学編",
    "title_en": "Calculus",
    "tagline": "...",
    "chapter_count": 12,
    "chapters": {
      "1": {
        "name": "Adam 最適化と学習の可視化",      // 日本語タイトル
        "name_en": "Adam optimization & GD",      // 英語サブタイ(Fraunces italic)
        "color": "indigo",                         // 章カラー(下記 9 + gray)
        "description": "SGD・Adam・AdamW を ...",  // 1〜2 文の説明
        "sections": [
          {"file": "1-1.html", "title": "Adam 最適化の可視化"},
          {"file": null, "title": "(節 1-X / RTF 移植予定)"}
        ]
      },
      "2": {...}
    }
  },
  "linear": {...}
}
```

**章カラー(9 + gray)**:
| color 値 | 用途 | hex |
|---|---|---|
| `indigo` | 第 1 回 / 機械学習 | `#4338ca` |
| `coral` | 第 2 回 / 三角関数応用 | `#ea580c` |
| `navy` | 第 3 回 / 解析 / ε-δ | `#1e3a8a` |
| `teal` | 第 4 回 / 微分応用 | `#0f766e` |
| `purple` | 第 5 回 / 級数 | `#7c3aed` |
| `amber` | 第 6 回 / 積分 | `#d97706` |
| `cyan` | 第 7 回 / 多変数 | `#0891b2` |
| `emerald` | 第 8 回 / 偏微分 / DS | `#059669` |
| `rose` | 第 9 回 / ベクトル解析 | `#be185d` |
| `gray` | 準備中 / placeholder | `#64748b` |

CSS 側では `.chapter-card.chap-indigo` 等の class で適用される(`assets/style.css` 定義済)。

**スキーマ変更時の注意**:
- `chapters[N]` を **list** から **dict(name/color/sections 等を持つ)** に変更したのは v2(2026-05-05、デザイン強化時)
- 古いスキーマ([list] 直下)で書かれたデータがあっても `new-tool.py` は自動で v2 に移行する

---

## 4. デザイン方針(SaaS 風モダン、統一)

- **配色トークン**(`assets/tool-style.css` の `:root` で定義):
  - `--tool-brand`: スカイブルー(主役、リンクや active 状態)
  - `--tool-brand-2`: インディゴ(brand のサブ、グラデ用)
  - `--tool-accent`: ティール(強調・成功・正解)
  - `--tool-accent-2`: レッド(失敗・エラー・反例)
  - `--tool-pop`: アンバー(警告・注意喚起・「ここに注目」のハイライト)
  - 用途: brand と accent は併用 OK、accent-2 と pop は同時使用に注意(視覚的にうるさい)
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

### 5-5. 数学的正確性の検証(教育倫理、最重要)

東進シリーズは全国の高校生・浪人生が視聴 → **数値実験を見て「定理が成り立つ」と勘違いさせない**設計が必要。

#### 必須の確認項目

新規ツールを書くときに、**以下のすべて**を必ず点検する:

1. **定義域**: 関数が未定義になる入力(0 除算、負の log、特異点)で **NaN/Infinity** を画面に出さない。エラー領域は灰色で塗るか「定義域外」とラベルを付ける
2. **特異点・境界値**: 既知の特異点(`x → 0` で `1/x`、`x → -1` で `log(1+x)` 等)を含めて挙動を確認する
3. **既知値での検算**: 既知の数値解(例: `e^0 = 1`、`sin(π/2) = 1`、`∫₀^1 x dx = 1/2`)が実装で正しく出るか検算する。最低 3 ケース
4. **数値近似と切り詰め**: 描画で値を clamp する場合は「ここは画面範囲で打ち切られています」を明示
5. **定理の仮定を UI に短く出す**: 「この可視化は連続関数を前提」「a, b > 0 のとき成立」など、**ツール内で見える形で**示す。`<details>` で折り畳み可

#### 「数値実験 ≠ 証明」の明示(必須)

可視化で「成り立つように見える」だけでは数学的に何も保証しない。学習者を誤誘導しないため、ツール内で必ずどこかに以下のような注記を置く:

> 例: 「このグラフでは X が成り立っているように見えますが、これは数値実験の表示範囲内での観察です。一般の証明には [仮定] が必要です。」

書きすぎ NG(教師目線の長文化に陥る)。1〜2 文で。

#### よく踏むトラップ(避ける)

- ❌ 関数定義域外で `NaN` をそのまま `<text>` 描画 → 画面が壊れる
- ❌ 浮動小数の丸めで `0.30000000000000004` がそのまま表示 → `formatNumber` を使う
- ❌ 「数値で確かめた」を「数学的に証明した」と取り違える文言

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

「完全オフライン対応」は **CDN 依存ゼロ** を意味する。

### CDN 利用の判断ルール(明文化)

- **オフライン要件が明示されているとき** → CDN 雛形(`saas-d3`, `saas-three`)は **使わない**。`saas-offline` か `saas-canvas` を選ぶ
- **オフライン要件が明示されていないとき** → 教育効果を優先して CDN 雛形(D3 / Three.js)を選んで OK
- 判断に迷ったら Step 1 で「3D 優先か、完全オフライン優先か」を **先に確認する**(Step 3 で雛形選択した後に戻ると手戻りが大きい)

### オフライン要件が必須なケース(参考)
- 配布・同梱(USB/メールで配る)を想定する場合
- 学校/予備校の教室 Wi-Fi が不安定な環境向け
- ユーザーが「オフライン版がほしい」と明言した場合

完全オフラインなら:
- 雛形 `saas-offline` または `saas-canvas` を使う
- `<script src="https://...">` `<link href="https://...">` を**書かない**
- フォントは system-ui のみ(Google Fonts もダメ)
- 共通 `assets/tool-style.css` `tool-helpers.js` は OK(同一サイト内)

オンライン前提(D3, Three.js)なら CDN OK。だが**必要なライブラリだけ**(jQuery 等は不要)、**バージョンを必ず pin する**(unpkg なら `@0.160.0` 等)。

### CDN 利用の副作用(README / NOTICE.md に記載)

- 利用者の IP・ブラウザ情報が CDN プロバイダ(unpkg / d3js.org)に記録される可能性
- ライセンスは `NOTICE.md` を参照(Three.js MIT、D3.js ISC 等)

---

## 8-2. ブラウザ対応表

| ブラウザ | 最低バージョン | 備考 |
|---|---|---|
| Chrome | **109+** | MathML Core が Chrome 109 で追加。importmap は 89+ |
| Firefox | 108+ | importmap, MathML 標準対応 |
| Safari (macOS / iOS) | **16.4+** | 16.3 以下では importmap 非対応(Three.js 雛形が真っ白になる) |
| Android Chrome | **109+** | MathML Core(Chrome と同系統) |

学校端末・古いタブレット(Safari 14-16 系、Chrome 100 未満等)が想定される場合は:
- `saas-three` の WebGL fallback メッセージ(雛形に組み込み済)
- MathML 未対応時の `<code>` フォールバック(雛形必須)
- 古いブラウザでも壊れないことを目視確認

出典: [Chrome 109 release note](https://developer.chrome.com/blog/new-in-chrome-109/)

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

## 13. 既存 32 ツールとの関係(rev3 後の方針更新)

- `_source/caliculus/*.html` (33 HTML + 7 RTF) は**正本として保存**(編集しない)
- `tools/calculus/*.html` (32 HTML) は**配信用デコード版**
- 既存 32 ツールは各自が `<style>` を inline で持つ(独自スタイル尊重)
- 各自の `<style>` を尊重しつつ、**`scripts/inject-tool-overlay.py` で共通オーバーレイ(toshin.web-tools nav + footer)を注入** する(2026-05-05 追加方針)
  - 注入対象: `<head>` 末尾に `<link rel="stylesheet" href="../../assets/tool-overlay.css" data-toshin-overlay>`
  - `<body>` 直後に上部 nav(ロゴ + 戻るリンク)
  - `</body>` 直前に下部 footer(クレジット + ナビ)
  - 冪等(`data-toshin-overlay` 属性で判定、再実行 OK)
  - ロールバック可: `python3 scripts/inject-tool-overlay.py --remove`
  - 既存ツールの class とは衝突しない(`toshin-overlay-` prefix で名前空間化)

### オーバーレイ運用ルール

- 新規ツールを `new-tool.py` で作った後、必要なら `inject-tool-overlay.py` を実行(雛形側にも統一感を出すため、ただし雛形には別途 `tool-style.css` がある)
- オーバーレイの内容を変更したいときは `assets/tool-overlay.css` を編集 → 全ツールに即反映(注入は class 参照だけなので、CSS 1 ファイル変更で全ツール変わる)
- 既存ツールの inline `<style>` 自体は触らない。ハブ統一感は overlay CSS で出す

---

## 14. commit / push のルール

### 14-1. submodule push 順序(厳守)
1. **submodule(`toshin-web-tools`)** を先に push
2. **親リポ(`my-company`)** で submodule 参照を進めて push

逆順だとリモートで参照切れになる。memory ルール「submodule push 順序の厳守」を参照。

#### 親 push 前の必須確認(SHA 存在確認)

親リポを push する直前に、submodule SHA がリモートに存在するか **必ず** 確認:

```bash
# 親リポ側で submodule SHA を取得
SUBMODULE_SHA=$(git -C .company/education/toshin/web-tools rev-parse HEAD)

# リモートに存在するか確認
git ls-remote https://github.com/mikikof/toshin-web-tools.git | grep "$SUBMODULE_SHA"
```

#### 万が一 push 順序を間違えた場合の救済 runbook(再現コマンド)

**症状**: 親リポを先に push し、submodule push を忘れた → リモートで「submodule の SHA が存在しない」状態に。
他の作業者が `git submodule update --init --recursive` で fetch 失敗する。

**救済 — ケース A: submodule の commit がローカルに残っているとき(よくあるケース)**

```bash
# 1. submodule に入って rev-parse で SHA を確認
cd .company/education/toshin/web-tools
git rev-parse HEAD
# → c32a46e... 等

# 2. submodule を push(後追いで送る)
git push origin main

# 3. push が成功したことを確認
git ls-remote origin | grep "$(git rev-parse HEAD)"  # 一致行が出れば OK

# 4. 親リポに戻って整合性確認
cd ../../../..
git ls-remote https://github.com/mikikof/toshin-web-tools.git | grep "$(git -C .company/education/toshin/web-tools rev-parse HEAD)"
# 一致行が出れば、親リポの参照と submodule リモートが一致した = 救済完了
```

**救済 — ケース B: submodule の commit が消失(reflog 切れ等)**

```bash
# 1. 親リポの bad commit を特定
git log --oneline -5 -- .company/education/toshin/web-tools
# → 直近の submodule 参照更新 commit を特定(例: abcdef0)

# 2. その commit を revert(submodule 参照を 1 つ前に戻す)
git revert abcdef0
# revert 後、競合があれば手動解消、submodule 行を元 SHA に戻す

# 3. revert commit を push
git push origin main

# 4. submodule で正しい状態を作り直す
cd .company/education/toshin/web-tools
git checkout main && git pull
# 必要な変更を再度コミット → push

# 5. 親リポで submodule SHA を再度進める(順序: submodule → 親)
cd ../../../..
git -C .company/education/toshin/web-tools rev-parse HEAD  # 新 SHA
# ↑ がリモートにあることを ls-remote で確認してから親リポ commit
git add .company/education/toshin/web-tools
git commit -m "education+toshin: submodule 参照復旧"
git push origin main
```

**予防**: 親 push 前に必ず `git ls-remote origin <SUBMODULE_SHA>` で remote 存在確認(本節冒頭参照)。

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

## 16. 「テーマ X」を受けたときの最短手順 — SKILL の 9 ステップ対応表

| SKILL Step | 内容 | 主な参照先 |
|---|---|---|
| 1. テーマ受領 + 章節決定 + **完全オフライン要件確認** | AskUserQuestion で章節・分野(`--field calculus/linear`)・オフライン要件 | §3 命名 / §8 オフライン |
| 2. 既存事例の参照 | EXAMPLES.md で類似テーマ検索 → 既存ツール 1-2 件を Read | `_template/EXAMPLES.md` |
| 3. 雛形選択(offline/canvas/d3/three) | オフライン要件 + 可視化手段で決定 | §7 可視化 / §8 オフライン |
| 4. 教育設計 | プリセット 3 つ + 気づき仕掛け 2 つ以上 + 4 段階構造 | §5 教育設計 |
| 5. 数式設計 + **数学的正確性の検証** | MathML + code 併記、定義域・特異点・既知値の検算 | §6 数式 / §5-5 正確性 |
| 6. 雛形 copy & カスタマイズ | `python3 scripts/new-tool.py <ch>-<sec> "<title>" --template <type>` | `scripts/new-tool.py` |
| 7. 動作確認 | `curl 200` + `grep -c "TODO"` + `grep "https://"` 依存検出 + ブラウザ目視 | §8-2 ブラウザ対応表 |
| 8. CHECKLIST セルフ点検 | 全項目で OK 確認 | `_template/CHECKLIST.md` |
| 9. commit & push | submodule → 親リポ、整合性レポートでユーザー承認 | §14 commit/push + §14-1 救済 runbook |

詳細は `.claude/skills/toshin-tool/SKILL.md` 参照。

---

## 17. 改訂履歴

| 日付 | 改訂内容 |
|---|---|
| 2026-05-05 | 初版。Phase 1(既存 32 ツール取り込み)+ Phase A(量産化体制)で確立 |
