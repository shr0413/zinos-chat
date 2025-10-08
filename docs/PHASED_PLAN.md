# 阶段化任务计划 - 按需求点划分

## 📋 总览

**目标**：完成 API 迁移并实现三大核心需求  
**时间**：5 天  
**策略**：基础迁移 + 3个需求点并行推进

---

## 🗂️ 阶段划分

```
阶段0: 基础迁移（OpenAI → Qwen）         Day 1 
阶段1: 需求1 - TTS 语音升级               Day 2
阶段2: 需求2 - RAG 检索优化               Day 3
阶段3: 需求3 - 智能体实时搜索             Day 4
阶段4: 整合测试与上线                     Day 5
```

---

## 🔧 阶段0：基础迁移（Day 1）

### 目标
将所有 OpenAI API 调用替换为 Qwen API，确保基础功能正常运行

### 任务清单

#### 准备工作（1小时）

- [ ] **0.1 环境配置**
  - [ ] 复制 `env.template` 为 `.env`
  - [ ] 注册阿里云账号：https://dashscope.aliyun.com/
  - [ ] 开通 Qwen-Turbo 模型服务
  - [ ] 获取 DashScope API Key
  - [ ] 填充 `.env` 文件：
    ```bash
    DASHSCOPE_API_KEY=sk-xxxxx
    QWEN_MODEL_NAME=qwen-turbo
    VECTOR_DB_PATH=db5  # 暂时使用旧向量库
    ```

- [ ] **0.2 安装依赖**
  ```bash
  pip install dashscope langchain-community python-dotenv
  ```

#### 核心迁移（3小时）

- [ ] **0.3 创建配置加载模块**
  - [ ] 创建 `config.py`：
    ```python
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    class Config:
        # Qwen LLM
        DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
        QWEN_MODEL = os.getenv("QWEN_MODEL_NAME", "qwen-turbo")
        
        # 温度参数
        TEMP_CONVERSATION = float(os.getenv("QWEN_TEMPERATURE_CONVERSATION", "0.0"))
        TEMP_SCORING_POS = float(os.getenv("QWEN_TEMPERATURE_SCORING_POS", "0.2"))
        TEMP_SCORING_NEG = float(os.getenv("QWEN_TEMPERATURE_SCORING_NEG", "0.0"))
        TEMP_SEMANTIC = float(os.getenv("QWEN_TEMPERATURE_SEMANTIC", "0.4"))
        
        # 向量库
        VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "db5")
        
        # Supabase
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    config = Config()
    ```

- [ ] **0.4 替换 LLM 调用**
  - [ ] 修改 `main.py` 导入部分：
    ```python
    from langchain_community.llms import Tongyi
    from config import config
    ```
  
  - [ ] 替换 4 个 LLM 实例：
    ```python
    # 1. 语义匹配（行68）
    semantic_model = Tongyi(
        model_name=config.QWEN_MODEL,
        temperature=config.TEMP_SEMANTIC,
        dashscope_api_key=config.DASHSCOPE_API_KEY
    )
    
    # 2. 正向评分（行130）
    model_positive = Tongyi(
        model_name=config.QWEN_MODEL,
        temperature=config.TEMP_SCORING_POS,
        dashscope_api_key=config.DASHSCOPE_API_KEY
    )
    
    # 3. 负向评分（行131）
    model_negative = Tongyi(
        model_name=config.QWEN_MODEL,
        temperature=config.TEMP_SCORING_NEG,
        dashscope_api_key=config.DASHSCOPE_API_KEY
    )
    
    # 4. 对话生成（行321）
    model = Tongyi(
        model_name=config.QWEN_MODEL,
        temperature=config.TEMP_CONVERSATION,
        dashscope_api_key=config.DASHSCOPE_API_KEY
    )
    ```

#### 验证测试（1小时）

- [ ] **0.5 功能测试**
  - [ ] 测试基础对话（10个问题）
  - [ ] 测试亲密度评分（5条正向+5条负向）
  - [ ] 测试贴纸触发（4种贴纸）
  - [ ] 验证数据库记录
  
- [ ] **0.6 性能对比**
  - [ ] 记录响应延迟
  - [ ] 对比回答质量
  - [ ] 调整 temperature 参数（如有需要）

### 交付物
- ✅ `.env` 配置文件（已填充）
- ✅ `config.py` 配置模块
- ✅ `main.py`（已迁移到 Qwen）
- ✅ 功能测试报告

