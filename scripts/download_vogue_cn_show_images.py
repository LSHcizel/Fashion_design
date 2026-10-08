#!/usr/bin/env python3
"""Download evenly sampled runway looks from vogue.com.cn show pages.

Example:
  python scripts/download_vogue_cn_show_images.py \\
    --season 2026-aw-RTW \\
    --target 800 \\
    --out-dir fashion_research_dir/image_inverse/vogue_cn_fw26_batch2 \\
    --skip-existing-dir fashion_research_dir/image_inverse/vogue_cn_fw26
"""
from __future__ import annotations

import argparse
import json
import re
import ssl
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[1]
UA = {"User-Agent": "Mozilla/5.0 (compatible; fashion-agents/1.0)"}
IMG_RE = re.compile(r"https://shows\.vogueimg\.com\.cn[^\"'\s]+?/collection/(\d{5})-[^\"'\s]+?\.(?:jpg|jpeg|png|webp)", re.I)

# Priority brands for balanced coverage (slug as used on vogue.com.cn).
PRIORITY_SLUGS = [
    # existing FW26 batch
    "chanel",
    "christian-dior",
    "gucci",
    "balenciaga",
    "balmain",
    "bottega-veneta",
    "celine",
    "chloe",
    "dolce-gabbana",
    "dries-van-noten",
    "fendi",
    "hermes",
    "jil-sander",
    "khaite",
    "loewe",
    "acne-studios",
    "altuzarra",
    "comme-des-garcons",
    "erdem",
    "issey-miyake",
    "gabriela-hearst",
    "3-1-phillip-lim",
    "7-for-all-mankind",
    "all-in",
    "6397",
    # paper "other brands" gaps + hot houses
    "azzedine-alaia",
    "row",
    "schiaparelli",
    "prada",
    "miu-miu",
    "louis-vuitton",
    "saint-laurent",
    "valentino",
    "givenchy",
    "alexander-mcqueen",
    "maison-martin-margiela",
    "jacquemus",
    "max-mara",
    "burberry",
    "versace",
    "ferragamo",
    "ferragamo",  # keep one; dedupe later
    "salvatore-ferragamo",
    "tory-burch",
    "proenza-schouler",
    "rodarte",
    "sacai",
    "undercover",
    "yohji-yamamoto",
    "junya-watanabe",
    "noir-kei-ninomiya",
    "stella-mccartney",
    "victoria-beckham",
    "simon-rocha",
    "simone-rocha",
    "jw-anderson",
    "jw-anderson",
    "j-w-anderson",
    "lemiare",
    "lemaire",
    "the-row",
    "row",
    "alaia",
    "azzedine-alaia",
    "mugler",
    "coperni",
    "courreges",
    "courrèges",
    "courreges",
    "lanvin",
    "nina-ricci",
    "paco-rabanne",
    "rabanne",
    "issey-miyake",
    "kenzo",
    "isabel-marant",
    "toteme",
    "nanushka",
    "ganni",
    "sportmax",
    "msgm",
    "moschino",
    "diesel",
    "off-white",
    "rick-owens",
    "ann-demeulemeester",
    "haider-ackermann",
    "thom-browne",
    "ralph-lauren",
    "michael-kors",
    "carolina-herrera",
    "oscar-de-la-renta",
    "marchesa",
    "zimmermann",
    "self-portrait",
    "ulla-johnson",
    "ganne",
    "collina-strada",
    "eckhaus-latta",
    "area",
    "luar",
    "toga",
    "sacai",
    "cfcl",
    "anrealage",
    "noir-kei-ninomiya",
    "comme-des-garcons-homme-plus",
    "hui",
    "shuting-qiu",
    "angel-chen",
    "susan-fang",
    "shang-xia",
    "uma-wang",
]


