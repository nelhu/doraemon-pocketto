#!/usr/bin/env python3
"""Generate a compact, self-contained simulated page-load waterfall fragment."""

from __future__ import annotations

import argparse
import html
import math
import random
import secrets
from pathlib import Path

PROFILES = {
    "wifi": ("Wi-Fi", 0.68),
    "fast4g": ("Fast 4G", 1.0),
    "slow4g": ("Slow 4G", 1.72),
}
COLORS = (
    "var(--viz-series-1, #2563eb)",
    "var(--viz-series-4, #9333ea)",
    "var(--viz-series-2, #16a34a)",
    "var(--viz-series-3, #d97706)",
    "var(--viz-series-6, #e11d48)",
    "var(--viz-series-5, #0891b2)",
)
MILESTONE_COLORS = {
    "TTFB": "var(--viz-series-1, #2563eb)",
    "FCP": "var(--viz-series-4, #9333ea)",
    "LCP": "var(--viz-series-3, #d97706)",
    "TTI": "var(--viz-series-6, #e11d48)",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="destination .html fragment")
    parser.add_argument("--profile", choices=PROFILES, default="fast4g")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--title", default="前端页面加载耗时")
    return parser.parse_args()


def format_ms(value: int) -> str:
    if value >= 1000:
        digits = 2 if value >= 2000 else 1
        return f"{value / 1000:.{digits}f} s"
    return f"{value} ms"


def build_sample(rng: random.Random, multiplier: float) -> tuple[list[dict[str, int | str]], dict[str, int]]:
    ttfb = rng.randint(150, 230)
    document_duration = rng.randint(300, 410)
    css_start = rng.randint(150, 240)
    css_duration = rng.randint(340, 470)
    app_start = rng.randint(230, 350)
    app_duration = rng.randint(820, 1080)
    hero_start = rng.randint(470, 650)
    hero_duration = rng.randint(820, 1080)
    api_start = rng.randint(760, 980)
    api_duration = rng.randint(520, 720)
    hydration_start = max(app_start + app_duration - rng.randint(30, 100), 1120)
    hydration_duration = rng.randint(820, 1080)

    tasks = [
        {"name": "Document", "start": 0, "duration": document_duration},
        {"name": "critical.css", "start": css_start, "duration": css_duration},
        {"name": "app.js", "start": app_start, "duration": app_duration},
        {"name": "hero.webp", "start": hero_start, "duration": hero_duration},
        {"name": "/api/home", "start": api_start, "duration": api_duration},
        {"name": "Hydration", "start": hydration_start, "duration": hydration_duration},
    ]
    fcp = max(css_start + css_duration, ttfb + 320)
    lcp = max(hero_start + hero_duration, fcp + 420)
    tti = max(hydration_start + hydration_duration, lcp + 340)
    milestones = {"TTFB": ttfb, "FCP": fcp, "LCP": lcp, "TTI": tti}

    for task in tasks:
        task["start"] = round(int(task["start"]) * multiplier)
        task["duration"] = round(int(task["duration"]) * multiplier)
    milestones = {name: round(value * multiplier) for name, value in milestones.items()}
    return tasks, milestones


