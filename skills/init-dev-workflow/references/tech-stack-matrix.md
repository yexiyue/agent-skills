# Tech Stack Matrix

四种预设技术栈的推荐默认值 + 兄弟规则（遇到未知栈时的推理路径）。Claude 按 SKILL.md Step 1 扫描出栈类型后，查本表取具体值。

## 目录

- [Tauri v2 桌面端](#tauri-v2-桌面端)
- [Expo React Native](#expo-react-native)
- [Next.js](#nextjs)
- [Vite + React](#vite--react)
- [兄弟规则（未知栈）](#兄弟规则未知栈)

---

## Tauri v2 桌面端

**探针**：根目录或 `src-tauri/` 下有 `tauri.conf.json`。

### 知识主题（4 个文件）

| 文件名 | 主题范围 |
|---|---|
| `theme-and-styling.md` | UI 组件库、主题/颜色变量、窗口装饰（macOS Overlay / Win 自定义标题栏） |
| `editor.md` *（可选）* | 如果项目有编辑器：CM6 / ProseMirror / BlockNote 等的坑 |
| `rust-backend.md` | Tauri command 约定、SeaORM/数据库、错误类型、P2P/async、tracing |
| `toolchain.md` | pnpm/Vite、Biome/Clippy、Lefthook、Lingui、Cargo workspace、CI |

如果项目没有编辑器，合并 editor 内容到 rust-backend 或删掉。

### 通用 skill 引用

```
- `/vercel-react-best-practices` — React 性能优化（re-render、bundle、waterfalls）
- `/tauri-v2` — Tauri v2 IPC、capabilities、配置
- `/rust-best-practices` — Rust 通用规范
- `/rust-async-patterns` — Tokio、异步事件循环、取消/并发
- `/lingui-best-practices` — i18n（若使用）
- `/tailwindcss` / `/tailwind-css-patterns` / `/tailwind-design-system` — Tailwind（若使用）
- `/sea-orm-2` — 如果用 SeaORM
```

### Stop hook 监控路径

- 代码路径：`src/` + `src-tauri/src/`
- hook grep 表达式：`^(src/|src-tauri/src/)`

### Lint 命令块

```bash
# 前端
pnpm lint
pnpm exec tsc --noEmit

# Rust
cd src-tauri && cargo fmt
cd src-tauri && cargo clippy -- -D warnings
cd src-tauri && cargo test
```

---

## Expo React Native

**探针**：`app.json` 含 `expo` 字段，或 `package.json` 依赖含 `expo`。

### 知识主题（4 个文件）

| 文件名 | 主题范围 |
|---|---|
| `theme-and-styling.md` | NativeWind / Tamagui、CSS 变量、Portal、Appearance |
| `editor.md` *（可选）* | 如果项目有 WebView 编辑器：Comlink bridge、bundle rebuild 流程 |
| `rust-bridge.md` *（可选）* | 如果用 uniffi-bindgen-rn：Turbo Module、JSI 类型映射 |
| `toolchain.md` | Metro、pnpm hoisted、prebuild、Lingui、EAS、lightningcss 锁版本 |

没有 WebView 编辑器或 Rust bridge 的情况下删对应主题。

### 通用 skill 引用

```
- `/vercel-react-native-skills` — React Native / Expo 通用最佳实践
- `/vercel-react-best-practices` — React 性能优化模式
- `/lingui-best-practices` — i18n（若使用）
- `/tailwindcss` / `/tailwind-css-patterns` / `/tailwind-design-system` — NativeWind 基于 Tailwind
- `/uniffi-bindgen-rn` — 如果用 Rust bridge
```

### Stop hook 监控路径

- 代码路径：`src/`（含所有 app/components/hooks/lib）
- 如果 Rust bridge 在 `packages/*/rust/` 下，加 `packages/.*/rust/`
- hook grep 表达式（仅 app）：`^src/`

### Lint 命令块

```bash
pnpm lint
pnpm exec tsc --noEmit
```

---

## Next.js

**探针**：`next.config.{js,ts,mjs}` 存在。

### 知识主题（3 个文件）

| 文件名 | 主题范围 |
|---|---|
| `theme-and-styling.md` | shadcn/ui、Tailwind、主题变量、`next/font` |
| `routing-and-data.md` | App Router、RSC、server actions、fetch 缓存 |
| `toolchain.md` | ESLint/Biome、Turbopack/Webpack、环境变量、部署 |

### 通用 skill 引用

```
- `/vercel-react-best-practices` — **首选**（为 Next.js 而生）
- `/tailwindcss` / `/tailwind-css-patterns` / `/tailwind-design-system`
- `/lingui-best-practices` — 如果用 Lingui；否则删掉
- `/claude-api` / `/ai-sdk` — 如果是 AI 应用
```

### Stop hook 监控路径

- 代码路径：`app/` 或 `src/app/`（看项目结构），加 `components/`、`lib/`
- hook grep 表达式（默认）：`^(app/|src/|components/|lib/)`

### Lint 命令块

```bash
pnpm lint
pnpm exec tsc --noEmit
```

---

## Vite + React

**探针**：`vite.config.{js,ts}` + `package.json` 依赖含 `react`，**无** `tauri.conf.json` / `next.config.*`。

### 知识主题（3 个文件）

| 文件名 | 主题范围 |
|---|---|
| `theme-and-styling.md` | UI 库、Tailwind、主题变量 |
| `routing-and-state.md` | Router（TanStack / React Router）、状态管理 |
| `toolchain.md` | Vite 配置、Biome/ESLint、构建、部署 |

### 通用 skill 引用

```
- `/vercel-react-best-practices` — 虽然名字有 Vercel，React 部分完全通用
- `/tailwindcss` / `/tailwind-css-patterns`
- `/lingui-best-practices` — 视需要
```

### Stop hook 监控路径

- `^src/`

### Lint 命令块

```bash
pnpm lint
pnpm exec tsc --noEmit
```

---

## 兄弟规则（未知栈）

按以下启发式推导，**不要**凭空猜测：

### 规则 1：判断语言

- `Cargo.toml` 根目录 → 包含 Rust 代码；加 `cargo fmt` / `cargo clippy` 到 Lint 命令
- `package.json` + 非以上四种前端栈 → 判断是"纯 Node 库 / CLI"还是"Web UI"
- 两者都没 → 是否纯 Python/Go/其他？基于探针文件定位（`pyproject.toml` / `go.mod` 等），生成对应命令块

### 规则 2：判断代码路径

按顺序检查这些候选路径是否存在并含代码：
- `src/`
- `src-tauri/src/`
- `packages/*/src/`（monorepo）
- `app/`
- `lib/` / `cmd/`（Go 风格）
- Rust crate 根目录的 `src/`

Stop hook grep 表达式从存在的候选路径组合。**单栈 1 个、monorepo 可能 3+ 个**。

### 规则 3：判断通用 skill

打开 `package.json` / `Cargo.toml`，用其 dependencies 的 keyword 匹配 `~/.claude/skills/` 下已安装的 skill。比如：

- `react`、`next` → `/vercel-react-best-practices`
- `react-native`、`expo` → `/vercel-react-native-skills`
- `@codemirror/*` → 编辑器主题文件里记录 CM6 约束
- `yjs` → 同上，加一条关于 Utf16 OffsetKind（如果用 Rust yrs）
- `tauri`、`@tauri-apps/*` → `/tauri-v2`
- `sea-orm` → `/sea-orm-2`
- `lingui` → `/lingui-best-practices`
- `tailwindcss` → `/tailwindcss`

**只引用实际存在的 skill**。调用前可以用 Bash 验证：`ls ~/.claude/skills/ | grep <name>`。

### 规则 4：判断知识主题最小集

任何项目至少有 `toolchain.md`（构建/lint/格式/CI）。其余主题按"是否存在对应代码范畴"决定：

| 存在什么 | 添加主题 |
|---|---|
| UI 组件库 / 样式系统 | `theme-and-styling.md` |
| 数据库 ORM | `database.md`（或合并到 backend） |
| 后端业务逻辑 | `backend.md` 或 `rust-backend.md` |
| 编辑器 / 富文本 | `editor.md` |
| 多语言 | 合并 i18n 条目到 toolchain 或 theme |

**合并优先于新建**。3-4 个文件是甜蜜点，超过 5 个就太细了。

### 规则 5：Stop hook 跨平台 bash 可用性

Stop hook 命令必须能在 `bash -c '...'` 里跑。Windows 下 Claude Code 使用的是 git-bash 或 WSL。所以：

- 用 `grep -E`、`git diff`、`head` 这种 POSIX 命令
- **不要**用 PowerShell 语法
- 字符串转义注意反斜杠
