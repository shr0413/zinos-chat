# Qwen API 迁移计划 - 5天完成方案

## 📋 迁移概览

**目标**：将项目中所有 OpenAI API 调用替换为 Qwen（通义千问）API  
**时间**：5 天（2025-10-06 至 2025-10-10）  
**策略**：每天完成一个核心需求  
**风险等级**：中 - Qwen 提供 OpenAI 兼容接口，迁移风险可控

---

## 🎯 迁移范围分析

### 当前 OpenAI API 使用情况

| 位置 | 用途 | 代码行 | 替换方案 |
|------|------|--------|---------|
| **LLM 调用（4处）** | | | |
| `main.py:68` | 语义匹配模型 | `OpenAI(temperature=0.4)` | `Tongyi(temperature=0.4)` |
| `main.py:130` | 正向评分模型 | `OpenAI(temperature=0.2)` | `Tongyi(temperature=0.2)` |
| `main.py:131` | 负向评分模型 | `OpenAI(temperature=0)` | `Tongyi(temperature=0)` |
| `main.py:321` | 对话生成模型 | `OpenAI(temperature=0)` | `Tongyi(temperature=0)` |
| **Embeddings（1处）** | | | |
| `main.py:762` | 向量嵌入 | `OpenAIEmbeddings()` | `DashScopeEmbeddings()` |
| **TTS（计划新增）** | | | |
| `speak_text()` | 语音合成 | gTTS（旧） | 阿里云 CosyVoice |

**总计**：6 处核心替换点

---

## 📅 5天详细计划

### 第1天：环境准备 + LLM 基础替换

**目标**：完成开发环境配置，替换基础 LLM 调用

#### 任务清单

**上午（3小时）**：
- [ ] **任务 1.1**：注册阿里云账号并开通服务
  - 访问：https://dashscope.aliyun.com/
  - 开通模型服务：Qwen-Turbo（免费额度 100万 tokens/月）
  - 获取 API Key（DashScope）
  
- [ ] **任务 1.2**：安装必要依赖
  ```bash
  pip install dashscope langchain-community
  # 或使用 LangChain 官方集成
  pip install langchain-alibaba-cloud
  ```

- [ ] **任务 1.3**：配置环境变量
  - 在 `.streamlit/secrets.toml` 中添加：
  ```toml
  DASHSCOPE_API_KEY = "sk-xxx"  # Qwen API Key
  ```

**下午（4小时）**：
- [ ] **任务 1.4**：替换对话生成模型（main.py:321）
  ```python
  # 修改前
  from langchain_community.llms import OpenAI
  model = OpenAI(temperature=0)
  
  # 修改后
  from langchain_community.llms import Tongyi
  model = Tongyi(
      model_name="qwen-turbo",  # 或 qwen-plus, qwen-max
      temperature=0,
      dashscope_api_key=st.secrets["DASHSCOPE_API_KEY"]
  )
  ```

- [ ] **任务 1.5**：测试对话功能
  - 运行应用，测试基础对话
  - 对比回复质量（OpenAI vs Qwen）
  - 记录响应时间和准确性

**预期成果**：
- ✅ Qwen API 可正常调用
- ✅ 基础对话功能正常
- ✅ 响应延迟 < 3 秒

---

### 第2天：亲密度评分系统迁移

**目标**：替换亲密度评分中的两个 OpenAI 模型调用

#### 任务清单

**上午（3小时）**：
- [ ] **任务 2.1**：替换正向评分模型（main.py:130）
  ```python
  # 修改 update_intimacy_score 函数
  model_positive = Tongyi(
      model_name="qwen-turbo",
      temperature=0.2,
      dashscope_api_key=st.secrets["DASHSCOPE_API_KEY"]
  )
  ```

- [ ] **任务 2.2**：替换负向评分模型（main.py:131）
  ```python
  model_negative = Tongyi(
      model_name="qwen-turbo",
      temperature=0,
      dashscope_api_key=st.secrets["DASHSCOPE_API_KEY"]
  )
  ```

**下午（4小时）**：
- [ ] **任务 2.3**：优化评分提示词
  - Qwen 对中文提示词理解更好，优化 `prompt_positive` 和 `prompt_negative`
  - 示例优化：
  ```python
  prompt_positive = f"""
  分析以下用户回复，判断是否符合这些积极标准：
  {positive_criteria}
  
  用户回复："{response_text}"
  
  对每个标准，回答"是"或"否"，并说明理由。
  格式：标准名: 是/否 - 理由
  """
  ```

