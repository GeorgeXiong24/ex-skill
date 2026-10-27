# QQ agent One-key Startup

> 语言 / Language：[中文](onekey-startup_zh.md)

## 0. What this launcher does

It brings up four components in dependency order with one double-click:

```text
QQ NT -> SnowLuma (OneBot gateway) -> DeepSeek Harness -> qq-bridge -> status summary
```

The hard parts are not "starting programs":

1. **Dependency order** — SnowLuma can only inject into QQ after the client is logged in; the bridge can only connect after DSH is up and its port is known.
2. **DSH uses a random port** — the desktop app starts its web server with `--port 0`, so the port changes on every launch. The bridge stores a fixed `dsh.baseUrl` in `config.json`, so the current port must be written back each time.
3. **Re-running must be safe** — users double-click twice; the script must not start duplicates.

## 1. Four design rules

| Rule | How |
| --- | --- |
| Self-locating | Derive every path from the script itself: `%~dp0` in `.bat`, `$PSScriptRoot` in `.ps1`; never hardcode the repo root |
| Idempotent | Probe ports/processes first; skip components that are already running and print `OK already running` |
| Order is the dependency graph | Each step waits for the previous step's readiness signal (a listening port) |
| Diagnosable failures | Print `OK` / `!!` per step and tell the user where to look when something fails |

## 2. File layout

```text
<any directory>\
├── qq-bridge\
│   ├── startup.bat              <- entry point, double-click this
│   ├── start.bat                <- bridge supervisor loop (restart after 5s)
│   ├── restart.bat              <- restart the bridge
│   ├── config.json              <- bridge config (dsh.baseUrl, allowlists)
│   ├── state\                   <- runtime data (lock, logs, console token); never copy across machines
│   └── scripts\
│       ├── launch-all.ps1       <- the actual orchestration
│       └── local-dsh-url.mjs    <- discover DSH's current port and write it back
└── SnowLuma\                    <- must be a sibling of qq-bridge
    ├── node.exe
    └── index.mjs
```

**Key convention**: `SnowLuma` and `qq-bridge` must be siblings; `launch-all.ps1` derives the SnowLuma path from that relationship, so the whole tree can be moved without editing anything.

## 3. Step 1: write `startup.bat`

It only does three things: change to its own directory, call the PowerShell orchestrator, forward arguments.

