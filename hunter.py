#!/usr/bin/env python3
"""
github-ui-bug-hunter/hunter.py — Flutter 工具类 App 点击无响应 Bug 猎手

Requirements: Python 3.8+, GitHub CLI authenticated (gh auth login)

Usage:
  python hunter.py                      # 读取 .env 默认参数
  python hunter.py --platform ios       # 只看 iOS 的点击 bug
  python hunter.py --output-format json # 输出 JSON
"""

import argparse
import csv
import json
import math
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


# ─────────────────────────────── .env 加载 ──────────────────────────────── #

def load_env():
    env_path = Path(__file__).parent / ".env"
    env = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env


ENV = load_env()


def _env_get(key, default):
    val = ENV.get(key)
    if val is None:
        return default
    return int(val) if isinstance(default, int) else val


def _load_csv_keywords(filename: str) -> list:
    """Load first column from keywords/{filename}.csv, skip header row."""
    csv_path = Path(__file__).parent / "keywords" / filename
    if not csv_path.exists():
        print(f"[warn] keywords/{filename} 不存在，该关键词列表为空", file=sys.stderr)
        return []
    keywords = []
    with csv_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            kw = row.get("keyword", "").strip()
            if kw:
                keywords.append(kw)
    if not keywords:
        print(f"[warn] keywords/{filename} 为空文件，该关键词列表为空", file=sys.stderr)
    return keywords


def _load_blacklist() -> set:
    """Load blacklisted repo full_names from blacklist.csv."""
    bl_path = Path(__file__).parent / "blacklist.csv"
    if not bl_path.exists():
        return set()
    repos = set()
    with bl_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            repo = row.get("repo", "").strip()
            if repo:
                repos.add(repo.lower())
    return repos


# ─────────────── Keywords — sourced from keywords/*.csv ─────────────────── #

INTERACTION_KEYWORDS = _load_csv_keywords("interaction.csv")
ANDROID_KEYWORDS    = _load_csv_keywords("android.csv")
IOS_KEYWORDS        = _load_csv_keywords("ios.csv")
TOOL_APP_KEYWORDS   = _load_csv_keywords("tool_app.csv")
NON_APP_SIGNALS     = _load_csv_keywords("non_app_signals.csv")
TOOL_CATEGORIES     = _load_csv_keywords("tool_categories.csv")

BLACKLIST = _load_blacklist()


# ─────────────────── Fuzzy Matching (Minimum Edit Distance) ─────────────── #

def edit_distance(a: str, b: str) -> int:
    """Levenshtein distance between two strings (O(m*n) DP)."""
    if a == b:
        return 0
    m, n = len(a), len(b)
    if m < n:
        a, b, m, n = b, a, n, m
    dp = list(range(n + 1))
    for ch_a in a:
        prev, dp[0] = dp[0], dp[0] + 1
        for j, ch_b in enumerate(b, 1):
            prev, dp[j] = dp[j], prev if ch_a == ch_b else 1 + min(prev, dp[j], dp[j - 1])
    return dp[n]


def _threshold(kw: str) -> int:
    """Allowed edit distance based on keyword length.
    ≤4 chars  → 0 (exact only, avoids false positives on short words)
    5-8 chars → 1 (one typo allowed)
    ≥9 chars  → 2 (two typos allowed)
    """
    n = len(kw)
    if n <= 4:
        return 0
    if n <= 8:
        return 1
    return 2


def fuzzy_match(text: str, keywords: list) -> bool:
    """Return True if any keyword approximately matches a word-ngram in text.

    Algorithm:
    1. Exact substring check first (fast path).
    2. Tokenise text into words, build sliding windows of the same word-count
       as the keyword, compute character-level edit distance on joined window.
    3. Match if distance ≤ threshold (scales with keyword length).
    """
    text_lower = text.lower()
    words = text_lower.split()

    for kw in keywords:
        kw = kw.lower().strip()
        if not kw:
            continue
        thr = _threshold(kw)

        # Fast path: exact substring
        if kw in text_lower:
            return True
        if thr == 0:
            # Short keyword — exact-only, skip fuzzy to avoid false positives
            continue

        # Fuzzy path: sliding n-gram window
        kw_words = kw.split()
        n = len(kw_words)
        for i in range(len(words) - n + 1):
            window = " ".join(words[i: i + n])
            if edit_distance(window, kw) <= thr:
                return True

    return False


