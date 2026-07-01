<!--
迷你品牌规范模板。对应 references/design-principles-guide.md 第八章总结的
"品牌理念 → 视觉规范(Logo核心+配套系统) → 治理与应用" 三段式骨架（11 节）。

使用方式：复制这份模板，把 {{...}} 占位符替换成实际内容；方括号里的默认值
（0.5X、16/32/48/180/192/512 等）来自 design-principles-guide.md 第九章
"适合写成硬性规则的规范"，没有特殊理由不要改动；标了"经验法则/默认起点"的数值
可以按项目情况调整，但要在文档里如实说明这是可调整项而非绝对标准。
没有做的章节（比如很多小项目不需要单独的构造网格页）可以整节删除，不要留空占位。
-->

# {{BRAND_NAME}} 品牌 / Logo 使用规范

> 版本 {{VERSION}} · {{DATE}}

## 1. 品牌理念

- **使命/定位**：{{MISSION}}
- **目标受众**：{{AUDIENCE}}
- **品牌人格（3-5 个形容词）**：{{PERSONALITY}}
- **语调 Voice & Tone**：{{VOICE_TONE}}

## 2. Logo 总览

{{LOGO_OVERVIEW_IMAGE}}

- **类型**：{{LOGO_TYPE}}（如：Combination Mark / Wordmark / Lettermark，参见 design-principles-guide.md 第一章）
- **构成说明**：{{LOGO_COMPONENTS}}（图形符号代表什么、文字标使用了什么处理）

## 3. 构造网格（可选）

> 只在真正用网格系统起草过设计时保留这一节；如果网格是事后补画的展示图，
> 要如实说明"仅供比例参考"，不要包装成"数学必然性"（design-principles-guide.md 2.4）。

{{CONSTRUCTION_GRID_IMAGE}}

- **网格类型**：{{GRID_TYPE}}（圆形网格 / 黄金比例网格 / 模块网格 / 三角辅助线）
- **基准单位**：{{GRID_UNIT}}

## 4. 安全间距 Clear Space

{{CLEARSPACE_IMAGE}}

- **单位 X 的定义**：{{X_DEFINITION}}（如：图形符号高度 / 某关键字母的 cap height）
- **四周最小留白**：≥ **{{CLEARSPACE_MULTIPLE, 默认 0.5X}}**

## 5. 最小使用尺寸

| 场景 | 最小尺寸 |
|---|---|
| 印刷 · 完整 Logo | ≥ {{PRINT_MIN_FULL, 默认 20–25mm}} |
| 印刷 · 仅图标 | ≥ {{PRINT_MIN_ICON, 默认 6–10mm}} |
| 数字 · 完整 Logo | ≥ {{DIGITAL_MIN_FULL, 默认 60–80px}} |
| 数字 · 仅图标 / favicon | ≥ {{DIGITAL_MIN_ICON, 默认 16–32px}} |

低于最小尺寸时，切换到 [第 8 节](#8-版本变体) 的简化图标版或纯文字版，不要无限缩小主版本。

## 6. 色彩规范

| 层级 | 名称 | Pantone(C/U) | CMYK | RGB | Hex |
|---|---|---|---|---|---|
| 主色 1 | {{COLOR_NAME}} | {{PANTONE}} | {{CMYK}} | {{RGB}} | {{HEX}} |
| 主色 2 | | | | | |
| 辅助色 | | | | | |

- **明背景适配**：{{LIGHT_BG_RULE}}（默认：0–20% 深度背景用全彩版或纯黑版）
- **暗背景适配**：{{DARK_BG_RULE}}（默认：60–100% 深度背景必须用反白版）
- **禁止事项**：不擅自调整以上数值；不叠加渐变/阴影/发光等未授权效果；强调色不用于文字、不升级为主色

## 7. 字体规范

- **Logo 专用字体/处理**：{{LOGO_FONT}}（是否定制、基于哪款现成字体做了哪些修改）
- **品牌正文字体**：{{BODY_FONT}}（含字重梯度）
- **字距**：{{TRACKING_VALUE}}
- **字体授权**：{{FONT_LICENSE_NOTE}}（默认建议：wordmark 转曲交付，避免依赖字体文件本身；活文本场景需单独确认 Web/App 授权）

## 8. 版本变体

| 版本 | 触发场景 | 文件 |
|---|---|---|
| 完整 Lockup 版 | 官网首屏、海报、名片 | {{FILE_FULL}} |
| 主标版（去 slogan） | 常规 Header、文章配图 | {{FILE_MAIN}} |
| 简化图标版 | App 图标、社交头像、水印 | {{FILE_ICON}} |
| 极简 Favicon 版 | 16–32px 标签页 | {{FILE_FAVICON}} |
| 纯黑版 / 纯白反白版 | 单色印刷、深色背景 | {{FILE_MONO}} |

验收标准：去掉文字后，仅凭图标版是否仍能认出品牌？不能则退回重新设计（design-principles-guide.md 7.4）。

## 9. 错误示范 Misuse / Don't

> 默认用 design-principles-guide.md 第六章的 14 类禁止行为，按项目实际情况增删；
> 每条配一句极简祈使句，"左正确用法 + 右错误用法缩略图"是行业惯例格式。

- [ ] 禁止拉伸/压缩变形
- [ ] 禁止旋转/倾斜
- [ ] 禁止改变组合元素间相对比例、位置或排列顺序
- [ ] 禁止添加阴影、描边、渐变、3D、发光等特效
- [ ] 禁止改变官方配色
- [ ] 禁止在低对比度或杂乱背景上使用
- [ ] 禁止破坏安全间距、与其他元素拥挤放置
- [ ] 禁止拆解、重组或重排内部构成元素
- [ ] {{OTHER_MISUSE_RULES}}

## 10. 实际应用场景

{{APPLICATION_EXAMPLES}}（网站头图、App 图标、社交头像、周边物料等真实载体示意，附带该场景下的特殊例外规则）

## 11. 治理与联系方式

- **商标/版权声明**：{{TRADEMARK_NOTE}}（若含 AI 生成内容，参见 ai-generation-guide.md 5.4 节的商用风险自查清单）
- **使用授权范围**：{{USAGE_SCOPE}}
- **素材下载**：{{ASSET_DOWNLOAD_LINK}}
- **联系方式 / 审批流程**：{{CONTACT}}
