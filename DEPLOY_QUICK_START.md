# 🚀 快速部署指南 - 5 分钟上线！

## 📋 部署前检查清单

### ✅ 必需账户
- [ ] GitHub 账户
- [ ] Qwen API Key（https://dashscope.aliyun.com/）
- [ ] Supabase 账户（https://app.supabase.com/）

### ✅ 必需文件（已准备好）
- [x] `main.py` - 主应用
- [x] `tts_utils.py` - TTS 工具
- [x] `requirements.txt` - 依赖列表
- [x] `.gitignore` - Git 忽略规则
- [x] `.streamlit/config.toml` - 配置文件

---

## 🎯 3 步部署

### 步骤 1: 推送到 GitHub（2 分钟）

```bash
# 运行自动化脚本
./deploy_to_streamlit.bat
```

**或手动操作**:
```bash
# 1. 初始化 Git（如果还没有）
git init

# 2. 添加所有文件
git add .

# 3. 创建提交
git commit -m "Deploy Zino's Chat"

# 4. 关联 GitHub 仓库（替换为你的仓库 URL）
git remote add origin https://github.com/你的用户名/zinos-chat.git

# 5. 推送
git branch -M main
git push -u origin main
```

---

### 步骤 2: 在 Streamlit Cloud 部署（2 分钟）

1. **访问**: https://streamlit.io/cloud

2. **登录**: 点击 "Sign in with GitHub"

3. **新建应用**: 点击 "New app"

4. **填写信息**:
   - **Repository**: `你的用户名/zinos-chat`
   - **Branch**: `main`
   - **Main file path**: `main.py`

5. **点击**: "Deploy!"

---

### 步骤 3: 配置环境变量（1 分钟）

**在部署页面点击 "Advanced settings" → "Secrets"**

粘贴以下内容（**替换为你的实际值**）:

```toml
DASHSCOPE_API_KEY = "sk-你的Qwen_API_Key"
SUPABASE_URL = "https://你的项目.supabase.co"
SUPABASE_KEY = "你的Supabase_Anon_Key"
QWEN_MODEL_NAME = "qwen-turbo"
QWEN_EMBEDDING_MODEL = "text-embedding-v2"
QWEN_TTS_MODEL = "qwen3-tts-flash"
QWEN_TTS_VOICE = "Cherry"
```

**保存** → 应用自动重启 → **完成！** 🎉

---

## 🔗 获取应用链接

部署完成后，你的应用 URL：
```
https://你的应用名.streamlit.app
```

**分享给朋友**，让他们体验 Fred！

---

## 🔑 获取 API Keys

### 1. Qwen API Key（免费）

1. 访问：https://dashscope.aliyun.com/
2. 登录/注册（支持微信/支付宝）
3. 进入 **"API-KEY 管理"**
4. 创建 API Key
5. 复制保存（格式：`sk-xxxxx`）

**免费额度**:
- 100 万 tokens/月（LLM）
- 包含 TTS 和 Embeddings

---

### 2. Supabase（免费）

1. 访问：https://app.supabase.com/
2. 用 GitHub 登录
3. 创建新项目
4. 进入 **"Settings" → "API"**
5. 复制：
   - **Project URL**: `https://xxx.supabase.co`
   - **anon public key**: `eyJxxx...`

**创建表**（可选，用于日志）:
```sql
CREATE TABLE interactions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id TEXT,
  user_msg TEXT,
  ai_msg TEXT,
  intimacy_score FLOAT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## ⚠️ 常见问题

### 1. 部署失败：ModuleNotFoundError

**解决**:
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

---

### 2. TTS 不工作

**检查**:
- ✅ `DASHSCOPE_API_KEY` 正确
- ✅ API Key 已开通 TTS 权限
- ✅ Secrets 配置无误

---

### 3. 向量数据库为空

**原因**: Streamlit Cloud 重启会清空文件

**解决**: 应用会自动检测并提示上传文档

或在代码中添加：
```python
@st.cache_resource
def init_vector_db():
    # 首次部署时自动构建
    if not os.path.exists('db5_qwen'):
        rebuild_db()
```

---

### 4. 应用访问慢

**优化**:
1. 启用缓存：
   ```python
   @st.cache_data
   @st.cache_resource
   ```

2. 减少 API 调用

3. 优化 RAG 参数

---

## 📊 部署后检查

### ✅ 功能测试

- [ ] 语言切换（英语/葡萄牙语）
- [ ] 音色切换（Cherry/Ethan）
- [ ] 聊天对话
- [ ] TTS 语音
- [ ] Friendship Score
- [ ] Sticker 奖励
- [ ] Fact Check

### ✅ 性能测试

- [ ] 首次加载时间 < 5s
- [ ] 对话响应时间 < 3s
- [ ] TTS 生成时间 < 1s

---

## 🎉 部署成功！

### 分享你的应用

```markdown
🐦 **Zino's Chat 现已上线！**

🔗 **体验地址**: https://你的应用名.streamlit.app

✨ **特色功能**:
- 🌍 双语支持（英语/葡萄牙语）
- 🎤 自然语音（Qwen TTS）
- 🤖 AI 对话（Qwen LLM）
- 🎁 互动奖励系统

与 Fred the Zino's Petrel 一起探索生物多样性！
```

---

## 📈 监控和维护

### Streamlit Cloud 控制台

- **查看日志**: 实时应用日志
- **监控性能**: CPU/内存使用
- **查看分析**: 用户访问统计
- **管理 Secrets**: 更新环境变量

### 自动更新

```bash
# 修改代码后
git add .
git commit -m "Update feature"
git push

# Streamlit Cloud 自动检测并重新部署！
```

---

## 🆘 需要帮助？

- 📖 **详细指南**: [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md)
- 🐛 **报告问题**: [GitHub Issues](https://github.com/你的用户名/zinos-chat/issues)
- 💬 **Streamlit 论坛**: https://discuss.streamlit.io

---

**祝部署顺利！** 🚀✨

