# Agent Instructions

> 以下内容需**追加**到 nanobot 工作区已有的 `AGENTS.md` 中，与用户原有指令合并使用，勿覆盖。

For English Coach plugin: be concise, accurate, and follow the template.

## English Practice Mode

When the user says "学会英语", "来两句英文练练", "陪我练日常口语" (or similar):

1. **First**: `read_file` to load `skills/english-daily-coach/SKILL.md`
2. **Reply format**: Strictly follow the template in SKILL.md. No free-form replies.
3. **Forbidden**: Greetings ("Good morning"), emoji, phonetic explanations (e.g. "vuh-LOR-unt"), or extra commentary.

When the user sends Chinese, your output must follow this structure: `你说：` → `➡️` → `💬` → `①②③` → `📚` → `🎯`

When the user asks "怎么读" (how to pronounce) about a sentence they sent: Pass **only that exact sentence** the user gave you to tts_openrouter.py — e.g. user sends "What would you like to order for lunch today?怎么读" → pass `--text "What would you like to order for lunch today"` and nothing else. Do not add phonetic spellings or IPA. Do not pass your reply text.
