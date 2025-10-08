# 🐦 Zino's Chat - AI 互动学习体验

与 Fred（Zino's Petrel - 齐诺氏圆尾鹱）对话，了解濒危鸟类和生物多样性保护！

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)

---

## ✨ 功能特点

### 🌍 双语支持
- 🇬🇧 **英语**（English）
- 🇵🇹 **葡萄牙语**（Português）

### 🎤 自然语音
- **Qwen TTS**: 高质量文本转语音
- **双音色**: Cherry（女声）/ Ethan（男声）
- **即时播放**: 自动语音回复

### 🤖 智能 AI
- **Qwen LLM**: 阿里云通义千问大模型
- **个性化对话**: Fred 以第一人称讲述生活
- **RAG 检索**: 基于科学知识的准确回答

### 🎁 互动系统
- **❤️ Friendship Score**: 对话质量评分
- **🎁 Sticker 奖励**: 解锁特殊贴纸
- **🏅 成就勋章**: 达到满分获得礼物

### ✅ 事实验证
- **Fact Check**: 查看回答的知识来源
- **科学依据**: 基于权威知识库

---

## 🚀 快速开始

### 方式 1：本地运行（5 分钟）

#### 1. 克隆仓库
```bash
git clone https://github.com/你的用户名/zinos-chat.git
cd zinos-chat
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 配置环境变量
复制 `config.env.template` 为 `.env`，填入你的 API Keys：

```bash
# Qwen API (必需)
DASHSCOPE_API_KEY=sk-你的API密钥

# Supabase (必需 - 用于日志)
SUPABASE_URL=https://你的项目.supabase.co
SUPABASE_KEY=你的Supabase密钥

# 可选配置
QWEN_MODEL_NAME=qwen-turbo
QWEN_EMBEDDING_MODEL=text-embedding-v2
QWEN_TTS_MODEL=qwen3-tts-flash
QWEN_TTS_VOICE=Cherry
```

#### 4. 运行应用
```bash
streamlit run main.py
```

#### 5. 访问应用
浏览器自动打开 `http://localhost:8501`

---

### 方式 2：在线部署（3 步骤）

#### 步骤 1: 推送到 GitHub

```bash
# 初始化 Git
git init
git add .
git commit -m "Deploy Zino's Chat"

# 关联远程仓库
git remote add origin https://github.com/你的用户名/zinos-chat.git
git branch -M main
git push -u origin main
```

#### 步骤 2: Streamlit Cloud 部署

1. 访问：https://streamlit.io/cloud
2. 用 GitHub 登录
3. 点击 **"New app"**
4. 填写信息：
   - **Repository**: `你的用户名/zinos-chat`
   - **Branch**: `main`
   - **Main file path**: `main.py`
5. 点击 **"Deploy!"**

#### 步骤 3: 配置环境变量

在部署页面点击 **"Advanced settings" → "Secrets"**，粘贴：

```toml
DASHSCOPE_API_KEY = "sk-你的Qwen_API_Key"
SUPABASE_URL = "https://你的项目.supabase.co"
SUPABASE_KEY = "你的Supabase_Anon_Key"
QWEN_MODEL_NAME = "qwen-turbo"
QWEN_EMBEDDING_MODEL = "text-embedding-v2"
QWEN_TTS_MODEL = "qwen3-tts-flash"
QWEN_TTS_VOICE = "Cherry"
```

**保存** → 应用自动重启 → **完成！** 🎉

你的应用 URL：`https://你的应用名.streamlit.app`

---

## 🔑 获取 API Keys

### 1. Qwen API Key（免费）

1. 访问：https://dashscope.aliyun.com/
2. 登录/注册（支持微信/支付宝）
3. 进入 **"API-KEY 管理"**
4. 创建 API Key
5. 复制保存（格式：`sk-xxxxx`）

**免费额度**:
- 100 万 tokens/月（LLM）
- 包含 TTS 和 Embeddings

### 2. Supabase（免费）

1. 访问：https://app.supabase.com/
2. 用 GitHub 登录
3. 创建新项目
4. 进入 **"Settings" → "API"**
5. 复制：
   - **Project URL**: `https://xxx.supabase.co`
   - **anon public key**: `eyJxxx...`

**创建数据表**（用于日志）:

