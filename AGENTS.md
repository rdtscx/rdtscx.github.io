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
- 页面内所有指向 GitHub 的链接必须写完整所有者：`https://github.com/rdtscx/<repo>/...`。禁止省略 `rdtscx/`（曾因 `/releases/tag/<tag>` 缺所有者导致全部关联链接 404）。

## 4. 视觉规范

- 统一使用根站视觉语言：同一套 CSS 变量（`--bg`、`--text`、`--dim`、`--accent`、`--line` 等）、卡片圆角、`rise` 入场动画、粘性顶栏、等宽字体（ui-monospace）显示版本号。
- 下载区样式自包含（`dlx-` 前缀），深浅色跟随 `prefers-color-scheme`，不依赖宿主页面变量时给出回退值。
- 尊重 `prefers-reduced-motion`：动效可关闭。
- 页面语言为简体中文，商务简洁，不用 Emoji，不用感叹式营销文案。

## 5. 数据与页面一致性

- 版本数量与最新版本号以**本仓库实际 Releases** 为准；页面数据与 Release 不一致时，先修数据再展示。
- 根站 `scripts/sync.py` 在注入数据块时同时写入仓库列表快照 `SNAPSHOT`；GitHub API 被限流或不可达时，前端用快照兜底渲染，不出现空白页。
- 根站首屏直接用本地缓存或 `SNAPSHOT` 渲染列表，GitHub API 只做后台增量刷新；接口失败时状态灯降级为「使用本地快照」，列表与链接不得消失。
- 根站数据块位于 `index.html` 的 `/* SYNC:START … SYNC:END */` 标记内，**禁止手改该块内容**，只能由脚本生成。

## 6. 同步机制

- 每个备份仓库每天 **08:00 / 20:00（北京时间）** 各同步一次上游：镜像代码与 Release 安装包（只增不删），随后重建页尾下载区并提交推送。
- GitHub Actions 的 cron 用 UTC，写作 `0 0 * * *` 与 `0 12 * * *`。
- 根站同一时刻（08:00 / 20:00）拉取各仓库 Releases，更新 `APPINFO`（版本数量、最新版本号）与仓库索引；有新版本时自动映射到对应映射页。
- 镜像与重建不得覆盖站点自有文件：同步上游代码时排除 `index.html`、`scripts/`、`.github/`、本文件。
- 推送使用 SSH 远端 `git@github.com:rdtscx/<repo>.git`；OAuth 令牌不含 `workflow` scope，无法通过 HTTPS 推送 workflow 文件。
- 镜像的上游项目 `.gitignore` 常把 `scripts/` 列为忽略项，`scripts/build_downloads.py` 必须 `git add -f` 强制入库；CI 的刷新步骤会先校验该文件存在，缺失即失败退出。
- 镜像 tag 只增不删：用 `git fetch --no-tags --force upstream '+refs/tags/*:refs/tags/*'` 对齐本地，再只推送远端缺失的 tag，避免上游重打同版本 tag 导致 `would clobber existing tag` 直接中断。
- 上游改名时（如 `wanwuwww/Sii` → `wanwuwww/Sii-Browser`），需同步更新 workflow 的 `UPSTREAM_REPO`、`scripts/build_downloads.py` 的 `up` 字段与仓库简介链接。

## 7. 上游跟随（强制，备份站与引用型站点同时适用）

上游仓库改名、迁移组织、默认分支从 `main` 改 `master` 时，本站必须自动跟上，不允许人工改 workflow 才算修好；旧名被他人占用后 GitHub 的 301 重定向会失效，写死上游名等于定时炸弹。

### 7.1 上游关系登记

- 每个存在上游的仓库（备份站、镜像站、引用型站点）根目录必须有 `upstream.json`：

```json
{
  "repo": "wanwuwww/Sii-Browser",
  "branch": "auto",
  "mode": "mirror",
  "aliases": ["wanwuwww/Sii"],
  "resolved_at": "2026-11-27T10:45:56Z",
  "history": [{"from": "wanwuwww/Sii", "to": "wanwuwww/Sii-Browser", "at": "2026-11-27T10:45:56Z"}]
}
```

- `branch` 固定写 `auto`（跟随上游默认分支），**禁止**硬编码 `main` / `master`。
- `mode` 取 `mirror`（镜像代码与 Release）或 `reference`（只维护引用与页脚上游链接，不镜像代码）。
- `aliases` 由脚本自动累积历史名，勿手删；`history` 保留最近 12 次改名记录。
- 没有上游关系的自建站点（`tariff`、`arpu`、`tc`、`fp` 等）不需要 `upstream.json`，其余规则不受影响。

### 7.2 解析脚本

- 仓库根 `scripts/resolve_upstream.py`，以根站同名文件为准（新增仓库直接复制，勿各自改写）。
- 每次同步先跑 `python3 scripts/resolve_upstream.py --apply --repo-name "${GITHUB_REPOSITORY#*/}"`，由它：
  1. 用 `gh api repos/<upstream>` 拿到真实 `full_name` 与 `default_branch`（GitHub 会跟随改名 301）；
  2. 当前名 404 时回退 `aliases` 逐个探活，找回改名后的仓库；
  3. 改名时回写 `upstream.json`（含别名与历史）、`scripts/build_downloads.py` 里对应仓库的 `up` 字段、仓库简介中的上游地址；
  4. 输出 `repo` / `branch` / `status` / `renamed` 四个 Actions 输出。
