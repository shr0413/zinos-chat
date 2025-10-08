# Day 1: 阶段0 - 基础迁移开始指南

## 🎯 今日目标

完成 OpenAI → Qwen 的基础迁移，确保核心对话功能正常运行。

**预计时间**：5小时  
**难度**：⭐⭐（中等）

---

## ✅ 准备工作（30分钟）

### Step 1: 创建 .env 配置文件

```bash
# 复制模板
cp config.env.template .env
```

### Step 2: 获取 API Keys

#### Qwen API（必需）
1. 访问：https://dashscope.aliyun.com/
2. 注册/登录阿里云账号
3. 点击"开通模型服务" → 选择 **Qwen-Turbo**
4. 进入"API-KEY管理" → 创建新 API Key
5. 复制 `sk-` 开头的密钥

#### Supabase（必需）
1. 访问：https://app.supabase.com/
2. 创建新项目
3. 进入 Project Settings → API
4. 复制 **Project URL** 和 **anon public key**

### Step 3: 填充配置

编辑 `.env` 文件：

```bash
# 必需配置
DASHSCOPE_API_KEY=sk-你的实际密钥
SUPABASE_URL=https://你的项目.supabase.co
SUPABASE_KEY=你的实际密钥

# TTS 配置（使用默认即可）
TTS_PROVIDER=qwen
QWEN_TTS_VOICE=Cherry
QWEN_TTS_LANGUAGE=Chinese
```

### Step 4: 验证配置

```bash
python verify_config.py
```

**期望输出**：
```
✅ 配置验证通过！可以开始使用。
```

---

## 🔧 核心迁移（3小时）

### Step 5: 安装依赖

```bash
# 安装新依赖
pip install dashscope>=1.24.6
pip install langchain-community
pip install python-dotenv
pip install numpy

# 验证安装
python -c "import dashscope; print('✅ DashScope 安装成功')"
```

### Step 6: 备份原文件

```bash
# 备份 main.py
cp main.py main_openai_backup.py

echo "✅ 备份完成"
```

### Step 7: 测试 Qwen 连接

创建测试脚本 `test_qwen.py`：

```python
from config import config
from langchain_community.llms import Tongyi

# 测试 LLM
print("测试 Qwen LLM...")
llm = Tongyi(
    model_name=config.QWEN_MODEL,
    temperature=0,
    dashscope_api_key=config.DASHSCOPE_API_KEY
)

response = llm("你好，请用一句话介绍齐诺海燕")
print(f"✅ LLM 测试成功: {response}")

# 测试 Embeddings
print("\n测试 Qwen Embeddings...")
from langchain_community.embeddings import DashScopeEmbeddings

embeddings = DashScopeEmbeddings(
    model=config.QWEN_EMBEDDING_MODEL,
    dashscope_api_key=config.DASHSCOPE_API_KEY
)

result = embeddings.embed_query("测试文本")
print(f"✅ Embeddings 测试成功: 向量维度 {len(result)}")

print("\n🎉 所有测试通过！")
```

运行测试：
```bash
python test_qwen.py
```

---

## 📝 修改 main.py（1.5小时）

### 修改 1: 导入部分（第 16-17 行）

**修改前**：
```python
from langchain_community.llms import OpenAI
from langchain_openai import OpenAIEmbeddings
```

**修改后**：
```python
from langchain_community.llms import Tongyi
from langchain_community.embeddings import DashScopeEmbeddings
from config import config
```

### 修改 2: API Key 配置（第 66-68 行）

**修改前**：
```python
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

semantic_model = OpenAI(temperature=0.4)
```

**修改后**：
```python
# Qwen API 配置（从 config.py 加载）
os.environ["DASHSCOPE_API_KEY"] = config.DASHSCOPE_API_KEY

semantic_model = Tongyi(
    model_name=config.QWEN_MODEL,
    temperature=config.TEMP_SEMANTIC,
    dashscope_api_key=config.DASHSCOPE_API_KEY
)
```

### 修改 3: 正向评分模型（第 130 行）

**修改前**：
```python
model_positive = OpenAI(temperature=0.2)
```

**修改后**：
```python
model_positive = Tongyi(
    model_name=config.QWEN_MODEL,
    temperature=config.TEMP_SCORING_POS,
    dashscope_api_key=config.DASHSCOPE_API_KEY
)
```

### 修改 4: 负向评分模型（第 131 行）

**修改前**：
```python
model_negative = OpenAI(temperature=0)
```

**修改后**：
```python
model_negative = Tongyi(
    model_name=config.QWEN_MODEL,
    temperature=config.TEMP_SCORING_NEG,
    dashscope_api_key=config.DASHSCOPE_API_KEY
)
```

### 修改 5: 对话生成模型（第 321 行）

**修改前**：
```python
model = OpenAI(temperature=0)
```