### 验收标准
- [ ] 所有 LLM 调用成功切换到 Qwen
- [ ] 基础对话功能正常
- [ ] 亲密度评分准确率 > 85%
- [ ] 响应延迟 < 3 秒

---

## 🎤 阶段1：需求1 - TTS 语音升级（Day 2）

### 目标
将 gTTS 替换为阿里云自然语音合成，实现情感化、自然化的语音输出

### 任务清单

#### 准备工作（1小时）

- [ ] **1.1 开通阿里云语音服务**
  - [ ] 访问：https://nls.console.aliyun.com/
  - [ ] 开通"智能语音交互"服务
  - [ ] 创建项目获取 AppKey
  - [ ] 获取 Access Key ID 和 Secret
  - [ ] 填充 `.env`：
    ```bash
    ALIYUN_NLS_APPKEY=xxxxx
    ALIYUN_NLS_ACCESS_KEY_ID=xxxxx
    ALIYUN_NLS_ACCESS_KEY_SECRET=xxxxx
    TTS_VOICE=siqi
    TTS_SPEECH_RATE=0
    TTS_PITCH_RATE=50
    USE_GTTS_FALLBACK=true
    ```

- [ ] **1.2 安装 SDK**
  ```bash
  pip install alibabacloud-nls-python-sdk
  ```

#### TTS 功能开发（3小时）

- [ ] **1.3 创建 TTS 模块**
  - [ ] 创建 `tts_handler.py`：
    ```python
    import os
    import base64
    import uuid
    from aliyunsdkcore.client import AcsClient
    from aliyunsdkcore.request import CommonRequest
    from config import config
    from gtts import gTTS
    from pydub import AudioSegment
    
    class TTSHandler:
        def __init__(self):
            self.use_aliyun = config.FEATURE_NEW_TTS
            self.fallback_to_gtts = config.USE_GTTS_FALLBACK
            
            if self.use_aliyun:
                self.client = AcsClient(
                    config.ALIYUN_NLS_ACCESS_KEY_ID,
                    config.ALIYUN_NLS_ACCESS_KEY_SECRET,
                    'cn-shanghai'
                )
        
        def synthesize(self, text):
            """语音合成"""
            if self.use_aliyun:
                try:
                    return self._aliyun_tts(text)
                except Exception as e:
                    print(f"阿里云TTS失败: {e}")
                    if self.fallback_to_gtts:
                        return self._gtts_fallback(text)
            else:
                return self._gtts_fallback(text)
        
        def _aliyun_tts(self, text):
            """阿里云TTS实现"""
            # 1. 获取Token
            token = self._get_token()
            
            # 2. 调用语音合成
            request = CommonRequest()
            request.set_domain('nls-gateway.cn-shanghai.aliyuncs.com')
            request.set_version('2019-02-28')
            request.set_action_name('SpeechSynthesizer')
            request.add_query_param('Format', 'mp3')
            request.add_query_param('Voice', config.TTS_VOICE)
            request.add_query_param('SpeechRate', config.TTS_SPEECH_RATE)
            request.add_query_param('PitchRate', config.TTS_PITCH_RATE)
            request.add_query_param('Text', text)
            
            response = self.client.do_action_with_exception(request)
            return response
        
        def _gtts_fallback(self, text):
            """gTTS降级方案"""
            tts = gTTS(text, lang='en', slow=False)
            tts.save("temp.mp3")
            sound = AudioSegment.from_file("temp.mp3")
            lively_sound = sound.speedup(playback_speed=1.3)
            
            filename = f"output_{uuid.uuid4().hex}.mp3"
            lively_sound.export(filename, format="mp3")
            
            with open(filename, "rb") as f:
                return f.read()
        
        def _get_token(self):
            """获取访问Token"""
            request = CommonRequest()
            request.set_method('POST')
            request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
            request.set_version('2019-02-28')
            request.set_action_name('CreateToken')
            
            response = self.client.do_action_with_exception(request)
            return response['Token']['Id']
    ```

