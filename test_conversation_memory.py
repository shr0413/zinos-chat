"""
测试对话上下文记忆功能
验证 ConversationalRetrievalChain 是否能记住之前的对话
"""

import os
from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain_community.llms import Tongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma

# 加载环境变量
load_dotenv()

def test_conversation_memory():
    """测试对话记忆功能"""
    
    print("=" * 60)
    print("🧪 对话上下文记忆功能测试")
    print("=" * 60)
    
    # 初始化配置
    dashscope_key = os.getenv("DASHSCOPE_API_KEY")
    persist_directory = "db5_qwen"
    
    print(f"\n✅ API Key: {dashscope_key[:10]}...")
    print(f"✅ 向量库: {persist_directory}")
    
    # 加载向量数据库
    print("\n[1/4] 加载向量数据库...")
    embeddings = DashScopeEmbeddings(
        model=os.getenv("QWEN_EMBEDDING_MODEL", "text-embedding-v3"),
        dashscope_api_key=dashscope_key
    )
    
    vectordb = Chroma(
        embedding_function=embeddings,
        persist_directory=persist_directory,
        collection_name="zinos_petrel_knowledge"
    )
    print("✅ 向量数据库已加载")
    
    # 创建 LLM
    print("\n[2/4] 创建 LLM...")
    model = Tongyi(
        model_name=os.getenv("QWEN_MODEL_NAME", "qwen-turbo"),
        temperature=0,
        dashscope_api_key=dashscope_key
    )
    print("✅ LLM 已创建")
    
    # 创建 Retriever
    print("\n[3/4] 创建 Retriever...")
    retriever = vectordb.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 3,
            "fetch_k": 9,
            "lambda_mult": 0.3
        }
    )
    print("✅ Retriever 已创建")
    
    # 创建对话记忆
    print("\n[4/4] 创建对话记忆...")
    memory = ConversationBufferWindowMemory(
        k=5,
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )
    print("✅ Memory 已创建（保留最近5轮对话）")
    
    # 创建 ConversationalRetrievalChain
    print("\n创建 ConversationalRetrievalChain...")
    
    base_prompt = """You are Fred, a friendly and knowledgeable Zino's Petrel (Freira da Madeira). 
You are a seabird living in Madeira, Portugal. You love to share information about your species, 
habitat, and conservation. Be warm, personal, and enthusiastic!"""
    
    combine_docs_prompt = PromptTemplate(
        template=f"""
{base_prompt}

Use the following context to answer the question. If you don't know the answer based on the context, say so honestly.

Context:
{{context}}

Question: {{question}}

Answer:""",
        input_variables=["context", "question"]
    )
    
    chain = ConversationalRetrievalChain.from_llm(
        llm=model,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": combine_docs_prompt},
        return_source_documents=True,
        verbose=False
    )
    print("✅ Chain 已创建")
    
    # 测试场景：上下文对话
    print("\n" + "=" * 60)
    print("🧪 测试场景：上下文对话理解")
    print("=" * 60)
    
    test_conversations = [
        {
            "question": "Where do you live?",
            "expected_keywords": ["Madeira", "mountains", "island", "Portugal"],
            "context_check": None
        },
        {
            "question": "How high is it there?",
            "expected_keywords": ["altitude", "elevation", "meters", "mountain"],
            "context_check": "能否理解 'it' 指代 Madeira 或栖息地"
        },
        {
            "question": "Is it cold at night?",
            "expected_keywords": ["temperature", "cold", "night", "climate"],
            "context_check": "能否理解 'it' 指代栖息地的温度"
        },
        {
            "question": "What do you eat?",
            "expected_keywords": ["fish", "squid", "food", "prey"],
            "context_check": None
        },
        {
            "question": "How do you catch them?",
            "expected_keywords": ["catch", "hunt", "dive", "sea"],
            "context_check": "能否理解 'them' 指代食物（fish/squid）"
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_conversations, 1):
        print(f"\n{'─' * 60}")
        print(f"测试 {i}/{len(test_conversations)}")
        print(f"{'─' * 60}")
        print(f"📝 问题: {test['question']}")
        if test['context_check']:
            print(f"🎯 上下文检查: {test['context_check']}")
        
        # 调用 chain
        try:
            result = chain.invoke({"question": test['question']})
            answer = result.get("answer", "")
            
            print(f"\n💬 Fred 的回答:\n{answer}\n")
            
            # 关键词检查
            found_keywords = []
            for keyword in test['expected_keywords']:
                if keyword.lower() in answer.lower():
                    found_keywords.append(keyword)
            
            coverage = len(found_keywords) / len(test['expected_keywords']) * 100
            
            print(f"📊 关键词覆盖率: {coverage:.1f}%")
            print(f"   找到: {', '.join(found_keywords) if found_keywords else '无'}")
            
            # 评估
            if test['context_check']:
                # 需要人工判断上下文是否被理解
                print(f"\n❓ 请手动判断: {test['context_check']}")
                passed = coverage >= 25  # 宽松标准，主要看上下文理解
            else:
                passed = coverage >= 40
            
            results.append({
                "question": test['question'],
                "passed": passed,
                "coverage": coverage,
                "context_check": test['context_check']
            })
            
            if passed:
                print("✅ 测试通过")
            else:
                print("⚠️ 覆盖率较低，建议检查")
                
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
            results.append({
                "question": test['question'],
                "passed": False,
                "coverage": 0,
                "error": str(e)
            })
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    passed_count = sum(1 for r in results if r['passed'])
    total_count = len(results)
    
    print(f"\n✅ 通过测试: {passed_count}/{total_count} ({passed_count/total_count*100:.1f}%)")
    
    # 显示对话历史
    print("\n" + "=" * 60)
    print("💭 当前对话历史 (Memory 存储)")
    print("=" * 60)
    
    print(f"\n总对话轮数: {len(memory.chat_memory.messages) // 2}")
    print(f"Memory 窗口大小: 最近 {memory.k} 轮")
    
    if len(memory.chat_memory.messages) > 0:
        print("\n对话记录:")
        for i, msg in enumerate(memory.chat_memory.messages):
            role = "👤 用户" if msg.type == "human" else "🐦 Fred"
            content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            print(f"  {role}: {content}")
    
    print("\n" + "=" * 60)
    print("🎉 测试完成！")
    print("=" * 60)
    
    print("\n💡 验证要点:")
    print("  1. 第2个问题能否理解 'it there' 指代栖息地")
    print("  2. 第3个问题能否理解 'it' 指代栖息地的温度")
    print("  3. 第5个问题能否理解 'them' 指代食物")
    
    return results

if __name__ == "__main__":
    test_conversation_memory()

