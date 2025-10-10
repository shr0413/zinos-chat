"""
Supabase 连接测试脚本
测试数据库连接和交互记录功能
"""

import os
import uuid
from dotenv import load_dotenv
from supabase import create_client, Client

# 加载环境变量
load_dotenv()

def test_supabase_connection():
    """测试 Supabase 连接"""
    print("=" * 60)
    print("🔍 测试 Supabase 连接")
    print("=" * 60)
    
    # 1. 检查环境变量
    print("\n[1/4] 检查环境变量...")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url:
        print("❌ SUPABASE_URL 未设置")
        return False
    if not supabase_key:
        print("❌ SUPABASE_KEY 未设置")
        return False
    
    print(f"✅ SUPABASE_URL: {supabase_url[:30]}...")
    print(f"✅ SUPABASE_KEY: {supabase_key[:20]}...")
    
    # 2. 创建客户端
    print("\n[2/4] 创建 Supabase 客户端...")
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ 客户端创建成功")
    except Exception as e:
        print(f"❌ 客户端创建失败: {str(e)}")
        return False
    
    # 3. 测试表访问
    print("\n[3/4] 测试 interactions 表访问...")
    try:
        # 尝试读取最近 5 条记录
        response = supabase.table("interactions").select("*").limit(5).execute()
        print(f"✅ 表访问成功，找到 {len(response.data)} 条记录")
        
        if len(response.data) > 0:
            print(f"\n📊 最近一条记录:")
            latest = response.data[0]
            print(f"   - Session ID: {latest.get('session_id', 'N/A')}")
            print(f"   - 用户消息: {latest.get('user_msg', 'N/A')[:50]}...")
            print(f"   - 亲密度: {latest.get('intimacy_score', 'N/A')}")
        else:
            print("   ℹ️  表为空（尚无交互记录）")
            
    except Exception as e:
        print(f"❌ 表访问失败: {str(e)}")
        print("\n可能的原因:")
        print("   1. 表 'interactions' 不存在")
        print("   2. API Key 权限不足")
        print("   3. 网络连接问题")
        return False
    
    # 4. 测试写入权限
    print("\n[4/4] 测试写入权限...")
    try:
        # 生成测试用的 UUID
        test_session_id = str(uuid.uuid4())
        
        test_data = {
            "session_id": test_session_id,
            "user_msg": "测试连接",
            "ai_msg": "连接测试成功",
            "ai_name": "Test",
            "intimacy_score": 0.0,
            "sticker_awarded": None,
            "gift_given": False,
            "response_analysis": {}
        }
        
        response = supabase.table("interactions").insert(test_data).execute()
        print("✅ 写入测试成功")
        
        # 清理测试数据
        supabase.table("interactions").delete().eq("session_id", test_session_id).execute()
        print("✅ 测试数据已清理")
        
    except Exception as e:
        print(f"⚠️  写入测试失败: {str(e)}")
        print("   提示: 应用可以读取但无法写入数据")
    
    print("\n" + "=" * 60)
    print("✅ Supabase 连接测试通过！")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_supabase_connection()
    
    if success:
        print("\n✨ 下一步:")
        print("   运行: streamlit run main.py")
    else:
        print("\n❌ 请检查:")
        print("   1. .env 文件中的 SUPABASE_URL 和 SUPABASE_KEY")
        print("   2. Supabase 项目是否正常运行")
        print("   3. interactions 表是否已创建")
        print("   4. 网络连接是否正常")

