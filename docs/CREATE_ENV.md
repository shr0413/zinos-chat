# 创建 .env 配置文件

## 步骤 1: 创建文件

在项目根目录创建一个名为 `.env` 的文件（注意前面有个点）

```powershell
# 方法 1: 使用记事本
notepad .env

# 方法 2: 使用 VS Code
code .env

# 方法 3: 复制模板
copy config.env.template .env
```

## 步骤 2: 填入以下内容

```bash
# ============= 必需配置 =============

# 1. Qwen API（核心LLM + TTS + Embeddings）
DASHSCOPE_API_KEY=sk-your-dashscope-api-key-here

# 2. Qwen 模型配置
QWEN_MODEL_NAME=qwen-turbo
QWEN_EMBEDDING_MODEL=text-embedding-v2

# 3. Supabase 数据库
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key-here

# ============= TTS 配置 =============
TTS_PROVIDER=qwen
QWEN_TTS_MODEL=qwen3-tts-flash
QWEN_TTS_VOICE=Cherry
QWEN_TTS_LANGUAGE=Chinese
QWEN_TTS_STREAM=true

# ============= RAG 配置 =============
VECTOR_DB_PATH=db5
RAG_MMR_K=4
RAG_MMR_FETCH_K=20
RAG_MMR_LAMBDA=0.5

# ============= 可选配置 =============
# 实时搜索（需求3）
# TAVILY_API_KEY=tvly-your-tavily-api-key-here

# 重排序（需求2高级功能）  
# COHERE_API_KEY=your-cohere-api-key-here

# OpenAI 降级方案（可选）
# OPENAI_API_KEY=sk-your-openai-key-here
```

## 步骤 3: 替换实际的 API Keys

### 获取 Qwen API Key
1. 访问：https://dashscope.aliyun.com/
2. 注册/登录 → 开通 Qwen-Turbo
3. 创建 API Key → 复制 `sk-` 开头的密钥
4. 替换 `DASHSCOPE_API_KEY` 的值

### 获取 Supabase 配置
1. 访问：https://app.supabase.com/
2. 创建项目 → Settings → API
3. 复制 **Project URL** 和 **anon public key**
4. 替换 `SUPABASE_URL` 和 `SUPABASE_KEY` 的值

## 步骤 4: 保存文件

确保：
- 文件名是 `.env`（前面有点）
- 保存在项目根目录（与 main.py 同级）
- 编码是 UTF-8

## 步骤 5: 验证配置

```powershell
python verify_config.py
```

期望输出：
```
✅ 配置验证通过！可以开始使用。
```

## 常见问题

### Q: 找不到 .env 文件？
**A**: Windows 默认隐藏点开头的文件，使用命令行或 VS Code 创建。

### Q: API Key 无效？
**A**: 确保：
1. 已开通对应服务
2. Key 格式正确（Qwen 是 `sk-` 开头）
3. 没有多余的空格或引号

### Q: Supabase 连接失败？
**A**: 检查：
1. URL 是否包含 `https://`
2. Key 是否是 **anon public** key（不是 service role）

