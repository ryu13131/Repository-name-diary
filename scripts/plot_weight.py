#!/usr/bin/env python3
"""data/weight.csv から体重推移グラフ（7日移動平均付き）を PNG で出力する。

使い方:
    python3 scripts/plot_weight.py              # 全期間 → data/weight.png
    python3 scripts/plot_weight.py --days 30    # 直近30日
    python3 scripts/plot_weight.py --out graph.png

data/goal.md に目標体重が書いてあれば、目標ラインも引く。
"""
import argparse
import csv
import re
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = ROOT / "data" / "weight.csv"
DEFAULT_OUT = ROOT / "data" / "weight.png"
GOAL_MD = ROOT / "data" / "goal.md"

JP_FONTS = ["Hiragino Sans", "Hiragino Kaku Gothic ProN", "Yu Gothic", "Meiryo",
            "Noto Sans CJK JP", "Noto Sans JP", "IPAexGothic", "IPAGothic",
            "TakaoGothic", "WenQuanYi Zen Hei"]


def read_weights(path):
    """(date, kg) のリストを日付順で返す。同じ日付は後の行を優先。"""
    rows = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                d = date.fromisoformat((r.get("date") or "").strip())
                kg = float((r.get("weight_kg") or "").strip())
            except ValueError:
                continue  # 空行や書き間違いは飛ばす
            rows[d] = kg
    return sorted(rows.items())


def read_goal(path):
    """goal.md の「目標体重」の数値を返す（なければ None）。"""
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if "目標体重" in line:
            m = re.search(r"\|\s*([0-9]+(?:\.[0-9]+)?)\s*\|?\s*$", line)
            if m:
                return float(m.group(1))
    return None


def moving_average(points, window=7):
    """記録のある日ごとに、その日を含む直近 window 日の平均を出す（記録のない日は飛ばす）。"""
    out = []
    for d, _ in points:
        vals = [kg for dd, kg in points if d - timedelta(days=window - 1) <= dd <= d]
        out.append(sum(vals) / len(vals))
    return out


def pick_font(font_manager):
    names = {f.name for f in font_manager.fontManager.ttflist}
    return next((n for n in JP_FONTS if n in names), None)


def main():
    ap = argparse.ArgumentParser(description="体重推移グラフを作る")
    ap.add_argument("--csv", default=str(DEFAULT_CSV), help="体重CSV（既定: data/weight.csv）")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="出力PNG（既定: data/weight.png）")
    ap.add_argument("--days", type=int, default=0, help="直近N日だけ表示（0=全期間）")
    args = ap.parse_args()

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.dates as mdates
        import matplotlib.pyplot as plt
        from matplotlib import font_manager
    except ImportError:
        print("matplotlib が見つかりません。`pip install matplotlib` でインストールしてください。")
        return 1

    points = read_weights(args.csv)
    if args.days > 0 and points:
        start = points[-1][0] - timedelta(days=args.days - 1)
        # 移動平均の計算用に、表示範囲より6日前から読む
        calc = [p for p in points if p[0] >= start - timedelta(days=6)]
        ma_all = moving_average(calc)
        pairs = [(p, m) for p, m in zip(calc, ma_all) if p[0] >= start]
        points = [p for p, _ in pairs]
        ma = [m for _, m in pairs]
    else:
        ma = moving_average(points)

    if len(points) < 2:
        print("体重の記録が2件未満のため、グラフは作りませんでした。")
        return 0

    font = pick_font(font_manager)
    if font:
        plt.rcParams["font.family"] = font
        L = {"daily": "体重", "ma": "7日移動平均", "goal": "目標", "title": "体重の推移", "y": "kg"}
    else:  # 日本語フォントがない環境では英語ラベル
        L = {"daily": "Weight", "ma": "7-day average", "goal": "Goal", "title": "Weight", "y": "kg"}

    dates = [d for d, _ in points]
    kgs = [kg for _, kg in points]
    goal = read_goal(GOAL_MD)

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=120)
    ax.plot(dates, kgs, "o", color="#9ccfb6", markersize=4, label=L["daily"])
    ax.plot(dates, ma, "-", color="#2f8f6a", linewidth=2.5, label=L["ma"])
    if goal:
        ax.axhline(goal, color="#e0803b", linestyle="--", linewidth=1.5, label=f'{L["goal"]} {goal:g}kg')

    first, last = kgs[0], kgs[-1]
    diff = last - first
    ax.set_title(f'{L["title"]}  {dates[0]:%m/%d} {first:.1f}kg → {dates[-1]:%m/%d} {last:.1f}kg ({diff:+.1f})')
    ax.set_ylabel(L["y"])
    ax.grid(axis="y", color="#e6ece9")
    ax.spines[["top", "right"]].set_visible(False)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=8))
    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    print(f"グラフを保存しました: {out}（{len(points)}件、{dates[0]}〜{dates[-1]}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