# ──────────────────────── GitHub API helpers ─────────────────────────────── #

def _run(cmd: str, allow_fail=False):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if p.returncode != 0 and not allow_fail:
        raise RuntimeError(f"Command failed: {cmd}\n{p.stderr}")
    return p.stdout, p.returncode


def _gh_search(q: str, limit: int = 30):
    cmd = (
        f"gh api search/repositories --method GET "
        f"-F q={shlex.quote(q)} -F per_page={min(limit, 100)} --jq '.items'"
    )
    out, rc = _run(cmd, allow_fail=True)
    if rc != 0 or not out.strip():
        return []
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return []


def gh_search_multi(queries: list, per_query: int = 30):
    """Run multiple searches and deduplicate by full_name."""
    seen, combined = set(), []
    for q in queries:
        for item in _gh_search(q, limit=per_query):
            name = item.get("full_name")
            if name and name not in seen:
                seen.add(name)
                combined.append(item)
    return combined


def _paginated(base_cmd: str, max_pages: int, per_page: int):
    all_items = []
    for page in range(1, max_pages + 1):
        cmd = f"{base_cmd} -F per_page={per_page} -F page={page} --jq '.'"
        out, rc = _run(cmd, allow_fail=True)
        if rc != 0 or not out.strip():
            break
        try:
            batch = json.loads(out)
        except json.JSONDecodeError:
            break
        if not batch:
            break
        all_items.extend(batch)
        if len(batch) < per_page:
            break
    return all_items


def get_issues(owner_repo: str, max_pages: int, per_page: int = 100):
    base = f"gh api repos/{owner_repo}/issues --method GET -F state=open"
    raw = _paginated(base, max_pages, per_page)
    return [i for i in raw if "pull_request" not in i]


def get_releases(owner_repo: str, max_pages: int, per_page: int = 30):
    base = f"gh api repos/{owner_repo}/releases --method GET"
    return _paginated(base, max_pages, per_page)


# ──────────────────────── Classification helpers ─────────────────────────── #

def _repo_text(item) -> str:
    desc = (item.get("description") or "").lower()
    name = (item.get("full_name") or "").lower()
    topics = " ".join(t.lower() for t in (item.get("topics") or []))
    return f"{desc} {name} {topics}"


def is_tool_app(item) -> bool:
    text = _repo_text(item)
    if fuzzy_match(text, NON_APP_SIGNALS):
        return False
    return fuzzy_match(text, TOOL_APP_KEYWORDS)


def is_platform_repo(item, platform: str) -> bool:
    """Check that the repo targets the given platform."""
    if platform == "all":
        return True
    keywords = ANDROID_KEYWORDS if platform == "android" else IOS_KEYWORDS
    return fuzzy_match(_repo_text(item), keywords)


def is_platform_interaction_issue(title: str, body: str, platform: str) -> bool:
    """Check if an issue describes a click/tap-no-response bug on the target platform.

    Rules:
    - Must match INTERACTION_KEYWORDS (fuzzy).
    - If platform != 'all': must ALSO mention the platform (fuzzy).
      This ensures Android bugs are not mixed in with iOS reports and vice-versa.
    """
    # Limit body scan to first 800 chars for performance
    text = title + " " + (body or "")[:800]

    if not fuzzy_match(text, INTERACTION_KEYWORDS):
        return False

    if platform == "android":
        return fuzzy_match(text, ANDROID_KEYWORDS)
    if platform == "ios":
        return fuzzy_match(text, IOS_KEYWORDS)
    return True  # platform == "all" — no platform restriction on issues


# ──────────────────────── Core analysis ──────────────────────────────────── #

