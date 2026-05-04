# 新規ツール 完成時 チェックリスト

新規ツールを作ったら、commit 前に必ずこのリストで自己チェックする。
Claude(自動)とユーザー(目視)の両方が使う。

---

## 1. ファイル構造

- [ ] ファイル配置: `tools/calculus/<chapter>-<section>.html` (微分積分編)
      もしくは `tools/linear/<chapter>-<section>.html` (線形代数編)
- [ ] `<title>` がツールタイトル + ` | toshin-web-tools` 形式
- [ ] `<meta name="description">` が 1〜2 文で内容を説明
- [ ] `<link rel="stylesheet" href="../../assets/tool-style.css">` がある
- [ ] `<script src="../../assets/tool-helpers.js"></script>` がある
      (3D 雛形では `import` 経由でも可、`window.toshin` は使う)
- [ ] `<body class="tool-page">` を付けている
- [ ] 戻るリンク `<a class="tool-back" href="../../calculus/lesson-NN/">` が機能する

## 2. 教育設計(必須)— 4 段階構造を個別チェック

- [ ] 「**このツールで体感すること**」カードに、学習者が**動かして何を発見するか**を 1〜2 文で書いている(教科書の引き写しではない)
- [ ] **段階 1 / プリセット 3 つ**(押すだけ体験)があり、それぞれが意味のあるシナリオに対応(典型例 / 極端な値 / 反例 など)
- [ ] **段階 2 / 単一パラメータ操作**(代表的なスライダーを 1 つ動かして基本挙動を見せる導線)が UI 上に存在
- [ ] **段階 3 / 複数パラメータの組み合わせ**(2 つ以上のスライダーを併用してこそ気づきが生まれる)が機能している
- [ ] **段階 4 / 比較・反例・極端値**を体感できる(例: ラジオボタンで関数を切り替えて並列比較、極端値で発散を見る)
- [ ] **スライダーは 2〜6 個**(増やしすぎない、減らしすぎない)
- [ ] 「**気づき**」を仕掛ける構造が **2 つ以上** ある(極端値で発散、反例の対比、隠す→予測、A/B 並列、段階的開示 から)
- [ ] **教師目線の「答え」を直接書いていない**。学習者が触って気づく構造になっている

## 3. 数式表示と数学的正確性(必須)— 教育倫理の核

### 3-A. 数式表示
- [ ] 主要な数式は `<math>` (MathML) で書いている
- [ ] **MathML 未対応ブラウザ向けに ASCII / code 表記を併記**(`<code class="tool-mono">...</code>`)
- [ ] 数式に `aria-label` で読み上げテキストを付けている

### 3-B. 数学的正確性(高校生向け公開講座 = 最優先)

- [ ] **定義域の処理**: 関数が未定義になる入力(0 除算、負の log、特異点)で `NaN`/`Infinity` を画面に出さない。エラー領域は灰色塗りや「定義域外」ラベルで明示
- [ ] **特異点・境界値**: 既知の特異点(`1/x` の `x=0`、`log(1+x)` の `x=-1` 等)を含めて挙動が壊れない
- [ ] **既知値での検算 ≥ 3 ケース**: 例 `e^0=1`、`sin(π/2)=1`、`∫₀^1 x dx = 1/2`。実装で実際にこの値が出ることを確認
- [ ] **数値近似・切り詰めの明示**: 描画範囲で値を clamp する場合、画面上で「打ち切り」と分かる表現
- [ ] **浮動小数の表示**: `formatNumber(x, 3)` 等で丸める。`0.30000000000000004` のような raw 値を見せない
- [ ] **定理の仮定を UI に短く出す**: 「a, b > 0 のとき成立」「連続関数を前提」など、ツール内で `<details>` か注記で表示
- [ ] **「数値実験 ≠ 証明」の明示**: 1〜2 文で「画面で成り立つように見えるのは数値実験の表示範囲内の話、一般には [仮定] が必要」と注記。書きすぎ NG

## 4. アクセシビリティ

