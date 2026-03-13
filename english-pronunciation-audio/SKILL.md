---
name: english-pronunciation-audio
description: Generate Telegram pronunciation audio files for English practice replies using OpenRouter audio output and the Telegram Bot API. Use together with english-daily-coach when the user is practicing spoken English, when the assistant reply contains short English lines that should be heard aloud, or when the user asks how an English sentence is pronounced. Extract only the spoken English lines, skip Chinese guidance such as lines prefixed with "提示:", and send at most one audio file per reply.
---

# English Pronunciation Audio

## Operating Mode

- Use this skill together with `english-daily-coach` or whenever the user wants to hear how an English sentence is pronounced.
- Generate at most one audio file per reply.
- Only read the English lines that should be spoken aloud.
- Skip Chinese guidance lines, especially lines prefixed with `提示:`.
- Skip error examples such as `You said:`. Only read corrected lines such as `More natural:` and `Reusable phrase:`.
- If the user ends the session, skip audio for the final closing reply.

## Supported Reply Shapes

- This skill assumes `english-daily-coach` uses one fixed template per reply.
- Supported labels are:
  - `Translation:`
  - `You can say:`
  - `Now you try:`
  - `More natural:`
  - `Reusable phrase:`
- `You can say:` is a container label only and is not spoken.
- Bullet lines under `You can say:` are spoken.
- `提示:` and `You said:` are ignored.

## Script

- Use `scripts/tts_openrouter.py`.
- Pass the full draft reply text with `--text`. The script extracts the spoken English automatically.
- The script reads configuration from `assets/tts-config.json`, calls OpenRouter TTS in streaming mode, wraps the returned `pcm16` audio into a temporary `.wav`, uploads it with Telegram `sendAudio`, and deletes the temporary file.
- If the script returns `no_spoken_text` or `too_long`, send only the normal text reply.
- If the script fails, do not block the normal reply and do not retry more than once.

Example:

```bash
python3 scripts/tts_openrouter.py --text "Translation: I don't know how to say it.\nYou can say:\n- Let me think about it.\n- That's a good question.\nNow you try: What do you want to say first?\n提示: 先选一句。"
```

## Reply Shaping

- Keep each spoken reply concise.
- Keep the extracted English under 300 characters total.
- Keep Chinese hints on separate lines with the `提示:` prefix.
- Use only one template per reply so extraction stays deterministic.

## Debugging

- Use `--extract-only` to inspect which English lines will be spoken.
- Use `--dry-run` to skip Telegram upload after audio generation if you only need to verify the TTS call.
