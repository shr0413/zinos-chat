@echo off
chcp 65001 > nul
echo ==========================================
echo   快速修复 - pysqlite3 缺失问题
echo ==========================================
echo.

echo [步骤 1] 安装 pysqlite3-binary...
pip install pysqlite3-binary
echo.

echo [步骤 2] 安装 dashscope（Qwen API）...
pip install dashscope>=1.24.6
echo.

echo [步骤 3] 安装 numpy...
pip install numpy
echo.

echo [步骤 4] 验证安装...
python -c "import pysqlite3; print('✅ pysqlite3-binary 安装成功')" 2>nul
if errorlevel 1 (
    echo ❌ pysqlite3-binary 安装失败
    echo.
    echo 请尝试手动安装：
    echo   pip uninstall pysqlite3-binary -y
    echo   pip install pysqlite3-binary --force-reinstall
    pause
    exit /b 1
)

python -c "import dashscope; print('✅ dashscope 安装成功')" 2>nul
if errorlevel 1 (
    echo ❌ dashscope 安装失败
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   ✅ 修复完成！
echo ==========================================
echo.
echo 现在可以重新运行：
echo   streamlit run main.py
echo.
pause

