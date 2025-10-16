# 🧠 上下文记忆功能使用指南

## 📋 功能概述

Zino's Chat 现在支持**智能上下文记忆**，能够记住对话历史并理解代词指代，让对话更加自然流畅。

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| **记忆窗口** | 保留最近 **5 轮对话**（10 条消息） |
| **自动管理** | 使用 LangChain `ConversationBufferWindowMemory` |
| **上下文理解** | 理解代词指代（"它"、"那里"、"它们" 等） |
| **无缝集成** | 与 RAG 检索系统完美结合 |

---

## 🎯 使用示例

### 示例 1：地点上下文理解

```
👤 用户: Where do you live?
🐦 Fred: I live in the mountains of Madeira Island, Portugal...

👤 用户: How high is it there?  ← "it" 自动关联 Madeira
🐦 Fred: My nesting areas are located at elevations between 1,200 and 1,800 meters...

👤 用户: Is it cold at night?  ← "it" 指代栖息地的温度
🐦 Fred: Yes, temperatures can drop significantly at night in the mountains...
```

### 示例 2：主题延续

```
👤 用户: What do you eat?
🐦 Fred: I mainly feed on small fish and squid from the Atlantic Ocean...

👤 用户: How do you catch them?  ← "them" 指代食物
🐦 Fred: I catch my prey by surface seizing and plunge diving...

👤 用户: When do you usually hunt for them?  ← "them" 仍指代食物
🐦 Fred: I primarily hunt at night when my prey comes closer to the surface...
```

### 示例 3：多主题管理

```
👤 用户: Tell me about your breeding season.
🐦 Fred: Our breeding season starts in late April...

👤 用户: Where do you nest?
🐦 Fred: I nest in burrows on steep mountain slopes...

👤 用户: How long does it take?  ← "it" 指代 breeding
🐦 Fred: The entire breeding cycle takes about 4-5 months...
```

---

## 🧪 测试记忆功能

### 方法 1：运行测试脚本

```bash
cd zinos-chat
python test_conversation_memory.py
```

**测试场景：**
- ✅ 地点指代理解
- ✅ 温度上下文延续
- ✅ 食物主题跟踪
- ✅ 代词指代解析
- ✅ 多轮对话连贯性

### 方法 2：在 Streamlit 中手动测试

1. **启动应用**
   ```bash
   streamlit run main.py
   ```

2. **测试对话**
   - 问一个地点问题（如 "Where do you live?"）
   - 紧接着问 "How high is it?" 或 "Is it cold there?"
   - 观察 Fred 是否理解 "it" 指代之前提到的地点

3. **验证记忆**
   - 连续提问 6 个以上问题
   - 第 6 个问题提到第 1 个问题的内容时，检查是否仍记得（理论上会忘记，因为窗口是5轮）

---

## 🔧 技术实现细节

### 架构图

```
用户输入
    ↓
ConversationalRetrievalChain
    ├─→ Retriever (从 ChromaDB 检索文档)
    ├─→ Memory (获取最近5轮对话)
    └─→ LLM (结合文档 + 历史生成回答)
    ↓
    ├─→ answer (回答文本)
    └─→ source_documents (来源文档)
```

### 关键组件

#### 1. Memory 配置

```python
memory = ConversationBufferWindowMemory(
    k=5,                      # 保留最近5轮对话
    memory_key="chat_history", # LangChain 标准 key
    return_messages=True,      # 返回消息对象
    output_key="answer"        # Chain 输出 key
)
```

#### 2. Chain 创建

```python
chain = ConversationalRetrievalChain.from_llm(
    llm=model,
    retriever=retriever,
    memory=memory,
    return_source_documents=True  # 用于 Fact-Check
)
```

#### 3. 调用方式

```python
# 只需传入问题，Memory 会自动注入历史
result = chain.invoke({"question": user_input})

# 返回结果
answer = result["answer"]
source_docs = result["source_documents"]
```

---

## ⚙️ 配置选项

### 调整记忆窗口大小

在 `main.py` 的 `get_conversational_chain()` 函数中修改：

```python
memory = ConversationBufferWindowMemory(
    k=10,  # 改为保留最近 10 轮对话（20 条消息）
    # ... 其他参数
)
```

**注意事项：**
- ⚠️ 窗口越大，token 消耗越多
- ⚠️ 建议范围：3-10 轮
- ⚠️ 超过 10 轮可能导致响应变慢