```sql
CREATE TABLE interactions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id TEXT,
  user_msg TEXT,
  ai_msg TEXT,
  ai_name TEXT,
  intimacy_score FLOAT,
  sticker_awarded TEXT,
  gift_given BOOLEAN,
  response_analysis JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 📁 项目结构

```
zinos-chat/
├── main.py                    # 主应用
├── tts_utils.py              # TTS 工具
├── config.py                 # 配置文件
├── requirements.txt          # Python 依赖
├── config.env.template       # 环境变量模板
├── .gitignore               # Git 忽略规则
├── stickers/                # 贴纸资源
│   ├── home.png
│   ├── routine.png
│   ├── food.png
│   └── helper.png
├── zino.png                 # 应用图标
├── gift.png                 # 礼物图片
└── intro5.mp3              # 介绍音频
```

---

## 🛠️ 技术栈

### 核心框架
- **Streamlit**: Web 界面
- **LangChain**: LLM 编排

### AI 服务
- **Qwen (通义千问)**:
  - LLM: `qwen-turbo`
  - Embeddings: `text-embedding-v2`
  - TTS: `qwen3-tts-flash`

### 数据存储
- **ChromaDB**: 向量数据库（本地）
- **Supabase**: 交互日志（云端）

---

## 📊 功能模块

### 1. 对话系统
- AI 角色扮演（Fred the Petrel）
- 双语 Prompt 切换
- 自然对话流程

### 2. 语音合成
- Qwen TTS 集成
- 音色选择（Cherry/Ethan）
- 自动播放

### 3. RAG 检索
- ChromaDB 向量检索
- MMR 多样性算法
- 科学知识库

### 4. 评分系统
- **正向评分**（+1 分）：
  - ✅ Knowledge（知识）
  - ✅ Empathy（共情）
  - ✅ Conservation（保护意识）
  - ✅ Engagement（参与度）
  - ✅ Deep Interaction（深度互动）
- **负向评分**（-1 分）：
  - ❌ Harmful Intent（负面意图）
  - ❌ Disrespect（不尊重）

### 5. 奖励机制
- **4 种 Stickers**：
  - 🏡 Home Explorer
  - 🌙 Daily Life Detective
  - 🍽️ Food Finder
  - 🌱 Species Supporter
- **成就勋章**（满分奖励）

---

## 🎯 使用场景

- 🏫 **教育**: 生物多样性教学
- 🌍 **科普**: 濒危物种宣传
- 🗣️ **语言学习**: 双语环境练习
- 🎮 **互动体验**: 趣味学习游戏

---

## 📈 性能优化

### 已完成优化
- ✅ OpenAI → Qwen 迁移
- ✅ 响应速度：3.5s → 2.0s（**-43%**）
- ✅ LLM 调用：4 次 → 2 次（**-50%**）
- ✅ TTS 升级：gTTS → Qwen TTS
- ✅ TTS 速度：3.0s → 0.5s（**-83%**）
- ✅ 音质：机器音 → 自然人声

---

## ⚠️ 常见问题

### 1. 部署失败：ModuleNotFoundError

**解决**:
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

### 2. TTS 不工作

**检查**:
- ✅ `DASHSCOPE_API_KEY` 正确
- ✅ API Key 已开通 TTS 权限
- ✅ Secrets 配置无误

### 3. 向量数据库为空

**原因**: Streamlit Cloud 重启会清空文件

**解决**: 应用启动时会自动检测并提示上传文档

### 4. 应用访问慢

**优化建议**:
1. 启用缓存：`@st.cache_data` 和 `@st.cache_resource`
2. 减少 API 调用频率
3. 优化 RAG 检索参数

---

## 📝 环境变量说明

| 变量 | 说明 | 必需 | 默认值 |
|------|------|------|--------|
| `DASHSCOPE_API_KEY` | Qwen API Key | ✅ | - |
| `SUPABASE_URL` | Supabase 项目 URL | ✅ | - |
| `SUPABASE_KEY` | Supabase Anon Key | ✅ | - |
| `QWEN_MODEL_NAME` | LLM 模型 | ❌ | `qwen-turbo` |
| `QWEN_EMBEDDING_MODEL` | Embedding 模型 | ❌ | `text-embedding-v2` |
| `QWEN_TTS_MODEL` | TTS 模型 | ❌ | `qwen3-tts-flash` |
| `QWEN_TTS_VOICE` | TTS 音色 | ❌ | `Cherry` |

---

## 🔄 自动更新

修改代码后自动重新部署：

```bash
git add .
git commit -m "Update feature XYZ"
git push origin main

# Streamlit Cloud 会自动检测并重新部署！
```

---

## 🤝 贡献

欢迎贡献！请：
1. Fork 本仓库
2. 创建特性分支（`git checkout -b feature/AmazingFeature`）
3. 提交更改（`git commit -m 'Add some AmazingFeature'`）
4. 推送到分支（`git push origin feature/AmazingFeature`）
5. 开启 Pull Request

---

## 📝 许可证

本项目采用 MIT 许可证。

---

## 📞 联系方式

- 📧 Email: your-email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/你的用户名/zinos-chat/issues)

---

## 🙏 致谢

- **Qwen (通义千问)**: 提供 LLM、TTS、Embeddings
- **Streamlit**: 快速构建 Web 应用
- **Supabase**: 数据库服务
- **Zino's Petrel**: 灵感来源 🐦

---

## 📊 部署检查清单

### 本地运行
- [ ] 安装 Python 3.8+
- [ ] 克隆仓库
- [ ] 安装依赖 `pip install -r requirements.txt`
- [ ] 配置 `.env` 文件
- [ ] 运行 `streamlit run main.py`
- [ ] 访问 `http://localhost:8501`

### 在线部署
- [ ] 创建 GitHub 仓库并推送代码
- [ ] 访问 https://streamlit.io/cloud
- [ ] 用 GitHub 登录
- [ ] 点击 "New app"
- [ ] 选择仓库和分支
- [ ] 设置主文件为 `main.py`
- [ ] 配置环境变量（Secrets）
- [ ] 点击 "Deploy!"
- [ ] 等待部署完成（5-10 分钟）
- [ ] 测试应用 URL
- [ ] 分享链接！🎉

---

**与 Fred 开始对话！** 🐦✨

[🚀 在线体验](https://your-app.streamlit.app) | [🐛 报告问题](https://github.com/你的用户名/zinos-chat/issues)
