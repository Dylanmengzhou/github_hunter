# project-hunter

移动端工具类 App 点击无响应 Bug 猎手 — 自动在 GitHub 上搜索 Flutter、Android Native、React Native、iOS 项目的 UI 交互 bug。

## 安装

```bash
pip install project-hunter
```

需要先登录 GitHub CLI：

```bash
gh auth login
```

## 用法

```bash
project-hunter run                                    # 用 .env 默认参数（flutter）
project-hunter run --framework android                # Android Native
project-hunter run --framework react-native           # React Native
project-hunter run --framework ios                    # iOS Native
project-hunter run --framework all                    # 全框架
project-hunter run --limit 20                         # 输出 20 个仓库
project-hunter run --output-format json               # JSON 格式
project-hunter run --save-path ~/Desktop/report.md    # 指定保存路径
project-hunter run --help                             # 查看所有选项
```

## 配置

`.env` 文件按以下优先级查找：
1. **当前目录** `./.env`（推荐，项目级配置）
2. **全局配置** `~/.config/project-hunter/.env`（所有目录通用）

创建全局配置：

```bash
mkdir -p ~/.config/project-hunter
cat > ~/.config/project-hunter/.env << 'EOF'
FRAMEWORK=flutter
MIN_ISSUES=50
LIMIT=10
SAVE_PATH=~/Documents/bug-report.md
EOF
```

或在当前目录创建 `.env` 文件：

```ini
FRAMEWORK=flutter         # flutter | android | react-native | ios | all
MIN_ISSUES=50
LIMIT=10
CANDIDATES=140
MAX_ISSUE_PAGES=3
MAX_RELEASE_PAGES=2
OUTPUT_FORMAT=md          # md | json | text
SAVE_PATH=                # 留空 = 当前目录 bug-report.md
EDIT_DISTANCE_THRESHOLD=2
```


## 关键词文件说明

首次运行后，所有关键词文件自动生成到 `~/.config/project-hunter/keywords/`，可直接编辑。

搜索流程分四个阶段，每个阶段使用不同的关键词文件：

```mermaid
flowchart TD
    A([tool_categories.csv]) -->|生成搜索词| B[GitHub 搜索
几百个候选仓库]
    B --> C{是工具类 App？
tool_app.csv
non_app_signals.csv}
    C -->|否 - 跳过| BL[(blacklist.csv
自动追加)]
    C -->|是| D{是目标框架？
framework_flutter.csv
framework_android.csv
framework_react_native.csv
framework_ios.csv}
    D -->|--framework all 跳过此步| E
    D -->|否 - 跳过| BL
    D -->|是| E{issues 里有
点击无响应 bug？
interaction.csv}
    E -->|否 - 跳过| BL
    E -->|是| F[分析仓库
issue 数 / 版本 / 得分]
    F --> G([输出报告])
```

| 文件 | 用途 |
|------|------|
| `tool_categories.csv` | 生成 GitHub 搜索 query 的关键词（宽泛，用于找仓库） |
| `tool_app.csv` | 验证仓库是工具类 App 的关键词（细，如 pedometer/calorie/bmi） |
| `non_app_signals.csv` | 排除非 App 仓库的信号词（plugin/library/template 等） |
| `framework_flutter.csv` | Flutter 框架识别词（dart/pubspec/bloc/riverpod 等） |
| `framework_android.csv` | Android Native 识别词（kotlin/gradle/jetpack compose 等） |
| `framework_react_native.csv` | React Native 识别词（expo/metro/rn 等） |
| `framework_ios.csv` | iOS Native 识别词（swift/swiftui/xcode 等） |
| `interaction.csv` | 点击无响应 bug 关键词（not clickable/tap not working 等） |

`--framework` 选项决定使用哪个框架关键词文件过滤仓库，`--framework all` 跳过框架过滤。