- [ ] **任务 2.4**：批量测试亲密度评分
  - 准备 20 条测试用户输入（涵盖正负向案例）
  - 对比 OpenAI 和 Qwen 的评分结果
  - 调整 temperature 参数以达到最佳效果

**预期成果**：
- ✅ 亲密度评分准确率 > 85%
- ✅ 评分逻辑与原系统一致
- ✅ 中文理解能力增强

---

### 第3天：语义匹配 + Embeddings 迁移

**目标**：替换语义匹配模型和向量嵌入

#### 任务清单

**上午（3小时）**：
- [ ] **任务 3.1**：替换语义匹配模型（main.py:68, 374）
  ```python
  # 全局语义模型
  semantic_model = Tongyi(
      model_name="qwen-turbo",
      temperature=0.4,
      dashscope_api_key=st.secrets["DASHSCOPE_API_KEY"]
  )
  
  # semantic_match 函数无需修改，自动使用新模型
  ```

- [ ] **任务 3.2**：测试贴纸触发机制
  - 测试 4 种贴纸的语义匹配
  - 验证关键词匹配和语义匹配的准确性

**下午（4小时）**：
- [ ] **任务 3.3**：替换向量嵌入模型（main.py:762）
  ```python
  # 修改前
  from langchain_openai import OpenAIEmbeddings
  vectordb = Chroma(
      embedding_function=OpenAIEmbeddings(),
      persist_directory=get_vectordb(role)
  )
  
  # 修改后
  from langchain_community.embeddings import DashScopeEmbeddings
  vectordb = Chroma(
      embedding_function=DashScopeEmbeddings(
          model="text-embedding-v2",  # Qwen 的嵌入模型
          dashscope_api_key=st.secrets["DASHSCOPE_API_KEY"]
      ),
      persist_directory=get_vectordb(role)
  )
  ```

- [ ] **任务 3.4**：重建向量数据库（重要！）
  - **注意**：嵌入模型更换后，需要重新生成向量
  - 备份原 `db5/` 目录为 `db5_openai_backup/`
  - 创建新脚本重建向量库：
  
  ```python
  # rebuild_vectordb.py
  from langchain_community.embeddings import DashScopeEmbeddings
  from langchain_chroma import Chroma
  from langchain.text_splitter import RecursiveCharacterTextSplitter
  from langchain_community.document_loaders import PyPDFLoader
  import streamlit as st
  
  # 加载 PDF（假设在项目中）
  loader = PyPDFLoader("path/to/zino_knowledge.pdf")
  docs = loader.load()
  
  # 分割文档
  text_splitter = RecursiveCharacterTextSplitter(
      chunk_size=1000, 
      chunk_overlap=0
  )
  split_docs = text_splitter.split_documents(docs)
  
  # 创建新向量库
  embeddings = DashScopeEmbeddings(
      model="text-embedding-v2",
      dashscope_api_key=st.secrets["DASHSCOPE_API_KEY"]
  )
  
  vectordb = Chroma.from_documents(
      documents=split_docs,
      embedding=embeddings,
      persist_directory="db5_qwen"
  )
  
  print(f"✅ 向量库重建完成！共 {len(split_docs)} 个文档块")
  ```

- [ ] **任务 3.5**：验证检索质量
  - 测试 10 个常见问题的检索结果
  - 对比 OpenAI 和 Qwen 嵌入的相关性
  - 确保检索准确率不降低

**预期成果**：
- ✅ 语义匹配准确率 > 90%
- ✅ 向量检索质量与原系统相当或更好
- ✅ 贴纸触发机制正常

**关键风险**：
⚠️ **向量库重建耗时较长**（取决于文档数量）  
缓解措施：提前准备 PDF 文件，在第2天晚上开始重建

---

### 第4天：TTS 语音合成升级

**目标**：将 gTTS 替换为阿里云自然语音合成

#### 任务清单

**上午（3小时）**：
- [ ] **任务 4.1**：调研阿里云 TTS 方案
  - **方案 A**：阿里云语音合成（SpeechSynthesizer）
  - **方案 B**：CosyVoice（阿里最新 TTS 模型，自然度极高）
  - 推荐：**CosyVoice** - 效果接近真人

