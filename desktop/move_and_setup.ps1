<#
Move-and-Setup script for Delta Tool desktop
Usage (run PowerShell as Administrator):
  cd <repo-root>
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
  .\desktop\move_and_setup.ps1
#>
param(
    [string]$SourcePath = (Get-Location).Path
)

function Is-Admin {
    $current = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($current)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Is-Admin)) {
    Write-Warning "请以管理员身份运行此脚本 (右键 PowerShell -> 以管理员身份运行)。"
    exit 1
}

$DestRoot = "C:\\delta-tool"
$DestDesktop = Join-Path $DestRoot "desktop"

Write-Host "Source path: $SourcePath"

# If user passed a repo root, try to find desktop subfolder
$sourceDesktop = $SourcePath
if (-not (Test-Path (Join-Path $sourceDesktop "install.bat"))) {
    if (Test-Path (Join-Path $sourceDesktop "desktop")) {
        $sourceDesktop = Join-Path $sourceDesktop "desktop"
    } elseif (Test-Path (Join-Path $sourceDesktop "..\desktop")) {
        $sourceDesktop = (Resolve-Path (Join-Path $sourceDesktop "..\desktop")).Path
    } else {
        Write-Error "未在 $SourcePath 及其下找到 desktop 或 install.bat，请从仓库根目录或 desktop 目录运行本脚本。"
        exit 1
    }
}

Write-Host "Resolved source desktop: $sourceDesktop"

if (-not (Test-Path $sourceDesktop)) {
    Write-Error "源目录不存在： $sourceDesktop"
    exit 1
}

# Backup existing destination if present
if (Test-Path $DestDesktop) {
    $bak = "${DestDesktop}.bak_$(Get-Date -Format yyyyMMdd_HHmmss)"
    Write-Host "目标已存在，备份为： $bak"
    Move-Item -LiteralPath $DestDesktop -Destination $bak -Force
}

# Ensure dest root exists
New-Item -Path $DestRoot -ItemType Directory -Force | Out-Null

Write-Host "移动 $sourceDesktop -> $DestDesktop ..."
Try {
    Move-Item -LiteralPath $sourceDesktop -Destination $DestDesktop -Force
} Catch {
    Write-Error "移动失败: $_"
    exit 1
}

Write-Host "移动完成。现在以管理员身份打开 cmd 并运行 install.bat（如果出现 UAC 请允许）。"
Set-Location $DestDesktop
Start-Process -FilePath "cmd.exe" -ArgumentList "/k","install.bat" -Verb RunAs

Write-Host "如果 install.bat 运行成功，请等待安装完成；若需要我继续指导后续激活 venv 与安装依赖，请告知。"