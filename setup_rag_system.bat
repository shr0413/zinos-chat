@echo off
REM ==========================================
REM   RAG 系统快速设置脚本
REM ==========================================

echo ==========================================
echo   RAG 系统快速设置
echo ==========================================
echo.

REM 1. 安装依赖
echo [1/3] 安装依赖包...
pip install -q tqdm
echo ✅ 完成
echo.

REM 2. 运行向量化脚本
echo [2/3] Start vectorization (5-10 minutes)...
echo.
python vectorize_knowledge_base.py
echo.

REM 3. 完成
echo [3/3] 设置完成！
echo.
echo ==========================================
echo   🎉 RAG 系统已就绪!
echo ==========================================
echo.
echo 下一步: 
echo   运行 'streamlit run main.py' 开始使用
echo.
pause