- [ ] **任务 4.2**：注册语音合成服务
  - 访问：https://nls.console.aliyun.com/
  - 开通"智能语音交互"服务
  - 获取 AppKey 和 Access Token

**下午（4小时）**：
- [ ] **任务 4.3**：集成阿里云 TTS SDK
  ```bash
  pip install alibabacloud-nls-python-sdk
  ```

- [ ] **任务 4.4**：重写 speak_text 函数
  ```python
  import nls
  from alibabacloud_nls_python_sdk import SpeechSynthesizer
  
  def speak_text_qwen(text, loading_placeholder=None):
      """使用阿里云 TTS 生成语音"""
      try:
          audio_id = uuid.uuid4().hex
          filename = f"output_{audio_id}.mp3"
          
          if loading_placeholder:
              loading_placeholder.markdown("""
                  <div class="loading-container">
                      <div class="loading-spinner"></div>
                      <div>正在生成自然语音...</div>
                  </div>
              """, unsafe_allow_html=True)
          
          # 初始化语音合成
          synthesizer = SpeechSynthesizer(
              appkey=st.secrets["ALIYUN_NLS_APPKEY"],
              token=st.secrets["ALIYUN_NLS_TOKEN"]
          )
          
          # 设置参数
          synthesizer.set_voice("siqi")  # 女声-活泼
          synthesizer.set_format("mp3")
          synthesizer.set_speech_rate(0)  # -500~500，0为正常
          synthesizer.set_pitch_rate(50)  # 音调稍高，更活泼
          
          # 生成语音
          audio_data = synthesizer.synthesize(text)
          
          # 保存文件
          with open(filename, "wb") as f:
              f.write(audio_data)
          
          # Base64 编码（保持原有流程）
          b64_audio = base64.b64encode(audio_data).decode()
          
          if loading_placeholder:
              loading_placeholder.empty()
          
          # HTML5 播放（保持原有流程）
          audio_html = f"""
              <audio id="{audio_id}" autoplay>
                  <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
              </audio>
              <script>
                  document.getElementById('{audio_id}').play();
              </script>
          """
          components.html(audio_html)
          
          print(f"✅ 阿里云 TTS 生成成功: {filename}")
          time.sleep(1)
          
      except Exception as e:
          st.error(f"语音合成失败: {e}")
          # 降级方案：使用原 gTTS
          speak_text_original(text, loading_placeholder)
  ```

- [ ] **任务 4.5**：测试语音质量
  - 准备 10 条测试文本（长短句混合）
  - 对比 gTTS 和阿里云 TTS 的自然度
  - 邀请 3-5 人进行盲测评分

**预期成果**：
- ✅ 语音自然度提升 70%+
- ✅ 支持情感表达和自然停顿
- ✅ 保持原有播放流程不变

**备选方案**：
如果阿里云 TTS 集成复杂，可先使用 **Edge TTS**（微软免费 TTS）作为过渡：
```bash
pip install edge-tts
```

---

### 第5天：智能体集成 + 整体测试

**目标**：实现智能路由和实时搜索整合

#### 任务清单

**上午（3小时）**：
- [ ] **任务 5.1**：设计智能路由逻辑
  ```python
  def should_use_web_search(user_input):
      """判断是否需要实时搜索"""
      router_llm = Tongyi(
          model_name="qwen-turbo",
          temperature=0,
          dashscope_api_key=st.secrets["DASHSCOPE_API_KEY"]
      )
      
      prompt = f"""
      判断以下问题是否需要实时网络搜索？
      
      需要搜索的情况：
      - 询问最新数据、当前状态、近期事件
      - 包含"最新"、"现在"、"当前"、"2024"、"2025"等时间词
      
      不需要搜索的情况：
      - 询问基础知识、生物习性、栖息地等
      
      问题：{user_input}
      
      只回答"是"或"否"
      """
      
      response = router_llm(prompt).strip()
      return "是" in response
  ```

- [ ] **任务 5.2**：集成 DuckDuckGo 搜索（免费方案）
  ```python
  from langchain_community.tools import DuckDuckGoSearchRun
  
  search_tool = DuckDuckGoSearchRun()
  
  def search_web(query):
      """实时搜索"""
      try:
          results = search_tool.run(f"{query} Zino's Petrel conservation")
          return results[:500]  # 限制长度
      except Exception as e:
          print(f"搜索失败: {e}")
          return None
  ```

