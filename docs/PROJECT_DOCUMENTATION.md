# Zino's Chat - 项目文档

## 📋 项目概述

**Zino's Chat** 是一个基于 AI 的互动教育聊天应用，旨在通过与濒危鸟类"齐诺海燕"(Zino's Petrel) Maria 的对话，向用户传播生物多样性和环境保护知识。该项目结合了自然语言处理、语音合成、游戏化机制等多种技术，为用户提供沉浸式的学习体验。

### 核心特点

- 🦅 **AI 角色扮演**：与 Maria（一只齐诺海燕）进行自然对话
- 🎯 **游戏化学习**：通过亲密度评分系统和贴纸奖励机制激励用户互动
- 🔊 **语音输出**：AI 回复自动转换为语音播放
- 📊 **数据追踪**：所有对话记录存储到 Supabase 数据库
- 🎁 **成就系统**：达到特定条件可解锁贴纸和礼物

---

## 🏗️ 项目结构

```
zinos-chat/
│
├── main.py                          # 主应用程序入口
├── requirements.txt                 # Python 依赖包列表
├── packages.txt                     # 系统级依赖 (ffmpeg)
├── README.md                        # 基础安装和使用说明
│
├── create_table_interactions.sql   # Supabase 数据库表结构
│
├── zino.png                         # Maria 的头像图片
├── gift.png                         # 达成最高亲密度时的礼物图片
├── intro5.mp3                       # 开场音频（未使用）
├── temp.mp3                         # 临时音频文件
│
├── stickers/                        # 贴纸奖励图片目录
│   ├── home.png                     # "家园探索者" 贴纸
│   ├── routine.png                  # "日常生活侦探" 贴纸
│   ├── food.png                     # "食物发现者" 贴纸
│   └── helper.png                   # "物种支持者" 贴纸
│
├── db5/                             # ChromaDB 向量数据库
│   ├── chroma.sqlite3               # 向量数据库索引
│   └── a2cdbd0c-16ad-428c-9d92-e419124e3332/  # 向量存储
│
├── .streamlit/                      # Streamlit 配置
│   └── config.toml
│
├── .devcontainer/                   # 开发容器配置
│   └── devcontainer.json
│
└── .git/                            # Git 版本控制
```

---

## 🔧 技术栈

### 核心框架
- **Streamlit** (`streamlit`) - Web 应用框架
- **LangChain** (`langchain==0.2.11`) - LLM 应用开发框架

### AI/ML 组件
- **OpenAI API** (`langchain-openai==0.1.20`) - 大语言模型服务
- **ChromaDB** (`langchain-chroma==0.1.2`, `chromadb`) - 向量数据库
- **OpenAI Embeddings** - 文本嵌入模型

### 数据库
- **Supabase** (`st-supabase-connection==2.1.1`) - 后端数据存储
- **pysqlite3** (`pysqlite3-binary`) - SQLite 数据库驱动

### 音频处理
- **gTTS** (`gTTS`) - Google Text-to-Speech
- **pydub** (`pydub`) - 音频处理库
- **ffmpeg** - 音频编解码器
- **SpeechRecognition** (`SpeechRecognition==3.10.0`) - 语音识别（代码中导入但未使用）

### 文档处理
- **pypdf** (`pypdf`) - PDF 文档加载
- **tiktoken** (`tiktoken`) - Token 计数

---

## 🎯 功能模块详解

### 1. 对话系统 (Conversational AI)

#### 核心组件
- **向量数据库检索**：使用 ChromaDB 进行语义搜索
  - 采用 MMR (Maximal Marginal Relevance) 算法获取最相关的知识片段
  - 参数：`k=2, fetch_k=6, lambda_mult=1`
  
- **提示词工程**：精心设计的角色提示词
  - Maria 的人格设定：富有经验的齐诺海燕，从鸟类视角分享知识
  - 回复规则：60 字以内，第一人称，具象化表达
  
- **LLM 模型配置**：
  - 对话模型：`OpenAI(temperature=0)` - 保证回复一致性
  - 语义评估模型：`OpenAI(temperature=0.4)` - 略有创造性

#### 对话流程
```
用户输入 → 向量检索 → 构建提示词 → LLM 生成 → 文本处理 → 语音合成 → 展示回复
```

### 2. 亲密度评分系统 (Intimacy Scoring)

#### 评分维度

