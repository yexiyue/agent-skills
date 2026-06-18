---
name: anime-mascot-cards
description: |
  生成"二次元看板娘知识卡片 / 科普卡片"的成套提示词:根据知识主题自动设计贴合主题的看板娘角色人设,并产出一整套风格、角色高度统一的知识卡片提示词(主打 GPT-4o / gpt-image,同时兼容 Nano Banana / 即梦)。核心是把"角色 + 版式 + 配色 + 画风"固化成可复用骨架,每张卡只替换知识内容字段,从而让 AI 生成一整套看起来像同一个 IP、同一套风格的卡片(就是小红书 / B站 / X 上很火的那种)。
  触发场景:
  (1) 用户想做"看板娘知识卡片 / 二次元科普卡片 / 角色一致性卡片 / 一整套知识卡片",或提到那种带可爱角色讲解的科普图。
  (2) 用户要用 AI(GPT-4o / gpt-image / Nano Banana 等)批量生成风格统一的系列卡片、信息图、科普图,需要角色和画风跨图保持一致。
  (3) 用户想把一篇内容 / 一组知识点做成一套带固定二次元角色讲解的卡片。
  关键词:看板娘、知识卡片、科普卡片、二次元卡片、角色一致性、风格统一、成套卡片、系列卡片、信息图角色、gpt-image 卡片、Nano Banana 卡片、AI 知识卡。
  即使用户没明说"看板娘"或"提示词",只要诉求是"用 AI 做一套风格统一、带可爱角色的知识 / 科普卡片",都应使用本 skill。
---

# 二次元看板娘知识卡片提示词生成器

## 这个 skill 做什么

输入一个知识主题(和一组知识点),产出一整套**可直接复制粘贴**的看图提示词,让 AI 生图工具产出一系列**角色和风格高度统一**的二次元看板娘知识卡片。

- **产物是纯文本提示词**,不直接调 API 生图、不渲染 HTML。因此它跨 agent 通用(Claude Code / Codex / Cursor 都能跑),也不依赖任何 API key。
- **主打生图模型是 GPT-4o / gpt-image**(用户在 ChatGPT 里"上传参考图 + 粘贴提示词",或调 `gpt-image-1` API)。同一套提示词也能喂给 Nano Banana / 即梦,差异见 [references/workflow-gpt-image.md](references/workflow-gpt-image.md)。
- **核心价值不是"会画画",而是"会让一整套图统一"**。统一靠的是工程化的提示词结构,不是运气。

## 为什么这样能做出"统一的一整套"(先理解原理)

一套卡片看起来像"同一个 IP、同一套风格",靠的是四件事叠在一起。理解它们,你才能在任何主题上复刻,而不是死记模板:

1. **锚定一张角色参考图**——先把看板娘定稿成一张图,之后每张卡都以它为输入。模型有了明确的"身份基准",不靠每次文字描述去碰运气。
2. **把"不变的"全部固化进固定提示词块**——角色、画风、版式、配色、比例写成逐字不动的"角色块 + 模板块"。
3. **每张卡只替换"知识内容字段"**——把"会变的内容"和"不能变的风格"物理隔离,骨架原样复制,口径自然一致。
4. **末尾加强一致性约束句**——明确告诉模型"与参考图 100% 一致,只改文字内容",压住重抽时的漂移。

完整的杠杆清单(共 11 项)和每项"为什么有效",见 [references/consistency-factors.md](references/consistency-factors.md)。**生成任何一套卡片前都应先读它**——它是本 skill 的灵魂。

## 工作流

> 目标:走完五步,交给用户一份"角色档案 + 成套提示词清单 + 生图操作说明"。其中**第 2 步设计看板娘人设、第 4 步装配提示词**是质量关键。

### Step 1 · 收集输入并确认关键分叉

先弄清四件事(能从对话推断的就别问;只在必要时用 `AskUserQuestion` 问,一次最多 2-3 个):

| 要素 | 说明 | 缺省处理 |
|---|---|---|
| **知识主题 + 知识点** | 整套卡讲什么?每张卡一个知识点 | 用户只给大主题时,帮他拆成 N 个知识点(每张卡一个),拆完先跟用户对一遍 |
| **角色来源** | ① 据主题新设计一个看板娘 ② 复用已有角色档案(同一 IP 贯穿不同系列)③ 用户自带参考图 | 默认①;若用户之前用本 skill 做过、想沿用同一角色,走② |
| **画风方向** | 手绘信息图 / chibi Q版 / 日系赛璐珞 / 厚涂插画 / 吉卜力风 等 | 用户没指定就按主题在 Step 2 给推荐,并说明理由 |
| **卡片数量与画幅** | 几张?竖版(知识卡默认)还是其它 | 默认竖版;gpt-image 竖版用 `1024x1536`(2:3),见下文画幅说明 |

**角色来源**这一项最值得用 `AskUserQuestion` 确认——它决定整套卡的"脸"。

### Step 2 · 设计贴合主题的看板娘人设,并写成"角色档案"

这是让卡片"既统一又贴题"的关键。**人设要贴合知识主题**——讲编程配科技感少女、讲中医配汉服药童、讲理财配冷静职场风。主题 → 人设(发型 / 服装 / 配色 / 画风)的映射方法和示例,见 [references/persona-design.md](references/persona-design.md)。

产出一个**角色档案**(角色块的来源),用 [assets/mascot-profile-template.md](assets/mascot-profile-template.md) 模板填写。它包含:角色一句话设定、外观锁定项(发型 / 发色 / 瞳色 / 服装 / 配饰)、统一画风关键词、统一配色(给十六进制)、看板娘在卡片中的固定位置。

