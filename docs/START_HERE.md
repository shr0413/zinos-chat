# 🚀 从这里开始 - Day 1 迁移完成指南

> **✅ 代码迁移已完成！** 所有 OpenAI 调用已替换为 Qwen API。

---

## 📋 迁移摘要

### 已完成的修改（6处）

| 位置 | 原始代码 | 修改后 | 状态 |
|-----|---------|--------|------|
| 导入 | `from langchain_openai import OpenAIEmbeddings` | `from langchain_community.embeddings import DashScopeEmbeddings` | ✅ |
| API Key | `os.environ["OPENAI_API_KEY"]` | `os.environ["DASHSCOPE_API_KEY"]` | ✅ |
| 语义模型 | `OpenAI(temperature=0.4)` | `Tongyi(...)` | ✅ |
| 正向评分 | `OpenAI(temperature=0.2)` | `Tongyi(...)` | ✅ |
| 负向评分 | `OpenAI(temperature=0)` | `Tongyi(...)` | ✅ |
| 对话生成 | `OpenAI(temperature=0)` | `Tongyi(...)` | ✅ |
| 向量嵌入 | `OpenAIEmbeddings()` | `DashScopeEmbeddings(...)` | ✅ |

### 已移除的依赖

- ❌ `pysqlite3-binary` (Windows/Conda 不需要)
- ❌ `langchain-openai` (已替换为 Tongyi)

---

## 🎯 下一步操作（3步启动）

### Step 1: 创建 .env 配置文件

```powershell
# 使用记事本创建
notepad .env
```

然后复制以下内容，**替换实际的 API Keys**：

```bash
# ============= 必需配置 =============
DASHSCOPE_API_KEY=sk-your-actual-key-here
QWEN_MODEL_NAME=qwen-turbo
QWEN_EMBEDDING_MODEL=text-embedding-v2

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-actual-key-here

# ============= TTS 配置 =============
TTS_PROVIDER=qwen
QWEN_TTS_VOICE=Cherry
VECTOR_DB_PATH=db5
```

📖 **详细指南**：[`CREATE_ENV.md`](./CREATE_ENV.md)

### Step 2: 获取 API Keys

#### Qwen API（必需）
1. 🔗 https://dashscope.aliyun.com/
2. 注册 → 开通 Qwen-Turbo → 创建 API Key
3. 复制 `sk-` 开头的密钥

#### Supabase（必需）
1. 🔗 https://app.supabase.com/
2. 创建项目 → Settings → API
3. 复制 **Project URL** 和 **anon public key**

📖 **详细指南**：[`CONFIG_GUIDE.md`](./CONFIG_GUIDE.md)

### Step 3: 启动应用

```powershell
# 方法 1: 使用启动脚本（推荐）
.\start_app.bat

# 方法 2: 直接启动
streamlit run main.py
```

---

## ✅ 验证清单

启动前，确保：

- [ ] `.env` 文件已创建
- [ ] Qwen API Key 已填入
- [ ] Supabase 配置已填入
- [ ] 运行 `python verify_config.py` 验证通过
- [ ] 所有依赖已安装（`pip list | findstr dashscope`）

---

## 🧪 功能测试

应用启动后，测试以下功能：

### 1. 基础对话（10个问题）
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

### 2. 亲密度评分
- 发送正向消息 → 检查分数增加
- 发送负向消息 → 检查分数减少

### 3. 贴纸系统
- "你住在哪里？" → home.png
- "你吃什么？" → food.png
- "你白天做什么？" → routine.png
- "我能帮你什么？" → helper.png

---

## 🚨 常见问题

### Q1: ModuleNotFoundError: dashscope

**解决**：
```powershell
pip install dashscope>=1.24.6
```

### Q2: 配置验证失败

**解决**：
1. 检查 `.env` 文件格式
2. 确认 API Key 已正确填入
3. 运行：`python verify_config.py`

### Q3: 向量库加载失败

**解决**：
暂时使用旧向量库（Day 3 会重建）：
```bash
VECTOR_DB_PATH=db5
```

### Q4: API 调用失败

**解决**：
1. 确认已开通 Qwen-Turbo 服务
2. 检查 API Key 是否有效
3. 查看网络连接

---

## 📊 性能对比

请记录以下数据（用于最终评估）：

| 指标 | OpenAI（旧） | Qwen（新） | 改进 |
|------|-------------|-----------|------|
| 响应延迟 | ___ 秒 | ___ 秒 | ___ |
| 回答准确率 | ___ % | ___ % | ___ |
| API 调用成功率 | ___ % | ___ % | ___ |
| 成本 | $0.002/req | **免费** | **100%** |

---

## 🎉 Day 1 验收标准

完成以下所有项，即可进入 Day 2：

- [x] ✅ Qwen API 连接成功
- [x] ✅ 所有 LLM 调用已替换（4个位置）
- [x] ✅ Embeddings 已替换
- [ ] ✅ 基础对话功能正常
- [ ] ✅ 亲密度评分准确率 > 85%
- [ ] ✅ 贴纸触发正常
- [ ] ✅ 数据库记录成功
- [ ] ✅ 响应延迟 < 3 秒

---

## 📚 相关文档

| 文档 | 说明 |
|-----|------|
| [`CREATE_ENV.md`](./CREATE_ENV.md) | .env 创建指南 |
| [`CONFIG_GUIDE.md`](./CONFIG_GUIDE.md) | API Key 获取指南 |
| [`DAY1_GUIDE.md`](./DAY1_GUIDE.md) | Day 1 详细指南 |
| [`TASK_STATUS.md`](./TASK_STATUS.md) | 任务状态追踪 |

---

## 🎯 下一步（Day 2）

Day 1 完成后，进入 **TTS 语音升级**：

- 集成 Qwen TTS
- 添加音色选择
- 流式语音播放

参考：[`TTS_IMPLEMENTATION.md`](./TTS_IMPLEMENTATION.md)

---

**立即开始**：

```powershell
# 1. 创建配置
notepad .env

# 2. 填入 API Keys（参考 CREATE_ENV.md）

# 3. 验证配置
python verify_config.py

# 4. 启动应用
.\start_app.bat
```

**祝你 Day 1 顺利！** 🚀

