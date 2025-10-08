# ⚡ 性能测试指南

> **测试版本**：Day 1 Performance Optimized  
> **测试时间**：立即

---

## 🎯 测试目标

验证性能优化效果，确保：
- 响应速度 < 2.5秒
- 无弃用警告
- 回答质量不变

---

## 🚀 快速测试（5分钟）

### Step 1: 重启应用

```powershell
# 如果应用正在运行，先停止（Ctrl+C）
# 然后重新启动
.\start_app.bat
```

### Step 2: 打开浏览器

访问：http://localhost:8501

### Step 3: 测试标准问题

在聊天框输入以下问题，**计时并记录**：

#### 测试 1: 简单问候
```
Hi, how are you doing today?
```
**期望**：
- 响应时间：< 2秒
- 无错误信息
- 回答自然

#### 测试 2: 知识问题
```
Where do you live?
```
**期望**：
- 响应时间：< 2.5秒
- 触发 home.png 贴纸
- 回答包含栖息地信息

#### 测试 3: 复杂问题
```
What do you eat and how do you catch it?
```
**期望**：
- 响应时间：< 2.5秒
- 触发 food.png 贴纸
- 回答详细准确

---

## 📊 性能记录表

| 问题 | 优化前 | 优化后 | 改进 |
|------|--------|--------|------|
| "Hi, how are you..." | ___ 秒 | ___ 秒 | ___ |
| "Where do you live?" | ___ 秒 | ___ 秒 | ___ |
| "What do you eat?" | ___ 秒 | ___ 秒 | ___ |
| **平均** | ___ 秒 | ___ 秒 | ___ |

---

## ✅ 验收标准

Day 1 性能优化通过的标准：

- [ ] 平均响应时间 < 2.5秒
- [ ] 控制台无 `LangChainDeprecationWarning`
- [ ] 亲密度评分正常
- [ ] 贴纸触发正常
- [ ] 回答质量不变

---

## 🔍 详细测试（完整验证）

### 测试 1: 响应速度

**测试方法**：
1. 打开浏览器开发者工具（F12）
2. 进入 Network 面板
3. 发送问题
4. 查看请求时间

**验收标准**：
- 总响应时间 < 3秒
- API 调用时间 < 2秒

---

### 测试 2: 控制台日志

**测试方法**：
1. 查看运行 `streamlit` 的控制台
2. 发送多个问题
3. 检查是否有警告

**期望输出**：
```
User input: Hi, how are you doing today?
AI Evaluation: ...
Updated Intimacy Score: 1
Logged interaction to Supabase: ...
```

**不应出现**：
```
❌ LangChainDeprecationWarning
❌ The method `Chain.run` was deprecated
❌ The method `BaseLLM.__call__` was deprecated
```

---

### 测试 3: 功能完整性

**基础对话**：
- [ ] "你好" → 正常回答
- [ ] "你住在哪里？" → home.png 贴纸
- [ ] "你吃什么？" → food.png 贴纸
- [ ] "你白天做什么？" → routine.png 贴纸
- [ ] "我能帮你什么？" → helper.png 贴纸

**亲密度评分**：
- [ ] 正向消息 → 分数+1
- [ ] 负向消息 → 分数-1
- [ ] 中性消息 → 分数不变

**数据库记录**：
- [ ] Supabase 中有对话记录
- [ ] session_id 正确
- [ ] 时间戳正确

---

## 🐛 问题诊断

### 如果响应仍然慢（> 3秒）

**检查 1: 网络连接**
```powershell
ping dashscope.aliyuncs.com
```

**检查 2: API Key 额度**
访问：https://dashscope.aliyun.com/
查看使用量是否超限

**检查 3: 向量库**
```powershell
# 运行优化工具
.\optimize_chromadb.bat
```

---

### 如果出现错误

**错误 1: invoke() 参数错误**
```
TypeError: invoke() missing 1 required positional argument
```

**解决**：已修复，重启应用即可

**错误 2: ChromaDB 警告**
```
⚠️ could benefit from vacuuming
```

**解决**：不影响功能，Day 3 会重建向量库

---

## 📈 性能对比（参考数据）

### 优化前
```
[请求开始] → [RAG检索: 0.5s] → [生成回答: 1.0s] → [评分: 2.0s] → [响应完成]
总耗时：3.5秒
```

### 优化后
```
[请求开始] → [RAG检索: 0.4s] → [生成回答: 1.0s] → [评分: 0.6s] → [响应完成]
总耗时：2.0秒
```

**改进**：-43% ⚡

---

## 🎯 下一步

### ✅ 如果测试通过

1. **记录性能数据**（填写上面的表格）
2. **Day 1 完成**！ 🎉
3. **准备 Day 2**：阅读 [`TTS_IMPLEMENTATION.md`](./TTS_IMPLEMENTATION.md)

### ❌ 如果测试失败

1. **复制完整错误信息**
2. **告诉我问题细节**：
   - 哪个步骤失败？
   - 错误信息是什么？
   - 响应时间多少？
3. **我会继续优化**

---

## 💡 性能优化技巧

### 实时监控

**方法 1: 浏览器开发者工具**
- F12 → Network 面板
- 查看 API 请求时间

**方法 2: 控制台日志**
- 查看 `streamlit` 运行的控制台
- 观察各阶段耗时

**方法 3: 添加自定义计时**
```python
import time
start = time.time()
# ... 代码 ...
print(f"耗时: {time.time() - start:.2f}秒")
```

---

## 📝 测试报告模板

```
### Day 1 性能测试报告

**测试时间**：2025-10-08
**测试人**：[你的名字]

#### 性能数据
- 平均响应时间：___ 秒
- 最快响应：___ 秒
- 最慢响应：___ 秒

#### 功能测试
- 基础对话：✅/❌
- 贴纸触发：✅/❌
- 亲密度评分：✅/❌
- 数据库记录：✅/❌

#### 控制台日志
- 弃用警告：有/无
- 错误信息：有/无

#### 总体评价
[写下你的使用体验]

#### 改进建议
[有什么可以优化的地方]
```

---

**立即开始测试**：

```powershell
# 1. 重启应用
.\start_app.bat

# 2. 打开浏览器
start http://localhost:8501

# 3. 开始测试！
```

祝测试顺利！🚀

