# ex-skill

> 语言 / Language：[English](README.md)

一套自包含的 AI 技能，用于分析用户过往的感情证据，并生成一个能够复现前任的个性、语气和说话风格的模仿伴侣。

## 它能做什么

整个流程分为三个阶段：

```
evidence (聊天记录、文档、图片)
        │
        ▼
personality-analysis-skill  ──►  <subject>_personality_profile.md
        │
        ▼
imitation-skill-generator  ──►  imitation-<alias>/  （可直接使用的模仿技能）
        │
        ▼
imitation skill  ──►  以该对象的口吻生成的消息
```

1. **分析** —— `personality-analysis-skill` 读取用户上传的关于前任的聊天记录、文档和图片，生成一份单一的、机器可读的 Markdown 画像。
2. **生成** —— `imitation-skill-generator` 读取该画像，生成一个完整的、可直接投入使用的模仿技能。
3. **模仿** —— 生成的模仿技能复现该对象的语气、节奏、词汇、情绪风格和记忆。

## 技能

| 技能 | 用途 | 输入 | 输出 |
|-------|---------|-------|--------|
| `personality-analysis-skill` | 深度分析前任的个性、情绪、心理和说话方式 | 聊天记录、`.txt`/`.pdf`/`.docx`、图片、聊天导出 | 一份 `<subject>_personality_profile.md` |
| `imitation-skill-generator` | 将个性画像转化为可用的模仿技能 | 一份个性画像 `.md` | `imitation-<alias>/` 技能目录 |

使用生成器时会在本地生成 `skills/imitation-<alias>/`；生成的画像和技能不包含在本仓库中。

### personality-analysis-skill

- 解析并规范化聊天记录，对图片进行 OCR，提取文档文本。
- 区分「对象」的声音与「用户」的声音。
- 使用内置的评分标准对个性、情绪、心理和语言维度进行打分。
- 重建重要的记忆片段和事件级情绪。
- 输出一份严格遵循 `templates/personality_profile.template.md` 的画像，并附带机器可读的 JSON 契约。

### imitation-skill-generator

- 校验输入画像的 schema。
- 提取身份、核心特质、语气、标志性短语和模拟指引。
- 填充内置模板，并将画像作为唯一事实来源一并打包。
- 在 `skills/` 下输出一个经过校验、自包含的模仿技能。

## 目录结构

```
ex-skill/
├── skills/                            # 仓库内置技能
│   ├── personality-analysis-skill/
│   ├── imitation-skill-generator/
├── README.md / README_zh.md
└── qq-plugin.md / qq-plugin_zh.md
```

每个已注册的技能都包含一个 `SKILL.md`（frontmatter + 指令），以及它所需的任何捆绑资源
（`references/`、`templates/`）。这些技能都是自包含的：它们自带 schema、评分标准和模板，
作为技能资源不需要网络、数据库或自身目录之外的文件。模型推理由宿主 agent 运行环境处理，并可能使用其配置的服务商。
生成的画像、原始证据和 `imitation-<alias>/` 产物属于用户数据，不包含在仓库内置技能目录中。

## 如何构建 / 安装

这里没有编译步骤 —— 这些是由技能框架加载的声明式 Markdown 技能。

1. 克隆本仓库。
2. 将每个技能目录放到 `skills/<skill-name>/`。
   每个目录都必须包含一个 `SKILL.md`，其 frontmatter 中需有合法的 `name` 和 `description`。
3. 让捆绑资源与每个技能保持在同一目录下（例如
   `personality-analysis-skill/references/analysis_rubric.md` 和
   `personality-analysis-skill/templates/personality_profile.template.md`）。
4. 校验结构：每个 `SKILL.md` 都必须有 `name`、`description`（200 字符以内，说明「做什么」和「何时触发」），
   并且只能引用其自身目录内的文件。

一个技能只要符合 `skill-creator` 的目录结构即视为合法：

```
skills/<skill-name>/
├── SKILL.md
└── <bundled resources>
```

## 使用方法

1. 提供感情相关材料（聊天记录、文档、图片），调用 `personality-analysis-skill` 生成画像。
2. 将该画像交给 `imitation-skill-generator`，生成一个 `imitation-<alias>` 技能。
3. 用一段对话提示调用生成的模仿技能，即可得到以该对象口吻输出的消息。

## 隐私与安全

- 技能本身不包含发布或上传画像/生成技能的代码，生成文件会写入工作区；但 AI 运行环境可能会将提示词和你提供的材料
  发送给其配置的模型服务商。若材料不能离开本机，请检查运行环境及服务商的数据处理条款，并使用符合要求的本地模型。
- 原始证据以及任何包含真实姓名或聊天引用的画像都属于隐私内容，不应提交到公开仓库。
- 通用技能（`personality-analysis-skill`、`imitation-skill-generator`）不包含任何个人数据，可以安全共享。
- 请负责任地、仅在征得同意的前提下使用模仿技能；将心理层面的发现视为假设，而非诊断。

## 校验

仓库内置的技能目录包含 `TEST_REPORT.md`，用于记录结构检查、schema 有效性、自包含性和隐私检查。
修改内置技能后，请重新运行这些检查，以确认它仍能独立加载和运行。

## QQ 接入指南

将生成的 imitation skill 与 SnowLuma、qq-bridge 和 DeepSeek Harness 集成的完整操作流程，见 [QQ Plugin 接入说明](qq-plugin_zh.md)。

若希望集合所有前置程序直接开始运行主程序，见 [一键启动.bat文件](onekey-startup_zh.md)