# settings.json 拆分菜谱

`.claude/settings.json` 会被 git 跟踪（用于 hook + 团队共享的基础 permission），而 `.claude/settings.local.json` 留作本地私有（累积的临时 allow、用户机器特定路径）。

当项目首次引入 dev-workflow 时，settings.json 往往已经累积了几十上百条本地 allow。直接 git add 会把噪音一起入库。菜谱如下。

## 何时应用

- 现有 `settings.json` 的 `permissions.allow` 超过 ~30 条
- 或含有临时 / 一次性命令（gh issue edit、临时 ID、node -e 一次性脚本等）
- 或 `additionalDirectories` 含跨项目绝对路径（`d:\workspace\other-project\...`）

## 步骤

### 1. 合并到 local

把 `settings.json` 中 `permissions.allow` 和 `additionalDirectories` 合并到 `settings.local.json`（去重）。

```bash
node -e "
const fs = require('fs');
const main = JSON.parse(fs.readFileSync('.claude/settings.json','utf8'));
const localPath = '.claude/settings.local.json';
const local = fs.existsSync(localPath)
  ? JSON.parse(fs.readFileSync(localPath,'utf8'))
  : {};
local.permissions = local.permissions || {};
local.permissions.allow = local.permissions.allow || [];
local.permissions.additionalDirectories = local.permissions.additionalDirectories || [];

const allowSet = new Set(local.permissions.allow);
for (const a of (main.permissions?.allow || [])) {
  if (!allowSet.has(a)) { local.permissions.allow.push(a); allowSet.add(a); }
}

const dirSet = new Set(local.permissions.additionalDirectories);
for (const d of (main.permissions?.additionalDirectories || [])) {
  if (!dirSet.has(d)) { local.permissions.additionalDirectories.push(d); dirSet.add(d); }
}

fs.writeFileSync(localPath, JSON.stringify(local, null, 2));
console.log('local allow:', local.permissions.allow.length);
console.log('local additionalDirectories:', local.permissions.additionalDirectories.length);
"
```

### 2. 重写 settings.json 为精简版

保留：
- 全部 `hooks`
- 本项目**通用**的 permission（跨团队跨机器都能用的）
- 可信的 MCP 相关允许（比如 context7 query-docs）

精简版示意（按技术栈调整）：

```json
{
  "hooks": { ... },
  "permissions": {
    "allow": [
      "Bash(pnpm format:*)",
      "Bash(pnpm lint:*)",
      "Bash(pnpm install:*)",
      "Bash(pnpm test:*)",
      "Bash(cargo fmt:*)",
      "Bash(cargo clippy:*)",
      "Bash(cargo test:*)",
      "mcp__plugin_context7_context7__resolve-library-id",
      "mcp__plugin_context7_context7__query-docs"
    ]
  }
}
```

删除的：
- 一次性 gh CLI 命令（特定 issue number、特定 PVT_* ID）
- 一次性 node -e 脚本
- 临时 grep / find 命令
- 所有 `additionalDirectories`（跨机器不可移植；让 Claude Code 在需要时重新请求）

### 3. 验证

```bash
node -e "JSON.parse(require('fs').readFileSync('.claude/settings.json','utf8')); JSON.parse(require('fs').readFileSync('.claude/settings.local.json','utf8')); console.log('Both JSON valid');"
```

然后检查 `.gitignore`：
- `.claude/settings.local.json` 应该被忽略（通常由 `.claude/*` 规则覆盖）
- `.claude/settings.json` 应该**不**被忽略（需要反向允许，见 [gitignore-patch.md](gitignore-patch.md)）

## 幂等性

如果 settings.json 已经只有 hook + 少量 permission，Step 1 和 2 跳过，直接进入 dev-workflow hook 合并。

## 判断"通用 permission"的标准

问三个问题：
1. 这条命令在**本项目**的任意开发机器上都会被用到吗？
2. 这条命令在**本项目**的任意开发者身上都会用到吗？
3. 这条命令不包含**临时 ID / 个人路径 / 一次性参数**吗？

三个都是"是"才留在 settings.json。否则搬到 local。
