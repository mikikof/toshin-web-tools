---
name: toshin-tool
description: 受験数学の Web ツール (toshin-web-tools リポ) を量産するための skill。テーマを与えられたら、CLAUDE.md / EXAMPLES.md / CHECKLIST.md を参照し、雛形 4 種(offline / canvas / d3 / three)から選択してツールを設計・実装・動作確認・公開まで走らせる。トリガー — 「東進」「微分積分」「線形代数」「Web ツール」「受験数学」「可視化」「インタラクティブ教材」関連の依頼、または `/toshin-tool [テーマ]`。
---

# /toshin-tool — 受験数学 Web ツール 量産 skill

`toshin-web-tools` リポに新規 Web ツールを安定的に作るためのワークフロー定義。
**東進モード**(Opus 4.7 [1M] 維持、毎ターン extended thinking、品質優先)が適用される範囲です。

---

## いつ起動するか

- ユーザーが `/toshin-tool [テーマ]` と入力した
- 「東進向けの Web ツールを作って」「微分積分の◯◯を可視化したい」「テーマ X の解説ツール」のような依頼
- mikikof-lab の `practices/` や `lectures/` と紛らわしい場合は、**「受験数学」「微分積分」「線形代数」のキーワード**があれば本 skill を優先

---

## 作業着手前に必ず読む(順序厳守)

1. **`web-tools/CLAUDE.md`** ― 設計の聖典(配色・教育設計・MathML・命名・量産フロー)
2. **`_template/EXAMPLES.md`** ― 既存 32 ツールの逆引き早見表(類似事例検索)
3. **`_template/CHECKLIST.md`** ― 完成時チェックリスト(品質ゲート)
4. (テーマに近い既存ツール 1-2 件)― EXAMPLES から選んで `tools/calculus/N-N.html` を一読

これを読まずに書き始めると、毎回設計が揺れて量産価値が消える。

---

## 9 ステップ ワークフロー

### Step 1: テーマ受領 + 章節決定

ユーザーから受け取る情報:
- **テーマ**(必須):何を学ばせたいか(例:「逆関数の微分の挙動」)
- **章節番号**(できれば):章=東進「AI・データ分析のための大学数学」シリーズの回(1〜12)、節=その回の何本目か(1〜)
- **目的**(できれば):学習者にどう発見させたいか

不足があれば `AskUserQuestion` で確認:

```
Q1. 章節は? (例: 4-5 = 第4回 5本目)
   - 既存章に追加 → 章番号確認 + 次の節番号を提案
   - 新章として追加 → 章番号 + タイトル

Q2. 雛形は?(下記 Step 3 と兼ねて聞く場合あり)

Q3. 完全オフライン要件はあるか?(配布・教室Wi-Fi 不安定対策)
```

### Step 2: 既存事例の参照

`_template/EXAMPLES.md` で類似テーマを検索。例:

| 受領テーマ | 類似事例 | 学べること |
|---|---|---|
| 「テイラー展開のもう一つの題材」 | `5-2.html` | Canvas で関数 + 近似 + 誤差を並列表示 |
| 「3D で偏微分を見せたい」 | `8-1.html`, `7-1.html` | Three.js で曲面 + 切断面 |
| 「収束/発散の対比」 | `6-6.html` | D3.js で領域塗りつぶし |
| 「最適化アルゴリズム」 | `1-1.html` | 完全オフラインで SVG パス |

該当ツールの実装を **必ず一読**(state 構造・スライダー設計・プリセット定義をパクる素地に)。

### Step 3: 雛形選択

`AskUserQuestion` で:

```
雛形は?
- offline (CDN ゼロ・SVG 手描き) ← 完全オフライン要件、軽量、教室向け
- canvas (Canvas でリアルタイムグラフ) ← 関数プロット、複数曲線比較
- d3      (D3.js / 領域塗りつぶし)   ← 確率分布、収束/発散、ヒストグラム
- three   (Three.js / 3D)           ← 多変数関数、ベクトル場、立体
```

判断軸は CLAUDE.md §7 を参照。

### Step 4: 教育設計を計画

書き始める前に、**プリセット 3 つの中身**を決める。これが教育的価値の核。

