---
name: init-dev-workflow
description: |
  为当前项目生成一套 dev-workflow 基础设施：项目级 dev-workflow skill、按主题切分的 dev-notes/knowledge/ 知识库、Stop hook（提示代码变更后跑 /simplify）、CLAUDE.md 集成段。根据项目实际技术栈（Tauri / Expo / Next.js / Vite+React / 其他）定制通用 skill 列表、知识主题、hook 路径。
  触发场景：
  (1) 用户说"给这个项目加上 dev-workflow"、"初始化 dev-workflow"、"搭建开发知识库"
  (2) 用户在新项目里要求设置自动化的"开发前加载知识 / 开发后更新知识"流程
  (3) 用户想把已有项目的 dev-workflow 机制复制到另一个项目
  关键词：init dev-workflow、dev-workflow 初始化、项目知识库骨架、开发工作流集成
---

# Init Dev Workflow

## 概览

把一套"开发前加载 → 开发中遵循 → 开发后沉淀"的 dev-workflow 机制**落地**到一个具体项目里。产物包括：

1. `.claude/skills/dev-workflow/SKILL.md` — 项目级 dev-workflow skill（引用本项目的 knowledge 主题 + 适配本项目技术栈的通用 skill）
2. `dev-notes/knowledge/*.md` — 按主题切分的知识文件（4 个主题为推荐默认，可按项目调整）
3. `.claude/settings.json` 中的 Stop hook — 检测到代码变更时提示 `/simplify`
4. `CLAUDE.md` 头部的引用段 — 指明执行任何开发任务前调用 `/dev-workflow`
5. `.gitignore` 反向允许规则（如果项目已忽略 `.claude/*`）

本 skill **不**直接写脚本或自动化——中间会用 `AskUserQuestion` 和用户确认几个关键分叉点，然后按确认结果生成文件。

## 工作流

### Step 1. 扫描项目，识别技术栈

用 Read/Glob 检查以下"探针文件"，组合判断项目属于哪种预设类型。**不要一次性全读**，按 Glob 发现再选择性 Read：

| 探针文件 | 暗示 |
|---|---|
| `src-tauri/tauri.conf.json` | **Tauri v2 桌面端** |
| `app.json` 含 `expo` 字段 / `package.json` 有 `expo` 依赖 | **Expo React Native** |
| `next.config.{js,ts,mjs}` | **Next.js** |
| `vite.config.{js,ts}` + `package.json` 有 `react` | **Vite + React** |
| `Cargo.toml` 根目录（无 tauri） | **纯 Rust CLI/库** |
| `pnpm-workspace.yaml` / `packages/*` | **Monorepo**（需要额外判定子包技术栈） |

详细的"每种技术栈 → 推荐通用 skill + 知识主题 + hook 路径"对应关系见 [references/tech-stack-matrix.md](references/tech-stack-matrix.md)。Claude 应该读这个 reference 获取具体值，不要凭记忆填。

遇到未知技术栈：根据 `package.json` dependencies 和 `Cargo.toml` dependencies 自行推断，按 reference 的"兄弟规则"段落处理。

### Step 2. 通过 AskUserQuestion 确认关键分叉

**只问必要的问题**（2-3 个最多）。推荐模板：

1. **技术栈匹配**：Claude 识别出 `<detected-stack>`，让用户确认或修正
2. **知识文件初始化**：从现有 CLAUDE.md 拆解（如存在）/ 建空骨架 / 骨架 + 扫描代码提取首批条目
3. **Stop hook 监控路径**：给出 reference 推荐的默认值，让用户确认或自定义（比如 monorepo 需要 `packages/*/src/`）

如果项目没有 CLAUDE.md，跳过第 2 题的"拆解"选项。

### Step 3. 生成产物

按确认后的参数依次产出以下文件。**所有模板放在 `assets/`，不要在对话里临时拼接**——读 asset 文件内容，替换占位符后写出。

#### 3.1 `.claude/skills/dev-workflow/SKILL.md`

基于 [assets/dev-workflow-SKILL.md](assets/dev-workflow-SKILL.md)，替换占位符：

| 占位符 | 内容 |
|---|---|
| `{{CODE_PATHS}}` | Stop hook 监控路径（供 description 触发说明用，如 `src/ 或 src-tauri/src/`） |
| `{{KNOWLEDGE_TABLE}}` | 知识主题映射表（按识别出的主题切分） |
| `{{COMMON_SKILLS}}` | 本项目适用的通用 skill 列表 |
| `{{LINT_COMMANDS}}` | 本项目的 lint/format/typecheck 命令块 |

