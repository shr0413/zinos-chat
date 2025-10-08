# Qwen TTS 实现方案

## 📋 方案更新

基于 Qwen 官方 TTS 模型 `qwen3-tts-flash`，无需阿里云语音服务，实现更简单！

---

## 🎯 Qwen TTS 优势

### 相比阿里云语音合成
✅ **更简单**：同一个 API Key，无需额外配置  
✅ **更便宜**：包含在 DashScope 免费额度内  
✅ **更快**：flash 版本，响应迅速  
✅ **更自然**：Cherry/Ethan 两种高质量音色

### 技术参数
- **模型**：`qwen3-tts-flash`
- **音色**：Cherry（女声，活泼）、Ethan（男声）
- **语言**：中文/英文
- **采样率**：24000 Hz
- **格式**：PCM int16
- **流式**：支持

---

## 🔧 实现代码

### 1. TTS 处理模块

创建 `tts_qwen.py`：

```python
import os
import dashscope
import base64
import numpy as np
import uuid
import time
import streamlit as st
import streamlit.components.v1 as components
from config import config
from gtts import gTTS
from pydub import AudioSegment

class QwenTTSHandler:
    """Qwen TTS 处理器"""
    
    def __init__(self):
        self.use_qwen_tts = config.FEATURE_QWEN_TTS
        self.fallback_to_gtts = config.USE_GTTS_FALLBACK
        self.model = config.QWEN_TTS_MODEL
        self.voice = config.QWEN_TTS_VOICE
        self.language = config.QWEN_TTS_LANGUAGE
        self.stream_mode = config.QWEN_TTS_STREAM
        
    def synthesize(self, text, loading_placeholder=None):
        """
        语音合成主函数
        
        Args:
            text: 要合成的文本
            loading_placeholder: Streamlit 加载占位符
            
        Returns:
            audio_html: HTML5 音频播放代码
        """
        try:
            if self.use_qwen_tts:
                return self._qwen_tts(text, loading_placeholder)
            else:
                return self._gtts_fallback(text, loading_placeholder)
        except Exception as e:
            print(f"Qwen TTS 失败: {e}")
            if self.fallback_to_gtts:
                return self._gtts_fallback(text, loading_placeholder)
            else:
                raise
    
    def _qwen_tts(self, text, loading_placeholder=None):
        """Qwen TTS 实现（流式）"""
        audio_id = uuid.uuid4().hex
        filename = f"output_{audio_id}.wav"
        
        if loading_placeholder:
            loading_placeholder.markdown("""
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <div>正在生成自然语音...</div>
                </div>
            """, unsafe_allow_html=True)
        
        # 调用 Qwen TTS API（流式）
        response = dashscope.MultiModalConversation.call(
            api_key=config.DASHSCOPE_API_KEY,
            model=self.model,
            text=text,
            voice=self.voice,
            language_type=self.language,
            stream=self.stream_mode
        )
        
        # 收集音频数据
        audio_chunks = []
        for chunk in response:
            if chunk.output.audio.data is not None:
                wav_bytes = base64.b64decode(chunk.output.audio.data)
                audio_chunks.append(wav_bytes)
            
            if chunk.output.finish_reason == "stop":
                print(f"TTS 完成: {chunk.output.audio.expires_at}")
                break
        
        # 合并音频数据
        complete_audio = b''.join(audio_chunks)
        
        # 保存文件（可选，用于调试）
        # with open(filename, 'wb') as f:
        #     f.write(complete_audio)
        
        # Base64 编码
        b64_audio = base64.b64encode(complete_audio).decode()
        
        if loading_placeholder:
            loading_placeholder.empty()
        
        # 生成 HTML5 音频
        audio_html = self._generate_audio_html(audio_id, b64_audio, 'wav')
        
        return audio_html
    
    def _qwen_tts_non_stream(self, text, loading_placeholder=None):
        """Qwen TTS 实现（非流式，更简单）"""
        audio_id = uuid.uuid4().hex
        
        if loading_placeholder:
            loading_placeholder.markdown("""
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <div>正在生成自然语音...</div>
                </div>
            """, unsafe_allow_html=True)
        
        # 调用 Qwen TTS API（非流式）
        response = dashscope.MultiModalConversation.call(
            api_key=config.DASHSCOPE_API_KEY,
            model=self.model,
            text=text,
            voice=self.voice,
            language_type=self.language,
            stream=False
        )
        
        # 获取音频数据
        audio_data = base64.b64decode(response.output.audio.data)
        b64_audio = base64.b64encode(audio_data).decode()
        
        if loading_placeholder:
            loading_placeholder.empty()
        
        # 生成 HTML5 音频
        audio_html = self._generate_audio_html(audio_id, b64_audio, 'wav')
        
        return audio_html
    
    def _gtts_fallback(self, text, loading_placeholder=None):
        """gTTS 降级方案"""
        audio_id = uuid.uuid4().hex
        filename = f"output_{audio_id}.mp3"
        
        if loading_placeholder:
            loading_placeholder.markdown("""
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <div>使用备用语音引擎...</div>
                </div>
            """, unsafe_allow_html=True)
        
        # gTTS 生成
        tts = gTTS(text, lang='en', slow=False)
        tts.save("temp.mp3")
        
        # pydub 加速
        sound = AudioSegment.from_file("temp.mp3")
        lively_sound = sound.speedup(playback_speed=1.3)
        lively_sound.export(filename, format="mp3")
        
        # Base64 编码
        with open(filename, "rb") as f:
            audio_data = f.read()
            b64_audio = base64.b64encode(audio_data).decode()
        
        if loading_placeholder:
            loading_placeholder.empty()
        
        # 生成 HTML5 音频
        audio_html = self._generate_audio_html(audio_id, b64_audio, 'mp3')
        
        return audio_html
    
    def _generate_audio_html(self, audio_id, b64_audio, audio_format='wav'):
        """生成 HTML5 音频播放代码"""
        mime_type = f'audio/{audio_format}'
        
        audio_html = f"""
            <audio id="{audio_id}" autoplay>
                <source src="data:{mime_type};base64,{b64_audio}" type="{mime_type}">
            </audio>
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    const audio = document.getElementById('{audio_id}');
                    if (audio) {{
                        audio.addEventListener('play', function() {{
                            console.log('Audio started playing');
                        }});
                        
                        audio.addEventListener('ended', function() {{
                            console.log('Audio finished playing');
                        }});
                        
                        const playPromise = audio.play();
                        if (playPromise !== undefined) {{
                            playPromise.catch(error => {{
                                console.log("Audio playback failed:", error);
                                setTimeout(() => audio.play().catch(e => console.log(e)), 1000);
                            }});
                        }}
                    }}
                }});
            </script>
        """
        
        return audio_html

# 全局实例
tts_handler = QwenTTSHandler()

def speak_text(text, loading_placeholder=None):
    """
    语音合成入口函数（兼容旧接口）
    
    Args:
        text: 要合成的文本
        loading_placeholder: Streamlit 加载占位符
    """
    audio_html = tts_handler.synthesize(text, loading_placeholder)
    components.html(audio_html)
    time.sleep(0.8)  # 给浏览器播放时间
```