**下午（4小时）**：
- [ ] **任务 5.3**：实现结果融合
  ```python
  def enhanced_query(user_input):
      """增强查询：RAG + 可选实时搜索"""
      # 1. RAG 检索
      rag_results = vectordb.max_marginal_relevance_search(
          user_input, k=4, fetch_k=20, lambda_mult=0.5
      )
      
      # 2. 判断是否需要实时搜索
      need_search = should_use_web_search(user_input)
      
      # 3. 构建上下文
      if need_search:
          search_results = search_web(user_input)
          context = f"""
          【知识库内容】
          {rag_results}
          
          【实时搜索结果】
          {search_results}
          
          请优先使用知识库内容，用搜索结果补充最新信息。
          """
          sources = "🔖 知识库 + 🌐 实时搜索"
      else:
          context = rag_results
          sources = "🔖 知识库"
      
      # 4. 生成回答
      chain, _ = get_conversational_chain("Zino's Petrel")
      answer = chain.run(input_documents=context, question=user_input)
      
      return answer, sources
  ```

- [ ] **任务 5.4**：UI 改造 - 显示信息来源
  ```python
  # 在回复下方添加来源标签
  st.markdown(f"""
      <div style="
          background: #e8f4f8;
          padding: 8px 12px;
          border-radius: 8px;
          margin-top: 8px;
          font-size: 0.9em;
      ">
          📍 信息来源: {sources}
      </div>
  """, unsafe_allow_html=True)
  ```

- [ ] **任务 5.5**：全面测试
  - **功能测试**：
    - 基础对话（纯 RAG）
    - 实时问题（RAG + 搜索）
    - 亲密度评分
    - 贴纸奖励
    - 语音播放
    - 礼物触发
  
  - **性能测试**：
    - 响应延迟（< 3 秒）
    - 并发测试（10 用户同时访问）
    - 内存占用
  
  - **质量测试**：
    - 准备 50 个测试问题
    - 记录回答准确率
    - 用户满意度调查

**预期成果**：
- ✅ 智能路由准确率 > 85%
- ✅ 实时问题回答准确率 > 70%
- ✅ 所有原有功能正常
- ✅ 系统稳定运行

---

## 🔄 并行优化任务（可选）

在完成主线任务的同时，可以利用碎片时间完成以下优化：

### RAG 检索多样性增强
- [ ] 调整 MMR 参数：`lambda_mult=0.5, k=4, fetch_k=20`
- [ ] 实现对话历史去重
- [ ] 测试检索多样性

### 成本监控
- [ ] 添加 API 调用计数器
- [ ] 记录每日 Token 消耗
- [ ] 设置预算告警

### 文档更新
- [ ] 更新 README.md
- [ ] 更新 requirements.txt
- [ ] 记录迁移经验

---

## 💰 成本对比分析

### OpenAI vs Qwen 成本对比（10,000 次对话/月）

| 服务 | OpenAI | Qwen | 节省 |
|------|--------|------|------|
| **LLM 调用** | $20 | **免费**（额度内） | -$20 |
| **Embeddings** | $1 | **免费**（额度内） | -$1 |
| **TTS** | $7.5 | $3-5（阿里云） | -$3 |
| **合计** | **$28.5/月** | **$3-5/月** | **节省 80%+** |

**Qwen 免费额度**：
- Qwen-Turbo：100万 tokens/月（足够初期使用）
- Text-Embedding-V2：100万 tokens/月
- 超出后按量计费：¥0.0008/1K tokens（约 $0.0001）

**结论**：迁移到 Qwen 可大幅降低成本！

---

## 🔧 技术栈更新

### 修改 requirements.txt

```txt
# 删除
langchain-openai==0.1.20

# 新增
dashscope>=1.14.0
langchain-community>=0.2.10
langchain-alibaba-cloud>=0.1.0  # 可选，官方集成
alibabacloud-nls-python-sdk>=2.0.0  # TTS

# 搜索工具（可选）
duckduckgo-search>=4.0

# 保持不变
langchain==0.2.11
langchain-chroma==0.1.2
chromadb
pypdf
streamlit
tiktoken
SpeechRecognition==3.10.0
pysqlite3-binary
python-dotenv
gTTS  # 保留作为降级方案
pydub
ffmpeg
st-supabase-connection==2.1.1
```