- [ ] **1.4 集成到主应用**
  - [ ] 修改 `main.py` 中的 `speak_text` 函数：
    ```python
    from tts_handler import TTSHandler
    
    tts_handler = TTSHandler()
    
    def speak_text(text, loading_placeholder=None):
        try:
            audio_id = uuid.uuid4().hex
            
            if loading_placeholder:
                loading_placeholder.markdown("""
                    <div class="loading-container">
                        <div class="loading-spinner"></div>
                        <div>正在生成自然语音...</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # 使用新TTS处理器
            audio_data = tts_handler.synthesize(text)
            b64_audio = base64.b64encode(audio_data).decode()
            
            if loading_placeholder:
                loading_placeholder.empty()
            
            # HTML5播放（保持原逻辑）
            audio_html = f"""
                <audio id="{audio_id}" autoplay>
                    <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
                </audio>
            """
            components.html(audio_html)
            
        except Exception as e:
            st.error(f"语音合成失败: {e}")
    ```

#### 测试优化（1小时）

- [ ] **1.5 音质测试**
  - [ ] 准备测试文本（10条，包含长短句）
  - [ ] 对比 gTTS 和阿里云 TTS
  - [ ] 邀请 3-5 人盲测评分
  - [ ] 调整语速、音调参数

- [ ] **1.6 降级测试**
  - [ ] 模拟阿里云 API 失败
  - [ ] 验证 gTTS 降级是否生效
  - [ ] 确认错误处理完善

### 交付物
- ✅ `tts_handler.py` TTS处理模块
- ✅ 更新后的 `main.py`
- ✅ 音质测试报告

### 验收标准
- [ ] 语音自然度 > 4.0/5
- [ ] 降级机制正常
- [ ] 播放流程无卡顿
- [ ] 错误处理完善

---

## 🔍 阶段2：需求2 - RAG 检索优化（Day 3）

### 目标
优化检索策略，解决重复检索问题，提升结果多样性和相关性

### 任务清单

#### Embeddings 迁移（2小时）

- [ ] **2.1 替换向量嵌入模型**
  - [ ] 修改 `config.py` 添加配置：
    ```python
    # Embeddings
    QWEN_EMBEDDING_MODEL = os.getenv("QWEN_EMBEDDING_MODEL", "text-embedding-v2")
    ```
  
  - [ ] 修改 `main.py` 第 762 行：
    ```python
    from langchain_community.embeddings import DashScopeEmbeddings
    
    vectordb = Chroma(
        embedding_function=DashScopeEmbeddings(
            model=config.QWEN_EMBEDDING_MODEL,
            dashscope_api_key=config.DASHSCOPE_API_KEY
        ),
        persist_directory=config.VECTOR_DB_PATH
    )
    ```

- [ ] **2.2 重建向量库**
  - [ ] 备份旧库：`cp -r db5 db5_openai_backup`
  - [ ] 创建 `rebuild_vectordb.py`（见 Day 3 详细脚本）
  - [ ] 执行重建（预计 30-60 分钟）
  - [ ] 更新 `.env`：`VECTOR_DB_PATH=db5_qwen`

#### 检索优化（2.5小时）

- [ ] **2.3 调整 MMR 参数**
  - [ ] 更新 `.env` 配置：
    ```bash
    RAG_MMR_K=4
    RAG_MMR_FETCH_K=20
    RAG_MMR_LAMBDA=0.5
    ENABLE_HISTORY_DEDUP=true
    ```
  
  - [ ] 修改检索逻辑（main.py 第 763 行）：
    ```python
    most_relevant_texts = vectordb.max_marginal_relevance_search(
        current_input, 
        k=config.RAG_MMR_K,
        fetch_k=config.RAG_MMR_FETCH_K,
        lambda_mult=config.RAG_MMR_LAMBDA
    )
    ```

- [ ] **2.4 实现历史去重**
  - [ ] 创建 `rag_optimizer.py`：
    ```python
    class RAGOptimizer:
        def __init__(self):
            self.history_doc_ids = set()
        
        def deduplicate_with_history(self, docs, chat_history):
            """基于对话历史去重"""
            # 提取已使用的文档ID
            for msg in chat_history[-config.MAX_HISTORY_ROUNDS:]:
                if 'doc_ids' in msg:
                    self.history_doc_ids.update(msg['doc_ids'])
            
            # 过滤重复文档
            unique_docs = []
            for doc in docs:
                doc_id = hash(doc.page_content[:100])
                if doc_id not in self.history_doc_ids:
                    unique_docs.append(doc)
                    self.history_doc_ids.add(doc_id)
            
            return unique_docs
    ```
  
  - [ ] 集成到主流程：
    ```python
    from rag_optimizer import RAGOptimizer
    
    rag_optimizer = RAGOptimizer()
    
    # 在检索后去重
    most_relevant_texts = vectordb.max_marginal_relevance_search(...)
    unique_texts = rag_optimizer.deduplicate_with_history(
        most_relevant_texts, 
        st.session_state.chat_history
    )
    ```