- [ ] 全ての `<input type="range">` に `<label>` または `aria-label` がある
- [ ] 全ての `<button>` に意味のあるテキスト(絵文字だけは NG)がある
- [ ] SVG / Canvas / 3D ビューに `role="img"` と `aria-label` がある
- [ ] フォーカス時に枠が見える(`:focus-visible` は共通 CSS で設定済、上書きしていない)
- [ ] キーボード操作で全機能にアクセスできる(タブ移動 + スペース / 矢印キー)

## 5. モバイル対応

- [ ] PC で 2 カラム、モバイル(< 1024px)で 1 カラムに自動切替(`tool-grid` を使っていれば自動)
- [ ] スライダー thumb がモバイルで 30px 以上(共通 CSS で自動)
- [ ] ボタン min-height 48px(共通 CSS で自動)
- [ ] **iPhone Safari で実機 or DevTools の iPhone エミュレーションで動作確認した**(視覚確認)
- [ ] 横スクロールが発生していない

## 6. パフォーマンス

- [ ] ファイルサイズ ≤ 100 KB(超えるなら構造を見直す。Three.js / D3 系は除く)
- [ ] requestAnimationFrame ループは `RAFLoop` ヘルパーを使う(自前で `setInterval` を回さない)
  - **例外**: Three.js 雛形では `controls.update()` を毎フレーム呼ぶ必要があり `requestAnimationFrame` 直接で OK。代わりに `pagehide` で `renderer.dispose()` `geometry.dispose()` `material.dispose()` `controls.dispose()` を実行(memory leak 防止)
- [ ] スライダー `input` イベントで重い処理(数千点描画)を毎フレーム実行していない
- [ ] Three.js / D3 系はモバイルでも 30 fps 以上を維持

## 7. ハブ更新(data/chapters.json + build-hub.py に統一)

- [ ] `data/chapters.json` の該当章 sections に新規節が追記されている
  - `new-tool.py` 経由なら自動で追記される
  - 手動編集する場合は `python3 -c "import json; json.load(open('data/chapters.json'))"` で JSON syntax 確認
- [ ] `python3 scripts/build-hub.py` を実行してハブを再生成済み(`new-tool.py` 経由なら自動実行される)
- [ ] ハブから新規ツールへ辿れる(目視確認: ローカル http.server で確認)
  - `https://mikikof.github.io/toshin-web-tools/calculus/lesson-NN/` から該当節リンクをクリック → 新規ツール 200 OK

## 8. 動作確認(必須)

- [ ] `python3 -m http.server 8765` で起動 → `http://localhost:8765/tools/calculus/N-N.html` を開く
- [ ] **コンソールにエラーがない**
- [ ] **プリセット 3 つ全て**が意図通り動く
- [ ] **全スライダー**を動かして変化を確認
- [ ] PC + モバイル幅(DevTools のレスポンシブモード)両方で確認

## 9. 完全オフライン要件(雛形 saas-offline の場合)

- [ ] CDN 依存(`https://...` の `<script>` `<link>`)が**無い**
- [ ] フォントは system-ui 系のみ(Google Fonts も読み込まない)
- [ ] `<title>` に「(完全オフライン対応)」を付けるかは任意

## 10. commit / push

- [ ] commit メッセージは `feat: <chapter>-<section> <短縮タイトル>` 形式
- [ ] submodule(`toshin-web-tools`) で commit & push(先)
- [ ] 親リポ(`my-company`) で submodule 参照を進めて commit & push(後)
- [ ] **整合性レポート**(submodule SHA、Pages 配信、未コミット変更)をユーザーに見せて承認を取る

---

## 失敗パターン(やらかし事例 — 避ける)

- ❌ MathML を書かず KaTeX/MathJax の CDN を読み込む(雛形が saas-offline ならオフライン要件違反)
- ❌ プリセット 3 つが「α=0.1 / α=0.5 / α=1.0」のような単純なパラメータ違いだけ。意味のあるシナリオになっていない
- ❌ スライダーを 8 個以上配置して画面が破綻
- ❌ `console.log` を残したまま commit
- ❌ Three.js でメモリリーク(geometry / material を `dispose()` していない)
- ❌ submodule の参照進めを忘れて親リポを push → リモートで参照切れ
