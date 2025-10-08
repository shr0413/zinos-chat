@echo off
chcp 65001 > nul
echo ==========================================
echo   一键安装所有依赖
echo ==========================================
echo.

echo [1/6] 升级 pip...
python -m pip install --upgrade pip
echo.

echo [2/6] 安装核心框架...
pip install langchain==0.2.11
pip install langchain-chroma==0.1.2
pip install langchain-community==0.2.10
pip install chromadb
pip install streamlit
pip install python-dotenv
echo.

echo [3/6] 安装 Qwen 相关（Day 1 必需）...
pip install dashscope>=1.24.6
pip install numpy
echo.

echo [4/6] 安装音频处理...
pip install gTTS
pip install pydub
pip install ffmpeg-python
pip install SpeechRecognition==3.10.0
pip install pocketsphinx
echo.

echo [5/6] 安装其他依赖...
pip install pypdf
pip install tiktoken
pip install st-supabase-connection==2.1.1
echo.

echo [6/6] 验证关键模块...
echo.
python -c "from gtts import gTTS; print('✅ gTTS')" 2>nul || echo ❌ gTTS
python -c "import dashscope; print('✅ dashscope')" 2>nul || echo ❌ dashscope
python -c "import streamlit; print('✅ streamlit')" 2>nul || echo ❌ streamlit
python -c "from langchain_community.llms import Tongyi; print('✅ langchain-community')" 2>nul || echo ❌ langchain-community
python -c "import chromadb; print('✅ chromadb')" 2>nul || echo ❌ chromadb
python -c "from pydub import AudioSegment; print('✅ pydub')" 2>nul || echo ❌ pydub
echo.

echo ==========================================
echo   ✅ 安装完成！
echo ==========================================
echo.
echo 下一步：
echo   streamlit run main.py
echo.
pause

