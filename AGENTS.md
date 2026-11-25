# rdtscx 站点规范（AI 可读，长期生效）

> 本文件是 `rdtscx.github.io` 根站与 rdtscx 名下全部备份/镜像仓库的唯一规范来源。
> 任何 AI 或维护者在改动本站族页面、下载区、自动同步流程前，必须先完整读取本文件。

## 1. 适用范围

- 根站：`https://rdtscx.github.io/`（仓库 `rdtscx/rdtscx.github.io`）
- 软件映射页（仓库首页即站点页）：`/Android-AI-gateway/`、`/sii-browser-backup/`、`/AccessibilityManagerPro/`、`/shurufa/`
- 纯站点页：`/tariff/`、`/arpu/`、`/tc/`、`/fp/` 等
- 后续新增的所有备份站、镜像站仓库同样适用，无例外。

## 2. 站点拓扑与根站职责

- 根站只做仓库索引：卡片列出仓库名、简介、语言、更新时间、站点路径。
- 根站**不得**出现任何安装包下载直链，**不得**列出「版本号 + 体积」形式的版本清单。
- 根站对软件类仓库只登记两项数据：版本数量 `count`、最新版本号 `latest`，用于标记「软件」分类与跳转映射页。
- 每个仓库的可下载内容只在**该仓库映射页的页尾下载区**呈现。

## 3. 下载区规范（核心）

### 3.1 位置与形态

- 下载区以 `<div class="dlx" id="download">` 内联在映射页 `index.html` 中，**位于正文之后、`<footer>` 之前**。
- **禁止**：单独生成 `downloads.html` 二级页；在页面顶部或中部放“全部版本下载页”“立即下载”一类蓝色跳转文字；根站页尾放下载入口。
- 页面正文可以写作“最新版本 X”，但不得给出下载链接。

### 3.2 内容结构

- 区块标题：`下载`，右侧显示「N 个版本 · M 个文件」。
- 版本按版本号从新到旧排列；**最新版本默认展开**，其余版本为可折叠 `<details>`。
- 每个版本摘要行：版本号、`最新` 徽标（仅第一条）、收录日期、文件数、总体积。
- 展开后：该版本全部可下载文件，以 chip 形式列出文件名与体积，点击直接下载。
- 每个版本附**该版本的更新记录**（取自 Release body，去 Markdown 符号后保留 4 行、上限约 420 字），并给「完整更新记录见本仓库 Release」链接。
- 区块底部一行：`仓库：rdtscx/<repo> · 上游：<owner>/<repo>`。

### 3.3 文件命名与展示

- 多插件项目（如 fcitx5）文件名过长时，chip 显示压缩标签：`主程序 · arm64-v8a`、`rime · arm64-v8a` 等，完整文件名放在 `title` 悬浮提示。
- 版本日期标注为“收录 YYYY-MM-DD”，指本站收录该版本的时间；**不要**把镜像时间当作上游发布日期。
- 只展示用户可用的安装包（`.apk` 等）；`build-metadata*.json` 一类 CI 元数据不入库、不上页面。

### 3.4 下载来源（硬性要求）

- 安装包必须**先镜像到用户自有仓库**（`rdtscx/<repo>` 的 Releases），页面内所有下载地址只能指向 `github.com/rdtscx/...`。
- **禁止**任何形式的上游直链（`github.com/<upstream>/...`、F-Droid、Jenkins、Google Play 等第三方链接）。
- 上游仓库被删除、改名、转为私有，本站下载都必须依然可用。
- 页面不写“已完整镜像”“长期有效”“不使用上游链接”这类说明性长句，最多一句：`下面的文件全部托管在本仓库 Releases…`。

## 4. 视觉规范

- 统一使用根站视觉语言：同一套 CSS 变量（`--bg`、`--text`、`--dim`、`--accent`、`--line` 等）、卡片圆角、`rise` 入场动画、粘性顶栏、等宽字体（ui-monospace）显示版本号。
- 下载区样式自包含（`dlx-` 前缀），深浅色跟随 `prefers-color-scheme`，不依赖宿主页面变量时给出回退值。
- 尊重 `prefers-reduced-motion`：动效可关闭。
- 页面语言为简体中文，商务简洁，不用 Emoji，不用感叹式营销文案。

## 5. 数据与页面一致性

