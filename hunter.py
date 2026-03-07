#!/usr/bin/env python3
"""
github-ui-bug-hunter/hunter.py — Flutter 工具类 App 点击无响应 Bug 猎手

Requirements: Python 3.8+, GitHub CLI authenticated (gh auth login)
              pip install typer

Usage:
  python hunter.py                        # 读取 .env 默认参数
  python hunter.py --platform ios         # 只看 iOS 的点击 bug
  python hunter.py --output-format json   # 输出 JSON
  python hunter.py --help                 # 查看所有选项
"""

import csv
import json
import math
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional

import typer


# ─────────────────────────────── .env 加载 ──────────────────────────────── #

def load_env() -> tuple[dict, str]:
    """Load .env from (in priority order):
    1. Current working directory (./.env)
    2. User config directory (~/.config/project-hunter/.env)

    Returns (env_dict, config_path_used).
    """
    candidates = [
        Path.cwd() / ".env",
        Path.home() / ".config" / "project-hunter" / ".env",
    ]
    env = {}
    used = "(无配置文件，使用内置默认值)"
    for env_path in candidates:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, _, v = line.partition("=")
                    env[k.strip()] = v.strip()
            used = str(env_path)
            break
    return env, used


ENV, _ENV_SOURCE = load_env()

# Global edit-distance cap read once at startup
_EDIT_DISTANCE_MAX: int = int(ENV.get("EDIT_DISTANCE_THRESHOLD", 2))


# ──────────────────────────── CLI Enums ──────────────────────────────────── #

class Platform(str, Enum):
    android = "android"
    ios = "ios"
    all = "all"


class OutputFormat(str, Enum):
    md = "md"
    json = "json"
    text = "text"


app = typer.Typer(help="Flutter 工具类 App 点击无响应 Bug 猎手（读取 .env 默认参数）")


@app.callback()
def _root():
    """project-hunter — Flutter UI Bug 猎手"""


def _env_get(key, default):
    val = ENV.get(key)
    if val is None:
        return default
    return int(val) if isinstance(default, int) else val


# ──────────────────────────── Config Dir ────────────────────────────────── #

CONFIG_DIR = Path.home() / ".config" / "project-hunter"

_DEFAULT_KEYWORDS: dict[str, str] = {
    "interaction.csv": """keyword,notes
not responding,通用：组件无响应
no response,通用：没有响应
unresponsive,通用：无响应
not clickable,不可点击
can't click,无法点击
cannot click,无法点击
doesn't respond,没有响应
does not respond,没有响应
tap not working,点击不生效
tap doesn't work,点击不生效
tap does not work,点击不生效
click not working,点击不生效
click doesn't work,点击不生效
click does not work,点击不生效
button not working,按钮不生效
button doesn't work,按钮不生效
gesture not working,手势不生效
gesture doesn't work,手势不生效
onpressed,Flutter 按钮回调关键词
ontap,Flutter 点击回调关键词
gesturedetector,Flutter 手势检测器
inkwell,Flutter 水波纹点击组件
not tappable,不可点按
tap issue,点击问题
click issue,点击问题
press not working,按压不生效
not pressing,按压无效
no reaction,没有反应
no action,没有动作
nothing happens,什么都没发生
not interactive,不可交互
interaction broken,交互已损坏
""",
    "android.csv": """keyword,notes
android,最核心的平台词
androidx,AndroidX 支持库
gradle,Android 构建系统
apk,Android 安装包格式
aab,Android App Bundle 格式
material,Material Design（Android 设计规范）
jetpack,Android Jetpack 组件
playstore,Google Play 商店
play store,Google Play 商店（带空格）
android device,Android 设备
android phone,Android 手机
android tablet,Android 平板
android studio,Android 开发工具
android emulator,Android 模拟器
""",
    "ios.csv": """keyword,notes
ios,最核心的平台词
iphone,苹果手机
ipad,苹果平板
xcode,iOS 开发工具
swift,iOS 原生语言
objc,Objective-C 语言
appstore,苹果应用商店
app store,苹果应用商店（带空格）
cupertino,Flutter iOS 风格组件
uikit,iOS 原生 UI 框架
testflight,苹果公测平台
ios device,iOS 设备
ios simulator,iOS 模拟器
""",
    "non_app_signals.csv": """keyword,notes
plugin,Flutter/Dart 插件
library,代码库
sdk,开发工具包
framework,框架
package,包/库
wrapper,封装库
binding,绑定层
extension,扩展
module,模块
component,组件库
widget library,Widget 组件库
flutter plugin,Flutter 插件明示
dart package,Dart 包明示
pub.dev,Pub 包管理平台
boilerplate,样板代码
template,模板
starter,启动模板
demo,演示项目
example,示例项目
sample,样本项目
""",
    "tool_app.csv": """keyword,notes
fitness,健身类
workout,锻炼类
exercise,运动类
gym,健身房类
health,健康类
running,跑步类
cycling,骑行类
pedometer,计步器
calorie,卡路里计算
bmi,BMI 计算
step counter,步数计数
diet,饮食类
nutrition,营养类
food,食物记录
meal,餐食记录
recipe,菜谱类
eating,饮食追踪
fasting,间歇性断食
water intake,饮水记录
habit,习惯追踪
todo,待办事项
task manager,任务管理
reminder,提醒类
productivity,生产力类
journal,日记类
diary,日记类
checklist,清单类
routine,日常惯例
goal tracker,目标追踪
planner,计划类
pomodoro,番茄钟
calculator,计算器
finance,财务类
budget,预算类
expense,支出记录
money manager,财务管理
wallet,钱包类
accounting,记账类
music player,音乐播放器
audio player,音频播放器
music app,音乐 App
playlist,播放列表
podcast,播客类
radio,收音机类
equalizer,均衡器
timer,计时器
stopwatch,秒表
countdown,倒计时
alarm,闹钟
gallery,相册类
photo,照片类
media player,媒体播放器
weather app,天气 App
flashcard,闪卡记忆
language learning,语言学习
""",
    "tool_categories.csv": """keyword,notes
fitness,健身 App 搜索词
workout,锻炼 App 搜索词
diet nutrition,饮食营养 App 搜索词
food tracker,食物追踪 App 搜索词
habit tracker,习惯追踪 App 搜索词
todo app,待办 App 搜索词
music player,音乐播放器搜索词
audio player,音频播放器搜索词
calculator,计算器搜索词
budget expense,预算支出 App 搜索词
journal diary,日记 App 搜索词
timer stopwatch,计时/秒表 App 搜索词
photo gallery,相册 App 搜索词
weather,天气 App 搜索词
""",
}