#### 高级优化（可选，1.5小时）

- [ ] **2.5 混合检索（可选）**
  - [ ] 更新 `.env`：`ENABLE_HYBRID_SEARCH=true`
  - [ ] 实现 BM25 + 向量混合检索
  
- [ ] **2.6 重排序（可选）**
  - [ ] 如果启用 Cohere：填充 `COHERE_API_KEY`
  - [ ] 集成重排序逻辑

#### 验证测试（1小时）

- [ ] **2.7 检索质量测试**
  - [ ] 准备 20 个测试问题
  - [ ] 连续 5 轮对话，验证无重复
  - [ ] 记录检索相关性评分
  - [ ] 对比优化前后效果

### 交付物
- ✅ 新向量库（db5_qwen/）
- ✅ `rag_optimizer.py` 检索优化模块
- ✅ 更新后的 `main.py`
- ✅ 检索质量测试报告

### 验收标准
- [ ] 向量库重建成功
- [ ] 连续 5 轮对话无完全重复
- [ ] 检索相关性提升 30%+
- [ ] 响应延迟增加 < 500ms

---

## 🤖 阶段3：需求3 - 智能体实时搜索（Day 4）

### 目标
新增智能路由层，实现 RAG + 实时搜索的混合知识增强

### 任务清单

#### 智能路由开发（2小时）

- [ ] **3.1 配置搜索工具**
  - [ ] 更新 `.env`：
    ```bash
    USE_WEB_SEARCH=true
    WEB_SEARCH_PROVIDER=duckduckgo
    ENABLE_SMART_ROUTING=true
    ROUTING_CONFIDENCE_THRESHOLD=0.7
    ```
  
  - [ ] 安装依赖：
    ```bash
    pip install duckduckgo-search
    ```

- [ ] **3.2 创建智能路由模块**
  - [ ] 创建 `agent_router.py`：
    ```python
    from langchain_community.llms import Tongyi
    from langchain_community.tools import DuckDuckGoSearchRun
    from config import config
    
    class AgentRouter:
        def __init__(self):
            self.router_llm = Tongyi(
                model_name=config.QWEN_MODEL,
                temperature=config.TEMP_ROUTER,
                dashscope_api_key=config.DASHSCOPE_API_KEY
            )
            self.search_tool = DuckDuckGoSearchRun()
        
        def should_search_web(self, user_input):
            """判断是否需要实时搜索"""
            prompt = f"""
            判断以下问题是否需要实时网络搜索来回答？
            
            需要搜索的情况：
            - 询问最新数据、当前状态、近期事件
            - 包含"最新"、"现在"、"当前"、"2024"、"2025"等时间词
            - 询问保护动态、研究进展等实时信息
            
            不需要搜索的情况：
            - 询问基础知识、生物习性、栖息地等
            - 询问历史信息、固定事实
            
            问题：{user_input}
            
            只回答"需要"或"不需要"，不要解释。
            """
            
            response = self.router_llm(prompt).strip()
            return "需要" in response
        
        def search_web(self, query):
            """执行实时搜索"""
            try:
                # 优化搜索查询
                enhanced_query = f"{query} Zino's Petrel conservation latest"
                results = self.search_tool.run(enhanced_query)
                return results[:500]  # 限制长度
            except Exception as e:
                print(f"搜索失败: {e}")
                return None
    ```

#### 结果融合开发（2小时）

- [ ] **3.3 创建融合处理模块**
  - [ ] 创建 `knowledge_fusion.py`：
    ```python
    class KnowledgeFusion:
        @staticmethod
        def merge_sources(rag_results, web_results=None):
            """融合 RAG 和搜索结果"""
            context = {
                'internal_knowledge': rag_results,
                'external_updates': web_results,
                'source_tags': []
            }
            
            if rag_results:
                context['source_tags'].append('🔖 知识库')
            
            if web_results:
                context['source_tags'].append('🌐 实时搜索')
            
            # 构建融合提示词
            if web_results:
                context['instruction'] = """
                请基于以下信息回答：
                
                【知识库内容】（优先使用，权威可靠）
                {internal_knowledge}
                
                【实时搜索结果】（补充最新动态）
                {external_updates}
                
                回答要求：
                1. 优先使用知识库的权威信息
                2. 用搜索结果补充最新动态
                3. 保持Maria（齐诺海燕）的第一人称视角
                """
            else:
                context['instruction'] = """
                请基于知识库内容回答：
                {internal_knowledge}
                """
            
            return context
    ```

