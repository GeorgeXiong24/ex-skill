# 将 imitation skill 接入 QQ

> 语言 / Language：[English](qq-plugin.md)

本文说明如何把本仓库生成的 imitation skill 与 [qq-bridge](https://github.com/Derpyu520/qq-bridge)、
[SnowLuma](https://github.com/SnowLuma/SnowLuma) 和 DeepSeek Harness（DSH）配合使用，让 QQ 上的
消息由 DSH 按指定人格回复。

> **集成方式说明：** imitation skill 是一个包含 `SKILL.md` 和画像文件的技能目录；qq-bridge 控制台管理的是
> 人格/角色提示词。上游文档没有说明控制台支持上传或导入整个 skill 目录。因此，不要把复制整个目录到
> 控制台当作必需步骤；应从生成的 skill 中整理人格提示词，再在控制台创建角色。保留原 skill 目录作为本地
> 原始产物和事实来源。

## 组件与消息流

```text
聊天记录 / 文档 / 图片
        │
        ▼
personality-analysis-skill ──► 个性画像 .md
        │
        ▼
imitation-skill-generator ──► skills/imitation-<alias>/
        │                       ├── SKILL.md
        │                       └── references/<alias>_personality_profile.md
        ▼
从 skill 整理人格提示词 ──► qq-bridge 控制台「人格与角色」
                                      │
QQ 客户端 ◄── OneBot ◄── SnowLuma ◄── qq-bridge ◄──► DeepSeek Harness
```

- **ex-skill**：在本地分析材料、生成画像和 imitation skill。
- **SnowLuma**：连接 QQ 客户端并提供 OneBot 接口；由用户自行安装、登录和启动。
- **DeepSeek Harness**：运行 DSH agent 和模型。
- **qq-bridge**：把 QQ/OneBot 消息接入 DSH；其本地控制台管理运行模式、白名单和角色提示词。

## 前置准备

1. **准备 DeepSeek Harness**：在运行桥接的电脑上安装并启动 DSH，确认其本地 Web 地址可访问。qq-bridge
   README 当前示例使用 `http://127.0.0.1:3080`；如果你的 DSH 使用其他地址，应按实际配置修改。
2. **准备 SnowLuma**：从 [SnowLuma Releases](https://github.com/SnowLuma/SnowLuma/releases) 获取适用于你环境的
   发行包，按 SnowLuma 官方说明安装、启动、登录 QQ 并完成 WebUI 引导。SnowLuma WebUI 的默认地址通常为
   `http://localhost:5099`，以启动日志为准。
3. **准备本仓库的 skill**：在支持这些 skills 的 agent 环境中加载
   `skills/personality-analysis-skill/` 和 `skills/imitation-skill-generator/`。完整的本地生成流程见
   [README 的使用方法](./README_zh.md#使用方法)。
4. 仅使用你有权处理的材料，并在模仿真实人物前取得适当同意。聊天记录、画像和生成结果可能含有敏感信息。

## 操作流程

### 1. 分析材料并生成 imitation skill

1. 在本地向 `personality-analysis-skill` 提供聊天记录、文档或图片，明确指出哪一方是需要分析的对象。
   让技能输出一份遵循画像模板的 `<subject>_personality_profile.md`。
2. 检查画像中的对象、语言、特征、语气、记忆和置信度是否合理；证据不足时应保留不确定性，不要把推测当成事实。
3. 将画像交给 `imitation-skill-generator`，生成 `skills/imitation-<alias>/`。
4. 确认生成目录至少包含 `SKILL.md` 和
   `references/<alias>_personality_profile.md`。先在本地调用生成的 skill 做几轮测试，检查它是否忠于画像。

### 2. 安装并配置 qq-bridge

按照 [qq-bridge README](https://github.com/Derpyu520/qq-bridge) 的最新版说明操作。以下是仓库 README 所列的
典型步骤；上游版本更新时，以其文档和配置模板为准。

```bash
git clone https://github.com/Derpyu520/qq-bridge.git
cd qq-bridge
npm install
cp config.example.json config.json
```

Windows CMD 中用 `copy config.example.json config.json` 代替 `cp`。

编辑本地 `config.json`，至少检查这些配置：

- `dsh.baseUrl`：本机 DSH 地址，默认示例为 `http://127.0.0.1:3080`。
- `snowluma.wsUrl`：SnowLuma 的 OneBot WebSocket 地址，例如 `ws://127.0.0.1:3001`。
- `snowluma.httpUrl`：SnowLuma 的 OneBot HTTP API 地址，例如 `http://127.0.0.1:3000`。不要把 WebSocket 端口填在这里。
- `snowluma.accessToken`：填写 SnowLuma **HTTP API** 的 access token；未设置 token 时按模板留空。SnowLuma 的 HTTP token 和 WebSocket token 可能不同，桥接会尝试自动发现 WebSocket token。
- `snowluma.homeDir`：SnowLuma 解压/安装目录。桥接需要从此目录发现账号对应的 OneBot 配置和 WebSocket token；自动发现失败时应填实际目录。
- `allow.private`：允许触发机器人的**好友 QQ 号**列表；`allow.groups`：允许触发机器人的**QQ群号**列表。这里填写发消息的好友/群，不是机器人自己的 QQ 号。
- `deny.private` / `deny.groups`：拒绝列表；命中 deny 的用户或群即使也在 allow 中仍会被拒绝。
- `allowAllWhenEmpty`：保持 `false`。当 allow 两个列表都为空时，默认不会处理消息；设为 `true` 会在白名单空时放开全部私聊/群，风险很高。
- `consolePort` / `consoleToken`：本地控制台端口和访问令牌。使用默认端口时控制台为
  `http://127.0.0.1:3100`；令牌是访问凭据，不要公开或提交到仓库。

下面是一个**示例片段**，把占位字符串替换为你自己的数字 ID。它展示配置字段位置，不要把整段重复粘贴进已有 JSON；JSON 中不要添加注释：

```json
{
  "snowluma": {
    "wsUrl": "ws://127.0.0.1:3001",
    "httpUrl": "http://127.0.0.1:3000",
    "accessToken": "填写 SnowLuma 的 HTTP API token",
    "homeDir": "/你的/SnowLuma/安装目录"
  },
  "allow": {
    "private": ["REPLACE_WITH_ALLOWED_FRIEND_QQ_ID"],
    "groups": ["REPLACE_WITH_ALLOWED_GROUP_ID"]
  },
  "deny": {
    "private": [],
    "groups": []
  },
  "allowAllWhenEmpty": false,
  "ownerQQ": "REPLACE_WITH_ADMIN_QQ_ID",
  "consolePort": 3100,
  "consoleToken": ""
}
```

把占位字符串替换成你允许的好友 QQ 号和群号；`ownerQQ` 仅在 `closed-agent` 模式下需要填写。ID 用字符串形式书写，
桥接会将 ID 统一按字符串比较；也可以使用 JSON 数字。
SnowLuma 的 WS/HTTP 端口和 token 应以 WebUI 中的实际配置为准。默认 HTTP API 端口通常为 `3000`，WebSocket 服务端口通常为
`3001`；同一账号的 HTTP token 与 WS token 可能不同，`snowluma.accessToken` 填 HTTP token。桥接第一次连接 WS 时若出现一次
`1006` 后自动恢复并显示已连接，可能是 token 自愈的正常过程；持续自愈失败则检查 `homeDir` 和 SnowLuma 登录账号。

### 白名单在哪里设置

可直接编辑桥接目录下的 `config.json`（`allow.private`、`allow.groups`、`deny.*`），也可在运行中的 qq-bridge 控制台
「访问与安全」页面管理白名单。控制台修改后确认保存成功；直接改 `config.json` 后重启 qq-bridge 使设置生效。
白名单不只是限制“哪些消息会触发回复”：桥接提供给 agent 的发消息工具也会检查允许的群/好友目标。

若要使用 `closed-agent`（仅管理员私聊），还要在 `config.json` 的 `ownerQQ` 中填写管理员自己的 QQ 号；
同时把该 QQ 号加入 `allow.private`。`ownerQQ` 与白名单作用不同，不会自动代替 `allow.private`。
普通 `chat` 模式下按白名单设置可接入的好友/群。

### 3. 为 DSH 安装 qq-bridge preset 和 MCP

在 `qq-bridge` 仓库目录运行：

```bash
node scripts/setup-dsh.mjs
```

此步骤会配置 qq-bridge 使用的 `qq-chat` / `qq-chat-v2` preset 和 MCP server。完成后重启 DSH，使其加载这些配置。
这是桥接正常工作的必要步骤，不要因为桥接进程已能启动就跳过。

### 4. 启动 SnowLuma 和 qq-bridge

1. **启动 SnowLuma**：进入下载并解压后的发行目录。Windows 按上游说明运行 `launcher.bat`；Linux 运行 `launcher.sh`
   （需要时先执行 `chmod +x launcher.sh`）。其他系统按你下载的发行包附带的说明启动；上游 README 当前明确列出
   Windows 和 Linux 的启动命令。不要从本仓库运行 SnowLuma，也不要让桥接替你安装或启动它。
   在 SnowLuma WebUI 完成 QQ 登录后，进入 OneBot 配置，分别启用 **WebSocket 服务端** 和 **HTTP API**，记下各自端口
   与 access token。WebUI 的初始登录密码在 SnowLuma 启动日志中；首次登录后按引导设置自己的密码。该密码是
   **SnowLuma WebUI 密码**，不是 qq-bridge 控制台令牌。
2. **启动 DSH**：按 DeepSeek Harness 自身的安装方式启动 DSH 服务/应用，并确认 `dsh.baseUrl` 对应的本地地址可访问
   （示例 `http://127.0.0.1:3080`）。DSH 不是由 `npm start` 启动的。
3. **启动 qq-bridge**：在 `qq-bridge` 仓库根目录运行：

   ```bash
   npm start
   ```

   该命令实际运行 `node src/bridge.js`；Windows 也可按 qq-bridge 上游说明运行仓库根目录的 `start.bat` 守护启动。
   `npm start` 是前台进程，关闭终端会停止桥接。
4. 确认日志显示 SnowLuma 已连接。若持续失败，检查 OneBot WS 地址、HTTP 地址、HTTP token、SnowLuma 是否登录，以及
   `snowluma.homeDir` 是否指向当前正在运行的 SnowLuma 安装目录。
5. 打开 qq-bridge 本机控制台：`http://127.0.0.1:3100`（本机别名 `http://localhost:3100` 也可）。
   - 登录密钥是 **qq-bridge 的 console token**，不是 QQ 密码、SnowLuma WebUI 密码或 DSH 密码。
   - 若 `config.json` 的 `consoleToken` 非空，登录时使用该值。
   - 若 `consoleToken` 留空，桥接首次启动时会生成 token，并在 qq-bridge 启动日志中打印；同时保存到
     `qq-bridge/state/console-token`。找不到日志时，在本机打开这个文件查看。不要把 token 发给别人。
   - 也可在控制台「访问与安全」中修改/重新生成控制台令牌。若忘记令牌，停止桥接后可按上游文档重设
     `config.json` 中的 `consoleToken` 为一个新的明确值，再启动桥接。只把它改为空字符串不会清除已保存在
     `state/console-token` 的令牌；不要删除整个 `state/` 目录。

> JSON 路径建议使用正斜杠（如 `C:/SnowLuma`）；若使用 Windows 反斜杠，需在 JSON 中写成双反斜杠
> （如 `C:\\SnowLuma`），否则可能因转义字符导致配置解析失败。

### 5. 在 qq-bridge 中创建 imitation 角色

1. 在控制台进入 **「人格与角色」**，创建一个新角色，例如使用不含真实姓名的别名。
2. 在本地打开 `skills/imitation-<alias>/SKILL.md`，并参考同目录的
   `references/<alias>_personality_profile.md`。
3. 将适合长期注入对话的内容整理为**人格提示词**，再填入新角色。建议提取：
   - 画像中有证据支持的身份背景、核心特质和主要情绪/表达习惯；
   - 语气、句长、常用词、表情符号、回复节奏等语言特征；
   - 画像中确有记载且需要用于聊天的关键记忆；
   - 明确要求不确定时不要编造经历、关系或事实。
4. 不要原样粘贴 frontmatter、skill 框架说明、相对文件路径或与 QQ 无关的工具使用步骤。控制台角色提示词与
   skill 目录不是同一格式；需要用文本把必要的人格信息带入角色提示词。只加入运行所需的最少个人信息。
5. 保存角色，并在控制台选择/启用该角色。qq-bridge 的角色提示词会与 `qq-chat` 或 `qq-chat-v2` 等会话 preset
   配合使用；不要删除或覆盖 preset 中有关消息处理、工具边界和安全的规则。

如果你需要 DSH 在其他场景中以 skill 的形式使用完整生成目录，请通过 DSH 自身支持的 skill 安装/加载方式处理；
这与 qq-bridge 控制台的角色提示词配置是两件事。

### 6. 设置响应范围并端到端测试

1. 确认 `allow.private` / `allow.groups` 只包含测试用的 QQ 号或群号；`deny.*` 中的拒绝规则优先。
2. 在 qq-bridge 控制台选择适合的运行模式。只需要普通白名单聊天时，先使用上游支持的 `chat` 模式；如果要使用
   仿真模式，再按 qq-bridge 对 `reserved` / `reserved2` 的说明配置。首次部署不要为了“让所有群都能触发”而打开全量放行。
3. 用白名单中的测试账号向机器人发送一条普通消息，检查：
   - qq-bridge 日志收到消息并投递给 DSH；
   - DSH 使用预期的聊天 preset 和已启用角色生成回复；
   - SnowLuma 将回复发回 QQ。
4. 用不同类型的消息再测试几轮，并确认无白名单的账号/群不会触发回复。需要调整语气时，修改角色提示词并再次测试。

## 常见问题

| 现象 | 检查项 |
| --- | --- |
| QQ 没有回复 | DSH 是否运行；是否执行 `node scripts/setup-dsh.mjs` 并重启 DSH；桥接日志是否显示 SnowLuma 已连接；发送者/群是否在白名单中；运行模式是否正确。 |
| SnowLuma 已连接但 DSH 无会话/回复 | 检查 `dsh.baseUrl`、DSH 运行状态和桥接日志；确认 DSH 已加载 qq-chat preset 与 MCP。 |
| SnowLuma 连不上或反复自愈失败 | 检查 `wsUrl`/`httpUrl` 端口是否分别指向 WS/HTTP；`accessToken` 应是 HTTP token；检查 `homeDir` 是否是实际 SnowLuma 安装目录。HTTP 与 WS token 不同属于可能的正常情况。 |
| MCP 的 HTTP 动作报错 | 检查 `snowluma.httpUrl` 是否指向 HTTP API 端口，而不是 WebSocket 端口；核对 HTTP token。 |
| 控制台可以打开但无法登录 | 检查 `config.json` 的 `consoleToken`；若为空，从启动日志或 `state/console-token` 取值。注意它与 SnowLuma WebUI 初始密码是两把不同的密钥。 |
| 控制台无法访问 | 确认桥接正在运行并检查 `consolePort`；默认地址是 `http://127.0.0.1:3100`。 |
| 生成的 skill 在 QQ 回复中不起作用 | 检查是否已把画像中的必要人格信息整理并保存为控制台角色；单纯在本地生成 skill 不会自动让 qq-bridge 加载它。 |

## 隐私与安全

- 技能本身不会发布或上传原始证据、画像或生成的 skill；但 AI 运行环境可能会把提示词和你提供的内容发送给其配置的
  模型服务商。请检查 DSH/模型服务商的数据处理条款和运行配置；若内容不能离开本机，请使用合适的本地模型与运行环境。
- 不要把原始证据、画像或生成的 skill 提交到公开仓库、粘贴到公开 issue，或上传到不可信服务。
- `config.json`、访问令牌、QQ 号、群号以及包含私人对话/记忆的角色提示词都应视为敏感信息。
- 控制台绑定本机地址时不要通过公网或不可信网络暴露；不要公开控制台令牌。
- 用最小白名单验证功能。放宽白名单会使更多 QQ 用户的消息进入模型处理。
- 模仿真实人物仅应在取得适当同意的前提下使用，不要将 AI 回复冒充为该人物本人。

## 上游文档

- [qq-bridge README 与最新安装步骤](https://github.com/Derpyu520/qq-bridge)
- [qq-bridge DSH 设置说明](https://github.com/Derpyu520/qq-bridge/blob/main/docs/guides/DSH_SETUP.md)
- [SnowLuma README](https://github.com/SnowLuma/SnowLuma)
- [SnowLuma Releases](https://github.com/SnowLuma/SnowLuma/releases)