```bat
@echo off
chcp 65001 >nul
setlocal
title QQ Bot Launcher
cd /d "%~dp0"

set "LAUNCHER=%~dp0scripts\launch-all.ps1"
if not exist "%LAUNCHER%" (
    echo [ERROR] missing launcher: %LAUNCHER%
    pause
    exit /b 1
)

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

Why each part:

- `chcp 65001` — makes CMD render the script's Chinese output as UTF-8 instead of mojibake.
- `cd /d "%~dp0"` — pins the working directory to the script location so relative paths are reliable.
- `%~dp0scripts\launch-all.ps1` — the only correct form. Never hardcode `D:\...\launch-all.ps1`.
- `powershell -NoProfile -ExecutionPolicy Bypass -File` — runs the `.ps1` under Windows PowerShell 5.1, bypassing execution policy.
- The `--check` branch — self-check only, no `pause`, safe to call from other scripts.
- Trailing `pause` — keeps the window open on the status summary.

## 4. Step 2: write `scripts\launch-all.ps1`

### 4.1 Parameters and path derivation

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

`$PSScriptRoot` is `scripts\`; its parent is `qq-bridge\`; the sibling `SnowLuma` is the protocol side. The two parameters exist for unusual layouts.

### 4.2 Three external executable paths (must be edited on another machine)

```powershell
$QQExe   = 'C:\Program Files\Tencent\QQNT\QQ.exe'
$DshExe  = 'C:\Users\<user>\AppData\Local\Programs\DeepSeek Harness\DeepSeek Harness.exe'
$NodeExe = 'C:\Program Files\nodejs\node.exe'
```

This is the only machine-bound part:

- A missing `$QQExe` is a warning only;
- A missing `$NodeExe` is fatal — `local-dsh-url.mjs` and `setup-dsh.mjs` depend on it;
- A missing `$DshExe` means the script will not start DSH for you.

For portability, replace these with detection: QQ from the registry or the standard install path, DSH from `%LOCALAPPDATA%\Programs\DeepSeek Harness\`, Node from `Get-Command node`, falling back to the hardcoded values.

### 4.3 Two port helpers

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

Do not use `Get-NetTCPConnection` as the readiness check — it can require elevation and only reports listening state. A real TCP connect is the most reliable signal.

### 4.4 The four stages

| Stage | Ready when | If already running | If it must start |
| --- | --- | --- | --- |
| 1/4 QQ NT | `Get-Process QQ` | skip | `Start-Process $QQExe` |
| 2/4 SnowLuma | port 5099 (WebUI) | skip | run `index.mjs` with SnowLuma's bundled `node.exe`, hidden window |
| 3/4 OneBot | port 3001 (WS) | skip | do not start anything, just wait (opens after QQ login + injection), up to 180 s |
| 4/4 DSH | detected by `local-dsh-url.mjs` | skip | `Start-Process $DshExe -WorkingDirectory <DSH install dir>` |

Passing `-WorkingDirectory` to DSH matters: otherwise DSH inherits the launcher's working directory, locks the `qq-bridge` folder, and the tree can no longer be moved or renamed.

### 4.5 Writing the DSH port back (the core trick)

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

`local-dsh-url.mjs` finds ports owned by `DeepSeek Harness.exe` via `netstat`, mints a session cookie with the local signing key, calls the read-only `settings/describe` to confirm it is really DSH, then rewrites `config.json`'s `dsh.baseUrl`. This must run before the bridge starts.

### 4.6 Self-healing the DSH profile (optional, recommended)

Reinstalling or upgrading DSH can reset `~\.dsh`, wiping the MCP servers, the `qq-chat`/`qq-chat-v2` presets and `qq-mode`; the bridge then fails with `Unknown agent preset`. A cheap file-level check at startup fixes it:

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
    try { & $NodeExe 'scripts\setup-dsh.mjs' 'desktop' } finally { Pop-Location }
}
```

The profile name is `desktop` (desktop app), not the `web` default from the README.

### 4.7 Restart the bridge when the port changed

The bridge reads `config.json` only at startup. If DSH restarted on a new port while the bridge kept running, it will keep dialing the old one. Compare old and new values:

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

Otherwise reuse it, or start the supervisor with `cmd /c start.bat` (minimized). Note: invoke `.bat` files through `cmd /c`, never `Start-Process start.bat` — see section 6.

### 4.8 Final status summary

Read the token from `state\console-token` and query the bridge's own `/api/status`:

```powershell
$tok = (Get-Content (Join-Path $BridgeHome 'state\console-token') -Raw).Trim()
$s = Invoke-RestMethod -Uri ("http://127.0.0.1:3100/api/status?token=" + [uri]::EscapeDataString($tok)) -TimeoutSec 8
```

Print the mode, `dshReady`, SnowLuma's `connected/online/good/degraded`, and the private allowlist; if all three are healthy, print "all ready". This is the real value: users know whether it works without opening the console.

## 5. Encoding and line endings (the most common trap)

| File | Requirement | Why |
| --- | --- | --- |
| `launch-all.ps1` | **UTF-8 with BOM** | Windows PowerShell 5.1 decodes BOM-less `.ps1` as ANSI. Garbled Chinese comments swallow the following quotes and produce `Missing '=' operator after key in hash literal` / `Missing closing '}'` — it looks like a syntax error but is an encoding error |
| `startup.bat` | ANSI, or UTF-8 + `chcp 65001` | this implementation uses UTF-8 + `chcp 65001` |
| Line endings | CRLF | mixed endings break `cmd` parsing |

Check the BOM:

```powershell
Format-Hex -Path .\scripts\launch-all.ps1 -Count 3   # expect EF BB BF
```

Add it:

```powershell
$t=[IO.File]::ReadAllText($p,[Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText($p,$t,[Text.UTF8Encoding]::new($true))
```