#### 3.2 `dev-notes/knowledge/*.md`

按 Step 2 选择的初始化方式：

- **拆解 CLAUDE.md**：读 CLAUDE.md 全文，按主题归类条目（参考 [references/tech-stack-matrix.md](references/tech-stack-matrix.md) 的主题切分说明），写成每个 knowledge 文件
- **建骨架**：用 [assets/knowledge-topic.md](assets/knowledge-topic.md) 模板生成每个主题的空骨架文件
- **骨架 + 代码扫描**：骨架基础上，用 Grep 扫描项目常见坑（如 `@ts-ignore` / `biome-ignore` / 特殊注释 / 硬编码路径等）提取首批条目

知识条目格式见 [references/knowledge-entry-format.md](references/knowledge-entry-format.md)。

#### 3.3 `.claude/settings.json` 的 Stop hook

**重要**：不要覆盖现有 settings.json，只**合并** Stop hook。

1. 读现有 `.claude/settings.json`（可能不存在，那就创建新的仅含 hooks 和最小 permissions）
2. 从 [assets/stop-hook-snippet.json](assets/stop-hook-snippet.json) 读 hook 片段模板
3. 替换 `{{CODE_PATHS_REGEX}}`（例如 `^(src/|src-tauri/src/)`）
4. 合并进 `hooks.Stop` 数组。如果已存在 Stop hook 且提到 `/simplify`，**跳过**（幂等）

**如果 settings.json 累积了大量本地 permissions（> 30 条）**：主动建议把它们搬到 `settings.local.json`（被 `.claude/*` gitignore 规则屏蔽），再入库精简版。参考 [references/settings-split-recipe.md](references/settings-split-recipe.md)。

#### 3.4 更新 `CLAUDE.md`

如果 CLAUDE.md 存在：在文件**顶部**（`# CLAUDE.md` 之后）插入"开发工作流"段。模板见 [assets/claude-md-snippet.md](assets/claude-md-snippet.md)。

如果不存在：不要自动创建 CLAUDE.md——提示用户先跑 `/init`。

#### 3.5 `.gitignore` 反向允许（视需要）

如果 `.gitignore` 有 `.claude/*` 或 `.claude/settings*` 类规则，把这些路径加到反向允许列表，确保产物能入库：

```
!.claude/skills/dev-workflow/
!.claude/settings.json
```

具体位置见 [references/gitignore-patch.md](references/gitignore-patch.md)。

### Step 4. 验收提示

生成完成后向用户展示：

- 产物文件清单（带链接）
- 如何验证：在下一轮对话观察 `/dev-workflow` 是否被自动触发
- 下一步可选动作：push / commit / 继续补充 knowledge 条目

## 设计原则

- **不覆盖**：settings.json、CLAUDE.md、.gitignore 都是"合并"而不是"重写"
- **幂等**：如果文件已经是最终形态，跳过而不是重复
- **可撤销**：每一步产物都是独立的文件或可清晰定位的片段，用户能逐个 revert
- **不喧宾夺主**：knowledge 文件描述项目特有的约束，**不要**重复 Claude 已有的通用知识（见 knowledge-entry-format 里的 "不记录什么"）

## 何时不使用此 skill

- 项目已经有 `dev-workflow` skill 和 knowledge 目录：用户想**更新**的话不走 init，直接编辑对应文件
- 项目是一次性脚本或 throwaway 实验：基础设施成本不划算

## 资源

- [references/tech-stack-matrix.md](references/tech-stack-matrix.md) — 各技术栈的推荐 skill / 主题 / hook 路径 + 兄弟规则
- [references/knowledge-entry-format.md](references/knowledge-entry-format.md) — 知识条目的格式与该记录/不该记录的规则
- [references/settings-split-recipe.md](references/settings-split-recipe.md) — settings.json ↔ settings.local.json 权限拆分步骤
- [references/gitignore-patch.md](references/gitignore-patch.md) — `.gitignore` 反向允许规则的定位逻辑
- [assets/dev-workflow-SKILL.md](assets/dev-workflow-SKILL.md) — dev-workflow skill 模板
- [assets/knowledge-topic.md](assets/knowledge-topic.md) — 空知识文件骨架模板
- [assets/stop-hook-snippet.json](assets/stop-hook-snippet.json) — Stop hook JSON 片段
- [assets/claude-md-snippet.md](assets/claude-md-snippet.md) — 插入到 CLAUDE.md 顶部的引用段
