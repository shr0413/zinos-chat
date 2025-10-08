"""
用户问题快速测试脚本
专门测试实际用户提供的 9 个问题

使用方法:
    python test_user_questions.py
"""

import os
import time
from dotenv import load_dotenv
from rag_utils import get_rag_instance

# 加载环境变量
load_dotenv()

def test_user_questions(lambda_mult=0.3):
    """测试用户提供的 9 个实际问题"""
    print("=" * 70)
    print(f"👥 用户实际问题测试 (lambda_mult={lambda_mult})")
    print("=" * 70)
    print("测试以下 9 个用户问题的 RAG 检索效果：")
    print()
    
    # 检查 API Key
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 错误: 未找到 DASHSCOPE_API_KEY")
        return
    
    # 初始化 RAG
    rag = get_rag_instance("db5_qwen", api_key)
    
    # 9 个用户问题
    questions = [
        {
            "id": 1,
            "text": "Hi, how are you doing today?",
            "type": "问候",
            "sticker": "无",
            "keywords": ["petrel", "bird", "good", "fine"]
        },
        {
            "id": 2,
            "text": "Where do you usually have your nesting areas?",
            "type": "栖息地",
            "sticker": "🏡 Home",
            "keywords": ["nest", "Madeira", "mountains", "cliffs", "caves"]
        },
        {
            "id": 3,
            "text": "How long do you live approximately?",
            "type": "寿命",
            "sticker": "无",
            "keywords": ["years", "lifespan", "live", "age"]
        },
        {
            "id": 4,
            "text": "Why do you need to abort sometimes to protect your species, that's a very sad thing and I don't quite understand how does it help you",
            "type": "保护策略",
            "sticker": "🌱 Helper (可能)",
            "keywords": ["conservation", "protection", "breeding", "survival", "predators"]
        },
        {
            "id": 5,
            "text": "How long do you sleep?",
            "type": "日常习惯",
            "sticker": "🌙 Routine (可能)",
            "keywords": ["sleep", "rest", "night", "day", "active"]
        },
        {
            "id": 6,
            "text": "How do I find you?",
            "type": "观察指南",
            "sticker": "🏡 Home (如未触发)",
            "keywords": ["Madeira", "mountains", "sea", "observation", "location"]
        },
        {
            "id": 7,
            "text": "Do you have a friend?",
            "type": "社交",
            "sticker": "无",
            "keywords": ["mate", "colony", "pair", "social", "alone"]
        },
        {
            "id": 8,
            "text": "What do you eat for food and how do you catch it?",
            "type": "饮食",
            "sticker": "🍽️ Food",
            "keywords": ["fish", "squid", "food", "catch", "hunt", "sea"]
        },
        {
            "id": 9,
            "text": "How can I help you and your species thrive?",
            "type": "保护行动",
            "sticker": "🌱 Helper",
            "keywords": ["help", "protect", "conservation", "support", "habitat"]
        }
    ]
    
    total_coverage = 0
    total_time = 0
    passed = 0
    
    for q in questions:
        print(f"\n{'─' * 70}")
        print(f"问题 {q['id']}/9: {q['type']}")
        print(f"{'─' * 70}")
        print(f"❓ {q['text']}")
        print(f"🎁 预期贴纸: {q['sticker']}")
        
        # 检索
        start_time = time.time()
        docs = rag.retrieve(q['text'], lambda_mult=lambda_mult)
        elapsed = time.time() - start_time
        total_time += elapsed
        
        # 分析结果
        all_content = " ".join([doc.page_content.lower() for doc in docs])
        found = [kw for kw in q['keywords'] if kw.lower() in all_content]
        coverage = (len(found) / len(q['keywords']) * 100) if q['keywords'] else 0
        total_coverage += coverage
        
        # 输出结果
        print(f"\n⏱️  {elapsed:.2f}s | 📄 {len(docs)}个文档 | ✅ {coverage:.0f}% 覆盖率")
        
        if found:
            print(f"🔍 找到关键词: {', '.join(found)}")
        else:
            print(f"⚠️  未找到任何关键词")
        
        # 显示来源
        if docs:
            source = docs[0].metadata.get('source_file', 'Unknown')
            page = docs[0].metadata.get('page', '?')
            preview = docs[0].page_content[:100].replace('\n', ' ')
            print(f"📚 主要来源: {source} (页 {page})")
            print(f"   预览: {preview}...")
        
        # 评估
        if coverage >= 50:
            print(f"✅ 通过")
            passed += 1
        else:
            print(f"⚠️  待优化")
    
    # 总结
    print(f"\n{'=' * 70}")
    print(f"📊 测试总结")
    print(f"{'=' * 70}")
    print(f"✅ 通过: {passed}/9 ({passed/9*100:.0f}%)")
    print(f"📈 平均覆盖率: {total_coverage/9:.1f}%")
    print(f"⏱️  平均耗时: {total_time/9:.2f}秒")
    
    # 评级
    if passed >= 7:
        print(f"\n🎉 评级: A - 优秀！可以直接使用")
    elif passed >= 5:
        print(f"\n👍 评级: B - 良好，基本满足需求")
    elif passed >= 3:
        print(f"\n⚠️  评级: C - 一般，建议优化")
    else:
        print(f"\n❌ 评级: D - 需要重大改进")
    
    print(f"\n💡 下一步:")
    if passed >= 7:
        print(f"   → 运行 'streamlit run main.py' 开始使用")
    else:
        print(f"   → 调整 lambda_mult 参数（降低以提高相关性）")
        print(f"   → 检查向量化是否使用正确的 embedding 模型")
        print(f"   → 查看 RAG_SETUP_GUIDE.md 了解优化方法")
    print()

if __name__ == "__main__":
    test_user_questions()