## 6. Desktop shortcut: the Windows 11 Smart App Control trap

If **Smart App Control** is enabled, a `.lnk` that points straight at a `.bat` will not open and reports something like:

```text
An Application Control policy has blocked this file.
Dangerous file extension from the web.
```

Fix: point the shortcut at the Microsoft-signed `cmd.exe` and pass the `.bat` as an argument. The opened file type is then `cmd.exe`, which does not match the "dangerous extension" rule.

```powershell
$desktop = [Environment]::GetFolderPath('Desktop')
$link    = Join-Path $desktop 'QQ Bot (one-click).lnk'
$bat     = (Resolve-Path '.\startup.bat').Path

$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut($link)
$sc.TargetPath       = Join-Path $env:SystemRoot 'System32\cmd.exe'
$sc.Arguments        = '/c ""' + $bat + '""'
$sc.WorkingDirectory = Split-Path -Parent $bat
$sc.IconLocation     = 'C:\Program Files\Tencent\QQNT\QQ.exe,0'
$sc.Description      = 'One-click start: QQ -> SnowLuma -> DSH -> bridge'
$sc.Save()
```

Notes:

- The quotes in `Arguments` are deliberately doubled: `/c ""path""` so `cmd` parses paths containing spaces correctly.
- A `.lnk` stores absolute paths and is **not portable**; rebuild it on every machine.
- Keep the same code as `scripts\create-shortcut.ps1` so users can regenerate a machine-correct shortcut after copying the tree.
- If Smart App Control is off, pointing at the `.bat` also works, but the `cmd.exe` wrapper works in both cases — use it consistently.

## 7. Moving to another machine checklist

| Item | Action |
| --- | --- |
| `qq-bridge\state\` | Do not copy (lock, logs, console token, session mapping) |
| `config.json` | Update `snowluma.homeDir`, `snowluma.launcherPath`; adjust `allow.private`, `allow.groups`, `ownerQQ` |
| `launch-all.ps1` lines 26–28 | Update the three executable paths (or add detection) |
| DSH integration | Run `node scripts\setup-dsh.mjs desktop` once (junctions and MCP paths are machine-specific) |
| SnowLuma | Log in to QQ again; `data\` belongs to the previous account |
| Desktop shortcut | Rebuild with the code in section 6 |
| Verify | `startup.bat --check` |

## 8. Verify and troubleshoot

```text
startup.bat --check            path/config self-check, starts nothing
startup.bat                    normal start
startup.bat --console          start, then open http://127.0.0.1:3100
```

Debug order:

1. Is `startup.bat --check` all green?
2. Run `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\launch-all.ps1` directly and read the full output.
3. Bridge log: `state\bridge.log` (the last 30 lines usually suffice).
4. SnowLuma log: `SnowLuma\logs\snowluma-*.log` (search `[Hook]`, `[OneBot]`).
5. Console: `http://127.0.0.1:3100` (token in `state\console-token`).

Symptom to cause:

| Symptom | Cause |
| --- | --- |
| "This file is unsafe" when double-clicking the shortcut | Smart App Control blocking `.bat`; use the `cmd.exe` wrapper from section 6 |
| `Unknown agent preset: qq-chat` | `~\.dsh` was reset; re-run `setup-dsh.mjs desktop` |
| Bridge connects then drops with 0 frames | `dsh.baseUrl` points at a stale port; re-run `local-dsh-url.mjs --write` and restart the bridge |
| Port 3001 never appears | QQ is not logged in, or SnowLuma failed to inject (check the 5099 WebUI) |
| `.ps1` reports `Missing '=' operator` | the file has no UTF-8 BOM |

## 9. Security notes

- `state\` and `config.json` contain console/SnowLuma tokens and QQ numbers — never commit or share them.
- With empty allowlists and `allowAllWhenEmpty=false`, the bridge answers nobody (deliberate fail-closed default). Do not disable it for convenience.
- Ship shortcuts locally only; a `.lnk` is machine-specific and will break anywhere else.