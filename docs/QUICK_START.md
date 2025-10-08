# Qwen 迁移快速开始指南

## 🎯 5天冲刺目标

**将所有 OpenAI API 替换为 Qwen API**

---

## 📅 每日一图速览

```
Day 1: 注册Qwen → 替换对话LLM → 测试 ✅
Day 2: 替换评分LLM → 优化提示词 → 测试 ✅
Day 3: 替换Embeddings → 重建向量库 → 验证 ✅
Day 4: 集成阿里云TTS → 测试语音质量 ✅
Day 5: 智能路由 + 实时搜索 → 全面测试 ✅
```

---

## ⚡ Day 1 快速启动（今天就做）

### 1️⃣ 注册阿里云（15分钟）

```bash
# 访问
https://dashscope.aliyun.com/

# 步骤
1. 注册账号
2. 开通"模型服务"
3. 选择 Qwen-Turbo（免费额度100万tokens/月）
4. 复制 API Key（sk-开头）
```

### 2️⃣ 安装依赖（5分钟）

```bash
pip install dashscope langchain-community
```

### 3️⃣ 配置密钥（5分钟）

编辑 `.streamlit/secrets.toml`：
```toml
DASHSCOPE_API_KEY = "sk-你的密钥"
```

### 4️⃣ 测试连接（5分钟）

创建 `test.py`：
```python
import dashscope

dashscope.api_key = "sk-你的密钥"
response = dashscope.Generation.call(
    model='qwen-turbo',
    prompt='你好'
)
print(response.output.text)
```

运行：
```bash
python test.py
```

看到回复 → ✅ 环境就绪！

### 5️⃣ 替换核心代码（30分钟）

**修改 `main.py`**：

```python
# 第 16 行：修改导入
# from langchain_community.llms import OpenAI
from langchain_community.llms import Tongyi

# 第 66-68 行：配置API
os.environ["DASHSCOPE_API_KEY"] = st.secrets["DASHSCOPE_API_KEY"]
semantic_model = Tongyi(
    model_name="qwen-turbo",
    temperature=0.4,
    dashscope_api_key=st.secrets["DASHSCOPE_API_KEY"]
)

# 第 321 行：对话模型
model = Tongyi(
    model_name="qwen-turbo",
    temperature=0,
    dashscope_api_key=st.secrets["DASHSCOPE_API_KEY"]
)
```

### 6️⃣ 启动测试（5分钟）

```bash
streamlit run main.py
```

测试对话 → ✅ Day 1 完成！

---

## 📋 核心替换清单

### 需要替换的6个位置

| # | 位置 | 原代码 | 新代码 | 完成日 |
|---|------|--------|--------|--------|
| 1 | 16行 | `OpenAI` | `Tongyi` | Day 1 |
| 2 | 68行 | 语义模型 | `Tongyi(0.4)` | Day 1 |
| 3 | 130行 | 正向评分 | `Tongyi(0.2)` | Day 2 |
| 4 | 131行 | 负向评分 | `Tongyi(0)` | Day 2 |
| 5 | 321行 | 对话模型 | `Tongyi(0)` | Day 1 |
| 6 | 762行 | Embeddings | `DashScopeEmbeddings()` | Day 3 |

---

## 🔑 必需的API密钥

```toml
# .streamlit/secrets.toml

# Day 1-3 需要
DASHSCOPE_API_KEY = "sk-xxx"  # Qwen LLM + Embeddings

# Day 4 需要（可选）
ALIYUN_NLS_APPKEY = "xxx"      # 阿里云TTS
ALIYUN_NLS_TOKEN = "xxx"       

# 保持不变
[connections.supabase]
url = "https://xxx.supabase.co"
key = "xxx"
```

---

## ⚠️ 重要提醒

### Day 3 特别注意：

**需要重建向量库！**

原因：Embeddings模型变了，向量维度可能不同

步骤：
1. 备份：`cp -r db5 db5_backup`
2. 准备PDF文档
3. 运行重建脚本（见Day 3任务）
4. 更新配置：`persist_directory='db5_qwen'`

### 降级方案

每天都保留旧代码作为备份：
```python
# 备份文件
main_openai_backup.py
speak_text_original()  # 保留gTTS
```

---

## 📊 进度检查表

- [ ] Day 1: Qwen对话正常 ✅
- [ ] Day 2: 亲密度评分正常 ✅
- [ ] Day 3: 向量检索正常 ✅
- [ ] Day 4: 语音自然流畅 ✅
- [ ] Day 5: 智能体功能完整 ✅

---

## 💡 常见问题

### Q1: API调用失败怎么办？
**A**: 检查：
1. API Key是否正确
2. 是否开通了Qwen-Turbo服务
3. 网络连接是否正常

### Q2: 向量库重建要多久？
**A**: 取决于文档数量
- 100页PDF ≈ 20分钟
- 500页PDF ≈ 1小时

### Q3: 成本会增加吗？
**A**: 不会！Qwen更便宜
- OpenAI: $28/月
- Qwen: $3-5/月
- 节省80%+

### Q4: 效果会变差吗？
**A**: 不会！
- Qwen对中文理解更好
- 响应速度相当
- 自然语音更优

---

## 🚀 立即开始

**现在就执行Day 1的6个步骤！**

30分钟后你就能看到Qwen版的Zino's Chat运行了！

---

**需要帮助？**
- 📖 详细计划：`QWEN_MIGRATION_PLAN.md`
- 📋 每日任务：`QWEN_TASK_TRACKER.md`
- 📞 技术支持：阿里云工单

**祝迁移顺利！** 🎉