def build_fragment(title: str, profile: str, seed: int) -> str:
    profile_label, multiplier = PROFILES[profile]
    tasks, milestones = build_sample(random.Random(seed), multiplier)
    maximum = max(
        milestones["TTI"],
        *(int(task["start"]) + int(task["duration"]) for task in tasks),
    )
    ceiling = math.ceil(maximum * 1.08 / 500) * 500
    root_id = f"viz-load-{seed:08x}"
    summary_id = f"{root_id}-summary"

    metric_html = "".join(
        f"""<div class="vpw-metric" style="--vpw-color:{MILESTONE_COLORS[name]}">
          <span class="vpw-key"><i></i>{name}</span>
          <strong>{format_ms(value)}</strong>
        </div>"""
        for name, value in milestones.items()
    )
    ticks = "".join(
        f"<span>{format_ms(round(ceiling * index / 4))}</span>" for index in range(5)
    )
    milestone_lines = "".join(
        f'<i class="vpw-mark" style="left:{value / ceiling * 100:.3f}%;--vpw-color:{MILESTONE_COLORS[name]}"></i>'
        for name, value in milestones.items()
    )
    rows = []
    for index, task in enumerate(tasks):
        name = html.escape(str(task["name"]))
        start = int(task["start"])
        duration = int(task["duration"])
        rows.append(
            f"""<div class="vpw-row">
          <strong>{name}</strong>
          <div class="vpw-track" aria-label="{name} 从 {format_ms(start)} 开始，耗时 {format_ms(duration)}">
            {milestone_lines}
            <i class="vpw-bar" style="left:{start / ceiling * 100:.3f}%;width:{duration / ceiling * 100:.3f}%;--vpw-color:{COLORS[index]}"></i>
          </div>
          <span>{format_ms(duration)}</span>
        </div>"""
        )

    longest = max(tasks, key=lambda task: int(task["duration"]))
    longest_duration = int(longest["duration"])
    share = round(longest_duration / milestones["TTI"] * 100)
    summary = (
        f"{html.escape(str(longest['name']))} 持续 {format_ms(longest_duration)}，"
        f"约占 {profile_label} 档 TTI 的 {share}%。"
    )

    return f"""<section id="{root_id}" class="vpw" aria-labelledby="{root_id}-title">
  <style>
    #{root_id}{{width:100%;max-width:100%;overflow:hidden;color:var(--foreground,#18181b);background:var(--card,#fff);border:1px solid var(--border,#e4e4e7);border-radius:18px;font-family:ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
    #{root_id},#{root_id} *{{box-sizing:border-box}}
    #{root_id} .vpw-head{{display:flex;justify-content:space-between;gap:18px;padding:22px;border-bottom:1px solid var(--border,#e4e4e7)}}
    #{root_id} .vpw-kicker{{margin:0 0 7px;color:var(--muted-foreground,#71717a);font-size:11px;font-weight:700;letter-spacing:.13em;text-transform:uppercase}}
    #{root_id} h2{{margin:0;font-size:clamp(23px,4vw,32px);line-height:1.12;letter-spacing:-.035em}}
    #{root_id} .vpw-copy{{max-width:560px;margin:9px 0 0;color:var(--muted-foreground,#71717a);font-size:13px;line-height:1.5}}
    #{root_id} .vpw-profile{{align-self:flex-start;padding:8px 11px;border-radius:9px;background:var(--muted,#f4f4f5);color:var(--muted-foreground,#71717a);font-size:12px;font-weight:700;white-space:nowrap}}
    #{root_id} .vpw-metrics{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));border-bottom:1px solid var(--border,#e4e4e7)}}
    #{root_id} .vpw-metric{{padding:16px 20px}}
    #{root_id} .vpw-metric+ .vpw-metric{{border-left:1px solid var(--border,#e4e4e7)}}
    #{root_id} .vpw-key{{display:flex;align-items:center;gap:7px;margin-bottom:7px;color:var(--muted-foreground,#71717a);font-size:11px;font-weight:700;letter-spacing:.06em}}
    #{root_id} .vpw-key i{{width:8px;height:8px;border-radius:50%;background:var(--vpw-color)}}
    #{root_id} .vpw-metric strong{{font-size:clamp(21px,4vw,28px);font-variant-numeric:tabular-nums}}
    #{root_id} figure{{margin:0;padding:22px}}
    #{root_id} figcaption{{display:flex;justify-content:space-between;gap:12px;margin-bottom:16px;font-size:16px;font-weight:700}}
    #{root_id} figcaption span{{color:var(--muted-foreground,#71717a);font-size:11px;font-weight:400}}
    #{root_id} .vpw-axis,#{root_id} .vpw-row{{display:grid;grid-template-columns:104px minmax(0,1fr) 58px;gap:12px;align-items:center}}
    #{root_id} .vpw-axis{{margin-bottom:7px;color:var(--muted-foreground,#71717a);font-size:10px}}
    #{root_id} .vpw-ticks{{display:flex;justify-content:space-between}}
    #{root_id} .vpw-rows{{display:grid;gap:7px}}
    #{root_id} .vpw-row>strong{{overflow:hidden;font-size:12px;text-overflow:ellipsis;white-space:nowrap}}
    #{root_id} .vpw-row>span{{color:var(--muted-foreground,#71717a);font-size:11px;text-align:right;white-space:nowrap}}
    #{root_id} .vpw-track{{position:relative;height:38px;overflow:hidden;border-radius:9px;background:var(--muted,#f4f4f5)}}
    #{root_id} .vpw-bar{{position:absolute;top:10px;height:18px;min-width:4px;border-radius:6px;background:var(--vpw-color)}}
    #{root_id} .vpw-mark{{position:absolute;inset-block:0;width:1px;background:var(--vpw-color);opacity:.55}}
    #{root_id} .vpw-summary{{margin:17px 22px 22px;padding:13px 15px;border-left:3px solid var(--viz-series-2,#16a34a);border-radius:0 10px 10px 0;background:var(--muted,#f4f4f5);font-size:12px;line-height:1.5}}
    #{root_id} .vpw-summary strong{{margin-right:8px}}
    @media(max-width:520px){{
      #{root_id} .vpw-head{{display:grid;padding:17px}}
      #{root_id} .vpw-profile{{justify-self:start}}
      #{root_id} .vpw-metrics{{grid-template-columns:repeat(2,minmax(0,1fr))}}
      #{root_id} .vpw-metric{{padding:14px 16px}}
      #{root_id} .vpw-metric:nth-child(3){{border-left:0}}
      #{root_id} .vpw-metric:nth-child(n+3){{border-top:1px solid var(--border,#e4e4e7)}}
      #{root_id} figure{{padding:17px}}
      #{root_id} figcaption{{display:block}}
      #{root_id} figcaption span{{display:block;margin-top:4px}}
      #{root_id} .vpw-axis,#{root_id} .vpw-row{{grid-template-columns:1fr 52px;gap:5px 8px}}
      #{root_id} .vpw-axis>i{{display:none}}
      #{root_id} .vpw-ticks,#{root_id} .vpw-track{{grid-column:1/-1}}
      #{root_id} .vpw-track{{height:32px}}
      #{root_id} .vpw-bar{{top:7px}}
      #{root_id} .vpw-summary{{margin:15px 17px 17px}}
    }}
  </style>
  <header class="vpw-head">
    <div>
      <p class="vpw-kicker">Performance waterfall · 随机模拟</p>
      <h2 id="{root_id}-title">{html.escape(title)}</h2>
      <p class="vpw-copy">共享时间轴展示资源下载与主线程执行如何共同推迟可见内容和稳定交互。数值仅用于展示效果。</p>
    </div>
    <span class="vpw-profile">{profile_label}</span>
  </header>
  <div class="vpw-metrics" aria-label="页面性能里程碑">{metric_html}</div>
  <figure role="img" aria-describedby="{summary_id}">
    <figcaption>资源与主线程 waterfall <span>横轴：导航开始后的累计时间</span></figcaption>
    <div class="vpw-axis" aria-hidden="true"><i></i><div class="vpw-ticks">{ticks}</div><i></i></div>
    <div class="vpw-rows">{''.join(rows)}</div>
  </figure>
  <p class="vpw-summary" id="{summary_id}"><strong>主要瓶颈</strong>{summary}</p>
</section>
"""


def main() -> int:
    args = parse_args()
    if args.output.suffix.lower() != ".html":
        raise SystemExit("output must use a .html extension")
    seed = args.seed if args.seed is not None else secrets.randbits(32)
    fragment = build_fragment(args.title, args.profile, seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(fragment, encoding="utf-8")
    print(f"{args.output.resolve()} seed={seed} profile={args.profile}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
