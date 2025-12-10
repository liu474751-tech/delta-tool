# Tesseract OCR 安装脚本
# 运行方式: 右键此文件 -> 使用 PowerShell 运行

$ErrorActionPreference = 'Stop'

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Tesseract OCR 安装脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否已安装
$tesseractPath = 'C:\Program Files\Tesseract-OCR\tesseract.exe'
if (Test-Path $tesseractPath) {
    Write-Host "Tesseract 已安装在: $tesseractPath" -ForegroundColor Green
    & $tesseractPath --version
    Write-Host ""
    Write-Host "按任意键退出..."
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 0
}

Write-Host "正在下载 Tesseract OCR..." -ForegroundColor Yellow

# 下载链接 (UB Mannheim 版本，包含中文语言包)
$downloadUrl = 'https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.5.1.20250114.exe'
$installerPath = "$env:TEMP\tesseract-setup.exe"

try {
    # 使用 .NET WebClient 下载
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadFile($downloadUrl, $installerPath)
    Write-Host "下载完成!" -ForegroundColor Green
} catch {
    Write-Host "下载失败: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "请手动下载并安装:" -ForegroundColor Yellow
    Write-Host "  1. 打开浏览器访问: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor White
    Write-Host "  2. 下载 Windows 64-bit 安装程序" -ForegroundColor White
    Write-Host "  3. 安装时勾选 'Chinese (Simplified)' 语言包" -ForegroundColor White
    Write-Host ""
    Write-Host "按任意键退出..."
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}

Write-Host ""
Write-Host "正在启动安装程序..." -ForegroundColor Yellow
Write-Host "请在安装时:" -ForegroundColor Cyan
Write-Host "  1. 选择 'Install for all users'" -ForegroundColor White
Write-Host "  2. 在 'Additional language data' 中勾选:" -ForegroundColor White
Write-Host "     - Chinese (Simplified)" -ForegroundColor White
Write-Host "     - Chinese (Traditional) (可选)" -ForegroundColor White
Write-Host "  3. 完成安装" -ForegroundColor White
Write-Host ""

Start-Process -FilePath $installerPath -Wait

# 检查安装结果
if (Test-Path $tesseractPath) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  Tesseract 安装成功!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    
    # 添加到 PATH
    $currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    $tesseractDir = 'C:\Program Files\Tesseract-OCR'
    if ($currentPath -notlike "*$tesseractDir*") {
        [Environment]::SetEnvironmentVariable('Path', "$currentPath;$tesseractDir", 'User')
        Write-Host "已添加到用户 PATH" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "请重新打开 PowerShell 窗口后运行测试" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "安装可能未完成，请手动检查" -ForegroundColor Red
}

Write-Host ""
Write-Host "按任意键退出..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