**正向标准** (每项 +1 分，总计最多 +1 分)：
1. **知识探索** (`knowledge`) - 询问物种、生态系统、可持续性相关问题
2. **同理心** (`empathy`) - 表达温暖、关怀或情感连接
3. **保护行动** (`conservation_action`) - 承诺环保行为
4. **个人参与** (`personal_engagement`) - 分享个人经历或表达热情
5. **深度互动** (`deep_interaction`) - 提出深思熟虑的后续问题

**负向标准** (每项 -1 分，总计最多 -1 分)：
1. **有害意图** (`harmful_intent`) - 表达伤害动物或破坏环境的意图
2. **不尊重** (`disrespect`) - 表现出不尊重或恶意

#### 评分机制
- 使用 OpenAI API 对用户输入进行语义分析
- 分数范围：0-6 分
- 每次对话后实时更新
- 评估结果存储到 `session_state.last_analysis`

### 3. 贴纸奖励系统 (Sticker Rewards)

#### 四种贴纸

| 贴纸 | 触发问题 | 语义关键词 | 图片 |
|------|---------|-----------|------|
| 🏡 家园探索者 | "你住在哪里？" | home, live, nest, habitat | `stickers/home.png` |
| 🌙 日常生活侦探 | "你白天和晚上做什么？" | daily, routine, day, night | `stickers/routine.png` |
| 🍽️ 食物发现者 | "你吃什么？怎么捕食？" | eat, food, diet, prey, hunt | `stickers/food.png` |
| 🌱 物种支持者 | "我能帮你什么？" | help, support, conservation | `stickers/helper.png` |

#### 匹配算法
采用三层匹配策略：
1. **精确匹配**：问题文本完全相同
2. **语义匹配**：使用 OpenAI API 判断语义相似度
3. **关键词匹配**：至少匹配 2 个关键词

### 4. 礼物系统 (Gift System)

- **触发条件**：亲密度达到满分 (6 分)
- **礼物内容**："生物多样性开拓者奖章" (Biodiversity Trailblazer Medal)
- **展示方式**：弹窗对话框 (`st.dialog`)
- **状态控制**：
  - `gift_given` - 是否已授予礼物
  - `gift_shown` - 是否已显示礼物（避免重复展示）

### 5. 语音合成系统 (Text-to-Speech)

#### 音频处理流程
```python
gTTS 生成基础音频 → pydub 加速 1.3 倍 → Base64 编码 → HTML5 Audio 自动播放
```

#### 关键特性
- 每次生成唯一音频 ID（UUID）
- 临时文件自动清理（5 秒后删除旧文件）
- 加载指示器显示生成进度
- 自动播放失败时重试机制

### 6. 数据持久化 (Data Persistence)

#### Supabase 数据表结构
```sql
interactions (
  id                 BIGINT PRIMARY KEY,
  session_id         UUID NOT NULL,
  timestamp          TIMESTAMPTZ DEFAULT NOW(),
  user_msg           TEXT NOT NULL,
  ai_msg             TEXT NOT NULL,
  ai_name            TEXT NOT NULL,
  intimacy_score     NUMERIC,
  sticker_awarded    TEXT,
  gift_given         BOOLEAN DEFAULT FALSE,
  response_analysis  JSONB
)
```

#### 记录内容
- 会话 ID（每次新对话生成新 UUID）
- 用户消息和 AI 回复
- 实时亲密度分数
- 奖励的贴纸类型
- 是否赠送礼物
- 评分详细分析（JSON 格式）

#### 去重机制
- 使用 MD5 哈希防止重复记录同一对话
- 哈希键：`MD5(user_msg|ai_msg)`

---

## 🎨 UI/UX 设计

### 布局结构
- **双栏布局** (75% : 25%)
  - 左侧：对话区域
  - 右侧：亲密度显示 + 贴纸展示 + 事实核查

### 视觉风格
- **主题色**：
  - 背景：`#cdd5ae` (浅绿色)
  - 助手消息气泡：`#345e42` (深绿色)
  - 用户消息气泡：`#efe7e2` (浅灰色)
  - 强调色：`#a1b065` (橄榄绿)

- **交互元素**：
  - 聊天气泡圆角设计
  - 爱心图标显示亲密度 (❤️/🤍)
  - 加载动画（旋转 spinner）

### 功能按钮
1. **Tips 按钮** - 显示亲密度评分指南
2. **新对话按钮** - 重置所有状态

### 事实核查区域
- 可折叠面板展示知识库来源
- 显示用于生成回复的最相关文档片段

---

## 🚀 安装与运行

### 前置要求
- Python 3.8+
- OpenAI API Key
- Supabase 账户和项目

### 安装步骤

