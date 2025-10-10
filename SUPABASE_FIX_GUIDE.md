# 🔧 Supabase 连接问题修复指南

## ✅ 问题已修复

**问题：** Streamlit 缓存机制与 Supabase 客户端不兼容  
**解决：** 将全局连接改为函数内部创建

---

## 🚀 快速验证

### 1. 安装依赖
```bash
pip install supabase
```

### 2. 测试连接
```bash
python test_supabase.py
```

**期望输出：**
```
============================================================
🔍 测试 Supabase 连接
============================================================

[1/4] 检查环境变量...
✅ SUPABASE_URL: https://xxx.supabase.co...
✅ SUPABASE_KEY: eyJhbGciOiJIUzI1NiIs...

[2/4] 创建 Supabase 客户端...
✅ 客户端创建成功

[3/4] 测试 interactions 表访问...
✅ 表访问成功，找到 X 条记录

[4/4] 测试写入权限...
✅ 写入测试成功
✅ 测试数据已清理

============================================================
✅ Supabase 连接测试通过！
============================================================
```

---

## 🔍 故障排查

### ❌ 问题 1: 环境变量未设置

**错误：**
```
❌ SUPABASE_URL 未设置
❌ SUPABASE_KEY 未设置
```

**解决：**
1. 检查 `.env` 文件是否存在
2. 确认以下配置已填写：
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-supabase-anon-key
   ```

---

### ❌ 问题 2: 表不存在

**错误：**
```
❌ 表访问失败: relation "public.interactions" does not exist
```

**解决：**

在 Supabase 控制台执行以下 SQL 创建表：

```sql
-- 创建 interactions 表
CREATE TABLE IF NOT EXISTS public.interactions (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    session_id TEXT NOT NULL,
    user_msg TEXT,
    ai_msg TEXT,
    ai_name TEXT DEFAULT 'Maria the Zino''s Petrel',
    intimacy_score FLOAT DEFAULT 0,
    sticker_awarded TEXT,
    gift_given BOOLEAN DEFAULT FALSE,
    response_analysis JSONB DEFAULT '{}'::jsonb
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_interactions_session_id 
ON public.interactions(session_id);

CREATE INDEX IF NOT EXISTS idx_interactions_created_at 
ON public.interactions(created_at DESC);

-- 启用 RLS（行级安全）
ALTER TABLE public.interactions ENABLE ROW LEVEL SECURITY;

-- 创建策略（允许匿名插入和读取）
CREATE POLICY "Allow public insert" 
ON public.interactions 
FOR INSERT 
TO anon 
WITH CHECK (true);

CREATE POLICY "Allow public select" 
ON public.interactions 
FOR SELECT 
TO anon 
USING (true);
```

**步骤：**
1. 登录 [Supabase Dashboard](https://app.supabase.com/)
2. 选择您的项目
3. 左侧菜单 → SQL Editor
4. 粘贴上述 SQL
5. 点击 "Run"

---

### ❌ 问题 3: API Key 权限不足

**错误：**
```
❌ 表访问失败: permission denied for table interactions
```

**解决：**

1. **检查 API Key 类型**
   - 使用 `anon` (public) key，不要使用 `service_role` key
   - 在 Supabase Dashboard → Settings → API → Project API keys

2. **检查 RLS 策略**
   - 确保上述 SQL 中的策略已创建
   - 或者临时禁用 RLS（不推荐）：
     ```sql
     ALTER TABLE public.interactions DISABLE ROW LEVEL SECURITY;
     ```

---

### ❌ 问题 4: 网络连接问题

**错误：**
```
❌ 客户端创建失败: Connection timeout
```

**解决：**
1. 检查网络连接
2. 确认 Supabase 项目未暂停
3. 检查防火墙设置
4. 尝试使用 VPN

---

## 🎯 代码修复详情

### 修复前（有问题）
```python
# 全局创建连接（会导致缓存错误）
conn = st.connection("supabase", type=SupabaseConnection)

def log_interaction(...):
    execute_query(conn.table("interactions").insert(data))
```

### 修复后（正确）
```python
# 函数内部创建连接（避免缓存问题）
def get_supabase_connection():
    return st.connection("supabase", type=SupabaseConnection)

def log_interaction(...):
    conn = get_supabase_connection()  # 每次调用时创建
    execute_query(conn.table("interactions").insert(data))
```

---

## ✅ 验证修复

### 1. 重启应用
```bash
# 停止当前应用（Ctrl+C）
streamlit run main.py
```

### 2. 测试交互
- 在应用中发送一条消息
- 检查终端输出，应该看到：
  ```
  Logged interaction to Supabase: <session_id>
  ```

### 3. 检查数据库
- 登录 Supabase Dashboard
- Table Editor → interactions
- 应该看到新记录

---

## 📞 仍然有问题？

**运行完整诊断：**
```bash
python test_supabase.py
```

**查看详细错误：**
- 检查终端完整错误信息
- 查看 Supabase Dashboard → Logs
- 确认所有依赖已安装：`pip list | grep supabase`

---

## 📚 相关资源

- [Supabase 文档](https://supabase.com/docs)
- [st-supabase-connection](https://github.com/SiddhantSadangi/st_supabase_connection)
- [Streamlit 缓存机制](https://docs.streamlit.io/library/advanced-features/caching)

---

*修复完成时间：2025-10-09*

