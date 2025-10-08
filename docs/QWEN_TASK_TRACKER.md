# Qwen 迁移任务追踪 - 5天冲刺

## 🎯 总体目标

**将所有 OpenAI API 替换为 Qwen API**  
**时间轴**：2025-10-06 → 2025-10-10（5天）  
**进度**：Day 0 - 计划制定完成 ✅

---

## 📋 每日任务清单

### ✅ Day 0：规划阶段（2025-10-06）

- [x] 分析现有 OpenAI API 使用情况
- [x] 调研 Qwen API 能力和限制
- [x] 制定 5 天迁移计划
- [x] 创建任务追踪文档

**产出**：
- ✅ `QWEN_MIGRATION_PLAN.md`（详细计划）
- ✅ `QWEN_TASK_TRACKER.md`（本文档）

---

### 🔄 Day 1：环境准备 + LLM 基础替换（2025-10-07）

**目标**：完成 Qwen 环境配置，替换核心对话模型

#### 上午任务（9:00-12:00）

- [ ] **T1.1 - 注册与配置**（30分钟）
  - [ ] 访问 https://dashscope.aliyun.com/
  - [ ] 注册阿里云账号
  - [ ] 开通 Qwen-Turbo 模型服务
  - [ ] 获取 DashScope API Key
  - [ ] 记录 API Key 到安全位置

- [ ] **T1.2 - 安装依赖**（30分钟）
  ```bash
  pip install dashscope==1.14.0
  pip install langchain-community>=0.2.10
  pip install langchain-alibaba-cloud
  ```
  - [ ] 验证安装成功
  - [ ] 测试 API 连接

- [ ] **T1.3 - 配置环境变量**（20分钟）
  - [ ] 编辑 `.streamlit/secrets.toml`
  - [ ] 添加 `DASHSCOPE_API_KEY = "sk-xxx"`
  - [ ] 验证配置加载成功

- [ ] **T1.4 - 创建测试脚本**（40分钟）
  ```python
  # test_qwen_basic.py
  import dashscope
  from langchain_community.llms import Tongyi
  import streamlit as st
  
  # 测试 1：直接调用
  dashscope.api_key = st.secrets["DASHSCOPE_API_KEY"]
  response = dashscope.Generation.call(
      model='qwen-turbo',
      prompt='介绍一下齐诺海燕'
  )
  print("直接调用:", response.output.text)
  
  # 测试 2：LangChain 集成
  llm = Tongyi(
      model_name="qwen-turbo",
      dashscope_api_key=st.secrets["DASHSCOPE_API_KEY"]
  )
  result = llm("用50字介绍齐诺海燕")
  print("LangChain:", result)
  ```
  - [ ] 运行测试，确保成功

#### 下午任务（14:00-18:00）

- [ ] **T1.5 - 替换对话生成模型**（1.5小时）
  - [ ] 备份 `main.py` 为 `main_openai_backup.py`
  - [ ] 修改第 16 行导入：
    ```python
    # from langchain_community.llms import OpenAI
    from langchain_community.llms import Tongyi
    ```
  - [ ] 修改第 66-68 行配置：
    ```python
    # os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    # semantic_model = OpenAI(temperature=0.4)
    
    os.environ["DASHSCOPE_API_KEY"] = st.secrets["DASHSCOPE_API_KEY"]
    semantic_model = Tongyi(
        model_name="qwen-turbo",
        temperature=0.4,
        dashscope_api_key=st.secrets["DASHSCOPE_API_KEY"]
    )
    ```
  - [ ] 修改第 321 行对话模型：
    ```python
    # model = OpenAI(temperature=0)
    model = Tongyi(
        model_name="qwen-turbo",
        temperature=0,
        dashscope_api_key=st.secrets["DASHSCOPE_API_KEY"]
    )
    ```

- [ ] **T1.6 - 本地测试**（1.5小时）
  - [ ] 启动应用：`streamlit run main.py`
  - [ ] 测试基础对话（10 个问题）
  - [ ] 记录响应时间
  - [ ] 对比回答质量
  - [ ] 修复任何错误

- [ ] **T1.7 - 性能对比**（1小时）
  - [ ] 准备测试问题集（20 个）
  - [ ] 记录 OpenAI 和 Qwen 的回复
  - [ ] 评估质量差异
  - [ ] 调整 temperature 参数优化

