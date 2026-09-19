#!/usr/bin/env python3
"""GitHub 想法查重 —— 批量仓库检索。

用法:
    python scan.py                 # 跑内置示例清单
    python scan.py queries.txt     # 每行 "标签<TAB>检索式" 或 "标签 | 检索式"

匿名额度: core 60/h, search 10/min。脚本已内置节流与 403 重试。
"""
import json
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

socket.setdefaulttimeout(25)

API = "https://api.github.com/search/repositories?q={q}&per_page={n}"
HEADERS = {"User-Agent": "wb-prior-art-scan", "Accept": "application/vnd.github+json"}
GAP = 7.5          # 两次搜索之间的间隔（匿名限额 10/分钟）
RATE_WAIT = 68     # 撞到 403 后的冷却时间
NOISE = ("awesome-", "free-for-dev", "project-based-learning",
         "design-resources", "build-your-own-x", "public-apis")


def gh_search(query, n=6, tries=3):
    """返回 items 列表；额度耗尽时冷却重试。"""
    url = API.format(q=urllib.parse.quote(query), n=n)
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req) as r:
                return json.load(r)["items"]
        except urllib.error.HTTPError as e:
            if e.code == 403 and attempt < tries - 1:
                print(f"    [{query}] 额度耗尽，冷却 {RATE_WAIT}s ...")
                time.sleep(RATE_WAIT)
                continue
            raise
    return []


def is_noise(full_name, description):
    """过滤通用 awesome 清单之类的噪音。"""
    low = (full_name + " " + (description or "")).lower()
    return any(tag in low for tag in NOISE)


def scan(queries):
    """queries: [(标签, 检索式), ...]"""
    report = []
    for label, q in queries:
        try:
            items = gh_search(q)
        except Exception as exc:                       # noqa: BLE001
            report.append((label, q, f"ERR {exc}", []))
            time.sleep(GAP)
            continue
        hits, dropped = [], []
        for i in items:
            desc = (i.get("description") or "")[:105]
            if is_noise(i["full_name"], desc):
                dropped.append(i["full_name"])
                continue
            hits.append((i["full_name"], i["stargazers_count"], i.get("language"), desc))
        report.append((label, q, len(hits), hits, dropped))
        time.sleep(GAP)
    return report


def pretty(report):
    for row in report:
        label, q, total, hits = row[0], row[1], row[2], row[3]
        dropped = row[4] if len(row) > 4 else []
        print(f"### {label}\n    query: {q}\n    有效命中: {total}")
        for fn, star, lang, desc in hits:
            print(f"      {fn}  star={star}  [{lang}]  {desc}")
        if dropped:
            print(f"      (已剔除噪音 {len(dropped)}: {', '.join(dropped[:3])})")
        print()


DEFAULT = [
    ("A 签名照片->矢量SVG", "signature vectorization in:name,description"),
    ("A2 手写->SVG", "handwriting svg in:name,description"),
    ("B 去水印", "watermark removal in:name,description"),
    ("C 文档去阴影/清晰化", "document shadow removal enhancement in:name,description"),
    ("D 表格识别->Excel", "table extraction image in:name,description"),
    ("E 学习计划生成", "study plan generator in:name,description"),
    ("F MCP 记忆/上下文", "memory context mcp server in:name,description"),
]


def load(path):
    qs = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        sep = "\t" if "\t" in line else "|"
        label, _, query = line.partition(sep)
        qs.append((label.strip(), query.strip()))
    return qs


if __name__ == "__main__":
    queries = load(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    print(f"共 {len(queries)} 条检索式，预计耗时 {len(queries) * GAP:.0f}s\n")
    pretty(scan(queries))