```
□ プリセット 1: 典型例(基本の挙動)
   例(Adam): 「SGD: ジグザグを体験 ➜」
□ プリセット 2: 極端値 / 反例
   例(Adam): 「学習率を上げすぎると発散」
□ プリセット 3: 比較対象 / クライマックス
   例(Adam): 「AdamW で重み減衰の効果」
```

「気づき仕掛け」を 2 つ以上入れる(CLAUDE.md §5-2 参照)。
教師目線の長文解説は書かない(CLAUDE.md §5-3)。

### Step 5: 数式設計

主要な数式を MathML で書く準備をする。
**ASCII / code 表記を必ず併記**(MathML 未対応ブラウザ対策)。

```html
<div class="tool-math" aria-label="reads-as-text">
  <math display="block"><mrow>...</mrow></math>
</div>
<div class="tool-small tool-mute">
  (未対応なら) <code class="tool-mono">L = (1/2) x^2</code>
</div>
```

KaTeX/MathJax の CDN は **使わない**(CLAUDE.md §6)。

### Step 6: 雛形 copy & カスタマイズ

```bash
python3 scripts/new-tool.py <chapter>-<section> "<title>" --template <type>
# 例: python3 scripts/new-tool.py 4-5 "逆関数の挙動" --template canvas
```

これで:
- `tools/calculus/<chapter>-<section>.html` が生成される
- `data/chapters.json` に追記される
- `python3 scripts/build-hub.py` が呼ばれてハブ更新される

次に生成されたファイルを編集:

| 編集箇所 | 内容 |
|---|---|
| `<title>` 周辺 | 既に new-tool.py が埋めている。確認のみ |
| `<header>` の絵文字バッジ + サブタイ | テーマに合った 1 文字絵文字、サブタイは 1 行 |
| 「このツールで体感すること」カード | 1〜2 文。**学習者が動かして発見すること**を明記 |
| MathML + code 併記 | Step 5 で計画した数式を埋め込む |
| プリセット 3 つ | Step 4 で計画した内容にボタン文言とハンドラを書く |
| スライダー定義 | 2〜6 個。重要なパラメータに絞る |
| 観測値カード | KPI 1-2 個(リアルタイム表示) |
| `<script>` の関数本体 | テーマに応じた数学・物理シミュ。`trueFn` / `approxFn` などを埋める |
| `<script>` の redraw | state から SVG/Canvas/D3/3D を再構築 |

雛形の TODO コメントを **すべて埋める or 削除**(残しっぱなしは NG)。

### Step 7: 動作確認

```bash
# ローカル http サーバー起動(別シェルで実行 or run_in_background)
python3 -m http.server 8765

# curl で 200 OK + title 確認
curl -s http://localhost:8765/tools/calculus/<chapter>-<section>.html | grep -E "(<title>|<h1)"

# ブラウザで動作確認(ユーザーに依頼)
# - DevTools コンソールにエラーがないか
# - スライダー全部動くか
# - プリセット 3 つ全部効くか
# - モバイル幅(DevTools レスポンシブモード)で崩れないか
```

ユーザーへ:「http://localhost:8765/tools/calculus/<chapter>-<section>.html を開いて挙動確認をお願いします」と促す。

### Step 8: チェックリストで自己点検

`_template/CHECKLIST.md` を開いて、全項目を 1 つずつ確認:

- [ ] ファイル構造(共通 CSS/JS リンク、戻るリンク等)
- [ ] 教育設計(プリセット 3 つ、気づき仕掛け 2 つ以上)
- [ ] 数式(MathML + code 併記、aria-label)
- [ ] アクセシビリティ(label, ARIA, role="img")
- [ ] モバイル対応(タッチ規格、横スクロールなし)
- [ ] パフォーマンス(ファイルサイズ、RAFLoop)
- [ ] ハブ更新(自動済、目視確認)
- [ ] 動作確認(ローカル http.server)
- [ ] 完全オフライン要件(該当する場合)
- [ ] commit / push の準備

ユーザーに「チェックリスト全項目 ✅ です」と報告 → 次へ。

### Step 9: commit & push(順序厳守)