**Day 1 产出**：
- ✅ Qwen 环境就绪
- ✅ 基础对话功能迁移完成
- ✅ 测试报告（质量对比）

**验收标准**：
- [ ] Qwen API 调用成功率 100%
- [ ] 对话响应延迟 < 3 秒
- [ ] 回答准确率 ≥ OpenAI 的 90%

---

### 🔄 Day 2：亲密度评分系统迁移（2025-10-08）

**目标**：替换亲密度评分中的 LLM 调用，优化评分准确性

#### 上午任务（9:00-12:00）

- [ ] **T2.1 - 替换正向评分模型**（1小时）
  - [ ] 定位 `main.py` 第 130 行
  - [ ] 修改代码：
    ```python
    # model_positive = OpenAI(temperature=0.2)
    model_positive = Tongyi(
        model_name="qwen-turbo",
        temperature=0.2,
        dashscope_api_key=st.secrets["DASHSCOPE_API_KEY"]
    )
    ```

- [ ] **T2.2 - 替换负向评分模型**（1小时）
  - [ ] 定位 `main.py` 第 131 行
  - [ ] 修改代码：
    ```python
    # model_negative = OpenAI(temperature=0)
    model_negative = Tongyi(
        model_name="qwen-turbo",
        temperature=0,
        dashscope_api_key=st.secrets["DASHSCOPE_API_KEY"]
    )
    ```

- [ ] **T2.3 - 优化中文提示词**（1小时）
  - [ ] 修改 `prompt_positive`（第 116-121 行）：
    ```python
    prompt_positive = f"""
    请分析以下用户回复，判断是否符合这些积极标准：
    {positive_criteria}
    
    用户回复："{response_text}"
    
    对每个标准，明确回答"是"或"否"，并简要说明理由。
    输出格式：
    - knowledge: 是/否 - 理由
    - empathy: 是/否 - 理由
    （以此类推）
    """
    ```
  - [ ] 修改 `prompt_negative`（第 123-128 行）

#### 下午任务（14:00-18:00）

- [ ] **T2.4 - 批量测试评分系统**（2小时）
  - [ ] 创建测试脚本 `test_intimacy_scoring.py`：
    ```python
    test_cases = [
        # 正向案例
        {"input": "你们吃什么？怎么捕食？", "expected_score": +1},
        {"input": "我爱学习关于你的知识！", "expected_score": +1},
        {"input": "我会减少使用塑料！", "expected_score": +1},
        
        # 负向案例
        {"input": "我要去捕猎海鸟", "expected_score": -1},
        {"input": "你真无聊", "expected_score": -1},
        
        # 中性案例
        {"input": "你好", "expected_score": 0},
    ]
    
    for case in test_cases:
        score = test_intimacy_score(case["input"])
        print(f"输入: {case['input']}")
        print(f"预期: {case['expected_score']}, 实际: {score}")
        print("-" * 50)
    ```
  - [ ] 运行测试，记录准确率
  - [ ] 对比 OpenAI 和 Qwen 的评分差异

- [ ] **T2.5 - 参数调优**（1.5小时）
  - [ ] 尝试不同 temperature 值（0, 0.1, 0.2）
  - [ ] 调整提示词以提高准确性
  - [ ] 确定最佳配置

- [ ] **T2.6 - 集成测试**（30分钟）
  - [ ] 在完整应用中测试亲密度系统
  - [ ] 验证分数计算逻辑
  - [ ] 确认礼物触发机制

**Day 2 产出**：
- ✅ 亲密度评分系统迁移完成
- ✅ 评分准确率测试报告
- ✅ 优化后的提示词

**验收标准**：
- [ ] 评分准确率 > 85%
- [ ] 正负向识别无误
- [ ] 礼物触发正常

---

### 🔄 Day 3：语义匹配 + Embeddings 迁移（2025-10-09）

**目标**：替换语义模型和向量嵌入，重建向量库

#### 上午任务（9:00-12:00）

- [ ] **T3.1 - 替换语义匹配模型**（30分钟）
  - [ ] 第 68 行已在 Day 1 完成，验证即可
  - [ ] 测试 `semantic_match` 函数（第 358-375 行）

- [ ] **T3.2 - 测试贴纸触发**（1小时）
  - [ ] 准备测试问题：
    ```
    - "你住在哪里？" → home.png
    - "你白天做什么？" → routine.png
    - "你吃什么食物？" → food.png
    - "我能帮你什么？" → helper.png
    ```
  - [ ] 验证语义匹配准确性
  - [ ] 调整关键词权重