- [ ] **3.4 集成到主查询流程**
  - [ ] 修改 `main.py` 查询部分（第 760-780 行）：
    ```python
    from agent_router import AgentRouter
    from knowledge_fusion import KnowledgeFusion
    
    agent_router = AgentRouter()
    knowledge_fusion = KnowledgeFusion()
    
    # 在用户输入处理中
    if user_input:
        # 1. RAG 检索
        rag_results = vectordb.max_marginal_relevance_search(...)
        unique_results = rag_optimizer.deduplicate_with_history(...)
        
        # 2. 智能路由判断
        need_search = False
        web_results = None
        
        if config.ENABLE_SMART_ROUTING:
            need_search = agent_router.should_search_web(user_input)
            
            if need_search:
                web_results = agent_router.search_web(user_input)
        
        # 3. 融合结果
        fused_context = knowledge_fusion.merge_sources(
            unique_results, 
            web_results
        )
        
        # 4. 生成回答
        chain, role_config = get_conversational_chain(role)
        answer = chain.run(
            input_documents=fused_context['internal_knowledge'],
            question=user_input,
            additional_context=fused_context.get('external_updates', '')
        )
        
        # 5. 显示来源标签
        source_tags = " + ".join(fused_context['source_tags'])
        st.session_state.last_sources = source_tags
    ```

#### UI 改造（1小时）

- [ ] **3.5 添加来源标签**
  - [ ] 在回复下方添加来源显示：
    ```python
    # 在显示回复后
    if hasattr(st.session_state, 'last_sources'):
        st.markdown(f"""
            <div style="
                background: #e8f4f8;
                padding: 8px 12px;
                border-radius: 8px;
                margin-top: 8px;
                font-size: 0.9em;
            ">
                📍 信息来源: {st.session_state.last_sources}
            </div>
        """, unsafe_allow_html=True)
    ```

- [ ] **3.6 更新事实核查区域**
  - [ ] 修改右侧 Expander，分别展示内部和外部来源

#### 测试验证（1小时）

- [ ] **3.7 智能体功能测试**
  - [ ] 测试纯 RAG 场景（"你吃什么？"）
  - [ ] 测试混合场景（"最新的保护进展？"）
  - [ ] 验证路由准确率（50个测试问题）
  - [ ] 测试降级场景（搜索失败）

### 交付物
- ✅ `agent_router.py` 智能路由模块
- ✅ `knowledge_fusion.py` 融合处理模块
- ✅ 更新后的 `main.py`（含UI改造）
- ✅ 路由准确率测试报告

### 验收标准
- [ ] 智能路由准确率 > 85%
- [ ] 实时问题回答准确率 > 70%
- [ ] UI 明确显示信息来源
- [ ] 降级机制正常

---

## 🚀 阶段4：整合测试与上线（Day 5）

### 目标
全面测试所有功能，修复问题，完成文档，准备上线

### 任务清单

#### 全面测试（3小时）

- [ ] **4.1 功能回归测试**
  - [ ] 基础对话（20个问题）
  - [ ] 亲密度评分（20条输入）
  - [ ] 贴纸奖励（4种触发 × 3次）
  - [ ] 语音播放（10条回复）
  - [ ] 礼物触发（达到6分）
  - [ ] 实时搜索（10个问题）
  - [ ] 数据库记录

- [ ] **4.2 性能压测**
  - [ ] 10 用户并发测试
  - [ ] 响应延迟统计（100次请求）
  - [ ] 内存占用监控
  - [ ] API 限流测试

- [ ] **4.3 边缘情况测试**
  - [ ] API 失败场景
  - [ ] 网络超时场景
  - [ ] 向量库加载失败
  - [ ] TTS 降级测试
  - [ ] 搜索工具失败

#### 优化调整（2小时）

- [ ] **4.4 性能优化**
  - [ ] 分析性能瓶颈
  - [ ] 优化慢查询
  - [ ] 添加缓存机制（如有必要）

- [ ] **4.5 参数调优**
  - [ ] 调整 temperature 参数
  - [ ] 优化 MMR 参数
  - [ ] 调整路由阈值
  - [ ] 确定最佳 TTS 配置

