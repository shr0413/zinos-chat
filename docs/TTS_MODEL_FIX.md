# 🔧 TTS 模型名称修复

## 问题
❌ **错误**：`Model not found (qwen3-tts-flash)!`

## 原因
`qwen3-tts-flash` 模型不存在或未开通

## ✅ 解决方案

### 方法 1: 修改 .env 文件（推荐）

编辑 `.env` 文件，修改 TTS 模型配置：

```bash
# 旧的（不可用）
QWEN_TTS_MODEL=qwen3-tts-flash
QWEN_TTS_VOICE=Cherry

# 新的（可用）- 试试以下选项之一：

# 选项 1: CosyVoice（推荐）
QWEN_TTS_MODEL=cosyvoice-v1
QWEN_TTS_VOICE=longxiaochun     # 女声
# 或
QWEN_TTS_VOICE=longyaoyao       # 女声

# 选项 2: Sambert 中文
QWEN_TTS_MODEL=sambert-zhichu-v1
QWEN_TTS_VOICE=zhichu

# 选项 3: Sambert 英语
QWEN_TTS_MODEL=sambert-zhiying-v1
QWEN_TTS_VOICE=zhiying
```

### 方法 2: 查询你的可用模型

访问阿里云控制台查看已开通的模型：
1. 访问：https://dashscope.console.aliyun.com/
2. 进入"模型广场" → "语音合成"
3. 查看已开通的模型名称
4. 更新 `.env` 中的 `QWEN_TTS_MODEL`

### 方法 3: 临时降级到 gTTS

如果暂时无法解决，可以继续使用 gTTS（已自动降级）：

```bash
# 在 .env 中
TTS_PROVIDER=gtts  # 改为 gtts
```

---

## 🚀 快速测试

### Step 1: 修改 .env

```powershell
notepad .env
```

修改为：
```bash
QWEN_TTS_MODEL=cosyvoice-v1
QWEN_TTS_VOICE=longxiaochun
```

### Step 2: 重启应用

```powershell
.\start_app.bat
```

### Step 3: 测试

发送消息，查看日志：
- ✅ 成功：`[TTS DEBUG] Audio URL: http://...`
- ❌ 失败：尝试其他模型

---

## 📝 可用模型参考

### CosyVoice 系列（推荐）

```bash
QWEN_TTS_MODEL=cosyvoice-v1

# 可用音色：
QWEN_TTS_VOICE=longxiaochun    # 女声-小春
QWEN_TTS_VOICE=longyaoyao      # 女声-瑶瑶
QWEN_TTS_VOICE=longxiaobei     # 男声-小北
```

### Sambert 系列

```bash
# 中文
QWEN_TTS_MODEL=sambert-zhichu-v1
QWEN_TTS_VOICE=zhichu

# 英文
QWEN_TTS_MODEL=sambert-zhiying-v1
QWEN_TTS_VOICE=zhiying
```

---

## 💡 推荐配置

**Maria 角色（英文为主）**：

```bash
QWEN_TTS_MODEL=cosyvoice-v1
QWEN_TTS_VOICE=longxiaochun
```

**中文场景**：

```bash
QWEN_TTS_MODEL=sambert-zhichu-v1
QWEN_TTS_VOICE=zhichu
```

---

**立即修复**：

1. 编辑 `.env`：`notepad .env`
2. 修改模型名称
3. 重启：`.\start_app.bat`
4. 测试语音

告诉我哪个模型可用！🎤

