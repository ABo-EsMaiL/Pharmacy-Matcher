@echo off
setlocal
:: Check for administrator permissions
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Administrator permissions required to kill elevated zombie processes.
    echo [!] Requesting elevation...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd -ArgumentList '/c `\"%~f0`\"' -Verb RunAs"
    exit /b
)

title تحرير منافذ السيرفرات - فارما ماتش (Administrator)
echo ========================================================
echo    فارما ماتش: تحرير المنافذ 8000 و 8001
echo    (تم التشغيل بصلاحيات المسؤول Administrator)
echo ========================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$conns = Get-NetTCPConnection -LocalPort 8000,8001 -ErrorAction SilentlyContinue; " ^
    "if (-not $conns) { Write-Host '[+] All ports (8000 & 8001) are already FREE!' -ForegroundColor Green; } " ^
    "else { " ^
    "    $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique; " ^
    "    foreach ($p in $pids) { " ^
    "        if ($p -gt 0) { " ^
    "            try { " ^
    "                Stop-Process -Id $p -Force -ErrorAction Stop; " ^
    "                Write-Host \"[+] Successfully terminated PID: $p\" -ForegroundColor Green; " ^
    "            } catch { " ^
    "                Write-Host \"[-] Failed to terminate PID: $p ($($_.Exception.Message))\" -ForegroundColor Red; " ^
    "            } " ^
    "        } " ^
    "    } " ^
    "}"

echo.
echo ========================================================
echo [+] تم الانتهاء بنجاح! سيتم إغلاق النافذة تلقائياً...
echo ========================================================
timeout /t 3