def analyze_repo(item, platform: str, max_issue_pages: int, max_release_pages: int):
    owner_repo = item["full_name"]
    stars = item.get("stargazers_count", 0)

    issues = get_issues(owner_repo, max_issue_pages)
    issue_count = len(issues)

    interaction_issues = []
    for issue in issues:
        title = issue.get("title") or ""
        body = issue.get("body") or ""
        if is_platform_interaction_issue(title, body, platform):
            interaction_issues.append({
                "title": title,
                "url": issue.get("html_url") or "",
                "created_at": issue.get("created_at") or "",
            })

    interaction_ratio = len(interaction_issues) / issue_count if issue_count > 0 else 0.0

    raw_releases = get_releases(owner_repo, max_release_pages)
    one_year_ago = datetime.now(timezone.utc) - timedelta(days=365)
    recent_releases = 0
    release_details = []

    for rel in raw_releases:
        tag = rel.get("tag_name") or ""
        name = rel.get("name") or tag
        body_text = rel.get("body") or ""
        published = rel.get("published_at") or rel.get("created_at") or ""
        url = rel.get("html_url") or ""
        is_recent = False
        if published:
            try:
                dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
                if dt > one_year_ago:
                    is_recent = True
                    recent_releases += 1
            except Exception:
                pass
        release_details.append({
            "tag": tag,
            "name": name,
            "published_at": published,
            "url": url,
            "changelog_preview": body_text[:600].strip(),
            "is_recent": is_recent,
        })

    issue_score = math.log10(issue_count + 1) / 2 if issue_count > 0 else 0.0
    release_score = min(1.0, recent_releases / 12)
    final_score = issue_score * 0.50 + interaction_ratio * 0.35 + release_score * 0.15

    return {
        "repo": owner_repo,
        "html_url": item.get("html_url"),
        "description": item.get("description"),
        "stars": stars,
        "issue_count": issue_count,
        "interaction_issues_count": len(interaction_issues),
        "interaction_ratio": round(interaction_ratio, 3),
        "recent_releases": recent_releases,
        "score": round(final_score, 3),
        "interaction_issues": interaction_issues,
        "releases": release_details,
    }


# ─────────────────── Markdown 输出（一目了然，中文）────────────────────────── #

def render_md(results, platform: str, generated_at: str) -> str:
    platform_cn = {"android": "Android", "ios": "iOS", "all": "全平台"}.get(platform, platform)
    total_bugs = sum(r["interaction_issues_count"] for r in results)

    L = []

    # ── 标题 ──
    L.append(f"# 🐛 Flutter {platform_cn} 工具类 App — 点击无响应 Bug 报告")
    L.append("")
    L.append(
        f"**生成时间：** {generated_at}"
        f"　|　**平台：** {platform_cn}"
        f"　|　**仓库数：** {len(results)}"
        f"　|　**Bug 总计：** {total_bugs} 条"
    )
    L.append("")
    L.append("> 仅收录「点击 / 点按 没有反应」类交互 bug，"
             f"且 issue 中必须明确提及 **{platform_cn}** 平台。")
    L.append("")
    L.append("---")
    L.append("")

    # ── 总览表 ──
    L.append("## 📊 总览")
    L.append("")
    L.append("| 排名 | 仓库 | ⭐ Stars | 🐛 点击Bug | 📦 近期版本 | 综合得分 |")
    L.append("|:---:|:---|---:|:---:|:---:|:---:|")
    for idx, r in enumerate(results, 1):
        link = f"[{r['repo']}]({r['html_url']})"
        L.append(
            f"| {idx} | {link} | {r['stars']:,} "
            f"| {r['interaction_issues_count']} "
            f"| {r['recent_releases']} "
            f"| {r['score']:.3f} |"
        )
    L.append("")
    L.append("---")
    L.append("")

    # ── 详细报告 ──
    L.append("## 📋 详细报告")
    L.append("")

    for idx, r in enumerate(results, 1):
        L.append(f"### #{idx} [{r['repo']}]({r['html_url']})")
        L.append("")
        if r.get("description"):
            L.append(f"> {r['description']}")
            L.append("")

        # 基本数据卡片
        L.append("| 项目 | 数值 |")
        L.append("|------|------|")
        L.append(f"| ⭐ Stars | {r['stars']:,} |")
        L.append(f"| 📋 Open Issues | {r['issue_count']} 条 |")
        L.append(f"| 🐛 点击无响应 Bug | **{r['interaction_issues_count']} 条** |")
        L.append(f"| 📦 近期版本（1 年内）| {r['recent_releases']} 个 |")
        L.append(f"| 🏆 综合得分 | `{r['score']:.3f}` |")
        L.append("")

        # 交互 Bug 列表
        bug_cnt = r["interaction_issues_count"]
        L.append(f"#### 🖱 点击 / 点按无响应 Bug（{bug_cnt} 条）")
        L.append("")
        if r["interaction_issues"]:
            L.append("| Issue 标题 | 时间 | 链接 |")
            L.append("|:----------|:----:|:----:|")
            for iss in r["interaction_issues"]:
                date = iss["created_at"][:10] if iss.get("created_at") else "—"
                title = iss["title"].replace("|", "\\|")
                L.append(f"| {title} | {date} | [查看]({iss['url']}) |")
        else:
            L.append("*暂无匹配的点击无响应 Bug*")
        L.append("")

        # 版本记录
        shown = r["releases"][:6]
        L.append(f"#### 📦 版本记录（共 {len(r['releases'])} 个，展示最近 {len(shown)} 个）")
        L.append("")
        if shown:
            L.append("| 版本 | 发布时间 | 状态 | 更新摘要 |")
            L.append("|:-----|:--------:|:----:|:--------|")
            for rel in shown:
                date = rel["published_at"][:10] if rel.get("published_at") else "—"
                badge = "✅ 近期" if rel["is_recent"] else "⬜ 旧版"
                preview = (
                    rel["changelog_preview"]
                    .replace("\n", " ")
                    .replace("|", "\\|")
                    .strip()[:100]
                )
                tag_link = f"[{rel['tag']}]({rel['url']})"
                L.append(f"| {tag_link} | {date} | {badge} | {preview} |")
        else:
            L.append("*暂无版本记录*")
        L.append("")

        if idx < len(results):
            L.append("---")
            L.append("")

    return "\n".join(L)


