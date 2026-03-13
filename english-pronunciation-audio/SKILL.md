---
name: english-pronunciation-audio
description: Generate TTS audio for English practice replies and send via Telegram. Use together with english-daily-coach. Extracts spoken English lines, skips Chinese, and sends one audio file per reply. When user asks "怎么读", generate audio for the English sentence — do NOT explain pronunciation in text.
---

# English Pronunciation Audio

## CRITICAL Rules

1. This skill generates AUDIO files only. NEVER output text-based pronunciation guides (e.g. "vuh-LOR-unt", IPA symbols).
2. **When user asks "X怎么读"** (how to pronounce the sentence they sent): Pass ONLY the exact sentence X the user gave you. Example: user says "What would you like to order for lunch today?怎么读" → exec with `--text "What would you like to order for lunch today"`. Do NOT pass your reply or any extra text.
3. **When sending coaching reply**: Pass the full draft (你说/➡️/💬/📚/🎯) so the script extracts translation + examples + question.
4. Generate at most one audio file per reply.
5. Skip Chinese lines (lines starting with `提示:`, `你说:`, `📚`, `💬`).
6. Skip `You said:` lines. Only read `More natural:` and `Reusable phrase:` lines.
7. Skip vocabulary definitions (`• word — 释义`) and phonetic lines (IPA, "pronounced", "vuh-LOR-unt").
8. If the user ends the session, skip audio for the final reply.

## Supported Reply Shapes

Spoken content is extracted from:

- `➡️` line (translation)
- `①②③` lines (example sentences)
- Line after `🎯 我会这样继续问你：` (follow-up question)
- `Translation:` / `You can say:` / `Now you try:` / `More natural:` / `Reusable phrase:` (legacy labels)

## Script

- Use `scripts/tts_openrouter.py`.
- Pass the full draft reply text with `--text`. The script extracts spoken English automatically.
- Config: `assets/tts-config.json`.
- If script returns `no_spoken_text` or `too_long`, send text reply only.
- If script fails, do not block the text reply. Retry at most once.

## Reply Shaping

- Keep extracted English under 300 characters total.
- Keep Chinese on separate `提示:` lines.
- One template per reply for deterministic extraction.

## Debugging

- `--extract-only`: inspect extracted English as JSON.
- `--dry-run`: generate audio but skip Telegram upload.
- To verify what audio will be sent: `python3 scripts/tts_openrouter.py --text "your text" --extract-only`