### 更新 secrets.toml

```toml
# 删除
# OPENAI_API_KEY = "sk-xxx"

# 新增
DASHSCOPE_API_KEY = "sk-xxx"  # Qwen LLM + Embeddings
ALIYUN_NLS_APPKEY = "xxx"      # 语音合成
ALIYUN_NLS_TOKEN = "xxx"       # 语音合成 Token

# 保持不变
[connections.supabase]
url = "https://xxx.supabase.co"
key = "xxx"
```

---

## 📊 每日进度追踪表

| 日期 | 主要任务 | 预期产出 | 实际完成 | 备注 |
|------|---------|---------|---------|------|
| Day 1<br>10-06 | 环境准备 + LLM 替换 | ✅ 对话功能正常 | ⏸️ | |
| Day 2<br>10-07 | 亲密度评分迁移 | ✅ 评分系统正常 | ⏸️ | |
| Day 3<br>10-08 | 语义匹配 + Embeddings | ✅ 向量库重建完成 | ⏸️ | ⚠️ 耗时较长 |
| Day 4<br>10-09 | TTS 语音升级 | ✅ 语音自然度提升 | ⏸️ | |
| Day 5<br>10-10 | 智能体 + 整体测试 | ✅ 全功能上线 | ⏸️ | |

---

## ⚠️ 风险与缓解

### 风险 1：向量库重建耗时长
- **影响**：第3天任务可能延期
- **缓解**：
  - 提前准备 PDF 文件
  - 第2天晚上开始异步重建
  - 准备好原 db5 作为备份

### 风险 2：Qwen API 限流
- **影响**：高并发时响应变慢
- **缓解**：
  - 使用 Qwen-Plus（QPS 更高）
  - 添加请求队列和重试机制
  - 设置合理的超时时间

### 风险 3：TTS 集成复杂度
- **影响**：第4天可能无法完成
- **缓解**：
  - 准备降级方案（Edge TTS）
  - 保留 gTTS 作为 fallback
  - 简化参数配置

### 风险 4：模型效果差异
- **影响**：回答质量可能下降
- **缓解**：
  - 准备 100 条测试问题对比
  - 优化提示词以适配 Qwen
  - 必要时使用 Qwen-Max（更强模型）

---

## ✅ 验收标准

### 功能完整性
- [ ] 所有 OpenAI API 调用已替换
- [ ] 对话功能正常
- [ ] 亲密度评分准确
- [ ] 贴纸奖励触发正常
- [ ] 语音播放流畅
- [ ] 向量检索有效

### 性能指标
- [ ] 平均响应时间 < 3 秒
- [ ] 语音自然度评分 > 4.0/5
- [ ] 检索准确率 > 85%
- [ ] 系统稳定运行 24 小时无崩溃

### 成本控制
- [ ] 月度成本 < $10
- [ ] 在免费额度范围内运行
- [ ] 设置成本告警机制

---

## 🚀 第一步行动（立即执行）

### 今天就开始（15 分钟）

```bash
# 1. 注册阿里云账号
访问：https://dashscope.aliyun.com/

# 2. 开通服务
- 模型服务：Qwen-Turbo
- 获取 API Key

# 3. 安装依赖
pip install dashscope langchain-community

# 4. 测试连接
python -c "
import dashscope
dashscope.api_key = 'YOUR_API_KEY'
response = dashscope.Generation.call(
    model='qwen-turbo',
    prompt='你好'
)
print(response)
"
```

如果测试成功，说明环境已就绪，可以开始 Day 1 的正式任务！

---

## 📞 支持资源

### 官方文档
- [Qwen API 文档](https://help.aliyun.com/zh/dashscope/)
- [LangChain Tongyi 集成](https://python.langchain.com/docs/integrations/llms/tongyi)
- [阿里云 TTS 文档](https://help.aliyun.com/zh/isi/developer-reference/api-details)

### 代码示例
- [Qwen + LangChain 示例](https://github.com/QwenLM/Qwen-Agent)
- [DashScope Python SDK](https://github.com/aliyun/alibabacloud-nls-python-sdk)

---

**创建时间**：2025-10-06  
**预计完成**：2025-10-10（5 工作日）  
**负责人**：AI 开发团队  
**状态**：✅ 计划已制定，等待执行


