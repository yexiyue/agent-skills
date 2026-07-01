# agent-skills

一组面向 Claude Code 的 agent skill，用于快速为项目搭建开发基础设施。

## 可用 skill

| Skill | 用途 |
| ----- | ---- |
| [init-dev-workflow](skills/init-dev-workflow/) | 为一个项目生成 dev-workflow skill + 按主题切分的 knowledge 库 + Stop hook + CLAUDE.md 集成段。支持 Tauri v2 / Expo RN / Next.js / Vite+React 四种预设 |
| [tauri-specta](skills/tauri-specta/) | tauri-specta v2 类型安全 IPC 开发指南。Rust ↔ TypeScript 单一类型源,自动生成 bindings.ts。覆盖 `#[specta::specta]` 命令、`tauri_specta::Event`、`SpectaBuilder` 装配、bigint 处理、错误模式、CI 强制导出与常见踩坑 |
| [uniffi-bindgen-react-native](skills/uniffi-bindgen-react-native/) | uniffi-bindgen-react-native (ubrn) 开发指南:把 Rust crate 桥接成 React Native Turbo Module(也支持 WASM)。覆盖 `ubrn.config.yaml`、类型映射、async/Promise/AbortSignal、callback_interface / Foreign Trait、Megazord 多 crate、发布,以及生产中真实踩过的 12 个 build 坑 |
| [sea-orm-2](skills/sea-orm-2/) | SeaORM 2.0 Rust ORM 开发指南。新 `#[sea_orm::model]` Entity 格式、关系建模（1-1 / 1-N / M-N / 自引用 / 菱形 / Linked）、Entity Loader / Nested Select / Multi Select / Relational Query 五种查询、Nested ActiveModel 嵌套增删改、Entity First 工作流（`get_schema_registry`、`sync` vs `apply`、时间胶囊模式）、`raw_sql!` 宏（含数组展开 `{..ids}`）、RBAC + `RestrictedConnection`、1.0 → 2.0 迁移指南。基于 `2.0.0-rc.38` |
| [anime-mascot-cards](skills/anime-mascot-cards/) | 二次元看板娘知识卡片提示词生成器。根据知识主题自动设计贴合主题的看板娘人设,产出一整套**角色 / 风格高度统一**的知识卡片提示词(主打 GPT-4o / gpt-image,兼容 Nano Banana / 即梦)。核心是把"角色 + 版式 + 配色 + 画风"固化成可复用骨架,每张卡只换知识内容字段。纯文本、跨 agent 通用。覆盖统一一致性的 11 个关键因素、主题→人设映射、三类提示词模板、gpt-image 两步法生图与避坑 |
| [logo-designer](skills/logo-designer/) | Logo / 品牌视觉设计完整工作流：品牌定位访谈 -> 写出可直接粘贴进 Midjourney / GPT-4o / Nano Banana / Ideogram / 即梦等工具的生图提示词(七要素公式) -> 收敛评审(陈词滥调/识别性/类型匹配检查) -> 细化迭代 -> 本地脚本(vtracer/potrace/Pillow)把 AI 生成位图矢量化清理成干净 SVG -> 16/32/48/128/512px 多尺寸与黑白反白多背景可用性测试 -> 产出含安全间距/最小尺寸/色板/字体/14类误用禁忌的迷你品牌规范文档。references 里附两份调研整合文档(传统 logo 设计规范 + AI 生成 logo 实践指南),scripts 附三个跑通验证过的 Python 脚本 |

## 安装

本仓库遵循 [vercel-labs/skills](https://github.com/vercel-labs/skills) 的 skill 发现约定，所有 skill 都位于 `skills/<name>/` 下。

### 全部装到用户级

```bash
npx skills add yexiyue/agent-skills --global
```

### 只装某个

```bash
npx skills add yexiyue/agent-skills --skill init-dev-workflow --global
```

### 装到当前项目

省略 `--global` 即装到当前目录的 `.claude/skills/`：

```bash
npx skills add yexiyue/agent-skills --skill init-dev-workflow
```

### 查看有哪些 skill

```bash
npx skills add yexiyue/agent-skills --list
```

### 拷贝而不是 symlink

Windows 下 symlink 需要开发者模式或管理员权限，建议加 `--copy`：

```bash
npx skills add yexiyue/agent-skills --global --copy
```

## Skill 作者指南

新增 skill 的流程：

1. 在 `skills/` 下创建新目录，如 `skills/my-skill/`
2. 在目录内放 `SKILL.md`，frontmatter 至少包含 `name` 和 `description`：

   ```markdown
   ---
   name: my-skill
   description: |
     一句话说明能力 + 具体触发场景。
     触发关键词：...
   ---

   # My Skill

   ...
   ```

3. 可选：添加 `references/`（供 skill 运行时加载的参考文档）、`assets/`（供 skill 输出到用户项目的模板文件）、`scripts/`（供 skill 执行的可运行脚本）
4. SKILL.md body 中引用 references/assets 时用相对路径，如 `[references/foo.md](references/foo.md)`

详细的 skill 创作规范参考 [Claude skill-creator](https://github.com/anthropics/claude-code) 的官方指南。
