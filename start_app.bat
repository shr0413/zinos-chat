@echo off
chcp 65001 > nul
echo ==========================================
echo   Zino's Chat - 启动应用
echo ==========================================
echo.

echo [检查 1] 验证 .env 配置...
if not exist .env (
    echo ❌ 错误：未找到 .env 文件
    echo.
    echo 请先创建 .env 文件：
    echo   1. 阅读 CREATE_ENV.md
    echo   2. 创建 .env 文件
    echo   3. 填入 API Keys
    echo.
    pause
    exit /b 1
)
echo ✅ .env 文件存在
echo.

echo [检查 2] 验证配置有效性...
python verify_config.py
if errorlevel 1 (
    echo.
    echo ❌ 配置验证失败，请检查 .env 文件
    pause
    exit /b 1
)
echo.

echo [检查 3] 启动应用...
echo.
echo ========================================
echo   🚀 应用启动中...
echo   访问：http://localhost:8501
echo ========================================
echo.

streamlit run main.py

pause

