"""
配置验证脚本
检查所有必需的配置是否正确设置
"""

from dotenv import load_dotenv
import os
import sys

load_dotenv()

def verify_config():
    """验证配置"""
    
    # 必需配置
    required = {
        'DASHSCOPE_API_KEY': {
            'value': os.getenv("DASHSCOPE_API_KEY"),
            'name': 'Qwen API（LLM + TTS + Embeddings）',
            'hint': '从 https://dashscope.aliyun.com/ 获取'
        },
        'SUPABASE_URL': {
            'value': os.getenv("SUPABASE_URL"),
            'name': 'Supabase URL',
            'hint': '从 https://app.supabase.com/ 获取'
        },
        'SUPABASE_KEY': {
            'value': os.getenv("SUPABASE_KEY"),
            'name': 'Supabase Key',
            'hint': '从 https://app.supabase.com/ 获取'
        },
    }
    
    # 可选配置
    optional = {
        'TAVILY_API_KEY': {
            'value': os.getenv("TAVILY_API_KEY"),
            'name': 'Tavily 搜索',
            'hint': '从 https://tavily.com/ 获取（可选）'
        },
        'COHERE_API_KEY': {
            'value': os.getenv("COHERE_API_KEY"),
            'name': 'Cohere 重排序',
            'hint': '从 https://dashboard.cohere.com/ 获取（可选）'
        },
        'OPENAI_API_KEY': {
            'value': os.getenv("OPENAI_API_KEY"),
            'name': 'OpenAI 降级',
            'hint': '从 https://platform.openai.com/ 获取（可选）'
        },
    }
    
    print("=" * 60)
    print("配置验证")
    print("=" * 60)
    
    # 检查必需配置
    print("\n✅ 必需配置：")
    all_required_valid = True
    
    for key, info in required.items():
        value = info['value']
        name = info['name']
        hint = info['hint']
        
        if value and value not in [f'your-{key.lower().replace("_", "-")}-here', 
                                    f'sk-your-{key.lower().replace("_", "-")}-here',
                                    f'https://your-project.supabase.co',
                                    f'your-supabase-anon-key-here']:
            print(f"  ✅ {name}: 已配置")
        else:
            print(f"  ❌ {name}: 未配置")
            print(f"     提示: {hint}")
            all_required_valid = False
    
    # 检查可选配置
    print("\n⭕ 可选配置：")
    for key, info in optional.items():
        value = info['value']
        name = info['name']
        
        if value and value not in [f'your-{key.lower().replace("_", "-")}-here',
                                    f'tvly-your-tavily-api-key-here',
                                    f'sk-your-openai-key-here']:
            print(f"  ✅ {name}: 已配置")
        else:
            print(f"  ⚪ {name}: 未配置（使用默认）")
    
    # 检查 TTS 配置
    print("\n🎤 TTS 配置：")
    tts_provider = os.getenv("TTS_PROVIDER", "qwen")
    tts_voice = os.getenv("QWEN_TTS_VOICE", "Cherry")
    print(f"  📍 提供商: {tts_provider}")
    print(f"  🎵 音色: {tts_voice}")
    
    # 检查 RAG 配置
    print("\n🔍 RAG 配置：")
    vector_db = os.getenv("VECTOR_DB_PATH", "db5")
    mmr_lambda = os.getenv("RAG_MMR_LAMBDA", "0.5")
    print(f"  📁 向量库: {vector_db}")
    print(f"  🎯 多样性参数: {mmr_lambda}")
    
    # 总结
    print("\n" + "=" * 60)
    
    if all_required_valid:
        print("✅ 配置验证通过！可以开始使用。")
        print("\n下一步:")
        print("  1. 运行应用: streamlit run main.py")
        print("  2. 访问: http://localhost:8501")
        return True
    else:
        print("❌ 配置验证失败！请完成必需配置。")
        print("\n修复步骤:")
        print("  1. 编辑 .env 文件")
        print("  2. 填充缺失的 API Keys")
        print("  3. 重新运行: python verify_config.py")
        return False

if __name__ == "__main__":
    success = verify_config()
    sys.exit(0 if success else 1)