> 角色档案的意义:它就是"统一"的物理载体。一旦定稿,后面所有卡片的"角色块"逐字复制它。把它作为文件留给用户,下次做新系列想沿用同一 IP 时,直接复用即可(对应 Step 1 的角色来源②)。

同时,在档案里附一条**"角色定稿提示词"**——用于在 gpt-image 里先单独生成一张高质量角色立绘(可选再生成一张角色设定表 / 三视图)。这张立绘就是后续每张卡要上传的参考图(锚点)。

### Step 3 · 定卡片模板骨架(模板块)

固定整套卡的版式,写成逐字不变的"模板块":画幅比例、背景(肌理 / 底色)、标题区样式、正文分区(2–4 节)、配色、画风关键词、看板娘固定位置、留白与收尾词。模板块的标准结构和可选风格,见 [references/prompt-templates.md](references/prompt-templates.md)。

### Step 4 · 逐卡装配提示词

每张卡的最终提示词 = **角色块(Step 2)** + **模板块(Step 3)** + **该卡知识内容字段** + **一致性约束句**。

- 角色块、模板块在每张卡里**逐字相同**,只有"知识内容字段"(标题 + 2–4 个要点)每张不同。
- 一致性约束句针对 gpt-image 写,例如:"请保持与参考图中角色完全一致——面部特征、发型、发色、服装、配色、画风 100% 相同,仅更换文字内容与角色的自然姿态"。
- 第 2 张起追加一句"风格、版式、配色与上一张完全一致"。

三类模板(角色定稿提示词 / 模板块 / 成卡提示词)的完整原文与填空说明,见 [references/prompt-templates.md](references/prompt-templates.md)。**装配时读它,按占位符替换,不要凭记忆拼**。

### Step 5 · 输出成套提示词清单 + 生图操作说明

用 [assets/card-set-template.md](assets/card-set-template.md) 模板,把成果组织成一份清单交给用户:

1. **角色定稿提示词**(先生成参考图)
2. **每张卡的成卡提示词**(按知识点顺序排好,编号)
3. **生图操作说明**:在 gpt-image 里怎么用——先用角色定稿提示词生成立绘 → 之后每张卡"上传这张立绘作参考图 + 粘贴该卡提示词"。详见 [references/workflow-gpt-image.md](references/workflow-gpt-image.md)。
4. **校对提醒**:AI 生图的中文标注常出错别字 / 串字,逐张人工核对文字。

## 画幅与模型小贴士(主打 gpt-image)

- gpt-image(`gpt-image-1`)的尺寸只有 `1024x1024` / `1536x1024`(横)/ `1024x1536`(竖)/ `auto`。**知识卡用竖版 `1024x1536`(2:3)**,不要写"9:16"——gpt-image 不支持任意比例,9:16 是 Nano Banana / MJ 的写法。
- gpt-image 的一致性来自**上传参考图 + 明确的"保持一致"措辞**,不像 MJ 靠 `--seed`。所以提示词里别写 seed / `--ar` / `--cref` 这类 MJ 参数。
- gpt-image 中文文字渲染尚可但仍会错;复杂版式偶尔要多生成几张挑。具体避坑见 [references/workflow-gpt-image.md](references/workflow-gpt-image.md)。
- **诚实取舍**:论"跨图脸部一致性 + 中文文字"的上限,Nano Banana Pro 仍强于 gpt-image。本 skill 把 gpt-image 设为主打,是因为它**易获取、无水印、与 OpenAI / Codex 生态一致**,对多数知识卡足够好。若用户对脸部一致性要求极高、或整套卡频繁崩脸,建议把同一套提示词改投 Nano Banana Pro(只需把尺寸句改成 9:16,见 [references/workflow-gpt-image.md](references/workflow-gpt-image.md) 的差异表)。

## 何时不使用此 skill

- 用户要的是**纯代码渲染的信息图**(HTML / SVG、文字零误差、可精确控版):那更适合 `baoyu-infographic` 这类 skill,本 skill 主打的是二次元插画风的成套卡。
- 用户只要一张单图、不在乎"成套统一":直接写一条提示词即可,不必走全流程。
- 用户要的是表情包 / 贴纸:可借用本 skill 的一致性原理,但版式模板要换成网格贴纸式(可在 [references/prompt-templates.md](references/prompt-templates.md) 找到对应变体)。

## 资源

- [references/consistency-factors.md](references/consistency-factors.md) — **风格统一的 11 个关键因素 + 为什么有效 + gpt-image 专属技巧**(生成前必读)
- [references/prompt-templates.md](references/prompt-templates.md) — 角色定稿 / 模板块 / 成卡提示词三类模板原文与填空说明,含手绘卡 / chibi / 设定表 / 贴纸网格等变体
- [references/persona-design.md](references/persona-design.md) — 知识主题 → 看板娘人设(画风 / 服装 / 配色)的映射方法与示例库
- [references/workflow-gpt-image.md](references/workflow-gpt-image.md) — 在 ChatGPT / `gpt-image-1` API 里逐步生图的两步法、批量做法、与 Nano Banana / 即梦的差异、避坑清单
- [assets/mascot-profile-template.md](assets/mascot-profile-template.md) — 角色档案模板(沉淀角色设定,跨系列复用同一 IP)
- [assets/card-set-template.md](assets/card-set-template.md) — 一整套卡片的提示词清单输出模板