- [ ] **T3.3 - 准备 Embeddings 迁移**（1.5小时）
  - [ ] 安装 DashScope Embeddings：
    ```bash
    # 已包含在 langchain-community 中
    ```
  - [ ] 查找原始 PDF 文档
  - [ ] 备份现有向量库：
    ```bash
    cp -r db5 db5_openai_backup
    ```

#### 下午任务（14:00-18:00）⚠️ **关键任务**

- [ ] **T3.4 - 创建向量库重建脚本**（1小时）
  - [ ] 创建 `rebuild_vectordb_qwen.py`：
    ```python
    import sys
    import os
    sys.modules["sqlite3"] = __import__("pysqlite3")
    
    from langchain_community.embeddings import DashScopeEmbeddings
    from langchain_chroma import Chroma
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.document_loaders import PyPDFLoader
    import streamlit as st
    
    # 配置
    PDF_PATH = "knowledge/zino_petrel.pdf"  # 替换为实际路径
    NEW_DB_PATH = "db5_qwen"
    
    print("📚 开始重建向量数据库...")
    
    # 1. 加载 PDF
    print("1. 加载 PDF 文档...")
    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()
    print(f"   ✅ 加载了 {len(docs)} 页")
    
    # 2. 分割文档
    print("2. 分割文档...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=0
    )
    split_docs = text_splitter.split_documents(docs)
    print(f"   ✅ 分割为 {len(split_docs)} 个文本块")
    
    # 3. 创建 Embeddings
    print("3. 初始化 Qwen Embeddings...")
    embeddings = DashScopeEmbeddings(
        model="text-embedding-v2",
        dashscope_api_key=st.secrets["DASHSCOPE_API_KEY"]
    )
    
    # 4. 创建向量库
    print("4. 生成向量并存储...")
    vectordb = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings,
        persist_directory=NEW_DB_PATH
    )
    
    print(f"\n✅ 向量库重建完成！")
    print(f"   路径: {NEW_DB_PATH}")
    print(f"   文档数: {len(split_docs)}")
    
    # 5. 验证检索
    print("\n5. 验证检索功能...")
    test_query = "齐诺海燕吃什么？"
    results = vectordb.similarity_search(test_query, k=2)
    print(f"   测试问题: {test_query}")
    print(f"   检索结果: {len(results)} 条")
    print(f"   首条内容预览: {results[0].page_content[:100]}...")
    ```

- [ ] **T3.5 - 执行向量库重建**（2小时）⏰
  - [ ] 运行重建脚本
  - [ ] 监控进度（可能需要 30-60 分钟）
  - [ ] 验证新向量库完整性

- [ ] **T3.6 - 更新主应用配置**（1小时）
  - [ ] 修改 `main.py` 第 17 行：
    ```python
    # from langchain_openai import OpenAIEmbeddings
    from langchain_community.embeddings import DashScopeEmbeddings
    ```
  - [ ] 修改第 762 行：
    ```python
    vectordb = Chroma(
        embedding_function=DashScopeEmbeddings(
            model="text-embedding-v2",
            dashscope_api_key=st.secrets["DASHSCOPE_API_KEY"]
        ),
        persist_directory="db5_qwen"  # 使用新向量库
    )
    ```
  - [ ] 修改 `role_configs` 中的 `persist_directory`：
    ```python
    'persist_directory': 'db5_qwen'
    ```

- [ ] **T3.7 - 检索质量验证**（30分钟）
  - [ ] 测试 20 个常见问题
  - [ ] 对比 OpenAI 和 Qwen 的检索结果
  - [ ] 记录相关性评分

**Day 3 产出**：
- ✅ 新向量库（db5_qwen/）
- ✅ 检索功能正常
- ✅ 质量验证报告

**验收标准**：
- [ ] 向量库重建成功
- [ ] 检索准确率 ≥ 原系统的 90%
- [ ] 贴纸触发机制正常

**⚠️ 风险提示**：
- 向量库重建可能耗时较长
- 如果 PDF 文件缺失，需要先获取或使用现有文档重新提取

---

### 🔄 Day 4：TTS 语音合成升级（2025-10-10）

**目标**：将 gTTS 替换为阿里云自然语音

#### 上午任务（9:00-12:00）