**修改后**：
```python
model = Tongyi(
    model_name=config.QWEN_MODEL,
    temperature=config.TEMP_CONVERSATION,
    dashscope_api_key=config.DASHSCOPE_API_KEY
)
```

### 修改 6: 向量嵌入（第 762 行）

**修改前**：
```python
vectordb = Chroma(embedding_function=OpenAIEmbeddings(), persist_directory=get_vectordb(role))
```

**修改后**：
```python
vectordb = Chroma(
    embedding_function=DashScopeEmbeddings(
        model=config.QWEN_EMBEDDING_MODEL,
        dashscope_api_key=config.DASHSCOPE_API_KEY
    ),
    persist_directory=config.VECTOR_DB_PATH
)
```

---

## 🧪 测试验证（1小时）

### Step 8: 启动应用

```bash
streamlit run main.py
```

### Step 9: 功能测试

访问 http://localhost:8501，测试以下功能：

#### 测试清单

- [ ] **基础对话**（10个问题）
  ```
  - 你好
  - 你住在哪里？
  - 你吃什么？
  - 你白天做什么？
  - 我能帮你什么？
  - 你有什么特点？
  - 你喜欢什么？
  - 告诉我关于你的故事
  - 你面临什么威胁？
  - 谢谢你的分享
  ```

- [ ] **亲密度评分**
  - 发送正向消息（如"我爱学习关于你的知识"）
  - 检查分数是否增加
  - 发送负向消息（如"无聊"）
  - 检查分数是否减少

- [ ] **贴纸触发**
  - "你住在哪里？" → 应获得 home.png
  - "你吃什么？" → 应获得 food.png
  - "你白天做什么？" → 应获得 routine.png
  - "我能帮你什么？" → 应获得 helper.png

- [ ] **数据库记录**
  - 检查 Supabase 中的 interactions 表
  - 验证对话是否被记录

### Step 10: 性能对比

记录以下数据：

| 指标 | OpenAI（旧） | Qwen（新） | 改进 |
|------|-------------|-----------|------|
| 响应延迟 | ___ 秒 | ___ 秒 | ___ |
| 回答准确率 | ___ % | ___ % | ___ |
| API 调用成功率 | ___ % | ___ % | ___ |

---

## ✅ 验收标准

Day 1 完成的标准：

- [x] ✅ Qwen API 连接成功
- [x] ✅ 所有 LLM 调用已替换（4个位置）
- [x] ✅ Embeddings 已替换
- [x] ✅ 基础对话功能正常
- [x] ✅ 亲密度评分准确率 > 85%
- [x] ✅ 贴纸触发正常
- [x] ✅ 数据库记录成功
- [x] ✅ 响应延迟 < 3 秒

---

## 🚨 常见问题

### Q1: API Key 无效
**症状**：`Invalid API Key` 错误

**解决**：
```bash
# 1. 检查 .env 配置
cat .env | grep DASHSCOPE_API_KEY

# 2. 验证 Key 格式（应以 sk- 开头）
# 3. 确认已开通 Qwen-Turbo 服务
```

### Q2: 导入错误
**症状**：`No module named 'dashscope'`

**解决**：
```bash
pip install dashscope>=1.24.6
pip list | grep dashscope  # 验证安装
```

### Q3: 向量库加载失败
**症状**：`Failed to load vector database`

**解决**：
```bash
# 暂时使用旧向量库（Day 3 会重建）
# 在 .env 中设置：
VECTOR_DB_PATH=db5
```

### Q4: Streamlit 报错
**症状**：`KeyError: 'OPENAI_API_KEY'`

**解决**：
检查是否还有遗漏的 OpenAI 引用，全局搜索：
```bash
grep -r "OPENAI_API_KEY" main.py
grep -r "OpenAI(" main.py
```

---

## 📊 Day 1 完成检查清单

- [ ] API Keys 已获取并配置
- [ ] 依赖已安装（dashscope, python-dotenv）
- [ ] config.py 已创建
- [ ] verify_config.py 验证通过
- [ ] test_qwen.py 测试通过
- [ ] main.py 已修改（6处）
- [ ] 功能测试完成（10个问题）
- [ ] 性能数据已记录
- [ ] 备份文件已创建

---

## 🎯 下一步

Day 1 完成后，进入 **Day 2: TTS 语音升级**

参考文档：
- [`TTS_IMPLEMENTATION.md`](./TTS_IMPLEMENTATION.md)
- [`QWEN_TASK_TRACKER.md`](./QWEN_TASK_TRACKER.md)

---

## 📞 需要帮助？

- 📖 配置问题：`CONFIG_GUIDE.md`
- 🔧 技术问题：`QWEN_MIGRATION_PLAN.md`
- 📋 任务追踪：`QWEN_TASK_TRACKER.md`

**祝你 Day 1 顺利！** 🚀