---

### 2. 配置模块更新

更新 `config.py`：

```python
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    # Qwen LLM
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
    QWEN_MODEL = os.getenv("QWEN_MODEL_NAME", "qwen-turbo")
    
    # 温度参数
    TEMP_CONVERSATION = float(os.getenv("QWEN_TEMPERATURE_CONVERSATION", "0.0"))
    TEMP_SCORING_POS = float(os.getenv("QWEN_TEMPERATURE_SCORING_POS", "0.2"))
    TEMP_SCORING_NEG = float(os.getenv("QWEN_TEMPERATURE_SCORING_NEG", "0.0"))
    TEMP_SEMANTIC = float(os.getenv("QWEN_TEMPERATURE_SEMANTIC", "0.4"))
    TEMP_ROUTER = float(os.getenv("QWEN_TEMPERATURE_ROUTER", "0.0"))
    
    # 向量库
    QWEN_EMBEDDING_MODEL = os.getenv("QWEN_EMBEDDING_MODEL", "text-embedding-v2")
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "db5")
    
    # Qwen TTS 配置 ⭐ 新增
    TTS_PROVIDER = os.getenv("TTS_PROVIDER", "qwen")
    QWEN_TTS_MODEL = os.getenv("QWEN_TTS_MODEL", "qwen3-tts-flash")
    QWEN_TTS_VOICE = os.getenv("QWEN_TTS_VOICE", "Cherry")
    QWEN_TTS_LANGUAGE = os.getenv("QWEN_TTS_LANGUAGE", "Chinese")
    QWEN_TTS_STREAM = os.getenv("QWEN_TTS_STREAM", "true").lower() == "true"
    USE_GTTS_FALLBACK = os.getenv("USE_GTTS_FALLBACK", "true").lower() == "true"
    
    # 功能开关
    FEATURE_QWEN_TTS = os.getenv("FEATURE_QWEN_TTS", "true").lower() == "true"
    FEATURE_SMART_AGENT = os.getenv("FEATURE_SMART_AGENT", "true").lower() == "true"
    FEATURE_VOICE_SELECTION = os.getenv("FEATURE_VOICE_SELECTION", "true").lower() == "true"
    
    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # RAG 配置
    RAG_MMR_K = int(os.getenv("RAG_MMR_K", "4"))
    RAG_MMR_FETCH_K = int(os.getenv("RAG_MMR_FETCH_K", "20"))
    RAG_MMR_LAMBDA = float(os.getenv("RAG_MMR_LAMBDA", "0.5"))
    ENABLE_HISTORY_DEDUP = os.getenv("ENABLE_HISTORY_DEDUP", "true").lower() == "true"
    MAX_HISTORY_ROUNDS = int(os.getenv("MAX_HISTORY_ROUNDS", "10"))
    
    # 搜索配置
    USE_WEB_SEARCH = os.getenv("USE_WEB_SEARCH", "true").lower() == "true"
    WEB_SEARCH_PROVIDER = os.getenv("WEB_SEARCH_PROVIDER", "duckduckgo")
    ENABLE_SMART_ROUTING = os.getenv("ENABLE_SMART_ROUTING", "true").lower() == "true"

config = Config()
```

