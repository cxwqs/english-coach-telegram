#!/usr/bin/env python3
"""Generate pronunciation audio with OpenRouter and send it to Telegram."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import re
import sys
import tempfile
import urllib.error
import urllib.request
import uuid
import wave
from pathlib import Path

STRIP_LABELS = (
    "more natural:",
    "reusable phrase:",
    "translation:",
    "you mean:",
    "now you try:",
    "you can say:",
)
SKIP_LABELS = ("提示:", "you said:")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate pronunciation audio with OpenRouter and send it to Telegram."
    )
    parser.add_argument("--text", help="Full reply text. English lines will be extracted automatically.")
    parser.add_argument("--text-file", help="Read reply text from a file.")
    parser.add_argument(
        "--config",
        default=str(Path(__file__).resolve().parent.parent / "assets" / "tts-config.json"),
        help="Path to tts-config.json",
    )
    parser.add_argument(
        "--extract-only",
        action="store_true",
        help="Only print extracted spoken English as JSON.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate audio but skip Telegram upload.",
    )
    return parser.parse_args()


def read_input_text(args: argparse.Namespace) -> str:
    if args.text:
        return args.text
    if args.text_file:
        return Path(args.text_file).read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise SystemExit("Provide --text, --text-file, or stdin input.")


def load_config(config_path: str) -> dict:
    return json.loads(Path(config_path).read_text(encoding="utf-8"))


def normalize_line(line: str) -> str:
    line = line.strip()
    line = re.sub(r"^[*\-•]\s+", "", line)
    line = re.sub(r"^\d+\.\s+", "", line)
    line = line.replace("`", "").replace("**", "")
    return " ".join(line.split())


def looks_like_english(text: str) -> bool:
    letters = re.findall(r"[A-Za-z]", text)
    if len(letters) < 3:
        return False
    cjk = re.findall(r"[\u4e00-\u9fff]", text)
    return len(letters) >= max(3, len(cjk) * 2)


def strip_supported_label(line: str) -> str:
    lowered = line.lower()
    for label in STRIP_LABELS:
        if lowered.startswith(label):
            return normalize_line(line.split(":", 1)[1]) if ":" in line else ""
    return line


def extract_spoken_text(reply_text: str) -> str:
    spoken_lines: list[str] = []
    for raw_line in reply_text.splitlines():
        line = normalize_line(raw_line)
        if not line:
            continue
        lowered = line.lower()
        if lowered.startswith(SKIP_LABELS):
            continue
        line = strip_supported_label(line)
        if not line:
            continue
        if not looks_like_english(line):
            continue
        spoken_lines.append(line)
    return "\n".join(spoken_lines)


def ensure_length_limit(text: str, max_chars: int) -> tuple[bool, int]:
    return len(text) <= max_chars, len(text)


def build_opener(proxy_url: str | None) -> urllib.request.OpenerDirector:
    handlers: list[urllib.request.BaseHandler] = []
    if proxy_url:
        handlers.append(
            urllib.request.ProxyHandler(
                {
                    "http": proxy_url,
                    "https": proxy_url,
                }
            )
        )
    return urllib.request.build_opener(*handlers)


def join_url(base: str, path: str) -> str:
    return base.rstrip("/") + "/" + path.lstrip("/")


def call_openrouter_tts(text: str, config: dict) -> tuple[bytes, list[dict]]:
    openrouter_cfg = config["openrouter"]
    pronunciation_cfg = config["pronunciation"]
    opener = build_opener(openrouter_cfg.get("proxyUrl"))
    payload = {
        "model": openrouter_cfg["model"],
        "stream": True,
        "modalities": ["text", "audio"],
        "audio": {
            "voice": openrouter_cfg["voice"],
            "format": openrouter_cfg["format"],
        },
        "messages": [
            {
                "role": "system",
                "content": (
                    "Read the provided English exactly. "
                    "Use clear General American pronunciation for an English learner. "
                    "Speak at a natural, moderate pace. "
                    "Do not translate or add extra words."
                ),
            },
            {
                "role": "user",
                "content": text,
            },
        ],
    }
    request = urllib.request.Request(
        join_url(openrouter_cfg["baseUrl"], "/chat/completions"),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {openrouter_cfg['apiKey']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    timeout = int(pronunciation_cfg.get("timeoutMs", 30000)) / 1000.0
    chunks: list[dict] = []
    audio_parts: list[str] = []
    try:
        with opener.open(request, timeout=timeout) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line or line.startswith(":") or not line.startswith("data:"):
                    continue
                payload_text = line[5:].strip()
                if payload_text == "[DONE]":
                    break
                try:
                    chunk = json.loads(payload_text)
                except json.JSONDecodeError:
                    continue
                chunks.append(chunk)
                audio_chunk = find_audio_data(chunk)
                if audio_chunk:
                    audio_parts.append(audio_chunk)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenRouter HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"OpenRouter network error: {exc}") from exc

    audio_b64 = "".join(audio_parts)
    if not audio_b64:
        raise RuntimeError(
            "OpenRouter stream did not include audio data: "
            + json.dumps(chunks[-3:], ensure_ascii=False)[:600]
        )
    try:
        audio_bytes = base64.b64decode(audio_b64)
    except ValueError as exc:
        raise RuntimeError("Failed to decode streamed OpenRouter audio payload.") from exc
    return audio_bytes, chunks


def find_audio_data(payload: object) -> str | None:
    if isinstance(payload, dict):
        audio = payload.get("audio")
        if isinstance(audio, dict):
            data = audio.get("data")
            if isinstance(data, str) and data:
                return data
        for value in payload.values():
            found = find_audio_data(value)
            if found:
                return found
    elif isinstance(payload, list):
        for item in payload:
            found = find_audio_data(item)
            if found:
                return found
    return None


def write_wav_file(audio_bytes: bytes, config: dict) -> Path:
    pronunciation_cfg = config["pronunciation"]
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_path = Path(tmp_file.name)
    with wave.open(str(tmp_path), "wb") as wav_file:
        wav_file.setnchannels(int(pronunciation_cfg.get("channels", 1)))
        wav_file.setsampwidth(int(pronunciation_cfg.get("sampleWidthBytes", 2)))
        wav_file.setframerate(int(pronunciation_cfg.get("sampleRate", 24000)))
        wav_file.writeframes(audio_bytes)
    return tmp_path


def build_multipart_form(fields: dict[str, str], file_field: str, file_path: Path) -> tuple[bytes, str]:
    boundary = f"----nanobot-{uuid.uuid4().hex}"
    content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    parts: list[bytes] = []

    for name, value in fields.items():
        parts.append(f"--{boundary}\r\n".encode("utf-8"))
        parts.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
        parts.append(str(value).encode("utf-8"))
        parts.append(b"\r\n")

    file_bytes = file_path.read_bytes()
    parts.append(f"--{boundary}\r\n".encode("utf-8"))
    parts.append(
        (
            f'Content-Disposition: form-data; name="{file_field}"; '
            f'filename="{file_path.name}"\r\n'
        ).encode("utf-8")
    )
    parts.append(f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"))
    parts.append(file_bytes)
    parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(parts), boundary


def send_audio_to_telegram(audio_path: Path, text: str, config: dict) -> dict:
    telegram_cfg = config["telegram"]
    opener = build_opener(telegram_cfg.get("proxyUrl"))
    fields = {
        "chat_id": telegram_cfg["chatId"],
        "title": "English pronunciation",
        "performer": "nanobot",
        "caption": text if len(text) <= 1024 else text[:1021] + "...",
    }
    body, boundary = build_multipart_form(fields, "audio", audio_path)
    request = urllib.request.Request(
        join_url(
            f"https://api.telegram.org/bot{telegram_cfg['botToken']}",
            f"/{telegram_cfg['sendMethod']}",
        ),
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    timeout = int(config["pronunciation"].get("timeoutMs", 30000)) / 1000.0
    try:
        with opener.open(request, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Telegram network error: {exc}") from exc

    if not result.get("ok"):
        raise RuntimeError(f"Telegram rejected audio upload: {json.dumps(result, ensure_ascii=False)}")
    return result


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    full_text = read_input_text(args)
    spoken_text = extract_spoken_text(full_text)
    max_chars = int(config["pronunciation"].get("maxCharsPerReply", 300))
    within_limit, char_count = ensure_length_limit(spoken_text, max_chars)

    if not spoken_text:
        print(json.dumps({"status": "no_spoken_text"}, ensure_ascii=False))
        return 0

    if not within_limit:
        print(
            json.dumps(
                {
                    "status": "too_long",
                    "chars": char_count,
                    "maxCharsPerReply": max_chars,
                },
                ensure_ascii=False,
            )
        )
        return 0

    if args.extract_only:
        print(
            json.dumps(
                {
                    "status": "ok",
                    "spokenText": spoken_text,
                    "chars": char_count,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    audio_bytes, chunks = call_openrouter_tts(spoken_text, config)
    tmp_path = write_wav_file(audio_bytes, config)

    try:
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "status": "audio_generated",
                        "chars": char_count,
                        "spokenText": spoken_text,
                        "file": str(tmp_path),
                        "chunks": len(chunks),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0

        telegram_result = send_audio_to_telegram(tmp_path, spoken_text, config)
        print(
            json.dumps(
                {
                    "status": "sent",
                    "chars": char_count,
                    "spokenText": spoken_text,
                    "messageId": telegram_result.get("result", {}).get("message_id"),
                    "chunks": len(chunks),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
