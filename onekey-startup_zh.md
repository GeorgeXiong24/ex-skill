# QQ agent 一键启动

> 语言 / Language：[English](onekey-startup.md)

## 0. 这个启动器要做什么

一条命令按依赖顺序把四段拉起来：

```text
QQ NT → SnowLuma(OneBot 网关) → DeepSeek Harness → qq-bridge → 打印状态
```

难点不在「启动」，而在三件事：

1. **依赖顺序**：SnowLuma 要等 QQ 登录后才能注入，桥接要等 DSH 起来、端口确定后才能连。
2. **DSH 端口随机**：DSH 桌面版每次启动都用 `--port 0`，端口会变；桥接的 `config.json` 里 `dsh.baseUrl` 却是写死的，必须每轮启动后把当前端口写回去。
3. **重复运行要安全**：用户很可能连点两次，不能起第二份 QQ/SnowLuma/DSH/桥接。

## 1. 四条设计原则

| 原则 | 做法 |
| --- | --- |
| 自定位 | 只用脚本自身位置推导路径：`.bat` 用 `%~dp0`，`.ps1` 用 `$PSScriptRoot`，不写死仓库绝对路径 |
| 幂等 | 先探测端口/进程，已在跑的组件直接跳过并打印 `OK 已在运行` |
| 顺序即依赖 | 每一步都等上一步的就绪信号（端口出现）再继续 |
| 失败可诊断 | 每步打印 `OK` / `!!`，并在失败时给出「下一步去哪看日志」 |

## 2. 文件结构

```text
<任意目录>\
├── qq-bridge\
│   ├── startup.bat              ← 入口，双击它
│   ├── start.bat                ← 桥接守护循环（崩溃 5 秒后重启）
│   ├── restart.bat              ← 重启桥接
│   ├── config.json              ← 桥接配置（含 dsh.baseUrl、白名单）
│   ├── state\                   ← 运行时数据（锁、日志、控制台令牌），不要跨机器复制
│   └── scripts\
│       ├── launch-all.ps1       ← 真正的编排逻辑
│       └── local-dsh-url.mjs    ← 探测 DSH 当前端口并写回 config.json
└── SnowLuma\                    ← 必须与 qq-bridge 同级
    ├── node.exe
    └── index.mjs
```

**关键约定**：`SnowLuma` 与 `qq-bridge` 必须是同级目录，`launch-all.ps1` 默认按这个关系推导 `SnowLuma` 的位置。这样整个目录搬到哪儿都不用改脚本。

## 3. 第一步：写 `startup.bat`

它只做三件事：切到自己的目录、调用 PowerShell 编排脚本、透传参数。

```bat
@echo off
chcp 65001 >nul
setlocal
title QQ Bot Launcher
cd /d "%~dp0"

rem ============================================================
rem  QQ bot one-click launcher
rem  Order: QQ NT -> SnowLuma -> DSH desktop -> qq-bridge
rem
rem  This file only calls scripts\launch-all.ps1.
rem  All paths are derived from the ps1 location, so moving the
rem  whole folder does not require editing this file.
rem
rem  Usage:
rem    startup.bat            normal start (safe to run twice)
rem    startup.bat --check    path/config self-check, starts nothing
rem    startup.bat --console  start, then open the 3100 console
rem ============================================================

set "LAUNCHER=%~dp0scripts\launch-all.ps1"
if not exist "%LAUNCHER%" (
    echo [ERROR] missing launcher: %LAUNCHER%
    echo         run this file from the qq-bridge directory.
    pause
    exit /b 1
)

rem --check: self-check only, no pause (script friendly)
if /i "%~1"=="--check" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%LAUNCHER%" -CheckOnly
    exit /b %errorlevel%
)

set "EXTRA="
if /i "%~1"=="--console" set "EXTRA=-OpenConsole"

powershell -NoProfile -ExecutionPolicy Bypass -File "%LAUNCHER%" %EXTRA%
set "CODE=%errorlevel%"

echo.
if not "%CODE%"=="0" echo [WARN] launcher exited with code %CODE%
pause
exit /b %CODE%
```

逐段解释：

