# .gitignore 反向允许

许多项目用 `.claude/*` 全屏蔽 Claude Code 的本地文件，但 dev-workflow skill 和 settings.json 需要入库。这里规定添加反向允许的位置和规则。

## 检测现有规则

先读 `.gitignore`，看有没有 `.claude/*` 或类似的 catch-all：

```bash
grep -nE '\.claude' .gitignore
```

常见模式：
- `.claude/*` — 全屏蔽，需要反向允许
- `.claude/settings.local.json` — 只屏蔽 local，settings.json 已经可跟踪，**不需要**反向允许
- （无 `.claude` 规则） — 全部默认可跟踪，**不需要**改 gitignore

## 需要加的行

仅当存在 `.claude/*` 类 catch-all 时加：

```gitignore
# Claude Code - allow dev-workflow + project settings
!.claude/skills/
.claude/skills/*
!.claude/skills/dev-workflow/
!.claude/settings.json
```

逻辑解释：
1. `!.claude/skills/` — 允许跟踪 skills 父目录
2. `.claude/skills/*` — 但默认忽略所有子目录（避免无关 skill 泄漏）
3. `!.claude/skills/dev-workflow/` — 反向允许目标 skill
4. `!.claude/settings.json` — 反向允许 settings.json

## 位置

加到**现有** `.claude` 规则段的紧邻后面，不要散落在 .gitignore 其他位置。比如：

```gitignore
# ...
# Claude Code
.claude/*
!.claude/skills/
.claude/skills/*
!.claude/skills/dev-workflow/    # 新增
!.claude/settings.json           # 新增
# ...
```

## 多个已允许的 skill

项目可能已经有其他 skill 被允许（如 `!.claude/skills/project/`、`!.claude/skills/openspec-*/`）。只**追加** dev-workflow 一行，不要动已有规则。

## 验证

加完后跑：

```bash
git check-ignore -v .claude/settings.json .claude/skills/dev-workflow/SKILL.md
```

如果输出 `.gitignore:<line>:!...` 前缀带叹号，说明被反向允许（**不**被忽略），正确。
如果输出 `.gitignore:<line>:.claude/*`（无叹号），说明还在被忽略，检查规则顺序——反向允许必须**在** catch-all 之后。

## 顺序的坑

gitignore 规则按**从上到下**应用，后面的覆盖前面的。所以：

```gitignore
.claude/*                         # 全部忽略
!.claude/settings.json            # 最后生效——settings.json 被允许 ✓
```

但：

```gitignore
!.claude/settings.json            # 先允许
.claude/*                         # 后忽略——覆盖上面，settings.json 仍被忽略 ✗
```

**添加反向允许时，永远放在 catch-all 之**后**。**

## 子目录内容的陷阱

`!.claude/skills/dev-workflow/` 允许目录本身。但如果父规则 `.claude/skills/*` 存在，这条规则只允许**目录**，不自动允许目录内的文件——git 会跟踪目录的 mtime 等，但看不到内容。

gitignore 对 `*` 的行为是：只要目录被忽略，内部文件不能通过 `!` 再打开。所以 `.claude/skills/*` 后必须跟 `!.claude/skills/dev-workflow/`（注意 `/` 后缀——目录形式）。绝大多数情况下这种组合能正确工作；如果遇到"目录允许但文件仍然被忽略"的罕见情况，加更具体的一行：

```gitignore
!.claude/skills/dev-workflow/**
```