- [ ] **T4.1 - 开通阿里云语音服务**（1小时）
  - [ ] 访问 https://nls.console.aliyun.com/
  - [ ] 开通"智能语音交互"服务
  - [ ] 创建项目获取 AppKey
  - [ ] 获取 Access Token（24小时有效）
  - [ ] 记录凭证到 `secrets.toml`

- [ ] **T4.2 - 安装 TTS SDK**（30分钟）
  ```bash
  pip install alibabacloud-nls-python-sdk
  ```
  - [ ] 测试 SDK 导入

- [ ] **T4.3 - 创建 TTS 测试脚本**（1.5小时）
  ```python
  # test_aliyun_tts.py
  from aliyunsdkcore.client import AcsClient
  from aliyunsdkcore.request import CommonRequest
  import base64
  
  # 配置
  ACCESS_KEY_ID = "your_id"
  ACCESS_KEY_SECRET = "your_secret"
  APPKEY = "your_appkey"
  
  client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, 'cn-shanghai')
  
  request = CommonRequest()
  request.set_method('POST')
  request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
  request.set_version('2019-02-28')
  request.set_action_name('CreateToken')
  
  response = client.do_action_with_exception(request)
  
  # 测试语音合成
  test_text = "Hi! I'm Maria the Zino's Petrel. What would you like to ask me?"
  # ... 合成逻辑
  ```

#### 下午任务（14:00-18:00）

- [ ] **T4.4 - 开发新 TTS 函数**（2.5小时）
  - [ ] 创建 `speak_text_qwen()` 函数
  - [ ] 实现阿里云 TTS 调用
  - [ ] 保持 Base64 + HTML5 播放流程
  - [ ] 添加错误处理和降级逻辑

- [ ] **T4.5 - 替换主应用 TTS**（1小时）
  - [ ] 在 `main.py` 第 776 行替换调用：
    ```python
    # speak_text(answer, loading_placeholder)
    speak_text_qwen(answer, loading_placeholder)
    ```
  - [ ] 保留原 `speak_text()` 作为 fallback

- [ ] **T4.6 - 音质测试**（30分钟）
  - [ ] 准备 10 条测试文本
  - [ ] 生成音频样本
  - [ ] 邀请 3 人盲测评分
  - [ ] 对比 gTTS 和阿里云 TTS

**备选方案**（如果阿里云 TTS 集成困难）：
- [ ] 使用 Edge TTS（微软免费）
  ```bash
  pip install edge-tts
  ```

**Day 4 产出**：
- ✅ 自然语音合成功能
- ✅ 音质提升 60%+
- ✅ 降级方案就绪

**验收标准**：
- [ ] 语音自然度 > 4.0/5
- [ ] 播放流程无卡顿
- [ ] 错误处理完善

---

### 🔄 Day 5：智能体集成 + 全面测试（2025-10-11）

**目标**：实现智能路由和实时搜索，完成整体验收

#### 上午任务（9:00-12:00）

- [ ] **T5.1 - 实现智能路由**（1.5小时）
  - [ ] 创建 `agent_router.py`：
    ```python
    from langchain_community.llms import Tongyi
    
    def should_use_web_search(user_input, api_key):
        """判断是否需要实时搜索"""
        router_llm = Tongyi(
            model_name="qwen-turbo",
            temperature=0,
            dashscope_api_key=api_key
        )
        
        prompt = f"""
        判断以下问题是否需要实时网络搜索来回答？
        
        需要搜索：询问最新数据、当前状态、近期事件
        不需要搜索：询问基础知识、生物习性、栖息地
        
        问题：{user_input}
        
        只回答"需要"或"不需要"
        """
        
        response = router_llm(prompt).strip()
        return "需要" in response
    ```

- [ ] **T5.2 - 集成搜索工具**（1.5小时）
  ```bash
  pip install duckduckgo-search
  ```
  - [ ] 创建 `web_search.py`：
    ```python
    from langchain_community.tools import DuckDuckGoSearchRun
    
    def search_web(query):
        search = DuckDuckGoSearchRun()
        try:
            results = search.run(f"{query} Zino's Petrel conservation")
            return results[:500]
        except:
            return None
    ```

#### 下午任务（14:00-18:00）

- [ ] **T5.3 - 实现结果融合**（2小时）
  - [ ] 修改 `main.py` 查询流程（第 760-780 行）
  - [ ] 集成路由和搜索逻辑
  - [ ] 添加来源标注