#### 9-1. submodule(toshin-web-tools)で commit & push

```bash
cd .company/education/toshin/web-tools

git add -A
git status --short  # 確認

git commit -m "$(cat <<'EOF'
feat: <chapter>-<section> <短縮タイトル> (<雛形種類>)

- 教育設計: プリセット <内容>, 気づき仕掛け <内容>
- 数式: MathML + code 併記
- 動作確認: chrome / safari / mobile

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"

git push origin main
```

#### 9-2. 親リポ(my-company)で submodule 参照を進める

整合性レポートをユーザーに見せる(必須):

```
| 項目 | 状態 |
|---|---|
| submodule push 済み(<old SHA> → <new SHA>) | ✅ |
| GitHub Pages 配信中 | ⏳ <数分待ち> or ✅ |
| 親リポ未コミット変更 |  |
| .gitmodules 変更 | ✅ あり |
| .company/education/toshin/web-tools(submodule SHA) | ✅ 進める |
| その他 | (todos の更新等) |

コミットメッセージ案:
> education+toshin: web-tools <chapter>-<section> <短縮タイトル> — submodule 参照更新

push して大丈夫ですか?
```

ユーザー承認 → 親リポで commit & push。

```bash
cd ../../../..  # my-company root

git add .company/education/toshin/web-tools .gitmodules
# 必要に応じて他の変更も add

git commit -m "$(cat <<'EOF'
education+toshin: web-tools <chapter>-<section> <短縮タイトル> — submodule 参照更新

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"

git push
```

完了 → ユーザーに公開 URL `https://mikikof.github.io/toshin-web-tools/tools/calculus/<chapter>-<section>.html` を伝える(数分でデプロイ完了)。

---

## よくあるパターン別の進め方

### A. 「テーマだけ言われて、章節未指定」

→ Step 1 で `AskUserQuestion` で章節決定。EXAMPLES.md を見ながら「第 N 回に近い」と提案する。

### B. 「3D で見せたい」と明言

→ Step 3 で `three` 雛形即決定。Three.js の理解度がない学習者向けの場合、Step 4 で操作説明(回転・パン・ズーム)を `tool-note` で目立たせる。

### C. 「既存ツールを参考にした類似ツール」

→ Step 2 で既存ツールを **必ず先に読む**。state 構造・プリセット・スライダー定義を可能な限り再利用。

### D. 「完全オフライン版がほしい」

→ Step 3 で `offline` 雛形固定。CDN 依存ゼロを Step 6 で確認(`https://` の `<script>` `<link>` を入れない)。

### E. 「既存ツールの修正・改善」

→ skill 起動せず、直接 `tools/calculus/<chapter>-<section>.html` を編集。CHECKLIST.md は再確認。commit message は `fix:` または `improve:` で。

---

## 失敗したときのリカバリ

### 雛形 copy で間違えた / 上書きしてしまった

→ `git checkout HEAD -- tools/calculus/<file>` で復旧(commit 前なら)。

### `data/chapters.json` の構造が壊れた

→ JSON syntax 確認: `python3 -c "import json; json.load(open('data/chapters.json'))"`
→ 壊れたら `git checkout HEAD -- data/chapters.json` で復旧。

### submodule push に失敗(認証エラー)

→ `gh auth status` で認証確認。`mikikof` アカウントで `repo` scope があるか。

### 親リポで submodule 参照を進めるのを忘れた

→ `git add .company/education/toshin/web-tools` で参照進める → commit & push 追加。

---

## ユーザーへの最終報告(テンプレ)

```
✅ 新規ツール `<chapter>-<section> <短縮タイトル>` 公開完了

- 公開 URL: https://mikikof.github.io/toshin-web-tools/tools/calculus/<chapter>-<section>.html
- 雛形: <type>
- ファイルサイズ: <size> KB
- プリセット: <3 つの内容>
- 気づき仕掛け: <2 つ以上>

submodule SHA: <old> → <new>
親リポ commit: <SHA>

次にできること:
- ハブ(<https://mikikof.github.io/toshin-web-tools/calculus/lesson-NN/>)から辿れることを確認
- スマホで実機チェック
```
