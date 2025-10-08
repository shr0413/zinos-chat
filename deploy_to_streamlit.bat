@echo off
echo ==========================================
echo   Zino's Chat - Streamlit 部署准备
echo ==========================================
echo.

echo [1/5] 检查 Git 仓库...
if not exist .git (
    echo ✅ 初始化 Git 仓库...
    git init
    echo.
) else (
    echo ✅ Git 仓库已存在
    echo.
)

echo [2/5] 添加所有文件到 Git...
git add .
echo ✅ 完成
echo.

echo [3/5] 创建提交...
set /p commit_msg="请输入提交信息 (默认: Prepare for deployment): "
if "%commit_msg%"=="" set commit_msg=Prepare for deployment
git commit -m "%commit_msg%"
echo ✅ 完成
echo.

echo [4/5] 检查远程仓库...
git remote -v
if errorlevel 1 (
    echo.
    echo ⚠️  未配置远程仓库！
    echo.
    echo 请按以下步骤操作：
    echo 1. 访问 https://github.com/new 创建新仓库
    echo 2. 复制仓库 URL
    echo 3. 运行命令：
    echo    git remote add origin https://github.com/你的用户名/zinos-chat.git
    echo    git branch -M main
    echo    git push -u origin main
    echo.
    pause
    exit /b
)
echo.

echo [5/5] 推送到 GitHub...
git push
if errorlevel 1 (
    echo.
    echo ⚠️  推送失败！尝试首次推送...
    git push -u origin main
)
echo ✅ 完成
echo.

echo ==========================================
echo   🎉 准备完成！
echo ==========================================
echo.
echo 下一步：
echo 1. 访问：https://streamlit.io/cloud
echo 2. 用 GitHub 登录
echo 3. 点击 "New app"
echo 4. 选择你的仓库
echo 5. 主文件：main.py
echo 6. 配置环境变量（Secrets）
echo 7. 点击 "Deploy!"
echo.
echo 📖 详细指南：DEPLOYMENT_GUIDE.md
echo.
pause