- `chcp 65001`：让 CMD 按 UTF-8 显示中文，否则 `launch-all.ps1` 的中文输出是乱码。
- `cd /d "%~dp0"`：把工作目录固定到脚本所在目录，后面所有相对路径才可靠。
- `%~dp0scripts\launch-all.ps1`：**唯一正确的写法**。不要写 `D:\...\launch-all.ps1`。
- `powershell -NoProfile -ExecutionPolicy Bypass -File`：用 Windows PowerShell 5.1 跑 `.ps1`，跳过执行策略。
- `--check` 分支：只自检不启动，用来排查路径问题，且不 `pause`，方便被其他脚本调用。
- 结尾 `pause`：让窗口停在状态汇总，用户看完按任意键关闭。

## 4. 第二步：写 `scripts\launch-all.ps1`

### 4.1 参数与路径推导

```powershell
param(
    [switch]$OpenConsole,
    [switch]$CheckOnly,
    [string]$BridgeHome,
    [string]$SnowHome
)

$ErrorActionPreference = 'Stop'

if (-not $BridgeHome) { $BridgeHome = Split-Path -Parent $PSScriptRoot }
if (-not $SnowHome)   { $SnowHome   = Join-Path (Split-Path -Parent $BridgeHome) 'SnowLuma' }
```

`$PSScriptRoot` 是 `scripts\`，上一级就是 `qq-bridge\`；再上一级的 `SnowLuma` 就是协议端。两个参数留了口子，特殊布局可以手动传。

### 4.2 三个外部程序路径（换机器时必须改）

```powershell
$QQExe   = 'C:\Program Files\Tencent\QQNT\QQ.exe'
$DshExe  = 'C:\Users\<用户名>\AppData\Local\Programs\DeepSeek Harness\DeepSeek Harness.exe'
$NodeExe = 'C:\Program Files\nodejs\node.exe'
```

这是整套脚本里**唯一和机器绑定**的部分：

- `$QQExe` 找不到只打印黄色提示，不致命；
- `$NodeExe` 找不到会致命，后面 `local-dsh-url.mjs`、`setup-dsh.mjs` 都要用它；
- `$DshExe` 找不到则不会帮你拉起 DSH，需要用户自己先开 DSH。

想更通用，可以改成自动探测：QQ 查注册表或 `C:\Program Files\Tencent\QQNT\QQ.exe`，DSH 查 `%LOCALAPPDATA%\Programs\DeepSeek Harness\`，Node 先试 `Get-Command node`，最后才回落到写死的值。

### 4.3 两个端口探测工具

```powershell
function Test-Tcp {
    param([int]$Port, [int]$TimeoutMs = 600)
    $client = [System.Net.Sockets.TcpClient]::new()
    try {
        $task = $client.ConnectAsync('127.0.0.1', $Port)
        if (-not $task.Wait($TimeoutMs)) { return $false }
        return $client.Connected
    } catch { return $false }
    finally { $client.Dispose() }
}

function Wait-Tcp {
    param([int]$Port, [int]$Seconds)
    $deadline = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-Tcp -Port $Port) { return $true }
        Start-Sleep -Milliseconds 800
    }
    return $false
}
```

不要用 `Get-NetTCPConnection` 判断「是否已起」——它在部分环境下需要更高权限，而且只反映监听状态，不保证能连。直接建 TCP 连接最稳。

### 4.4 四个阶段

| 阶段 | 就绪判据 | 已在运行时 | 需要拉起时 |
| --- | --- | --- | --- |
| 1/4 QQ NT | `Get-Process QQ` | 跳过 | `Start-Process $QQExe` |
| 2/4 SnowLuma | 5099 端口（WebUI） | 跳过 | 用 SnowLuma 自带 `node.exe` 跑 `index.mjs`，隐藏窗口 |
| 3/4 OneBot | 3001 端口（WS） | 跳过 | 不主动启动，只等（QQ 登录并注入后才开），最多 180 秒 |
| 4/4 DSH | 由 `local-dsh-url.mjs` 探测 | 跳过 | `Start-Process $DshExe -WorkingDirectory <DSH 安装目录>` |

第 4 步里给 DSH 传 `-WorkingDirectory` 很关键：不传的话 DSH 会继承启动器的工作目录，把整个 `qq-bridge` 目录占住，之后想改名/移动就失败。

### 4.5 DSH 端口回写（这套方案的核心）

```powershell
$cfgPath = Join-Path $BridgeHome 'config.json'
$oldBaseUrl = ''
try {
    $oldBaseUrl = [string](Get-Content -LiteralPath $cfgPath -Raw -Encoding UTF8 | ConvertFrom-Json).dsh.baseUrl
} catch {}