### 清除记忆

用户点击 **"Clear and Restart"** 按钮时，记忆会自动清空：

```python
st.session_state.conversation_chain = None
st.session_state.conversation_memory = None
```

---

## 📊 性能优化

### Token 消耗

| 对话轮数 | 历史消息数 | 预估 Token (英文) |
|---------|----------|------------------|
| 1 轮    | 2 条     | ~100 tokens      |
| 3 轮    | 6 条     | ~300 tokens      |
| 5 轮    | 10 条    | ~500 tokens      |
| 10 轮   | 20 条    | ~1000 tokens     |

**优化建议：**
- ✅ 使用 `ConversationBufferWindowMemory`（自动丢弃旧对话）
- ✅ 保持窗口大小在 5 轮以内
- ⚠️ 避免使用 `ConversationBufferMemory`（无限保存）

---

## 🐛 故障排除

### 问题 1: AI 没有理解代词

**可能原因：**
- Memory 未正确初始化
- Chain 类型错误（使用了旧的 `load_qa_chain`）

**解决方案：**
```python
# 检查 session_state
print(st.session_state.conversation_memory)  # 应该不是 None

# 检查 Memory 内容
print(memory.chat_memory.messages)
```

### 问题 2: 对话历史丢失

**可能原因：**
- Session 被重置
- 用户点击了 "Clear and Restart"

**解决方案：**
- 不要在代码中意外清空 `conversation_chain` 或 `conversation_memory`

### 问题 3: 响应变慢

**可能原因：**
- 记忆窗口过大
- Token 消耗过多

**解决方案：**
```python
# 减小窗口大小
memory = ConversationBufferWindowMemory(k=3)  # 从 5 改为 3
```

---

## 📚 相关文档

- [LangChain Memory 官方文档](https://python.langchain.com/docs/modules/memory/)
- [ConversationalRetrievalChain 文档](https://python.langchain.com/docs/use_cases/question_answering/chat_history)
- [Streamlit Session State 管理](https://docs.streamlit.io/library/api-reference/session-state)

---

## 🎓 最佳实践

### ✅ 推荐做法

1. **保持窗口适中**: 5 轮对话足以支持大部分场景
2. **定期清理**: 提醒用户使用 "Clear" 按钮重置对话
3. **监控性能**: 注意 token 消耗和响应时间
4. **测试边界**: 测试第 6 轮是否正确忘记第 1 轮

### ❌ 避免的做法

1. **无限保存历史**: 不要使用 `ConversationBufferMemory`
2. **手动拼接历史**: 让 Memory 自动管理
3. **频繁重建 Chain**: 重用 `session_state.conversation_chain`

---

## 🌟 实际效果

### 用户体验提升

- ✅ **自然对话**: 不需要重复上下文
- ✅ **减少输入**: "它在哪里？" 而不是 "Madeira 在哪里？"
- ✅ **连贯性**: 主题切换更流畅
- ✅ **智能感**: AI 显得更"聪明"

### 示例对比

**❌ 没有记忆：**
```
👤: Where do you live?
🐦: I live in Madeira...

👤: Is it cold?
🐦: ❓ What do you mean by "it"? Could you clarify?
```

**✅ 有记忆：**
```
👤: Where do you live?
🐦: I live in Madeira...

👤: Is it cold?
🐦: Yes, my habitat in the Madeira mountains can be quite cold at night...
```

---

## 🚀 未来优化方向

### 阶段 2: 智能摘要（可选）

当对话超过 10 轮时，使用 LLM 生成对话摘要：

```python
from langchain.memory import ConversationSummaryBufferMemory

memory = ConversationSummaryBufferMemory(
    llm=model,
    max_token_limit=500,  # 摘要 token 限制
    memory_key="chat_history",
    return_messages=True
)
```

**优点：**
- 保留更多历史信息
- Token 消耗可控

**缺点：**
- 实现复杂度增加
- 需要额外 LLM 调用

### 阶段 3: 长期记忆（可选）

将重要对话存入 Supabase 或向量数据库：

```python
# 伪代码
if is_important_info(question, answer):
    save_to_longterm_memory(question, answer)
```

---

**✅ 上下文记忆功能已全面集成！开始体验更自然的对话吧！** 🎉

