# toshin-web-tools

受験数学の Web ツール集。
**微分積分学編** から順次拡充していきます。

## 公開サイト

- <https://mikikof.github.io/toshin-web-tools/>

## 構成

```
toshin-web-tools/
├── index.html              ハブ(分野別の入口)
├── calculus/               微分積分学編
│   ├── index.html          第1〜12回 一覧
│   └── lesson-NN/          各回(中身はページ内で完結する HTML/JS で実装)
└── assets/
    └── style.css           共通スタイル
```

## 開発メモ

- デザインは [mikikof-lab](https://mikikof.github.io/mikikof-lab/) のデザイントークンを踏襲
- 各回のページは静的 HTML(必要に応じて inline JS で計算/可視化を実装)
- 配信は GitHub Pages(main ブランチ root から)

## 関連リポ

- [mikikof-lab](https://github.com/mikikof/mikikof-lab) — 高校生向け学習ツール集
- [toshin-linear-algebra](https://github.com/mikikof/toshin-linear-algebra) — 東進・線形代数(PRIVATE)