```bash
# 1. 克隆项目
git clone <repository-url>
cd zinos-chat

# 2. 安装系统依赖
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# 下载 ffmpeg 并添加到 PATH

# 3. 安装 Python 依赖
pip install -r requirements.txt

# 4. 配置环境变量
# 方式1：导出环境变量
export OPENAI_API_KEY='sk-...'

# 方式2：在 .streamlit/secrets.toml 中配置
# OPENAI_API_KEY = "sk-..."
```

### 配置 Supabase

1. 在 Supabase 项目中执行 `create_table_interactions.sql`
2. 在 `.streamlit/secrets.toml` 中添加 Supabase 连接信息：
```toml
[connections.supabase]
url = "https://your-project.supabase.co"
key = "your-anon-key"
```

### 运行应用

```bash
streamlit run main.py
```

应用将在 `http://localhost:8501` 启动

---

## 📊 数据流程图

```
┌─────────────────┐
│   用户输入问题   │
└────────┬────────┘
         │
         v
┌─────────────────────────────┐
│  ChromaDB 向量检索 (MMR)     │
│  获取最相关知识片段 (k=2)    │
└────────┬────────────────────┘
         │
         v
┌─────────────────────────────┐
│  构建提示词 (Prompt)         │
│  + 角色设定                  │
│  + 检索到的知识              │
│  + 用户问题                  │
└────────┬────────────────────┘
         │
         v
┌─────────────────────────────┐
│  OpenAI API 生成回复         │
│  (temperature=0)             │
└────────┬────────────────────┘
         │
         ├──────────────────────────┐
         │                          │
         v                          v
┌─────────────────┐      ┌──────────────────┐
│  语音合成 (TTS)  │      │  亲密度评分分析   │
│  gTTS + pydub   │      │  (OpenAI API)    │
└────────┬────────┘      └────────┬─────────┘
         │                        │
         v                        v
┌─────────────────┐      ┌──────────────────┐
│  显示文本回复    │      │  更新分数 (0-6)   │
│  + 播放音频     │      │  检查贴纸奖励     │
└────────┬────────┘      └────────┬─────────┘
         │                        │
         └───────┬────────────────┘
                 │
                 v
        ┌─────────────────┐
        │  记录到 Supabase │
        │  + 去重机制      │
        └─────────────────┘
```

---

## 🔐 安全性考虑

### API 密钥管理
- 使用 Streamlit Secrets 管理敏感信息
- 不在代码中硬编码 API 密钥
- `.gitignore` 应包含 `.streamlit/secrets.toml`

### 数据隐私
- 会话 ID 使用 UUID 匿名化
- 用户消息存储在 Supabase（需确保符合 GDPR 等法规）

### 输入验证
- 当前未实现严格的输入过滤（可改进点）
- 建议添加：
  - 输入长度限制
  - 恶意内容检测
  - 速率限制

---

## 🐛 已知问题与限制

### 当前限制
1. **语音识别功能未启用**
   - 代码导入了 `speech_recognition` 但未使用
   - 仅支持文本输入

2. **向量数据库固定**
   - `db5/` 目录包含预构建的知识库
   - 未提供添加新文档的界面

3. **单一角色**
   - 虽然代码结构支持多角色，但只实现了 "Zino's Petrel"
   - `role_configs` 字典可扩展

4. **音频播放兼容性**
   - HTML5 Audio 自动播放可能在某些浏览器受限
   - 实现了重试机制但不保证 100% 成功

5. **临时文件清理**
   - 音频文件仅在 5 秒后清理
   - 长时间运行可能累积临时文件

### 潜在改进
- 添加多语言支持
- 实现语音输入功能
- 增加更多互动元素（如小游戏）
- 优化移动端体验
- 添加数据分析仪表板

---

## 📈 使用场景

### 教育机构
- 自然历史博物馆互动展览
- 学校环境教育课程
- 生物多样性工作坊

### 研究应用
- 公众科学传播效果研究
- 游戏化学习机制验证
- 对话 AI 教育应用测试

### 个人学习
- 生物学爱好者自学工具
- 儿童环保意识启蒙
- 濒危物种知识普及

---

## 👥 目标用户

### 主要受众
- **年龄**：8-18 岁学生（也适合成年人）
- **场景**：参观 Funchal 自然历史博物馆的访客
- **目标**：
  - 了解齐诺海燕的生活习性
  - 学习生物多样性保护知识
  - 培养环保意识

### 设计理念
- 拟人化的鸟类角色降低学习门槛
- 游戏化机制提升参与度
- 第一人称叙事增强沉浸感

---

## 🛠️ 技术亮点

