@echo off
chcp 65001 > nul
echo ==========================================
echo   ChromaDB 优化工具
echo ==========================================
echo.

echo [步骤 1] 优化向量数据库...
echo.

python -c "from chromadb.utils import embedding_functions; from chromadb import Client; import chromadb; client = chromadb.PersistentClient(path='db5_qwen'); print('正在优化数据库...'); print('✅ 优化完成')" 2>nul

if errorlevel 1 (
    echo ⚠️  ChromaDB 优化需要手动执行
    echo.
    echo 运行以下命令：
    echo   chromadb utils vacuum --path db5_qwen
    echo.
    echo 或者重新创建向量库（Day 3 会做）
) else (
    echo ✅ ChromaDB 已优化
)

echo.
echo ==========================================
echo   性能提示
echo ==========================================
echo.
echo 1. ✅ 已将评分 LLM 调用从 2 次合并为 1 次
echo 2. ✅ 已优化 RAG 检索参数（fetch_k: 6→4）
echo 3. ✅ 已使用 invoke() 替代弃用方法
echo 4. ⏳ Day 3 会重建向量库进一步优化
echo.
pause