- 版本数量与最新版本号以**本仓库实际 Releases** 为准；页面数据与 Release 不一致时，先修数据再展示。
- 根站 `scripts/sync.py` 在注入数据块时同时写入仓库列表快照 `SNAPSHOT`；GitHub API 被限流或不可达时，前端用快照兜底渲染，不出现空白页。
- 根站数据块位于 `index.html` 的 `/* SYNC:START … SYNC:END */` 标记内，**禁止手改该块内容**，只能由脚本生成。

## 6. 同步机制

- 每个备份仓库每天 **08:00 / 20:00（北京时间）** 各同步一次上游：镜像代码与 Release 安装包（只增不删），随后重建页尾下载区并提交推送。
- GitHub Actions 的 cron 用 UTC，写作 `0 0 * * *` 与 `0 12 * * *`。
- 根站同一时刻（08:00 / 20:00）拉取各仓库 Releases，更新 `APPINFO`（版本数量、最新版本号）与仓库索引；有新版本时自动映射到对应映射页。
- 镜像与重建不得覆盖站点自有文件：同步上游代码时排除 `index.html`、`scripts/`、`.github/`、本文件。
- 推送使用 SSH 远端 `git@github.com:rdtscx/<repo>.git`；OAuth 令牌不含 `workflow` scope，无法通过 HTTPS 推送 workflow 文件。

## 7. 新增备份站接入清单

1. 新建或复用 `rdtscx/<repo>`，开启 Pages（legacy，`main` 分支根目录）。
2. 克隆上游全部 Release 资产到本仓库 Releases（只增不删，失败重试，幂等跳过已存在资产）。
3. 复制 `scripts/build_downloads.py`，在 `APPS` 字典登记 `title`、`up`（上游全名）、`group`（是否多插件）。
4. 编写映射页 `index.html`：项目介绍（定位、能力、安装要求、来源说明）+ 页尾 `<!-- DLX:START -->…<!-- DLX:END -->` 下载区。
5. 运行 `python3 scripts/build_downloads.py <repo>` 注入下载区。
6. 新建 `.github/workflows/sync-upstream.yml`：双 cron、镜像上游、重建下载区、提交推送。
7. 在根站登记：运行 `GITHUB_TOKEN=... python3 scripts/sync.py`，确认 `APPINFO` 出现该仓库的 `count`/`latest`。
8. 线上验收：映射页命中 `id="download"`，版本数与 Release 数一致，页面无上游下载链接。

## 8. 文案与事实

- 页面只写可从仓库事实核实的内容（包名、ABI、许可证、端点、版本号）；不确定信息标【待确认】，不编造。
- 介绍页结构建议：一句话定位 → 解决什么问题 → 主要能力 → 安装/使用 → 文档 → 页尾下载区。
- 不写空洞客套话，不堆叠营销形容词。

## 9. 脚本与技术索引

| 文件 | 作用 |
| --- | --- |
| 根站 `scripts/sync.py` | 拉取账号仓库与 Releases，注入 `APPINFO` / `EXTRA` / `SNAPSHOT` |
| 根站 `index.html` | 仓库索引页；数据块由脚本注入 |
| 各仓库 `scripts/build_downloads.py` | 生成本仓库页尾下载区并注入 `index.html` |
| 各仓库 `index.html` | 映射页正文；`DLX` 标记块由脚本维护 |
| 各仓库 `.github/workflows/sync-upstream.yml` | 双 cron 同步 + 重建 + 推送 |
| 根站 `sites.json` | 站外条目清单（可选） |

- 数据来源统一为 `https://api.github.com/repos/rdtscx/<repo>/releases?per_page=100`，只统计已发布、非草稿、非预发布版本。
- 生成脚本仅依赖 Python 标准库与 `gh` CLI（本地镜像、发布资产时使用）。

## 10. 验收清单

- [ ] 根站无下载直链、无版本体积清单。
- [ ] 映射页下载区在页尾，`id="download"` 存在。
- [ ] 最新版本默认展开，其余可折叠，文件数 = Release 资产数。
- [ ] 每个版本有更新记录与 Release 链接。
- [ ] 所有下载地址指向 `rdtscx` 自有仓库。
- [ ] 页面风格与根站一致，深浅色正常。
- [ ] 双 cron 工作流存在，且不会覆盖站点自有文件。
- [ ] 根站 `APPINFO` 含该仓库 `count`/`latest`。
