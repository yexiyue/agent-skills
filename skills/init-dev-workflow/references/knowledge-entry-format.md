# 知识条目格式

dev-notes/knowledge 下每个主题文件的内部条目格式与该记录/不该记录的规则。

## 条目结构

每条知识用以下模板书写：

```markdown
### 条目标题

简短描述做了什么、为什么这样做。

**正确做法**：
- 具体的代码模式或配置

**不要做**（可选）：
- 错误的做法及原因

**相关文件**：`path/to/file`
```

要点：
- **标题**：3-7 字，描述问题域而非解法（好：`Y.Doc 必须使用 OffsetKind::Utf16`；差：`设置 Utf16`）
- **Why**：一句话解释上下文——踩过的坑、外部约束、前任决策。Claude 判断边界时靠这一句
- **正确做法**：具体到代码片段或配置行，不要泛泛
- **不要做**：只写确实会踩坑的反例。如果所有其他做法都 OK，就删掉这段
- **相关文件**：用 repo 相对路径，给 Claude 定位锚点

## 每个文件的顶部结构

```markdown
# 主题名

## 概览

一段话说明本主题覆盖什么，包含哪些子域。

## 子域 1

### 条目 A

### 条目 B

## 子域 2

### 条目 C
```

子域按"逻辑/流程"切分，不是按"字母序/时间序"。比如 `editor.md` 可以有"Y.Doc 约束 / CodeMirror 约束 / 图片与媒体 / 大纲提取"这些子域。

## 什么该记录

- **新引入的依赖 + 正确用法**：尤其是非显性的、易踩坑的
- **发现的配置坑和 workaround**：如 "Metro 不兼容 pnpm symlink node_modules，.npmrc 必须 node-linker=hoisted"
- **做出的架构决策 + 原因**：比如 "选 Arc<dyn> 而不是泛型，因为 XX"
- **与通用最佳实践不同的项目特定做法**：比如 "本项目不走 React Query，用 zustand + Tauri event 取代"
- **解决的 bug 的根因**（如果不明显的话）：commit message 能说清的不必重复

## 什么不该记录

- **代码本身能表达的东西**：变量命名、函数签名、目录结构
- **通用编程知识**：React 的 useEffect 用法、Rust 的所有权规则
- **临时性的调试信息**：某次 debug 用到的特定 log 语句
- **git 能查到的东西**：谁什么时候改的什么、版本升级 changelog
- **项目当前待办/已完成的事**：那是 issue tracker / milestone 的职责

## 条目应该独立可读

别人（或未来的你）读单个条目就能理解。不要依赖阅读顺序——如果条目 B 必须先读 A，要么合并，要么在 B 里提一句"假设已了解 A"。

## 记录时机

两个触发点：
1. **开发过程中主动记录**：遇到坑、做决策时当场写下
2. **开发结束时回看**：完成一个 feature 或修复一个 bug 后，检查"有没有新坑值得存"

两者都行，不要指望回头再补——那时候动机已经淡化。

## 示例（好）

```markdown
### Y.Doc 必须使用 OffsetKind::Utf16

所有 `yrs::Doc` 必须以 `OffsetKind::Utf16` 创建（与前端 JS yjs 一致）。
yrs 默认的 `OffsetKind::Bytes` 会导致 CJK 字符 `block_offset` 溢出 panic。

**正确做法**：
```rust
let opts = yrs::Options {
    offset_kind: OffsetKind::Utf16,
    ..Default::default()
};
let doc = Doc::with_options(opts);
```

**相关文件**：`src-tauri/src/yjs/mod.rs`
```

- 标题描述问题域（"必须使用 Utf16"）
- Why 带来源（与前端对齐）+ 错误后果（panic）
- 具体代码
- 相关文件给锚点

## 示例（差）

```markdown
### 使用 Utf16

设置 offset_kind 为 Utf16。
```

问题：不解释为什么、没有代码、没有文件指引。读了也不知道什么时候应该用它。