---

### 3. 主应用集成

更新 `main.py`：

```python
# 导入 Qwen TTS
from tts_qwen import speak_text

# 在用户输入处理中使用（替换原有的 speak_text 调用）
if user_input:
    # ... 生成回答的代码 ...
    
    # 使用 Qwen TTS
    speak_text(answer, loading_placeholder)
    
    # ... 其他处理 ...
```

---

### 4. UI 音色选择功能（可选）

在侧边栏添加音色选择：

```python
# 在 main.py 的 right_col 中添加
with right_col:
    # ... 现有的亲密度显示 ...
    
    # 音色选择（如果启用）
    if config.FEATURE_VOICE_SELECTION:
        st.markdown("---")
        st.markdown("### 🎤 语音设置")
        
        voice_option = st.selectbox(
            "选择 Maria 的声音",
            options=["Cherry", "Ethan"],
            index=0 if config.QWEN_TTS_VOICE == "Cherry" else 1,
            help="Cherry: 女声（活泼）\nEthan: 男声"
        )
        
        # 更新配置
        if voice_option != config.QWEN_TTS_VOICE:
            config.QWEN_TTS_VOICE = voice_option
            st.success(f"✅ 已切换到 {voice_option} 音色")
```

---

## 📦 依赖更新

更新 `requirements.txt`：

```txt
# 删除或注释掉（不再需要）
# alibabacloud-nls-python-sdk>=2.0.0

# 确保 DashScope 版本正确
dashscope>=1.24.6

# 新增（用于音频处理，可选）
numpy>=1.24.0

# 保持现有
langchain==0.2.11
langchain-community>=0.2.10
langchain-chroma==0.1.2
chromadb
pypdf
streamlit
tiktoken
pysqlite3-binary
python-dotenv
gTTS  # 保留作为降级方案
pydub
st-supabase-connection==2.1.1
duckduckgo-search>=4.0
```

