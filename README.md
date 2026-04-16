# agent-skills

一组面向 Claude Code 的 agent skill，用于快速为项目搭建开发基础设施。

## 可用 skill

| Skill | 用途 |
| ----- | ---- |
| [init-dev-workflow](skills/init-dev-workflow/) | 为一个项目生成 dev-workflow skill + 按主题切分的 knowledge 库 + Stop hook + CLAUDE.md 集成段。支持 Tauri v2 / Expo RN / Next.js / Vite+React 四种预设 |

## 安装

本仓库遵循 [vercel-labs/skills](https://github.com/vercel-labs/skills) 的 skill 发现约定，所有 skill 都位于 `skills/<name>/` 下。

### 全部装到用户级

```bash
npx skills add <owner>/agent-skills --global
```

> 把 `<owner>` 换成本仓库的 GitHub 用户名/组织名。

### 只装某个

```bash
npx skills add <owner>/agent-skills --skill init-dev-workflow --global
```

### 装到当前项目

省略 `--global` 即装到当前目录的 `.claude/skills/`：

```bash
npx skills add <owner>/agent-skills --skill init-dev-workflow
```

### 查看有哪些 skill

```bash
npx skills add <owner>/agent-skills --list
```

### 拷贝而不是 symlink

Windows 下 symlink 需要开发者模式或管理员权限，建议加 `--copy`：

```bash
npx skills add <owner>/agent-skills --global --copy
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