$dshReady = $false
Push-Location $BridgeHome
try {
    for ($i = 0; $i -lt 60; $i++) {
        $null = & $NodeExe 'scripts\local-dsh-url.mjs' --write 2>&1
        if ($LASTEXITCODE -eq 0) { $dshReady = $true; break }
        Start-Sleep -Seconds 2
    }
} finally { Pop-Location }
```

`local-dsh-url.mjs` 会：从 `netstat` 里找由 `DeepSeek Harness.exe` 监听的端口 → 用本机签名密钥铸一个 Cookie → 调一次只读的 `settings/describe` 确认确实是 DSH → 把 `config.json` 的 `dsh.baseUrl` 改成它。所以**桥接启动前必须跑这一步**，否则它连的是上一次的端口。

### 4.6 DSH profile 自愈（可选但推荐）

DSH 重装/升级可能把 `~\.dsh` 整个重置，MCP server、`qq-chat`/`qq-chat-v2` preset、`qq-mode` 全会消失，桥接随后报 `Unknown agent preset`。可以在启动时做一次文件级检查：

```powershell
$profilePkg = Join-Path $env:USERPROFILE '.dsh\profiles\desktop\package.json'
$needsSetup = $true
if (Test-Path -LiteralPath $profilePkg) {
    try {
        $pkgText = Get-Content -LiteralPath $profilePkg -Raw -Encoding UTF8
        if ($pkgText -match 'qq-agent-presets' -and $pkgText -match 'qq-mode-console') { $needsSetup = $false }
    } catch {}
}
if ($needsSetup) {
    Push-Location $BridgeHome
    try {
        & $NodeExe 'scripts\setup-dsh.mjs' 'desktop'
    } finally { Pop-Location }
}
```

注意 profile 名是 `desktop`（桌面版），不是 README 默认的 `web`。

### 4.7 端口变了就重启桥接

桥接只在启动时读一次 `config.json`。如果 DSH 重启换了端口、而桥接还活着，它会一直连旧端口。所以写完新端口后比较新旧值：

```powershell
$cfgBaseUrl = [string](Get-Content -LiteralPath $cfgPath -Raw -Encoding UTF8 | ConvertFrom-Json).dsh.baseUrl
$bridgeRunning = Test-Tcp -Port 3100
if ($bridgeRunning -and $oldBaseUrl -and $cfgBaseUrl -and ($cfgBaseUrl -ne $oldBaseUrl)) {
    Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', 'restart.bat' `
        -WorkingDirectory $BridgeHome -WindowStyle Minimized
    Start-Sleep -Seconds 4
    $bridgeRunning = Test-Tcp -Port 3100
}
```

没变就直接复用；没在跑就用 `cmd /c start.bat` 拉起守护窗口（最小化）。**注意用 `cmd /c` 调 `.bat`，不要 `Start-Process start.bat`**，原因见第 6 节。

### 4.8 最后的自检汇总

从 `state\console-token` 读令牌，调桥接自己的 `/api/status`：

```powershell
$tok = (Get-Content (Join-Path $BridgeHome 'state\console-token') -Raw).Trim()
$s = Invoke-RestMethod -Uri ("http://127.0.0.1:3100/api/status?token=" + [uri]::EscapeDataString($tok)) -TimeoutSec 8
```

打印模式、`dshReady`、SnowLuma 的 `connected/online/good/degraded`、私聊白名单；三者都正常时再输出一句「全部就绪」。这一步是整个脚本的价值所在：**用户不用开控制台就知道现在能不能用**。

## 5. 编码与换行（最容易踩的坑）

| 文件 | 要求 | 原因 |
| --- | --- | --- |
| `launch-all.ps1` | **UTF-8 with BOM** | Windows PowerShell 5.1 读无 BOM 的 `.ps1` 会按 ANSI 解码；中文注释被解成乱码后，引号会「吞掉」后面的代码，报 `Missing '=' operator after key in hash literal` / `Missing closing '}'`，看起来像语法错误，其实是编码问题 |
| `startup.bat` | ANSI 或 UTF-8 + `chcp 65001` | 本实现用 UTF-8 + `chcp 65001` |
| 换行 | CRLF | 混合换行会让 `cmd` 解析异常 |

检查 BOM：

```powershell
Format-Hex -Path .\scripts\launch-all.ps1 -Count 3   # 应看到 EF BB BF
```

补 BOM：

```powershell
$t=[IO.File]::ReadAllText($p,[Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText($p,$t,[Text.UTF8Encoding]::new($true))
```

## 6. 桌面快捷方式：Windows 11 的「智能应用控制」坑

如果系统开了 **智能应用控制（Smart App Control）**，把 `.lnk` 直接指向 `.bat` 会打不开，提示类似：

```text
An Application Control policy has blocked this file.
Dangerous file extension from the web.
```

解决办法：让快捷方式的目标是**微软签名的 `cmd.exe`**，把 `.bat` 作为参数传进去。被打开的文件类型是 `cmd.exe`，就不会命中「危险扩展名」规则。

```powershell
$desktop = [Environment]::GetFolderPath('Desktop')
$link    = Join-Path $desktop 'QQ机器人（一键启动）.lnk'
$bat     = (Resolve-Path '.\startup.bat').Path

$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut($link)
$sc.TargetPath       = Join-Path $env:SystemRoot 'System32\cmd.exe'
$sc.Arguments        = '/c ""' + $bat + '""'
$sc.WorkingDirectory = Split-Path -Parent $bat
$sc.IconLocation     = 'C:\Program Files\Tencent\QQNT\QQ.exe,0'
$sc.Description      = '一键启动 QQ 机器人：QQ -> SnowLuma -> DSH -> 桥接'
$sc.Save()
```

要点：

- `Arguments` 里的双引号是**成对两层**：`/c ""路径""`，这样 `cmd` 才能正确解析带空格的路径。
- `.lnk` 里存的是绝对路径，**天然不通用**，换机器/换目录必须重建。
- 同一份代码放进 `scripts\create-shortcut.ps1`，用户拷走目录后跑一次就能生成适配本机的快捷方式。
- 如果对方关闭了智能应用控制，用 `.bat` 当目标也能用，但用 `cmd.exe` 包装在两种情况下都成立，推荐统一。

## 7. 换机器适配清单

| 项 | 操作 |
| --- | --- |
| `qq-bridge\state\` | 不复制。里面是锁、日志、控制台令牌、会话映射 |
| `config.json` | 改 `snowluma.homeDir`、`snowluma.launcherPath`；按需改 `allow.private`、`allow.groups`、`ownerQQ` |
| `launch-all.ps1` 第 26–28 行 | 改三个 exe 路径（或改成自动探测） |
| DSH 集成 | 跑一次 `node scripts\setup-dsh.mjs desktop`（junction 和 MCP 路径按本机生成） |
| SnowLuma | 重新扫码登录 QQ；`data\` 是别人的登录数据，不能照搬 |
| 桌面快捷方式 | 用第 6 节代码重建 |
| 验证 | `startup.bat --check` |

## 8. 验证与排错

```text
startup.bat --check            只自检路径和配置，不启动任何东西
startup.bat                    正常启动
startup.bat --console          启动后打开 http://127.0.0.1:3100
```

排错顺序：

1. `startup.bat --check` 是否全绿；
2. 直接跑 `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\launch-all.ps1` 看完整输出；
3. 桥接日志 `state\bridge.log`（最后 30 行通常就够）；
4. SnowLuma 日志 `SnowLuma\logs\snowluma-*.log`（搜 `[Hook]`、`[OneBot]`）；
5. 控制台 `http://127.0.0.1:3100`（令牌在 `state\console-token`）。

常见现象对照：

| 现象 | 原因 |
| --- | --- |
| 双击快捷方式报「文件不安全」 | 智能应用控制拦截 `.bat`，按第 6 节改成 `cmd.exe` 包装 |
| `Unknown agent preset: qq-chat` | `~\.dsh` 被重置，重跑 `setup-dsh.mjs desktop` |
| 桥接连上又断、0 帧 | `dsh.baseUrl` 指向旧端口，重跑 `local-dsh-url.mjs --write` 并重启桥接 |
| 3001 一直不出来 | QQ 没登录，或 SnowLuma 没注入成功（看 5099 的 WebUI） |
| `.ps1` 报 `Missing '=' operator` | 文件没有 UTF-8 BOM |

## 9. 安全提醒

- `state\`、`config.json` 里含控制台令牌、SnowLuma 令牌、QQ 号，**不要提交到仓库或发给别人**。
- 白名单为空且 `allowAllWhenEmpty=false` 时桥接不响应任何人，这是刻意的 fail-closed 默认；不要为了省事关掉它。
- 快捷方式只放在本机桌面，不要把 `.lnk` 当安装包分发（里面是绝对路径，换机器必坏）。