### 1. 检索增强生成 (RAG)
- 结合向量数据库和 LLM
- 确保回复基于权威知识而非幻觉
- 提供事实核查功能增强可信度

### 2. 智能语义匹配
- 不依赖精确关键词
- 使用 LLM 理解问题意图
- 灵活的贴纸触发机制

### 3. 实时情感分析
- 分析用户态度（正向/负向）
- 多维度评估（知识、同理心、行动等）
- 动态调整亲密度分数

### 4. 无缝音频体验
- 自动语音合成
- 音速调节（1.3 倍速）使声音更活泼
- 加载状态可视化

### 5. 状态管理
- 利用 Streamlit Session State
- 持久化对话历史
- 防止重复记录

---

## 📚 代码架构分析

### 核心函数

#### 1. `main()`
- 应用程序入口
- 初始化所有 session state
- 管理 UI 布局和交互流程

#### 2. `update_intimacy_score(response_text)`
- 使用 OpenAI 分析用户输入
- 应用正向/负向评分标准
- 更新亲密度分数（0-6）

#### 3. `get_conversational_chain(role)`
- 加载 QA 链
- 配置提示词模板
- 返回 LangChain 对象

#### 4. `speak_text(text, loading_placeholder)`
- gTTS 生成语音
- pydub 调整播放速度
- Base64 编码并嵌入 HTML

#### 5. `semantic_match(user_input, question_key, reward_details)`
- 语义相似度判断
- 用于贴纸奖励触发
- 返回 yes/no 布尔值

#### 6. `log_interaction(...)`
- 记录对话到 Supabase
- 包含所有关键元数据
- 异常处理保证鲁棒性

### 设计模式

#### 单例模式
- ChromaDB 向量数据库复用
- OpenAI API 客户端共享

#### 策略模式
- 可配置的角色配置 (`role_configs`)
- 支持扩展多个 AI 角色

#### 观察者模式
- Session State 变化触发 UI 更新
- 亲密度分数变化检查礼物触发

---

## 🧪 测试建议

### 功能测试
- [ ] 对话流程完整性
- [ ] 贴纸触发准确性
- [ ] 礼物系统正确性
- [ ] 音频播放成功率
- [ ] 数据库记录完整性

### 性能测试
- [ ] 响应时间（目标 < 3 秒）
- [ ] 并发用户支持
- [ ] 向量检索效率
- [ ] 音频生成速度

### 兼容性测试
- [ ] Chrome/Firefox/Safari
- [ ] 桌面/平板/手机
- [ ] 不同网络环境

---

## 📝 维护指南

### 日常维护
1. **监控 API 使用量**
   - OpenAI API 调用次数
   - Supabase 存储空间

2. **清理临时文件**
   - 定期检查 `output_*.mp3` 文件
   - 考虑添加定时清理脚本

3. **更新知识库**
   - 添加新的 PDF 文档到向量数据库
   - 使用 `load_and_split()` 处理

### 升级路径
- LangChain 版本更新时注意 API 变化
- Streamlit 升级可能影响 UI 组件
- OpenAI 模型升级时测试回复质量

---

## 🤝 贡献指南

### 添加新角色
1. 在 `role_configs` 中添加新配置
2. 准备角色头像图片
3. 构建专属向量数据库
4. 编写角色提示词

### 添加新贴纸
1. 设计贴纸图片（PNG 格式）
2. 保存到 `stickers/` 目录
3. 在 `sticker_rewards` 中添加配置
4. 定义触发问题和关键词

### 扩展功能
- 多语言支持：集成 i18n 库
- 语音输入：激活 SpeechRecognition 模块
- 数据可视化：添加分析仪表板

---

## 📄 许可证

（请根据实际情况添加许可证信息）

---

## 📞 联系方式

（请根据实际情况添加联系方式）

---

## 🙏 致谢

- **LangChain** - 强大的 LLM 应用框架
- **Streamlit** - 简洁的 Web 应用开发工具
- **OpenAI** - 先进的语言模型服务
- **Madeira 自然历史博物馆** - 项目背景支持

---

## 📚 参考资源

### 技术文档
- [LangChain Documentation](https://python.langchain.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [ChromaDB Documentation](https://docs.trychroma.com/)

### 生态知识
- [Zino's Petrel Conservation](https://www.madeirabirdwatching.com/zinos-petrel)
- [Madeira Biodiversity](https://www.visitmadeira.com/en-gb/explore/nature)

---

**文档版本**: 1.0  
**最后更新**: 2025-10-06  
**适用代码版本**: Current (main.py 953 lines)