def unique_preserve(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        key = item.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def http_get(url: str, timeout: int = 60) -> bytes:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
        return resp.read()


def parse_looks(html: str) -> dict[str, dict[str, str]]:
    """Map look_id -> {M, L, S, raw} preferring largest available later."""
    looks: dict[str, dict[str, str]] = {}
    for m in IMG_RE.finditer(html):
        url = m.group(0)
        look = m.group(1)
        size = "raw"
        if url.endswith("_L.jpg") or "_L." in url:
            size = "L"
        elif url.endswith("_M.jpg") or "_M." in url:
            size = "M"
        elif url.endswith("_S.jpg") or "_S." in url:
            size = "S"
        bucket = looks.setdefault(look, {})
        bucket[size] = url
    return looks


def choose_url(sizes: dict[str, str]) -> tuple[str, str | None]:
    primary = sizes.get("L") or sizes.get("M") or sizes.get("S") or next(iter(sizes.values()))
    fallback = None
    if "L" in sizes and "M" in sizes:
        primary, fallback = sizes["L"], sizes["M"]
    elif "M" in sizes and "S" in sizes:
        primary, fallback = sizes["M"], sizes["S"]
    return primary, fallback


def evenly_sample(look_ids: list[str], k: int) -> list[str]:
    if k <= 0 or not look_ids:
        return []
    if k >= len(look_ids):
        return look_ids
    if k == 1:
        return [look_ids[len(look_ids) // 2]]
    # skip very first/last if enough room (often detail/exit looks)
    ids = look_ids
    n = len(ids)
    idxs = [round(i * (n - 1) / (k - 1)) for i in range(k)]
    # unique while preserving order
    out: list[str] = []
    seen: set[int] = set()
    for i in idxs:
        if i in seen:
            # nudge forward
            j = i
            while j < n and j in seen:
                j += 1
            if j >= n:
                j = i
                while j >= 0 and j in seen:
                    j -= 1
            i = max(0, min(n - 1, j))
        seen.add(i)
        out.append(ids[i])
    return out


def load_existing_keys(dirs: list[Path]) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    for d in dirs:
        if not d:
            continue
        man = d / "manifest.jsonl"
        if man.exists():
            for line in man.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                keys.add((str(row.get("slug", "")).lower(), str(row.get("look", "")).zfill(5)))
        for p in d.glob("*_*.jpg"):
            # brand_season_look.jpg
            name = p.stem
            parts = name.rsplit("_", 2)
            if len(parts) >= 3:
                slug = parts[0]
                look = parts[-1]
                keys.add((slug.lower(), look.zfill(5)))
    return keys


def discover_brand_slugs(shows_html_path: Path | None = None) -> list[str]:
    path = shows_html_path or (REPO_ROOT / "tmp_vogue_shows.html")
    if not path.exists():
        html = http_get("https://www.vogue.com.cn/shows/").decode("utf-8", "replace")
        path.write_text(html, encoding="utf-8")
    else:
        html = path.read_text(encoding="utf-8")
    found = re.findall(r"/shows/([a-zA-Z0-9.\-_]+)/", html)
    return unique_preserve(found)


def probe_show(slug: str, season: str) -> tuple[str, dict[str, dict[str, str]] | None, str]:
    page = f"https://www.vogue.com.cn/shows/{slug}/{season}/"
    try:
        html = http_get(page).decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        return page, None, f"fetch_fail:{exc}"
    looks = parse_looks(html)
    if not looks:
        return page, None, "no_looks"
    return page, looks, "ok"


def download_one(url: str, dest: Path, fallback: str | None = None) -> tuple[bool, str, int]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    for candidate in [url, fallback]:
        if not candidate:
            continue
        try:
            data = http_get(candidate, timeout=90)
            if len(data) < 1500:
                continue
            dest.write_bytes(data)
            return True, candidate, len(data)
        except Exception:
            continue
    return False, url, 0


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Download vogue.com.cn runway looks")
    p.add_argument("--season", default="2026-aw-RTW")
    p.add_argument("--target", type=int, default=800, help="目标新增图片数")
    p.add_argument(
        "--out-dir",
        type=Path,
        default=REPO_ROOT / "fashion_research_dir/image_inverse/vogue_cn_fw26_batch2",
    )
    p.add_argument(
        "--skip-existing-dir",
        action="append",
        default=[],
        help="已有下载目录（可重复），跳过相同 slug+look",
    )
    p.add_argument("--per-brand-min", type=int, default=4)
    p.add_argument("--per-brand-max", type=int, default=16)
    p.add_argument("--sleep", type=float, default=0.35)
    p.add_argument("--probe-only", action="store_true")
    p.add_argument("--brand", action="append", default=[], help="仅这些品牌 slug")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    out_dir: Path = args.out_dir
    if not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    skip_dirs = []
    for d in args.skip_existing_dir or [
        REPO_ROOT / "fashion_research_dir/image_inverse/vogue_cn_fw26"
    ]:
        skip_dirs.append(d if Path(d).is_absolute() else REPO_ROOT / d)
    existing = load_existing_keys(skip_dirs + [out_dir])
    print(f"skip existing keys: {len(existing)}")

    if args.brand:
        slugs = unique_preserve(args.brand)
    else:
        discovered = discover_brand_slugs()
        # Priority first, then fill from site brand index (cap probe budget).
        slugs = unique_preserve(PRIORITY_SLUGS + discovered)
        # Hard cap probing to keep runtime reasonable.
        slugs = slugs[:220]

    season_tag = "fw26" if "aw" in args.season.lower() else "ss26"
    if "2026" in args.season and "ss" in args.season.lower():
        season_tag = "ss26"

    # Probe available shows first
    available: list[tuple[str, str, dict[str, dict[str, str]]]] = []
    probe_log = out_dir / "probe_log.jsonl"
    with probe_log.open("w", encoding="utf-8") as flog:
        for i, slug in enumerate(slugs):
            page, looks, status = probe_show(slug, args.season)
            row = {"slug": slug, "page": page, "status": status, "n_looks": len(looks or {})}
            flog.write(json.dumps(row, ensure_ascii=False) + "\n")
            if looks:
                available.append((slug, page, looks))
                print(f"[{i+1}/{len(slugs)}] OK {slug}: {len(looks)} looks")
            elif i < 60:
                print(f"[{i+1}/{len(slugs)}] skip {slug}: {status}")
            time.sleep(args.sleep)
            # Enough brand capacity for target at per-brand-max.
            capacity = sum(min(args.per_brand_max, len(lk)) for _, _, lk in available)
            if capacity >= args.target + 50 and len(available) >= 40:
                print(f"probe stop early: brands={len(available)} capacity~{capacity}")
                break

    print(f"available shows: {len(available)}")
    if args.probe_only:
        return

    # Allocate looks per brand to hit target with coverage
    n_brands = max(1, len(available))
    base = max(args.per_brand_min, min(args.per_brand_max, max(1, args.target // n_brands)))
    plan: dict[str, int] = {slug: min(base, len(looks)) for slug, _, looks in available}

    def count_new_for_plan() -> int:
        total = 0
        for slug, _, looks in available:
            for lk in evenly_sample(sorted(looks.keys()), plan[slug]):
                if (slug, lk) not in existing:
                    total += 1
        return total

    guard = 0
    while count_new_for_plan() < args.target and guard < 3000:
        guard += 1
        progressed = False
        for slug, _, looks in sorted(available, key=lambda x: -len(x[2])):
            if plan[slug] < min(args.per_brand_max, len(looks)):
                plan[slug] += 1
                progressed = True
                if count_new_for_plan() >= args.target:
                    break
        if not progressed:
            break

    print(f"planned new downloads ~{count_new_for_plan()} across {n_brands} brands (base={base})")

    manifest_path = out_dir / "manifest.jsonl"
    saved = 0
    failed = 0
    by_brand: dict[str, int] = defaultdict(int)

    with manifest_path.open("a", encoding="utf-8") as mf:
        for slug, page, looks in available:
            if saved >= args.target:
                break
            look_ids = sorted(looks.keys())
            for look in evenly_sample(look_ids, plan[slug]):
                if saved >= args.target:
                    break
                if (slug, look) in existing:
                    continue
                url, fallback = choose_url(looks[look])
                fname = f"{slug}_{season_tag}_{look}.jpg"
                dest = out_dir / fname
                ok, used, nbytes = download_one(url, dest, fallback)
                row = {
                    "slug": slug,
                    "look": look,
                    "page": page,
                    "image_url": url,
                    "fallback_url": fallback,
                    "file": str(dest),
                    "bytes": nbytes,
                    "saved_url": used if ok else None,
                    "ok": ok,
                }
                mf.write(json.dumps(row, ensure_ascii=False) + "\n")
                mf.flush()
                if ok:
                    saved += 1
                    by_brand[slug] += 1
                    existing.add((slug, look))
                    print(f"saved {saved}/{args.target}: {fname} ({nbytes}B)")
                else:
                    failed += 1
                    print(f"FAIL {fname}")
                time.sleep(args.sleep)

    summary = {
        "season": args.season,
        "target": args.target,
        "saved": saved,
        "failed": failed,
        "brands": dict(sorted(by_brand.items(), key=lambda x: (-x[1], x[0]))),
        "out_dir": str(out_dir),
        "source": "https://www.vogue.com.cn/shows/",
    }
    (out_dir / "download_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