_DEFAULT_BLACKLIST = """repo,reason
flutter/flutter,官方框架，不是 App
flutter/packages,官方插件集合
flutter/samples,官方示例，非真实 App
dart-lang/dart-pad,在线编辑器工具
alibaba/flutter_boost,Flutter 混合框架
google/flutter.widgets,UI 组件库
invertase/melos,Monorepo 工具
rrousselGit/riverpod,状态管理框架
felangel/bloc,状态管理框架
jonataslaw/getx,状态管理框架
iampawan/FlutterExampleApps,示例合集，非单一 App
mitesh77/Best-Flutter-UI-Templates,UI 模板库
abuanwar072/Flutter-Responsive-Admin-Panel-or-Dashboard,UI 模板
FilledStacks/flutter-tutorials,教程代码
ResoCoder/flutter-tdd-clean-architecture-course,教程代码
"""


def _init_config_dir() -> None:
    """On first run, create ~/.config/project-hunter/ with default files."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    kw_dir = CONFIG_DIR / "keywords"
    kw_dir.mkdir(exist_ok=True)
    for filename, content in _DEFAULT_KEYWORDS.items():
        path = kw_dir / filename
        if not path.exists():
            path.write_text(content, encoding="utf-8")
    bl_path = CONFIG_DIR / "blacklist.csv"
    if not bl_path.exists():
        bl_path.write_text(_DEFAULT_BLACKLIST, encoding="utf-8")


def _load_csv_keywords(filename: str) -> list:
    """Load first column from CONFIG_DIR/keywords/{filename}."""
    csv_path = CONFIG_DIR / "keywords" / filename
    if not csv_path.exists():
        print(f"[warn] {csv_path} 不存在，该关键词列表为空", file=sys.stderr)
        return []
    keywords = []
    with csv_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            kw = row.get("keyword", "").strip()
            if kw:
                keywords.append(kw)
    if not keywords:
        print(f"[warn] {csv_path} 为空文件，该关键词列表为空", file=sys.stderr)
    return keywords


def _load_blacklist() -> set:
    """Load blacklisted repo full_names from CONFIG_DIR/blacklist.csv."""
    bl_path = CONFIG_DIR / "blacklist.csv"
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


def _append_to_blacklist(new_entries: list[tuple[str, str]]) -> int:
    """Append (repo, reason) pairs to CONFIG_DIR/blacklist.csv, skipping duplicates."""
    if not new_entries:
        return 0

    bl_path = CONFIG_DIR / "blacklist.csv"
    existing = _load_blacklist()

    to_write = [
        (repo, reason)
        for repo, reason in new_entries
        if repo.lower() not in existing
    ]
    if not to_write:
        return 0

    needs_header = not bl_path.exists() or bl_path.stat().st_size == 0
    with bl_path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if needs_header:
            writer.writerow(["repo", "reason"])
        for repo, reason in to_write:
            writer.writerow([repo, reason])

    return len(to_write)


# ─────────────── Keywords — sourced from CONFIG_DIR/keywords/*.csv ────────── #

_init_config_dir()

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
    """Allowed edit distance based on keyword length, capped by EDIT_DISTANCE_THRESHOLD.
    ≤4 chars  → 0 (exact only, avoids false positives on short words)
    5-8 chars → 1 (one typo allowed)
    ≥9 chars  → 2 (two typos allowed)
    """
    n = len(kw)
    if n <= 4:
        base = 0
    elif n <= 8:
        base = 1
    else:
        base = 2
    return min(base, _EDIT_DISTANCE_MAX)


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

@app.command("run")
def run_command(
    query: Optional[str] = typer.Option(
        None, help="自定义 GitHub 搜索 query（覆盖分类搜索）"
    ),
    platform: Platform = typer.Option(
        _env_get("PLATFORM", "android"), help="目标平台"
    ),
    limit: int = typer.Option(
        _env_get("LIMIT", 10), help="输出仓库数量"
    ),
    min_issues: int = typer.Option(
        _env_get("MIN_ISSUES", 50), help="最少 open issues 数量"
    ),
    candidates: int = typer.Option(
        _env_get("CANDIDATES", 140), help="搜索候选仓库数量"
    ),
    max_issue_pages: int = typer.Option(
        _env_get("MAX_ISSUE_PAGES", 3), help="issues 最大翻页数（每页 100 条）"
    ),
    max_release_pages: int = typer.Option(
        _env_get("MAX_RELEASE_PAGES", 2), help="releases 最大翻页数（每页 30 条）"
    ),
    output_format: OutputFormat = typer.Option(
        _env_get("OUTPUT_FORMAT", "md"), help="输出格式：md / json / text"
    ),
    save_path: str = typer.Option(
        _env_get("SAVE_PATH", ""), help="报告保存路径，默认：脚本同目录 flutter-bug-report.md"
    ),
):
    log = lambda *a: typer.echo(" ".join(str(x) for x in a), err=True)
    log(f"配置目录    : {CONFIG_DIR}")
    log(f"  .env      : {_ENV_SOURCE}")
    if _ENV_SOURCE.startswith("("):
        log(f"  → 在配置目录创建 .env: touch {CONFIG_DIR}/.env")
    log(f"  keywords/ : {CONFIG_DIR / 'keywords'}  (可编辑关键词)")
    log(f"  blacklist : {CONFIG_DIR / 'blacklist.csv'}  (可编辑黑名单)")
    log(f"平台        : {platform}")
    log(f"最少 issues : {min_issues}  |  目标数量 : {limit}")
    log(f"Issues 翻页 : 最多 {max_issue_pages} 页 × 100 = {max_issue_pages * 100} 条/仓库")
    log(f"Releases 翻页: 最多 {max_release_pages} 页 × 30 = {max_release_pages * 30} 条/仓库")
    log(f"输出格式    : {output_format}")
    log(f"匹配算法    : 最小编辑距离（fuzzy match）")
    log(f"黑名单      : {len(BLACKLIST)} 个仓库")
    log("")

    # Build search queries
    if query is not None:
        search_queries = [query]
    else:
        plat = ""
        if platform == Platform.android:
            plat = "android "
        elif platform == Platform.ios:
            plat = "ios "
        search_queries = [
            f"flutter {plat}{cat} language:dart stars:>30"
            for cat in TOOL_CATEGORIES
        ]

    per_query = max(10, candidates // len(search_queries))
    items = gh_search_multi(search_queries, per_query=per_query)
    log(f"共抓取 {len(items)} 个候选仓库")

    results = []
    skipped_for_blacklist: list[tuple[str, str]] = []

    for item in items:
        repo_name = item.get("full_name", "?")
        estimated_issues = item.get("open_issues_count", 0)

        if repo_name.lower() in BLACKLIST:
            log(f"  跳过  {repo_name}  (黑名单)")
            continue
        if estimated_issues < min_issues:
            log(f"  跳过  {repo_name}  (issues={estimated_issues})")
            skipped_for_blacklist.append((repo_name, f"issues不足({estimated_issues}<{min_issues})"))
            continue
        if not is_platform_repo(item, platform):
            log(f"  跳过  {repo_name}  (非 {platform} 仓库)")
            skipped_for_blacklist.append((repo_name, f"非{platform}仓库"))
            continue
        if not is_tool_app(item):
            log(f"  跳过  {repo_name}  (非工具类 App)")
            skipped_for_blacklist.append((repo_name, "非工具类App"))
            continue

        log(f"  分析  {repo_name}  (~{estimated_issues} issues) ...")
        try:
            r = analyze_repo(
                item,
                platform=platform,
                max_issue_pages=max_issue_pages,
                max_release_pages=max_release_pages,
            )
        except Exception as e:
            log(f"    错误: {e}")
            continue

        if r["issue_count"] < min_issues:
            log(f"    跳过（去重后实际 {r['issue_count']} issues）")
            continue

        log(
            f"    ✓  issues={r['issue_count']}"
            f"  {platform}交互bug={r['interaction_issues_count']}"
            f"  得分={r['score']}"
        )
        results.append(r)

        if len(results) >= limit * 3:
            break

    added = _append_to_blacklist(skipped_for_blacklist)
    if added:
        log(f"\n📋 已将 {added} 个跳过的仓库自动追加到 blacklist.csv")

    results.sort(key=lambda x: x["score"], reverse=True)
    results = results[:limit]

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    if output_format == OutputFormat.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif output_format == OutputFormat.md:
        md = render_md(results, platform, generated_at)
        md_path = save_path.strip()
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
        print(f"  Flutter {platform.upper()} 工具类 App 点击无响应 Bug — {len(results)} 个仓库")
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
    app()
