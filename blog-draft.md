# 我用 nanobot（小龙虾） 做了一个英语学习skill

## 为什么要做这个

学了很多年英语，阅读还行，一到开口就卡壳——这是很多中文学习者的常态。我想练日常口语，但不想：

- 约真人语伴（麻烦，还容易社恐）
- 背固定句型（枯燥，用不上）
- 用那些「AI 英语老师」App（要么收费，要么功能太重）

我平时用 **nanobot** 当个人 AI 助手，它支持 Telegram，可以挂各种 Skill。于是就想着：能不能在 nanobot 上做一个**轻量的英语口语练习 Skill**？用的时候跟它聊几句，不用就放着。

于是有了 [english-coach-telegram](https://github.com/cxwqs/english-coach-telegram)。

---

## 它能做什么

这是一个基于 nanobot 的 **Skill 插件组合**，包含两个技能：

### 1. english-daily-coach：日常口语教练

- 你说「来两句英文练练」「陪我练日常口语」就会启动，主题可自定义（如「今天练点餐」）或让 bot 询问
- 一次只问一个问题，节奏轻松，随时可说「结束」
- 你如果**说中文**，它会帮你翻译成自然的口语英文，并给 2～3 个可复用的回复示例
- 每 3～5 轮会纠正 2～3 个高价值错误（语法、表达）
- 每次回复会附带相关单词的中文释义

### 2. english-pronunciation-audio：发音音频

- 调用 TTS 生成朗读音频，通过 Telegram 发给你

---

## 一次练习长什么样

你发一句中文：

> 还行吧，实验有一点进展

它会回复：

```
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

如果哪句不会，就发信息给他，什么什么怎么读之类的。

---

### TTS 提供商可配置

发音部分支持多种 TTS 接口，不绑定某一家的 API，我用的是

- **OpenRouter(稳定大于一切)**：流式 chat+audio，适合 `gpt-audio-mini` 等

---

## 怎么用

1. 在 nanobot 的 `skills` 目录里放入 `english-daily-coach` 和 `english-pronunciation-audio`
2. 按 `tts-config.example.json` 复制并填写配置（TTS API Key、Telegram 等，可参考 nanobot 文档）
3. 对 bot 说「来两句英文练练」开始练习

详细说明见 [GitHub 仓库](https://github.com/cxwqs/english-coach-telegram)。

---

**项目地址**：<https://github.com/cxwqs/english-coach-telegram>
