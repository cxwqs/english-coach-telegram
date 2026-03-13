# English Coach Telegram Bot

一个基于 Telegram 的英语口语练习助手，配合语音发音功能，帮助中文学习者提升日常英语口语能力。

本仓库为 [nanobot](https://github.com/HKUDS/nanobot) 的 Skill 插件，可将 `english-daily-coach` 和 `english-pronunciation-audio` 放入 nanobot 的 skills 目录使用。

## 功能特点

- 🎯 **每日英语练习** - 用户主动触发，主题可自定义或让 bot 询问
- 🗣 **中英翻译** - 用户说中文，AI 翻译成自然的口语英文
- 💬 **回复示例** - 提供 3 个可复用的回复选项
- 📚 **单词讲解** - 附带中文释义
- 🎤 **语音发音** - 自动生成英文朗读音频
- 📝 **错误纠正** - 每 3-5 轮进行一次高价值错误纠正

## 项目结构

```
english-coach-telegram/
├── english-daily-coach/          # 主练习技能
│   └── SKILL.md                  # 技能定义
├── english-pronunciation-audio/  # 发音音频技能
│   ├── SKILL.md                  # 技能定义
│   ├── assets/
│   │   ├── tts-config.example.json  # 配置模板
│   │   └── tts-config.json         # 本地配置（复制 example 后填入 Key，勿提交）
│   └── scripts/
│       └── tts_openrouter.py     # TTS 音频生成脚本
└── README.md
```

## 快速开始

### 1. 配置文件

将 `english-pronunciation-audio/assets/tts-config.example.json` 复制为 `tts-config.json`，并填入你的 API Key：

```json
{
    "provider": "openai",
    "openai": {
        "apiKey": "YOUR_OPENAI_API_KEY",
        "model": "tts-1",
        "voice": "alloy",
        "response_format": "wav",
        "proxyUrl": "http://your-proxy:port"
    },
    "telegram": {
        "botToken": "YOUR_TELEGRAM_BOT_TOKEN",
        "chatId": "YOUR_CHAT_ID",
        "sendMethod": "sendAudio",
        "proxyUrl": "http://your-proxy:port"
    },
    "pronunciation": {
        "enabled": true,
        "accent": "general-american",
        "maxCharsPerReply": 300,
        "autoForSkill": "english-daily-coach",
        "timeoutMs": 30000,
        "sampleRate": 24000,
        "channels": 1,
        "sampleWidthBytes": 2
    }
}
```

### 2. 配置说明

- **provider**：`openai`（默认，纯 TTS 朗读）或 `openrouter`（对话式 audio 模型）
- **openai**：使用 OpenAI 官方 TTS API，直接朗读输入文本，无“回复”行为。需填入 `apiKey`，模型可选 `tts-1`、`tts-1-hd`
- **openrouter**：使用 OpenRouter 的 audio 模型（如 gpt-audio-mini），需在对应区块填入 Key
- **Telegram**：`botToken`、`chatId` 等请参考 [nanobot](https://github.com/HKUDS/nanobot) 与 Telegram 的配置文档，与 nanobot 主配置保持一致

### 3. 运行方式

```bash
# 测试发音脚本
python3 english-pronunciation-audio/scripts/tts_openrouter.py --text "Hello, how are you?"

# 提取英文文本（不生成音频）
python3 english-pronunciation-audio/scripts/tts_openrouter.py --text "Your reply text here" --extract-only
```

## 练习流程示例

```
🗣 英语练习

你说： 还行吧，实验有一点进展

➡️ It's going pretty well. I made some progress on the experiment today.

---

💬 你可以这样回复我：

① Not bad! I made some progress on my experiment today.
② It's going okay. The experiment is finally moving forward.
③ Pretty good! I had a small breakthrough in the lab.

---

📚 单词

• breakthrough — 突破
• experiment — 实验
• progress — 进展

---

🎯 我会这样继续问你：

"That's great! What kind of experiment is it? What progress did you make?"
```

## 依赖

- Python 3.8+
- OpenRouter API
- Telegram Bot API

## 许可证

MIT License

---

# English | 英文

## English Coach Telegram Bot

A Telegram-based English speaking practice assistant with pronunciation audio, designed for Chinese learners to improve daily spoken English.

This repo provides Skill plugins for [nanobot](https://github.com/HKUDS/nanobot). Copy `english-daily-coach` and `english-pronunciation-audio` into nanobot's skills directory.

### Features

- 🎯 **On-demand practice** - User initiates, topic is customizable or asked by bot
- 🗣 **Chinese→English translation** - Speak Chinese, get natural spoken English
- 💬 **Example responses** - 3 reusable reply options
- 📚 **Vocabulary notes** - Chinese definitions included
- 🎤 **Pronunciation audio** - Auto-generated TTS via OpenRouter
- 📝 **Error correction** - High-value corrections every 3–5 turns

### Quick Start

1. **Config**: Copy `tts-config.example.json` to `tts-config.json` and fill in TTS API keys.
2. **Telegram**: For `botToken`, `chatId`, etc., refer to [nanobot](https://github.com/HKUDS/nanobot) and Telegram configuration docs.
3. **Test**: `python3 english-pronunciation-audio/scripts/tts_openrouter.py --text "Hello, how are you?"`

### Dependencies

- Python 3.8+
- OpenRouter API
- Telegram Bot API

### License

MIT License