# ──────────────────────────── Entry point ────────────────────────────────── #

def main():
    parser = argparse.ArgumentParser(
        description="Flutter 工具类 App 点击无响应 Bug 猎手（读取 .env 默认参数）"
    )
    parser.add_argument("--query", default=None,
                        help="自定义 GitHub 搜索 query（覆盖分类搜索）")
    parser.add_argument("--platform", default=_env_get("PLATFORM", "android"),
                        choices=["android", "ios", "all"], help="目标平台")
    parser.add_argument("--limit", type=int, default=_env_get("LIMIT", 10),
                        help="输出仓库数量")
    parser.add_argument("--min-issues", type=int, default=_env_get("MIN_ISSUES", 50),
                        help="最少 open issues 数量")
    parser.add_argument("--candidates", type=int, default=_env_get("CANDIDATES", 140),
                        help="搜索候选仓库数量")
    parser.add_argument("--max-issue-pages", type=int,
                        default=_env_get("MAX_ISSUE_PAGES", 3),
                        help="issues 最大翻页数（每页 100 条）")
    parser.add_argument("--max-release-pages", type=int,
                        default=_env_get("MAX_RELEASE_PAGES", 2),
                        help="releases 最大翻页数（每页 30 条）")
    parser.add_argument("--output-format",
                        default=_env_get("OUTPUT_FORMAT", "md"),
                        choices=["md", "json", "text"],
                        help="输出格式：md / json / text")
    parser.add_argument("--md-output",
                        default=_env_get("MD_OUTPUT", ""),
                        help="Markdown 文件路径（默认：脚本同目录 flutter-bug-report.md）")
    args = parser.parse_args()

    log = lambda *a: print(*a, file=sys.stderr)
    log(f"平台        : {args.platform}")
    log(f"最少 issues : {args.min_issues}  |  目标数量 : {args.limit}")
    log(f"Issues 翻页 : 最多 {args.max_issue_pages} 页 × 100 = {args.max_issue_pages * 100} 条/仓库")
    log(f"Releases 翻页: 最多 {args.max_release_pages} 页 × 30 = {args.max_release_pages * 30} 条/仓库")
    log(f"输出格式    : {args.output_format}")
    log(f"匹配算法    : 最小编辑距离（fuzzy match）")
    log(f"黑名单      : {len(BLACKLIST)} 个仓库")
    log("")

    # Build search queries
    if args.query is not None:
        search_queries = [args.query]
    else:
        plat = ""
        if args.platform == "android":
            plat = "android "
        elif args.platform == "ios":
            plat = "ios "
        search_queries = [
            f"flutter {plat}{cat} language:dart stars:>30"
            for cat in TOOL_CATEGORIES
        ]

    per_query = max(10, args.candidates // len(search_queries))
    items = gh_search_multi(search_queries, per_query=per_query)
    log(f"共抓取 {len(items)} 个候选仓库")

    results = []
    for item in items:
        repo_name = item.get("full_name", "?")
        estimated_issues = item.get("open_issues_count", 0)

        if repo_name.lower() in BLACKLIST:
            log(f"  跳过  {repo_name}  (黑名单)")
            continue
        if estimated_issues < args.min_issues:
            log(f"  跳过  {repo_name}  (issues={estimated_issues})")
            continue
        if not is_platform_repo(item, args.platform):
            log(f"  跳过  {repo_name}  (非 {args.platform} 仓库)")
            continue
        if not is_tool_app(item):
            log(f"  跳过  {repo_name}  (非工具类 App)")
            continue

        log(f"  分析  {repo_name}  (~{estimated_issues} issues) ...")
        try:
            r = analyze_repo(
                item,
                platform=args.platform,
                max_issue_pages=args.max_issue_pages,
                max_release_pages=args.max_release_pages,
            )
        except Exception as e:
            log(f"    错误: {e}")
            continue

        if r["issue_count"] < args.min_issues:
            log(f"    跳过（去重后实际 {r['issue_count']} issues）")
            continue

        log(
            f"    ✓  issues={r['issue_count']}"
            f"  {args.platform}交互bug={r['interaction_issues_count']}"
            f"  得分={r['score']}"
        )
        results.append(r)

        if len(results) >= args.limit * 3:
            break

    results.sort(key=lambda x: x["score"], reverse=True)
    results = results[: args.limit]

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    if args.output_format == "json":
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif args.output_format == "md":
        md = render_md(results, args.platform, generated_at)
        md_path = (args.md_output or "").strip()
        if not md_path:
            md_path = str(Path(__file__).parent / "flutter-bug-report.md")
        out_path = Path(os.path.expanduser(md_path))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        log(f"\n✅ Markdown 报告已保存：{out_path}")
        log(f"   用 VS Code 打开：code '{out_path}'")
        log(f"   或直接查看：cat '{out_path}'")

    else:  # text
        print(f"\n{'=' * 70}")
        print(f"  Flutter {args.platform.upper()} 工具类 App 点击无响应 Bug — {len(results)} 个仓库")
        print(f"  生成时间: {generated_at}")
        print(f"{'=' * 70}\n")
        for idx, r in enumerate(results, 1):
            print(f"[{idx}] {r['repo']}  ⭐{r['stars']:,}  得分:{r['score']:.3f}")
            print(f"     {r['html_url']}")
            print(f"     {r.get('description') or '—'}")
            print(
                f"     共 {r['issue_count']} issues"
                f" | {r['interaction_issues_count']} 条点击无响应 bug"
                f" | 近期版本 {r['recent_releases']} 个"
            )
            if r["interaction_issues"]:
                print(f"\n     ── 点击无响应 Bug ──")
                for iss in r["interaction_issues"]:
                    print(f"     • {iss['title']}")
                    print(f"       {iss['url']}")
            if r["releases"]:
                print(f"\n     ── 版本记录（最近 {min(5, len(r['releases']))} 个）──")
                for rel in r["releases"][:5]:
                    tag = "[近期] " if rel["is_recent"] else ""
                    print(f"     • {tag}{rel['tag']}  {rel['published_at'][:10]}")
                    print(f"       {rel['url']}")
            print()


if __name__ == "__main__":
    main()
