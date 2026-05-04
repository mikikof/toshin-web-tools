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

## 2. 教育設計(必須)

- [ ] 「**このツールで体感すること**」カードに、学習者が**動かして何を発見するか**を 1〜2 文で書いている(教科書の引き写しではない)
- [ ] **プリセット 3 つ**(押すだけ体験)があり、それぞれが意味のあるシナリオに対応(典型例 / 極端な値 / 反例 など)
- [ ] **スライダーは 2〜6 個**(増やしすぎない、減らしすぎない)
- [ ] 「**気づき**」を仕掛ける構造がある(極端値で発散、反例の対比、隠す→予測 など、いずれか 1 つ以上)
- [ ] **教師目線の「答え」を直接書いていない**。学習者が触って気づく構造になっている
- [ ] 段階的難易度(プリセット → 単一パラメータ → 複数 → 比較 / 反例)を意識している

## 3. 数式表示(必須)

- [ ] 主要な数式は `<math>` (MathML) で書いている
- [ ] **MathML 未対応ブラウザ向けに ASCII / code 表記を併記**(`<code class="tool-mono">...</code>`)
- [ ] 数式に `aria-label` で読み上げテキストを付けている

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
- [ ] スライダー `input` イベントで重い処理(数千点描画)を毎フレーム実行していない
- [ ] Three.js / D3 系はモバイルでも 30 fps 以上を維持

## 7. ハブ更新

- [ ] `scripts/_chapters.py`(または `scripts/build-hub.py`)の CHAPTERS dict に追記済み
- [ ] `python3 scripts/build-hub.py` を実行してハブを再生成済み
- [ ] ハブから新規ツールへ辿れる(目視確認: ローカル http.server で確認)

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
