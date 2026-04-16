## 开发工作流

**IMPORTANT**：执行任何开发任务（编写代码、修改配置、添加依赖）前，必须先调用 `/dev-workflow` skill。它会加载项目知识库（`dev-notes/knowledge/`）中的最佳实践和踩坑记录，并在开发完成后引导更新知识库。

知识库主题：

{{KNOWLEDGE_LINKS}}

<!--
{{KNOWLEDGE_LINKS}} 占位示例（按项目的实际 knowledge 文件替换）：

- `dev-notes/knowledge/theme-and-styling.md` — shadcn/ui、主题变量、窗口装饰
- `dev-notes/knowledge/editor.md` — CM6、Y.Doc、y-codemirror.next
- `dev-notes/knowledge/rust-backend.md` — Tauri command、SeaORM、YDocManager
- `dev-notes/knowledge/toolchain.md` — Biome、Lefthook、Lingui、Cargo workspace

插入位置：CLAUDE.md 文件开头的 `# CLAUDE.md` 和第一行 Overview 之间，
作为独立段落。这样 Claude 在读 CLAUDE.md 时第一眼看到 /dev-workflow 引导。
-->