- 上游彻底删除或转私有时输出 `status=missing`，流程跳过镜像、保留本地已有内容，页面照常可用。

### 7.3 工作流要求

- workflow 的第一个 job 必须是 `resolve-upstream`；后续 job 通过 `needs.resolve-upstream.outputs.repo` / `.branch` 取上游名与分支，**禁止**在工作流里写死上游。
- 模板：`scripts/templates/sync-upstream.yml` + `scripts/templates/upstream.example.json`，复制后填好真实上游即可，代码与 Release 镜像、tag 只增、页尾重建均已内置。
- 引用型站点：从模板删掉 `mirror-code` / `mirror-releases`，保留 `resolve-upstream` 与 `refresh-downloads`。
- 同步时排除 `upstream.json` 与 `scripts/`，避免被上游文件覆盖。
- 上游解析成功但代码拉取失败必须 `::error::` 并以非零退出，禁止只留 `::warning::` 静默跳过（曾因分支写错 `main`，`shurufa` 连续多日「同步成功」但镜像步骤一直跳过）。

### 7.4 改名演练（验收方式）

1. 把 `upstream.json` 的 `repo` 改回旧名（如 `wanwuwww/Sii`），清空 `aliases`；
2. 手动触发 `sync-upstream`；
3. 确认 run 成功、`upstream.json` 已回写新名、`aliases` 含旧名、`build_downloads.py` 的 `up` 已更新、页面页脚上游链接指向新地址。

## 8. 新增备份站接入清单

1. 新建或复用 `rdtscx/<repo>`，开启 Pages（legacy，`main` 分支根目录）。
2. 登记 `upstream.json`（`repo`、`branch: auto`、`mode: mirror|reference`），放入 `scripts/resolve_upstream.py` 与 `scripts/templates/sync-upstream.yml`；无上游的自建站点跳过此步。
2. 克隆上游全部 Release 资产到本仓库 Releases（只增不删，失败重试，幂等跳过已存在资产）。
3. 复制 `scripts/build_downloads.py`，在 `APPS` 字典登记 `title`、`up`（上游全名）、`group`（是否多插件）。
4. 编写映射页 `index.html`：项目介绍（定位、能力、安装要求、来源说明）+ 页尾 `<!-- DLX:START -->…<!-- DLX:END -->` 下载区。
5. 运行 `python3 scripts/build_downloads.py <repo>` 注入下载区。
6. 新建 `.github/workflows/sync-upstream.yml`：双 cron、镜像上游、重建下载区、提交推送。
7. 在根站登记：运行 `GITHUB_TOKEN=... python3 scripts/sync.py`，确认 `APPINFO` 出现该仓库的 `count`/`latest`。
8. 线上验收：映射页命中 `id="download"`，版本数与 Release 数一致，页面无上游下载链接。

## 9. 文案与事实

- 页面只写可从仓库事实核实的内容（包名、ABI、许可证、端点、版本号）；不确定信息标【待确认】，不编造。
- 介绍页结构建议：一句话定位 → 解决什么问题 → 主要能力 → 安装/使用 → 文档 → 页尾下载区。
- 不写空洞客套话，不堆叠营销形容词。

## 10. 脚本与技术索引

| 文件 | 作用 |
| --- | --- |
| 根站 `scripts/sync.py` | 拉取账号仓库与 Releases，注入 `APPINFO` / `EXTRA` / `SNAPSHOT` |
| 根站 `index.html` | 仓库索引页；数据块由脚本注入 |
| 各仓库 `scripts/build_downloads.py` | 生成本仓库页尾下载区并注入 `index.html` |
| 各仓库 `index.html` | 映射页正文；`DLX` 标记块由脚本维护 |
| 各仓库 `.github/workflows/sync-upstream.yml` | 双 cron：先跟随上游 → 镜像 → 重建 → 推送 |
| 各仓库 `upstream.json` | 上游关系登记（真实全名、auto 分支、历史别名） |
| 各仓库 `scripts/resolve_upstream.py` | 跟随上游改名与默认分支变更，回写配置 |
| `scripts/templates/sync-upstream.yml` | 新仓库接入模板（备份站与引用型站点通用） |
| 根站 `sites.json` | 站外条目清单（可选） |

- 数据来源统一为 `https://api.github.com/repos/rdtscx/<repo>/releases?per_page=100`，只统计已发布、非草稿、非预发布版本。
- 生成脚本仅依赖 Python 标准库与 `gh` CLI（本地镜像、发布资产时使用）。

## 11. 验收清单

- [ ] 根站无下载直链、无版本体积清单。
- [ ] 映射页下载区在页尾，`id="download"` 存在。
- [ ] 最新版本默认展开，其余可折叠，文件数 = Release 资产数。
- [ ] 每个版本有更新记录与 Release 链接。
- [ ] 所有下载地址指向 `rdtscx` 自有仓库。
- [ ] 页面风格与根站一致，深浅色正常。
- [ ] 双 cron 工作流存在，且不会覆盖站点自有文件。
- [ ] `upstream.json` 存在、`branch` 为 `auto`，workflow 未写死上游名；按 7.4 演练过一次改名跟随。
- [ ] 根站 `APPINFO` 含该仓库 `count`/`latest`。