#### 文档完善（1.5小时）

- [ ] **4.6 更新文档**
  - [ ] 更新 `README.md`
  - [ ] 更新 `requirements.txt`
  - [ ] 创建 `DEPLOYMENT.md` 部署指南
  - [ ] 记录已知问题和限制

- [ ] **4.7 创建用户手册**
  - [ ] 功能说明
  - [ ] 使用教程
  - [ ] 常见问题

#### 部署准备（1.5小时）

- [ ] **4.8 环境检查**
  - [ ] 确认所有 API Keys 有效
  - [ ] 验证生产环境配置
  - [ ] 设置监控告警

- [ ] **4.9 发布准备**
  - [ ] 代码提交和标签
  - [ ] 备份数据库
  - [ ] 准备回滚方案

### 交付物
- ✅ 完整测试报告
- ✅ 性能优化报告
- ✅ 更新后的文档
- ✅ 部署检查清单

### 验收标准
- [ ] 所有功能正常
- [ ] 性能指标达标
- [ ] 文档完整准确
- [ ] 生产环境就绪

---

## 📊 总体进度追踪

| 阶段 | 需求点 | 预估时间 | 完成度 | 状态 |
|------|--------|---------|--------|------|
| 阶段0 | 基础迁移 | Day 1 (5h) | 0% | ⏸️ 待开始 |
| 阶段1 | 需求1 - TTS升级 | Day 2 (5h) | 0% | ⏸️ 待开始 |
| 阶段2 | 需求2 - RAG优化 | Day 3 (6h) | 0% | ⏸️ 待开始 |
| 阶段3 | 需求3 - 智能体 | Day 4 (6h) | 0% | ⏸️ 待开始 |
| 阶段4 | 整合测试 | Day 5 (8h) | 0% | ⏸️ 待开始 |

**总体进度**：0/5 阶段完成

---

## 🎯 关键里程碑

- [ ] **M0**：Qwen API 调用成功（阶段0 - Day 1）
- [ ] **M1**：自然语音上线（阶段1 - Day 2）
- [ ] **M2**：检索多样性提升（阶段2 - Day 3）
- [ ] **M3**：智能体功能完整（阶段3 - Day 4）
- [ ] **M4**：全功能验收通过（阶段4 - Day 5）

---

## 💰 成本预算

| 服务 | 预估用量 | 成本 |
|------|---------|------|
| Qwen LLM | 100K tokens | 免费额度内 |
| Qwen Embeddings | 50K tokens | 免费额度内 |
| 阿里云 TTS | 10K 字符 | ¥10 |
| DuckDuckGo 搜索 | 不限 | 免费 |
| **总计** | - | **≈ ¥10/月** |

---

## 📝 配置文件结构

```
zinos-chat/
├── .env                    # 实际配置（不提交）
├── env.template            # 配置模板
├── config.py               # 配置加载模块
├── main.py                 # 主应用（已更新）
├── tts_handler.py          # TTS处理模块
├── rag_optimizer.py        # RAG优化模块
├── agent_router.py         # 智能路由模块
├── knowledge_fusion.py     # 知识融合模块
├── rebuild_vectordb.py     # 向量库重建脚本
└── requirements.txt        # 依赖列表（已更新）
```

---

## ⚠️ 关键注意事项

### 🔴 高优先级
1. **Day 1 必须完成**：基础迁移是后续的基础
2. **Day 3 风险点**：向量库重建耗时，提前准备
3. **配置安全**：`.env` 文件不能提交到 Git

### 🟡 中优先级
1. **降级方案**：每个模块都要有 fallback
2. **测试覆盖**：每个阶段都要测试
3. **文档同步**：代码和文档保持一致

### 🟢 低优先级
1. **性能优化**：可以在上线后持续优化
2. **高级功能**：混合检索、重排序可选

---

## 🚀 立即开始

### 第一步（5分钟）
```bash
# 1. 复制配置模板
cp .env .env

# 2. 编辑 .env 文件
# 填充必需的 API Keys

# 3. 验证配置
python -c "from config import config; print(config.DASHSCOPE_API_KEY)"
```

### 第二步（30分钟）
- 按照阶段0的任务清单执行
- 完成基础迁移

### 第三步（持续）
- 每完成一个阶段，更新进度表
- 记录遇到的问题和解决方案
- 准备下一阶段

---

**准备好了吗？开始阶段0！** 🎯

