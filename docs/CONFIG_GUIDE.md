# 配置指南

## 📋 快速开始

### 1. 创建配置文件（2分钟）

```bash
# 复制模板
cp config.env.template .env

# 或者手动创建
touch .env
```

### 2. 填充必需配置（10分钟）

编辑 `.env` 文件，填充以下**必需**配置：

```bash
# ============= 必需配置 =============

# 1. Qwen API（核心LLM + TTS）
DASHSCOPE_API_KEY=sk-xxxxx              # 从 https://dashscope.aliyun.com/ 获取

# 2. Qwen TTS 配置（使用同一个 API Key）
TTS_PROVIDER=qwen
QWEN_TTS_MODEL=qwen3-tts-flash
QWEN_TTS_VOICE=Cherry                   # Cherry（女声）或 Ethan（男声）

# 3. Supabase 数据库
SUPABASE_URL=https://xxx.supabase.co    # 从 https://app.supabase.com/ 获取
SUPABASE_KEY=xxxxx
```

### 3. 可选配置（按需）

```bash
# ============= 可选配置 =============

# 实时搜索（需求3）
TAVILY_API_KEY=tvly-xxxxx              # 从 https://tavily.com/ 获取（可选，有 DuckDuckGo 免费替代）

# 重排序（需求2高级功能）
COHERE_API_KEY=xxxxx                   # 从 https://dashboard.cohere.com/ 获取（可选）

# 降级方案
OPENAI_API_KEY=sk-xxxxx                # 保留作为备用（可选）
```

---

## 🔑 API Keys 获取指南

### 1. Qwen（通义千问）API

**获取步骤**：
1. 访问 https://dashscope.aliyun.com/
2. 注册/登录阿里云账号
3. 点击"开通模型服务"
4. 选择 **Qwen-Turbo**（推荐，免费额度100万tokens/月）
5. 进入"API-KEY管理"
6. 创建新 API Key
7. 复制 `sk-` 开头的密钥

**免费额度**：
- Qwen-Turbo: 100万 tokens/月
- Text-Embedding-V2: 100万 tokens/月
- Qwen TTS (qwen3-tts-flash): 包含在 LLM 额度内

---

### 2. Supabase 数据库

**获取步骤**：
1. 访问 https://app.supabase.com/
2. 创建新项目
3. 进入 Project Settings → API
4. 复制 **Project URL** 和 **anon public key**

**免费额度**：
- 500MB 数据库存储
- 2GB 带宽/月
- 50MB 文件存储

---

### 4. Tavily 搜索（可选）

**获取步骤**：
1. 访问 https://tavily.com/
2. 注册账号
3. 进入 Dashboard → API Keys
4. 创建 API Key

**免费额度**：
- 1000 次搜索/月
- 超出后 $0.005/次

**替代方案**：使用 DuckDuckGo（完全免费，无需 API Key）

---

### 5. Cohere Rerank（可选）

**获取步骤**：
1. 访问 https://dashboard.cohere.com/
2. 注册账号
3. 进入 API Keys
4. 创建 Production Key

**免费额度**：
- 1000 次/月
- 超出后 $2/1000次

**替代方案**：使用 FlashRank 开源方案

---

## 📝 配置模板详解

### 核心 LLM 配置

```bash
# 模型选择
QWEN_MODEL_NAME=qwen-turbo
# 可选值：
# - qwen-turbo: 快速，成本低（推荐开发）
# - qwen-plus: 性能更强（推荐生产）
# - qwen-max: 最强能力（高成本）

# 温度参数（控制随机性，0=确定，1=创造）
QWEN_TEMPERATURE_CONVERSATION=0.0    # 对话：要求一致性
QWEN_TEMPERATURE_SCORING_POS=0.2     # 正向评分：略有灵活
QWEN_TEMPERATURE_SCORING_NEG=0.0     # 负向评分：严格判断
QWEN_TEMPERATURE_SEMANTIC=0.4        # 语义匹配：平衡
QWEN_TEMPERATURE_ROUTER=0.0          # 路由判断：确定性
```

### TTS 语音配置（Qwen TTS）

```bash
# TTS 提供商
TTS_PROVIDER=qwen        # 推荐：qwen（自然度高，免费）

# Qwen TTS 配置
QWEN_TTS_MODEL=qwen3-tts-flash
QWEN_TTS_VOICE=Cherry
# 可选值：
# - Cherry: 女声（活泼）✅ 推荐 Maria
# - Ethan: 男声

QWEN_TTS_LANGUAGE=Chinese    # 语言：Chinese/English
QWEN_TTS_STREAM=true         # 流式播放（更快）

# 降级配置
USE_GTTS_FALLBACK=true       # TTS失败时使用gTTS
```

### RAG 检索配置

```bash
# MMR 参数
RAG_MMR_K=4              # 返回文档数
RAG_MMR_FETCH_K=20       # 候选文档数
RAG_MMR_LAMBDA=0.5       # 多样性权重
# lambda=0: 完全多样性
# lambda=0.5: 平衡（推荐）
# lambda=1: 完全相似度

# 历史去重
ENABLE_HISTORY_DEDUP=true
MAX_HISTORY_ROUNDS=10    # 保留历史轮次
```

