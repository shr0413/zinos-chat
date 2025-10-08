# 🚀 立即测试 Qwen TTS

## ✅ 修复已完成

已采用 **qwen3-tts-flash 官方示例** 完全重写 TTS 模块！

---

## 📝 测试步骤

### 1. 重启应用
```powershell
# 停止当前应用（Ctrl+C）
.\start_app.bat
```

### 2. 观察启动日志
确认配置正确：
```
🎤 TTS 配置：
  📍 提供商: qwen
  🎵 音色: Cherry          ← 应显示 Cherry，不是 longxiaochun
```

### 3. 发送消息测试
在应用中输入任意消息，观察控制台输出。

---

## 🎯 预期正常输出

```
[TTS] Calling Qwen TTS (voice: Cherry)...
[TTS DEBUG] Model: qwen3-tts-flash, Voice: Cherry
[TTS DEBUG] Response received, checking output...
[TTS DEBUG] Audio URL: http://dashscope-result-sh.oss-cn-shanghai.aliyuncs.com/...
[TTS DEBUG] ✅ Success! Audio size: 45678 bytes
[TTS] ✅ Qwen TTS succeeded
```

然后**应该听到自然的语音播放**！🎉

---

## ❌ 如果还是失败

### 完整复制以下信息发给我：

1. **启动日志**（从 `.\start_app.bat` 开始的所有输出）
2. **TTS 错误信息**（所有 `[TTS]` 开头的行）
3. **完整错误栈**（如果有 `Traceback`）

特别注意：
- `[TTS DEBUG] Model:` 后面的模型名
- `[TTS DEBUG] Voice:` 后面的音色名
- 任何 Python 错误栈

---

## 🔧 快速排查

### 问题 1: API Key 错误
```
❌ Missing API Key
```
**解决**: 确认 `.env` 中 `DASHSCOPE_API_KEY` 已填写

### 问题 2: 网络错误
```
❌ Failed to connect / timeout
```
**解决**: 检查网络，确保可访问 `dashscope.aliyuncs.com`

### 问题 3: 权限错误
```
❌ Unauthorized / Invalid API Key
```
**解决**: 访问 https://dashscope.aliyun.com/ 确认 API Key 有效

---

## 📊 成功标志

- ✅ 控制台显示 `[TTS] ✅ Qwen TTS succeeded`
- ✅ 浏览器自动播放语音
- ✅ 音质自然，无机器感
- ✅ 音色可在 UI 中切换（Cherry/Ethan）

---

**立即测试，把结果告诉我！** 🚀

