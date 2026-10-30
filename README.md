# ダイエット管理プロジェクト

毎日の体重・食事・運動を記録し、Claude と会話しながら無理なく減量を続けるためのプロジェクトです。
Claude Code でこのフォルダを開くと、`CLAUDE.md` のルールに沿って「ダイエットの伴走コーチ」として返答します。

## 使い方

| コマンド | すること | 例 |
|---|---|---|
| `/log` | 話した内容を解析して記録に追記 | `/log 体重72.4、昼はそば、5km歩いた` |
| `/today` | 今日の食事ルールを○△×で振り返り、明日へのひとこと | `/today` |
| `/week` | 直近7日の体重・運動・ルール達成率と来週の重点（グラフ付き） | `/week` |
| `/menu` | 減塩・時短・子どもも食べられる夕食3案 | `/menu 豚こま、キャベツ、卵` |

最初に `data/goal.md` に現在の体重・目標体重・期限を書いておくと、ペースの判断に使われます。

## フォルダ構成

```
CLAUDE.md                 Claude の役割と私のルール
.claude/commands/         スラッシュコマンド（log / today / week / menu）
data/
  weight.csv              体重（date, weight_kg, memo）
  exercise.csv            運動（date, type, distance_km, minutes, memo）
  meals/YYYY-MM-DD.md     その日の食事とルールチェック（_template.md が書式）
  goal.md                 目標
scripts/plot_weight.py    体重グラフ（7日移動平均付き）→ data/weight.png
```

## 体重グラフ

```bash
pip install matplotlib                      # 初回のみ
python3 scripts/plot_weight.py              # 全期間
python3 scripts/plot_weight.py --days 30    # 直近30日
```

## 同じリポジトリにあるアプリ

- 📔 毎日日記：`index.html`
- 🥗 マイダイエット（スマホ用アプリ）：`diet.html`

GitHub Pages で公開しています。`_config.yml` で `data/` などはサイトに出ないようにしています。
- 📒 ダイエット記録（data/ の記録を見るアプリ）：`coach.html`
