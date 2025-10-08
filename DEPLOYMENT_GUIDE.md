# 🚀 Streamlit 应用部署指南

## 📋 目录
1. [Streamlit Community Cloud（推荐）](#streamlit-community-cloud)
2. [准备工作](#准备工作)
3. [部署步骤](#部署步骤)
4. [其他部署选项](#其他部署选项)
5. [常见问题](#常见问题)

---

## 🌟 Streamlit Community Cloud（推荐）

**最简单、免费、官方支持的部署方式！**

### ✅ 优势
- ✅ **完全免费**（公开项目）
- ✅ **自动部署**（推送到 GitHub 即自动更新）
- ✅ **HTTPS 支持**
- ✅ **无需服务器管理**
- ✅ **环境变量管理**

### 📊 限制
- 资源：1 CPU core, 800MB RAM
- 适合：中小型应用、演示、原型

---

## 📦 准备工作

### 1. 创建 GitHub 仓库

```bash
# 在项目目录初始化 Git
cd E:\ProjectFolder\Business_Data_Analyse\Musement\zinos-chat
git init
git add .
git commit -m "Initial commit: Zino's Chat App"

# 创建 GitHub 仓库（在 GitHub 网站上）
# 然后关联远程仓库
git remote add origin https://github.com/你的用户名/zinos-chat.git
git branch -M main
git push -u origin main
```

### 2. 准备必需文件

#### ✅ `requirements.txt`（已有）
确保包含所有依赖：
```txt
streamlit>=1.31.0
langchain>=0.1.0
langchain-community>=0.0.20
dashscope>=1.24.6
chromadb>=0.4.22
python-dotenv>=1.0.0
supabase>=2.0.0
st-supabase-connection>=0.1.0
requests>=2.31.0
```

#### ✅ `.streamlit/config.toml`（可选）
创建自定义配置：

```bash
mkdir .streamlit
```

创建文件：`.streamlit/config.toml`
```toml
[theme]
primaryColor = "#a1b065"
backgroundColor = "#cdd5ae"
secondaryBackgroundColor = "#345e42"
textColor = "#2d4f38"
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false
```

#### ✅ `.gitignore`
创建 `.gitignore` 防止敏感信息上传：
```gitignore
# 环境变量
.env
*.env
config.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Virtual environments
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Streamlit
.streamlit/secrets.toml

# Audio files
*.mp3
output_*.mp3
temp_*.mp3

# ChromaDB
db5_qwen/
chroma.sqlite3
```

---

## 🚀 部署步骤

### 步骤 1: 推送代码到 GitHub

```bash
# 确保所有文件已提交
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### 步骤 2: 访问 Streamlit Community Cloud

1. 访问：https://streamlit.io/cloud
2. 点击 **"Sign up"** 或 **"Sign in with GitHub"**
3. 授权 Streamlit 访问你的 GitHub

### 步骤 3: 部署应用

1. **点击 "New app"**
2. **填写部署信息**：
   - **Repository**: 选择 `你的用户名/zinos-chat`
   - **Branch**: `main`
   - **Main file path**: `main.py`
   - **App URL**: 自定义 URL（如 `zinos-chat`）

3. **配置环境变量**（点击 "Advanced settings"）：
   ```
   DASHSCOPE_API_KEY=你的Qwen_API_Key
   SUPABASE_URL=你的Supabase_URL
   SUPABASE_KEY=你的Supabase_Key
   QWEN_MODEL_NAME=qwen-turbo
   QWEN_EMBEDDING_MODEL=text-embedding-v2
   QWEN_TTS_MODEL=qwen3-tts-flash
   QWEN_TTS_VOICE=Cherry
   ```

4. **点击 "Deploy!"**

### 步骤 4: 等待部署完成

- ⏱️ 首次部署约 5-10 分钟
- 📊 可以查看部署日志
- ✅ 完成后会显示应用 URL

### 步骤 5: 访问应用

- 你的应用 URL：`https://你的应用名.streamlit.app`
- 分享给任何人试用！

---

## 🔐 环境变量配置

### 在 Streamlit Cloud 设置

1. 进入应用管理页面
2. 点击 **"⚙️ Settings"**
3. 选择 **"Secrets"**
4. 添加以下内容：

```toml
DASHSCOPE_API_KEY = "sk-your-qwen-api-key"
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-supabase-anon-key"
QWEN_MODEL_NAME = "qwen-turbo"
QWEN_EMBEDDING_MODEL = "text-embedding-v2"
QWEN_TTS_MODEL = "qwen3-tts-flash"
QWEN_TTS_VOICE = "Cherry"
```

### 代码中读取 Secrets

```python
import streamlit as st
import os

# 从 Streamlit Secrets 或环境变量读取
dashscope_key = os.getenv("DASHSCOPE_API_KEY") or st.secrets.get("DASHSCOPE_API_KEY")
```

---

## 🔄 自动更新

**代码更新后自动重新部署**：

```bash
# 修改代码后
git add .
git commit -m "Update feature XYZ"
git push origin main

# Streamlit Cloud 会自动检测并重新部署！
```

---

## 🌐 其他部署选项

### 1. Hugging Face Spaces

**优势**：免费 GPU、与 AI 社区集成

**步骤**：
1. 访问：https://huggingface.co/spaces
2. 创建 Space → 选择 Streamlit
3. 上传代码和 `requirements.txt`
4. 配置环境变量

**URL 格式**：`https://huggingface.co/spaces/你的用户名/应用名`

---

### 2. Railway

**优势**：500 小时免费、支持数据库

**步骤**：
1. 访问：https://railway.app
2. 连接 GitHub 仓库
3. 配置环境变量
4. 部署

**定价**：免费 $5/月额度

---

### 3. Render

**优势**：免费层级、自动 HTTPS

**步骤**：
1. 访问：https://render.com
2. 创建 Web Service
3. 连接 GitHub
4. 设置启动命令：
   ```bash
   streamlit run main.py --server.port=$PORT --server.address=0.0.0.0
   ```

**定价**：免费（有休眠限制）

---

### 4. Heroku

**步骤**：
1. 创建 `Procfile`：
   ```
   web: sh setup.sh && streamlit run main.py
   ```

2. 创建 `setup.sh`：
   ```bash
   mkdir -p ~/.streamlit/
   echo "\
   [server]\n\
   headless = true\n\
   port = $PORT\n\
   enableCORS = false\n\
   \n\
   " > ~/.streamlit/config.toml
   ```

3. 部署：
   ```bash
   heroku create
   git push heroku main
   ```

**定价**：基础版 $7/月

---

## 📁 项目结构检查

确保你的项目包含：

```
zinos-chat/
├── main.py                    # ✅ 主应用文件
├── tts_utils.py              # ✅ TTS 工具
├── requirements.txt          # ✅ 依赖列表
├── .env                      # ❌ 不上传（包含在 .gitignore）
├── .gitignore               # ✅ Git 忽略规则
├── .streamlit/
│   └── config.toml          # ✅ Streamlit 配置
├── stickers/                # ✅ 静态资源
│   ├── home.png
│   ├── routine.png
│   ├── food.png
│   └── helper.png
├── zino.png                 # ✅ 图片资源
└── gift.png                 # ✅ 图片资源
```

---

## ⚠️ 常见问题

### 1. 部署失败：ModuleNotFoundError

**原因**：`requirements.txt` 缺少依赖

**解决**：
```bash
# 生成完整的依赖列表
pip freeze > requirements.txt

# 或手动添加缺失的包
echo "missing-package>=1.0.0" >> requirements.txt
```

---

### 2. ChromaDB 持久化问题

**原因**：Streamlit Cloud 重启会清空文件

**解决方案 A**：使用云存储（推荐）
- 改用 Pinecone、Weaviate 等云向量数据库

**解决方案 B**：启动时重建
```python
import os

def ensure_vector_db():
    if not os.path.exists('db5_qwen'):
        # 重新创建向量数据库
        rebuild_vector_db()
```

---

### 3. 环境变量未生效

**检查**：
```python
import streamlit as st

# 调试：打印环境变量（部署后删除）
st.write(f"API Key exists: {bool(st.secrets.get('DASHSCOPE_API_KEY'))}")
```

**确保**：
- Secrets 格式正确（TOML 格式）
- Key 名称完全匹配
- 重新部署后才生效

---

### 4. 应用运行缓慢

**优化**：
1. 使用 `@st.cache_data` 缓存数据
2. 使用 `@st.cache_resource` 缓存模型
3. 减少 API 调用频率
4. 优化向量检索参数

```python
@st.cache_resource
def load_model():
    return Tongyi(...)

@st.cache_data(ttl=3600)
def load_vector_db():
    return Chroma(...)
```

---

### 5. API 限流问题

**Qwen API 免费额度**：
- 100 万 tokens/月（LLM）
- 包含 TTS 和 Embeddings

**解决**：
- 监控使用量：https://dashscope.console.aliyun.com/
- 添加使用限制
- 升级到付费版本

---

## 🔗 快速部署清单

- [ ] 1. 创建 GitHub 仓库并推送代码
- [ ] 2. 创建 `.gitignore` 防止上传敏感信息
- [ ] 3. 确认 `requirements.txt` 包含所有依赖
- [ ] 4. 访问 https://streamlit.io/cloud
- [ ] 5. 用 GitHub 登录
- [ ] 6. 点击 "New app"
- [ ] 7. 选择仓库和分支
- [ ] 8. 设置主文件为 `main.py`
- [ ] 9. 配置环境变量（Secrets）
- [ ] 10. 点击 "Deploy!"
- [ ] 11. 等待部署完成（5-10 分钟）
- [ ] 12. 测试应用 URL
- [ ] 13. 分享链接！🎉

---

## 📞 获取帮助

**Streamlit 官方资源**：
- 文档：https://docs.streamlit.io/streamlit-community-cloud
- 论坛：https://discuss.streamlit.io
- GitHub：https://github.com/streamlit/streamlit

**本项目支持**：
- 遇到问题请查看日志
- 检查环境变量配置
- 确认所有依赖已安装

---

## 🎉 部署成功后

### 分享你的应用
```
🎊 Zino's Chat 现已上线！
🔗 链接：https://你的应用名.streamlit.app
🐦 与 Fred the Zino's Petrel 聊天
🌍 支持英语和葡萄牙语
🎤 Qwen TTS 自然语音
```

### 监控和维护
- 定期检查应用状态
- 查看使用分析
- 更新依赖版本
- 收集用户反馈

---

**祝部署成功！** 🚀✨

