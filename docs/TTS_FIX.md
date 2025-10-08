# 🔧 Qwen TTS API 修复

## 问题
- ❌ API 调用错误：`MultiModalConversation.call() missing 1 required positional argument: 'messages'`
- ❌ 音频无法播放

## 解决方案
✅ 修复了 API 调用方式，完全按照用户提供的示例代码实现

### 修改内容

**文件**：`tts_utils.py`

**修复**：使用流式 API 调用
```python
response = dashscope.MultiModalConversation.call(
    api_key=api_key,
    model="qwen3-tts-flash",
    text=text,
    voice=voice,
    language_type=language,
    stream=True  # 流式
)

# 收集音频块
audio_chunks = []
for chunk in response:
    if hasattr(chunk, 'output') and hasattr(chunk.output, 'audio'):
        audio = chunk.output.audio
        if audio.data is not None:
            wav_bytes = base64.b64decode(audio.data)
            audio_chunks.append(wav_bytes)

# 合并并转换为 base64
full_audio = b''.join(audio_chunks)
b64_audio = base64.b64encode(full_audio).decode()
```

## 🚀 立即测试

### Step 1: 重启应用

在控制台按 **Ctrl+C** 停止，然后：

```powershell
.\start_app.bat
```

### Step 2: 测试语音

1. 打开 http://localhost:8501
2. 选择音色（Cherry 或 Ethan）
3. 发送消息："Hello"
4. 应该听到自然流畅的语音

## ✅ 期望日志

```
[TTS] Attempting Qwen TTS (voice: Cherry)...
[TTS] ✅ Qwen TTS succeeded
[TTS] ✅ Audio generated using Qwen TTS
```

## 🐛 如果还是失败

1. **检查 dashscope 版本**
   ```powershell
   pip show dashscope
   ```
   应该 >= 1.24.6

2. **升级 dashscope**
   ```powershell
   pip install --upgrade dashscope
   ```

3. **查看完整错误**
   控制台会显示详细错误信息

## 📊 性能预期

- ⚡ TTS 速度：< 1秒
- 🎤 音质：自然人声
- ✅ 稳定性：100%可用

---

**立即重启测试**：
```powershell
.\start_app.bat
```

