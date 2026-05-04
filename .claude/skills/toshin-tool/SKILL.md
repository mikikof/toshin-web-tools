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

1. **設計の聖典** ― 配色・教育設計・MathML・命名・量産フロー
2. **既存 32 ツール逆引き早見表** ― 類似事例検索
3. **完成時チェックリスト** ― 品質ゲート
4. (テーマに近い既存ツール 1-2 件)― EXAMPLES から選んで `tools/calculus/N-N.html` を一読

これを読まずに書き始めると、毎回設計が揺れて量産価値が消える。

### 現在地別の参照パス

Claude が cwd に応じて、上の各ファイルへのパスがズレる:

| 現在地 | 設計の聖典 | EXAMPLES | CHECKLIST |
|---|---|---|---|
| submodule root(`web-tools/`) | `CLAUDE.md` | `_template/EXAMPLES.md` | `_template/CHECKLIST.md` |
| 親リポ root(`my-company/`) | `.company/education/toshin/web-tools/CLAUDE.md` | `.company/education/toshin/web-tools/_template/EXAMPLES.md` | `.company/education/toshin/web-tools/_template/CHECKLIST.md` |

迷ったら絶対パスで Read する。`pwd` で現在地を確認してから決める。

---

## 9 ステップ ワークフロー

### Step 1: テーマ受領 + 章節決定 + 完全オフライン要件確認

ユーザーから受け取る情報:
- **テーマ**(必須):何を学ばせたいか(例:「逆関数の微分の挙動」)
- **分野**(`--field`):`calculus`(微分積分編、既定)or `linear`(線形代数編)
- **章節番号**(できれば):章=東進「AI・データ分析のための大学数学」シリーズの回(1〜12)、節=その回の何本目か(1〜)
- **目的**(できれば):学習者にどう発見させたいか

不足があれば `AskUserQuestion` で **同時に** 確認(Step 3 で雛形を変える羽目にならないよう、最初から要件を引き出す):

```
Q1. 分野は? (calculus / linear)

Q2. 章節は? (例: 4-5 = 第4回 5本目)
   - 既存章に追加 → 章番号確認 + 次の節番号を提案
   - 新章として追加 → 章番号 + タイトル

Q3. 完全オフライン要件はあるか?(配布・教室Wi-Fi 不安定対策)
   - YES → Step 3 では offline / canvas のみ可
   - NO  → 全雛形が候補(教育効果を優先)

Q4. 主役の可視化(2D 関数 / 3D / 領域 / アニメ)
   ※ Step 3 の雛形選択と兼ねる
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

### Step 7: 動作確認(自動チェック + ユーザー目視)

#### 自動チェック(Claude が必ず実行)

```bash
# ローカル http サーバー起動(run_in_background で立てる)
python3 -m http.server 8765 > /dev/null 2>&1 &
SERVER_PID=$!
sleep 1

FILE="tools/<field>/<chapter>-<section>.html"

# 1. HTTP 200 確認
curl -s -o /dev/null -w "HTTP: %{http_code}\n" "http://localhost:8765/$FILE"

# 2. TODO 残存検出(雛形 TODO が埋め忘れているか)
echo "TODO 残存: $(grep -c 'TODO' $FILE) 件"
#  → 0 件が理想。残っていればユーザーに警告して中断

# 3. CDN 依存の検出(完全オフライン要件のとき重要)
echo "https:// 依存:"
grep -E '(<script[^>]*src="https://|<link[^>]*href="https://)' $FILE | head -5

# 4. <title>, <h1> が埋まっているか
curl -s "http://localhost:8765/$FILE" | grep -E "(<title>|<h1)" | head -3

kill $SERVER_PID 2>/dev/null
```

判断:
- TODO 残存 > 0 → 中断、ユーザーに「TODO が <N> 件残っています、埋めますか?」と確認
- HTTP ≠ 200 → エラー解析、ファイルの相対パス・タグ閉じ忘れを確認
- 完全オフライン雛形なのに `https://` 依存 → 雛形選択ミス、または不適切な追加 → 中断

#### ユーザー目視

自動チェックが OK になったら、ユーザーへ:

> 「http://localhost:8765/tools/<field>/<chapter>-<section>.html を開いて以下を確認してください:
> - DevTools コンソールにエラーがないか
> - スライダー全部動くか + 表示値が同期するか
> - プリセット 3 つ全部効くか
> - モバイル幅(DevTools レスポンシブモード)で崩れないか
> - **数学的に意味のある挙動になっているか**(定義域外 NaN、既知値で検算)」

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

# push 成功を確認(SHA がリモートにあるか)
SHA=$(git rev-parse HEAD)
git ls-remote origin | grep "$SHA" || echo "⚠ push 失敗の可能性、再 push 検討"
```

#### 9-2. 親リポ(my-company)で submodule 参照を進める

**親 push 前の必須確認**(submodule SHA がリモートに存在するか):

```bash
cd /Users/mikiokofune/my-company  # 親リポ root

# submodule SHA 取得
SUBMODULE_SHA=$(git -C .company/education/toshin/web-tools rev-parse HEAD)
echo "submodule SHA: $SUBMODULE_SHA"

# リモートに存在するか確認(なければ親 push しない)
git ls-remote https://github.com/mikikof/toshin-web-tools.git | grep "$SUBMODULE_SHA" \
    && echo "✅ remote 存在確認 OK" \
    || echo "❌ submodule push が完了していない、9-1 を再実行"
```

整合性レポートをユーザーに見せる(必須):

```
| 項目 | 状態 |
|---|---|
| submodule push 済み(<old SHA> → <new SHA>) | ✅ |
| submodule SHA がリモートに存在 | ✅(git ls-remote で確認済) |
| GitHub Pages 配信中 | ⏳ <数分待ち> or ✅ |
| 親リポ未コミット変更 |  |
| .gitmodules 変更 | 通常なし(あった場合のみ理由明記) |
| .company/education/toshin/web-tools(submodule SHA) | ✅ <new SHA> に進める |
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

→ **先に** `git status` で未コミット変更を確認。**ユーザーが書きかけた他の編集が混在していないか**を必ずチェック。
→ 影響範囲が新規ツール 1 ファイルだけなら `git checkout HEAD -- tools/<field>/<file>` で復旧。
→ 既存変更が混在しているなら、`git stash` で退避してから checkout、その後 stash pop。
→ commit 前ならいずれも復旧可能。commit 後なら `git revert <bad commit>` で。

### submodule push 順序を間違えた(親リポを先に push してしまった)

リモートで「親リポが指す submodule SHA が存在しない」状態に。
→ すぐに submodule リポで `git push origin main`(SHA を後追いで送る)
→ submodule の commit が消えていれば `git revert` で親リポの参照を戻す
→ 詳細は CLAUDE.md §14-1 救済 runbook を参照

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
