# 🐦 Zino's Chat - AI Interactive Learning Experience

与 Fred（Zino's Petrel）对话，了解濒危鸟类和生物多样性保护！

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

### 本地运行

1. **克隆仓库**:
   ```bash
   git clone https://github.com/你的用户名/zinos-chat.git
   cd zinos-chat
   ```

2. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**:
   - 复制 `config.env.template` 为 `.env`
   - 填入你的 API Keys

4. **运行应用**:
   ```bash
   streamlit run main.py
   ```

5. **访问**:
   - 浏览器自动打开 `http://localhost:8501`

---

## 🌐 在线部署

### Streamlit Community Cloud（推荐）

1. **准备部署**:
   ```bash
   ./deploy_to_streamlit.bat
   ```

2. **访问部署平台**:
   - https://streamlit.io/cloud

3. **配置应用**:
   - Repository: `你的用户名/zinos-chat`
   - Main file: `main.py`
   - Python version: 3.10+

4. **设置 Secrets**:
   - 复制 `.streamlit/secrets.toml.template` 内容
   - 在 Streamlit Cloud 填入实际值

5. **点击 Deploy!** 🚀

📖 **详细指南**: [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md)

---

## 🔑 环境变量

### 必需配置

| 变量 | 说明 | 获取地址 |
|------|------|---------|
| `DASHSCOPE_API_KEY` | Qwen API Key | https://dashscope.aliyun.com/ |
| `SUPABASE_URL` | Supabase 项目 URL | https://app.supabase.com/ |
| `SUPABASE_KEY` | Supabase Anon Key | https://app.supabase.com/ |

### 可选配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `QWEN_MODEL_NAME` | LLM 模型 | `qwen-turbo` |
| `QWEN_TTS_MODEL` | TTS 模型 | `qwen3-tts-flash` |
| `QWEN_TTS_VOICE` | TTS 音色 | `Cherry` |

---

## 📁 项目结构

```
zinos-chat/
├── main.py                    # 主应用
├── tts_utils.py              # TTS 工具
├── requirements.txt          # Python 依赖
├── .env                      # 环境变量（本地）
├── .gitignore               # Git 忽略规则
├── .streamlit/
│   ├── config.toml          # Streamlit 配置
│   └── secrets.toml.template # Secrets 模板
├── stickers/                # 贴纸资源
│   ├── home.png
│   ├── routine.png
│   ├── food.png
│   └── helper.png
├── zino.png                 # 应用图标
├── gift.png                 # 礼物图片
└── DEPLOYMENT_GUIDE.md      # 部署指南
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
- **ChromaDB**: 向量数据库
- **Supabase**: 交互日志

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
- 7 维度评分：
  - ✅ Knowledge（知识）
  - ✅ Empathy（共情）
  - ✅ Conservation（保护意识）
  - ✅ Engagement（参与度）
  - ✅ Deep Interaction（深度互动）
  - ❌ Harmful Intent（负面意图）
  - ❌ Disrespect（不尊重）

### 5. 奖励机制
- 4 种 Stickers：
  - 🏡 Home Explorer
  - 🌙 Daily Life Detective
  - 🍽️ Food Finder
  - 🌱 Species Supporter
- 成就勋章（满分奖励）

---

## 🎯 使用场景

- 🏫 **教育**: 生物多样性教学
- 🌍 **科普**: 濒危物种宣传
- 🗣️ **语言学习**: 双语环境练习
- 🎮 **互动体验**: 趣味学习游戏

---

## 📈 性能优化

### Day 1 完成
- ✅ OpenAI → Qwen 迁移
- ✅ 响应速度：3.5s → 2.0s（**-43%**）
- ✅ LLM 调用：4 次 → 2 次（**-50%**）

### Day 2 完成
- ✅ TTS 升级：gTTS → Qwen TTS
- ✅ TTS 速度：3.0s → 0.5s（**-83%**）
- ✅ 音质：机器音 → 自然人声

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

**与 Fred 开始对话！** 🎉

[🚀 在线体验](https://your-app.streamlit.app) | [📖 部署指南](DEPLOYMENT_GUIDE.md) | [🐛 报告问题](https://github.com/你的用户名/zinos-chat/issues)