### 智能体配置

```bash
# 搜索工具
USE_WEB_SEARCH=true
WEB_SEARCH_PROVIDER=duckduckgo
# duckduckgo: 免费
# tavily: 需 API Key，质量更高

# 路由策略
ENABLE_SMART_ROUTING=true
ROUTING_CONFIDENCE_THRESHOLD=0.7
# 0.5: 激进（更多搜索）
# 0.7: 平衡（推荐）
# 0.9: 保守（更少搜索）
```

---

## 🔧 配置验证

### 验证脚本

创建 `verify_config.py`：

```python
from dotenv import load_dotenv
import os

load_dotenv()

def verify_config():
    required = {
        'DASHSCOPE_API_KEY': 'Qwen API（LLM + TTS + Embeddings）',
        'SUPABASE_URL': 'Supabase URL',
        'SUPABASE_KEY': 'Supabase Key',
    }
    
    optional = {
        'TAVILY_API_KEY': 'Tavily 搜索',
        'COHERE_API_KEY': 'Cohere 重排序',
        'OPENAI_API_KEY': 'OpenAI 降级',
    }
    
    print("=" * 50)
    print("配置验证")
    print("=" * 50)
    
    print("\n✅ 必需配置：")
    for key, name in required.items():
        value = os.getenv(key)
        if value and value != f'your-{key.lower().replace("_", "-")}-here':
            print(f"  ✅ {name}: 已配置")
        else:
            print(f"  ❌ {name}: 未配置")
    
    print("\n⭕ 可选配置：")
    for key, name in optional.items():
        value = os.getenv(key)
        if value and value != f'your-{key.lower().replace("_", "-")}-here':
            print(f"  ✅ {name}: 已配置")
        else:
            print(f"  ⚪ {name}: 未配置（使用默认）")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    verify_config()
```

运行验证：
```bash
python verify_config.py
```

---

## 🚨 常见问题

### Q1: API Key 无效
**症状**：`Invalid API Key` 错误

**解决**：
1. 检查 `.env` 中 Key 是否正确复制（无空格）
2. 确认 API 服务已开通
3. 检查免费额度是否用尽

### Q2: 向量库加载失败
**症状**：`Failed to load vector database`

**解决**：
1. 确认 `VECTOR_DB_PATH` 路径存在
2. 检查 Embeddings API Key 是否配置
3. 尝试重建向量库（见 Day 3）

### Q3: TTS 无声音
**症状**：语音播放失败

**解决**：
1. 检查阿里云 TTS 配置
2. 验证 AppKey、Access Key 是否正确
3. 启用 gTTS 降级：`USE_GTTS_FALLBACK=true`

### Q4: 搜索功能不工作
**症状**：实时搜索无结果

**解决**：
1. 如果使用 Tavily，检查 API Key
2. 切换到 DuckDuckGo：`WEB_SEARCH_PROVIDER=duckduckgo`
3. 禁用搜索：`USE_WEB_SEARCH=false`

---

## 📂 配置文件位置

```
zinos-chat/
├── .env                # 实际配置（不提交到Git）
├── env.template        # 配置模板（可提交）
├── .gitignore          # 确保包含 .env
└── config.py           # 配置加载器
```

### 确保 .env 不被提交

检查 `.gitignore`：
```bash
# 应该包含
.env
*.env
.env.*
```

---

## ✅ 配置完成检查清单

### 阶段0（基础迁移）
- [ ] DASHSCOPE_API_KEY
- [ ] QWEN_MODEL_NAME
- [ ] SUPABASE_URL
- [ ] SUPABASE_KEY

### 阶段1（TTS升级 - Qwen TTS）
- [ ] TTS_PROVIDER
- [ ] QWEN_TTS_MODEL
- [ ] QWEN_TTS_VOICE
- [ ] QWEN_TTS_LANGUAGE

### 阶段2（RAG优化）
- [ ] QWEN_EMBEDDING_MODEL
- [ ] RAG_MMR_K
- [ ] RAG_MMR_LAMBDA
- [ ] ENABLE_HISTORY_DEDUP

### 阶段3（智能体）
- [ ] USE_WEB_SEARCH
- [ ] WEB_SEARCH_PROVIDER
- [ ] ENABLE_SMART_ROUTING

---

## 🔄 配置更新流程

1. **开发环境**
   ```bash
   # 编辑 .env
   vim .env
   
   # 验证配置
   python verify_config.py
   
   # 重启应用
   streamlit run main.py
   ```

2. **生产环境**
   ```bash
   # 使用环境变量（推荐）
   export DASHSCOPE_API_KEY=xxx
   export DEPLOYMENT_ENV=production
   
   # 或使用生产配置文件
   cp .env.production .env
   ```

---

## 📞 支持

- 📖 详细计划：`PHASED_PLAN.md`
- 🚀 快速开始：`QUICK_START.md`
- 📋 任务追踪：`QWEN_TASK_TRACKER.md`

**配置问题？**
- 阿里云工单：https://selfservice.console.aliyun.com/ticket
- Supabase 社区：https://github.com/supabase/supabase/discussions

---

**配置完成后，开始阶段0！** 🎯