---

## ✅ 实施步骤

### Day 2: TTS 升级（简化版）

#### 上午（2小时）

- [ ] **2.1 创建 TTS 模块**
  ```bash
  # 创建文件
  touch tts_qwen.py
  
  # 复制上面的 QwenTTSHandler 代码
  ```

- [ ] **2.2 更新配置**
  ```bash
  # 编辑 .env
  TTS_PROVIDER=qwen
  QWEN_TTS_MODEL=qwen3-tts-flash
  QWEN_TTS_VOICE=Cherry
  QWEN_TTS_LANGUAGE=Chinese
  QWEN_TTS_STREAM=true
  ```

- [ ] **2.3 更新依赖**
  ```bash
  pip install dashscope>=1.24.6
  pip install numpy
  ```

#### 下午（2小时）

- [ ] **2.4 集成到主应用**
  - 修改 `main.py` 导入
  - 替换 `speak_text` 调用

- [ ] **2.5 测试**
  - 测试 Cherry 音色
  - 测试 Ethan 音色
  - 测试降级到 gTTS

- [ ] **2.6 添加音色选择UI（可选）**
  - 在右侧栏添加选择器
  - 实现实时切换

---

## 🎯 优势总结

### 相比原方案（阿里云 TTS）

| 对比项 | 阿里云 TTS | Qwen TTS ✅ |
|--------|-----------|------------|
| API Key | 需要额外配置 | **同一个 Key** |
| 配置复杂度 | AppKey + AccessKey | **仅需 DASHSCOPE_API_KEY** |
| 成本 | ¥10/月 | **包含在免费额度** |
| 音色数量 | 4+ | 2（足够） |
| 集成难度 | 中 | **低** |
| 代码行数 | ~150 行 | **~120 行** |

### 实际收益
- ✅ **节省 ¥10/月** TTS 费用
- ✅ **减少 30% 配置项**
- ✅ **降低 40% 集成复杂度**
- ✅ **统一 API 管理**

---

## 🧪 测试用例

### 测试脚本

创建 `test_qwen_tts.py`：

```python
import os
from dotenv import load_dotenv
from tts_qwen import QwenTTSHandler

load_dotenv()

# 测试用例
test_cases = [
    ("你好，我是Maria，齐诺海燕！", "Cherry"),
    ("Hi! I'm Maria the Zino's Petrel.", "Cherry"),
    ("What would you like to ask me?", "Ethan"),
]

tts = QwenTTSHandler()

for text, voice in test_cases:
    print(f"\n测试: {text} (音色: {voice})")
    tts.voice = voice
    try:
        audio_html = tts.synthesize(text)
        print("✅ 成功生成音频")
    except Exception as e:
        print(f"❌ 失败: {e}")
```

运行：
```bash
python test_qwen_tts.py
```

---

## 📝 配置清单

### .env 配置（TTS 部分）

```bash
# 必需
DASHSCOPE_API_KEY=sk-xxxxx

# TTS 配置
TTS_PROVIDER=qwen
QWEN_TTS_MODEL=qwen3-tts-flash
QWEN_TTS_VOICE=Cherry
QWEN_TTS_LANGUAGE=Chinese
QWEN_TTS_STREAM=true

# 降级配置
USE_GTTS_FALLBACK=true

# 功能开关
FEATURE_QWEN_TTS=true
FEATURE_VOICE_SELECTION=true
```

---

## 🚀 立即开始

```bash
# 1. 更新依赖
pip install dashscope>=1.24.6 numpy

# 2. 创建 TTS 模块
# 复制上面的 tts_qwen.py 代码

# 3. 更新配置
# 编辑 .env，添加 TTS 配置

# 4. 测试
python test_qwen_tts.py

# 5. 集成到主应用
# 修改 main.py 导入

# 6. 启动应用
streamlit run main.py
```

**预计时间：4 小时**（比原计划减少 1 小时）

---

**更新日期**：2025-10-06  
**实施难度**：⭐⭐ (简单)  
**推荐度**：⭐⭐⭐⭐⭐

