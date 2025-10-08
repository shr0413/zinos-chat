@echo off
chcp 65001 > nul
echo ==========================================
echo   修复 pysqlite3-binary 安装问题
echo ==========================================
echo.

echo [方法 1] 从官方 PyPI 源安装...
pip install pysqlite3-binary -i https://pypi.org/simple
echo.

if errorlevel 1 (
    echo [方法 1] 失败，尝试方法 2...
    echo.
    echo [方法 2] 修改 main.py，移除 pysqlite3 依赖...
    echo.
    echo 在 Windows + Conda 环境下，通常不需要 pysqlite3
    echo 我们将注释掉这两行代码
    echo.
    
    python -c "import sys; content = open('main.py', 'r', encoding='utf-8').read(); content = content.replace('import pysqlite3\nsys.modules[\"sqlite3\"] = pysqlite3', '# import pysqlite3\n# sys.modules[\"sqlite3\"] = pysqlite3  # Windows/Conda 环境不需要'); open('main.py', 'w', encoding='utf-8').write(content); print('✅ main.py 已修改')"
    
    echo.
    echo ✅ 修复完成！pysqlite3 依赖已移除
) else (
    echo ✅ pysqlite3-binary 安装成功！
)

echo.
echo ==========================================
echo   下一步：启动应用
echo ==========================================
echo   streamlit run main.py
echo.
pause

