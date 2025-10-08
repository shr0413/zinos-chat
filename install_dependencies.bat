@echo off
chcp 65001 > nul
echo ==========================================
echo   Zino's Chat - 依赖安装脚本
echo ==========================================
echo.

echo [1/4] 检查 Python 环境...
python --version
if errorlevel 1 (
    echo ❌ 错误：未检测到 Python，请先安装 Python
    pause
    exit /b 1
)
echo ✅ Python 环境正常
echo.

echo [2/4] 升级 pip...
python -m pip install --upgrade pip
echo.

echo [3/4] 安装核心依赖...
pip install -r requirements.txt
echo.

echo [4/4] 验证关键模块...
python -c "import pysqlite3; print('✅ pysqlite3-binary 安装成功')"
python -c "import dashscope; print('✅ dashscope 安装成功')"
python -c "import streamlit; print('✅ streamlit 安装成功')"
python -c "from langchain_community.llms import Tongyi; print('✅ langchain-community 安装成功')"
echo.

echo ==========================================
echo   ✅ 所有依赖安装完成！
echo ==========================================
echo.
echo 下一步：
echo   1. 配置 .env 文件
echo   2. 运行：python verify_config.py
echo   3. 启动应用：streamlit run main.py
echo.
pause

