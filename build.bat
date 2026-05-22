@echo off
chcp 65001 >nul
echo ========================================
echo   猜杯子游戏 - 打包工具
echo ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 并勾选 "Add Python to PATH"
    echo 下载地址: https://python.org
    pause
    exit /b 1
)
echo [OK] Python 已就绪

:: 安装依赖
echo [1/3] 安装依赖...
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo [错误] 依赖安装失败，尝试单独安装...
    pip install pygame pyinstaller
)
echo [OK] 依赖安装完成

:: 清理旧构建
echo [2/3] 清理旧构建...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist *.spec del /q *.spec

:: 打包
echo [3/3] 开始打包...
pyinstaller --onefile --windowed --name "猜杯子游戏" --icon "assets\images\shell_cup_game.ico" --add-data "data;data" --add-data "assets;assets" main.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 打包失败，请检查上方错误信息
    pause
    exit /b 1
)

echo.
echo ========================================
echo   打包成功！
echo   .exe 文件在 dist 文件夹中
echo   文件名: 猜杯子游戏.exe
echo ========================================
echo.
echo 提示：把 dist\猜杯子游戏.exe 复制到桌面就可以玩了
echo       也可以发给其他人，不需要安装 Python
echo.
pause