- [ ] **T5.4 - UI 改造**（1小时）
  - [ ] 在回复下方添加来源标签
  - [ ] 更新事实核查区域

- [ ] **T5.5 - 全面测试**（3小时）⚠️ **关键**
  
  **功能测试清单**：
  - [ ] 基础对话（10 个问题）
  - [ ] 实时问题（5 个问题）
  - [ ] 亲密度评分（10 条输入）
  - [ ] 贴纸奖励（4 种触发）
  - [ ] 语音播放（5 条回复）
  - [ ] 礼物触发（达到 6 分）
  
  **性能测试**：
  - [ ] 响应延迟（50 次请求平均）
  - [ ] 并发测试（5 用户同时）
  - [ ] 内存占用监控
  
  **质量测试**：
  - [ ] 准备 100 个测试问题
  - [ ] 记录回答准确率
  - [ ] 用户满意度调查（5 人）

**Day 5 产出**：
- ✅ 智能体系统上线
- ✅ 全功能验收通过
- ✅ 测试报告完整

**验收标准**：
- [ ] 所有原有功能正常
- [ ] 智能路由准确率 > 85%
- [ ] 系统稳定运行无崩溃
- [ ] 用户满意度 > 4/5

---

## 📊 总体进度看板

```
Day 1: [██████████░░░░░░░░░░] 0%  环境准备 + LLM 替换
Day 2: [░░░░░░░░░░░░░░░░░░░░] 0%  亲密度评分迁移
Day 3: [░░░░░░░░░░░░░░░░░░░░] 0%  语义 + Embeddings
Day 4: [░░░░░░░░░░░░░░░░░░░░] 0%  TTS 语音升级
Day 5: [░░░░░░░░░░░░░░░░░░░░] 0%  智能体 + 测试
```

**总体完成度**：10%（计划阶段完成）

---

## 🎯 关键里程碑

- [ ] **M1**：Qwen API 首次成功调用（Day 1 上午）
- [ ] **M2**：基础对话功能正常（Day 1 下午）
- [ ] **M3**：亲密度系统迁移完成（Day 2）
- [ ] **M4**：向量库重建成功（Day 3）
- [ ] **M5**：自然语音上线（Day 4）
- [ ] **M6**：全功能验收通过（Day 5）

---

## 💰 成本追踪

| 服务 | 预估用量 | 成本 | 实际成本 |
|------|---------|------|---------|
| Qwen-Turbo | 100K tokens | 免费额度内 | - |
| Text-Embedding | 50K tokens | 免费额度内 | - |
| 阿里云 TTS | 10K 字符 | ¥10 | - |
| **总计** | - | **≈ ¥10** | - |

---

## ⚠️ 每日风险监控

### Day 1 风险
- ❌ API 注册失败 → 备用：使用测试 Key
- ❌ 网络连接问题 → 备用：配置代理

### Day 2 风险
- ❌ 评分准确率下降 → 备用：优化提示词或调整参数

### Day 3 风险
- ⚠️ **PDF 文件缺失** → 备用：使用现有向量库迁移工具
- ⚠️ **重建耗时过长** → 备用：异步执行，使用旧库过渡

### Day 4 风险
- ❌ TTS 集成复杂 → 备用：使用 Edge TTS

### Day 5 风险
- ❌ 时间不足 → 备用：智能体功能延后，先完成核心迁移

---

## 📝 每日总结模板

### Day X 总结（日期）

**完成任务**：
- ✅ 任务 1
- ✅ 任务 2

**遇到问题**：
- ❌ 问题 1 - 解决方案：...
- ❌ 问题 2 - 解决方案：...

**明日计划**：
- [ ] 任务 A
- [ ] 任务 B

**关键决策**：
- 决策 1：原因 + 影响

---

## 🚀 立即行动（Day 1 启动检查清单）

在开始 Day 1 之前，确认：
- [ ] 有稳定的网络连接
- [ ] Python 环境版本 ≥ 3.8
- [ ] `main.py` 已备份
- [ ] 已阅读完整迁移计划
- [ ] 分配了 6-8 小时开发时间
- [ ] 准备好调试工具

**准备就绪？开始 Day 1！** 🎯

---

**创建时间**：2025-10-06  
**最后更新**：2025-10-06  
**状态**：✅ 就绪，等待执行


