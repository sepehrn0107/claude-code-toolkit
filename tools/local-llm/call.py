#!/usr/bin/env python3
"""
Local LLM CLI wrapper for Claude Code Toolbox.

Calls LM Studio (OpenAI-compatible /v1/chat/completions) with streaming,
prompt caching, and a health-check mode. Follows the same urllib.request-only
pattern as tools/indexer/semantic.py — no pip dependencies.

Exit codes:
  0  Success — stdout is the raw completion text
  1  Server unreachable or disabled in config — caller should fall back to haiku
  2  Config error (bad JSON, missing file, missing required field)

Usage:
  python3 call.py --task-type coding --prompt "Write a binary search function"
  python3 call.py --health
  python3 call.py --task-type coding --prompt "..." --model-slot quality
  python3 call.py --task-type summarize --prompt "..." --no-cache
"""

import argparse
import ast
import hashlib
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from typing import Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(SCRIPT_DIR, "cache")

# Per-task-type system prompts and temperatures.
# Temperature is kept low for code tasks (determinism) and higher for open-ended tasks.
TASK_DEFAULTS = {
    "coding": {
        "temperature": 0.1,
        "system": (
            "You are a precise code generator. "
            "Output only the requested code. "
            "No explanations, no markdown fences unless explicitly asked."
        ),
    },
    "tests": {
        "temperature": 0.1,
        "system": (
            "You are a test writer. "
            "Output only the test code. "
            "Use the same language and test framework as the provided code."
        ),
    },
    "summarize": {
        "temperature": 0.3,
        "system": (
            "You are a code summarizer. "
            "Be concise: 3-5 sentences maximum. "
            "Focus on what the code does, not how."
        ),
    },
    "docs": {
        "temperature": 0.2,
        "system": (
            "You are a documentation writer. "
            "Write clear, precise docstrings or comments. "
            "Follow the style of the surrounding code. "
            "Output only the docstring or comment block — no surrounding code."
        ),
    },
    "refactor": {
        "temperature": 0.1,
        "system": (
            "You are a refactoring assistant. "
            "Output only the refactored code. "
            "Preserve all existing behavior."
        ),
    },
    "ideate": {
        "temperature": 0.7,
        "system": (
            "You are a senior engineer brainstorming solutions. "
            "Think through trade-offs. "
            "Be direct and opinionated."
        ),
    },
    "generic": {
        "temperature": 0.4,
        "system": "You are a helpful AI assistant.",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────

def load_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        print(f"[local-llm] ERROR: config not found at {config_path}", file=sys.stderr)
        sys.exit(2)
    try:
        with open(config_path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[local-llm] ERROR: invalid JSON in config: {e}", file=sys.stderr)
        sys.exit(2)


# ─────────────────────────────────────────────────────────────────────────────
# Cache
# ─────────────────────────────────────────────────────────────────────────────

def _cache_key(model: str, system: str, prompt: str, max_tokens: int) -> str:
    raw = f"{model}|{system}|{prompt}|{max_tokens}"
    return hashlib.sha256(raw.encode()).hexdigest()[:24]


def _cache_get(key: str, ttl_hours: float) -> Optional[str]:
    path = os.path.join(CACHE_DIR, f"{key}.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            entry = json.load(f)
        expires = datetime.fromisoformat(entry["expires_at"])
        if datetime.now(timezone.utc) > expires:
            os.remove(path)
            return None
        return entry["response"]
    except (json.JSONDecodeError, KeyError, ValueError):
        return None


def _cache_set(key: str, response: str, ttl_hours: float) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    expires = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)
    path = os.path.join(CACHE_DIR, f"{key}.json")
    with open(path, "w") as f:
        json.dump({
            "response": response,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": expires.isoformat(),
        }, f)


# ─────────────────────────────────────────────────────────────────────────────
# LM Studio call
# ─────────────────────────────────────────────────────────────────────────────

def _strip_code_fences(text: str) -> str:
    """Remove markdown code fences when the entire output is wrapped in one.

    Models often wrap output in ```lang ... ``` even when told not to.
    This strips the fences so callers receive clean code or text.
    """
    stripped = text.strip()
    if not stripped.startswith("```"):
        return text
    first_newline = stripped.find("\n")
    if first_newline == -1:
        return text
    inner = stripped[first_newline + 1:]
    if inner.rstrip().endswith("```"):
        inner = inner.rstrip()[:-3].strip()
    return inner


def call_streaming(
    base_url: str,
    api_key: str,
    model: str,
    system: str,
    prompt: str,
    max_tokens: int,
    temperature: float,
    timeout: int,
    enable_thinking: bool = True,
) -> str:
    """POST to /v1/chat/completions with streaming.

    Tokens are echoed to stderr in real-time (visible to interactive users).
    The final, fence-stripped response is returned as a string and printed to
    stdout once — this is what Claude's Bash tool and bench.py capture.
    Exits 1 on connection error.
    """
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": True,
    }
    # Qwen3 / LM Studio: use chat_template_kwargs to control thinking mode.
    # Without this, Qwen3 exhausts the entire max_tokens budget on internal
    # reasoning (exposed in 'reasoning_content' deltas) and emits zero visible
    # 'content' tokens. Setting enable_thinking=False via chat_template_kwargs
    # keeps reasoning but ensures visible output is always produced.
    if not enable_thinking:
        payload["chat_template_kwargs"] = {"enable_thinking": False}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers=headers,
    )

    chunks = []
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            for raw_line in resp:
                line = raw_line.decode("utf-8", errors="replace").rstrip()
                if not line.startswith("data: "):
                    continue
                data = line[6:]
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    content = chunk["choices"][0]["delta"].get("content")
                    if content:
                        # Real-time feedback on stderr; stdout stays clean for capture
                        print(content, end="", flush=True, file=sys.stderr)
                        chunks.append(content)
                except (json.JSONDecodeError, KeyError, IndexError):
                    pass
    except urllib.error.URLError as e:
        print(f"\n[local-llm] ERROR: connection failed: {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"\n[local-llm] ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(file=sys.stderr)  # newline after streamed output on stderr
    full_text = "".join(chunks)
    return _strip_code_fences(full_text)


# ─────────────────────────────────────────────────────────────────────────────
# Health check
# ─────────────────────────────────────────────────────────────────────────────

def health_check(base_url: str, api_key: str, model: str, timeout: int) -> None:
    """GET /v1/models to confirm LM Studio is reachable. Exits 0/1."""
    url = base_url.rstrip("/") + "/models"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {api_key}"})
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp.read()
        latency = time.monotonic() - t0
        print(f"[local-llm] status=ok model={model} latency={latency:.2f}s")
        sys.exit(0)
    except urllib.error.URLError as e:
        print(f"[local-llm] status=unreachable error={e}")
        sys.exit(1)
    except OSError as e:
        print(f"[local-llm] status=error error={e}")
        sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Local LLM CLI wrapper — calls LM Studio and streams output to stdout"
    )
    parser.add_argument("--prompt", help="The prompt to send to the model")
    parser.add_argument(
        "--task-type",
        default="generic",
        choices=list(TASK_DEFAULTS.keys()),
        help="Adjusts system prompt and temperature (default: generic)",
    )
    parser.add_argument("--system", help="Override the system prompt entirely")
    parser.add_argument("--model", help="Override the model name from config")
    parser.add_argument(
        "--model-slot",
        choices=["fast", "quality"],
        help="Use a named model slot from config.models",
    )
    parser.add_argument("--max-tokens", type=int, help="Override max_tokens from config")
    parser.add_argument("--no-cache", action="store_true", help="Skip cache for this call")
    parser.add_argument(
        "--config",
        default=os.path.join(SCRIPT_DIR, "config.json"),
        help="Path to config.json (default: same directory as call.py)",
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="Run a health check (GET /v1/models) and exit",
    )
    args = parser.parse_args()

    cfg = load_config(args.config)

    # ── Health check mode ──────────────────────────────────────────────────
    if args.health:
        health_check(
            cfg["base_url"],
            cfg.get("api_key", "lm-studio"),
            cfg.get("model", "unknown"),
            min(cfg.get("timeout_seconds", 300), 10),  # health check uses a short timeout
        )
        return  # unreachable — health_check exits

    # ── Require prompt ─────────────────────────────────────────────────────
    if not args.prompt:
        print("[local-llm] ERROR: --prompt is required", file=sys.stderr)
        sys.exit(2)

    # ── Check enabled ──────────────────────────────────────────────────────
    if not cfg.get("enabled", True):
        print("[local-llm] disabled in config", file=sys.stderr)
        sys.exit(1)

    # ── Resolve model ──────────────────────────────────────────────────────
    model = cfg.get("model", "")
    if args.model:
        model = args.model
    elif args.model_slot:
        model = cfg.get("models", {}).get(args.model_slot, model)

    if not model:
        print("[local-llm] ERROR: no model configured", file=sys.stderr)
        sys.exit(2)

    # ── Resolve task settings ──────────────────────────────────────────────
    task_defaults = TASK_DEFAULTS.get(args.task_type, TASK_DEFAULTS["generic"])
    system = args.system or task_defaults["system"]
    temperature = task_defaults["temperature"]
    max_tokens = args.max_tokens or cfg.get("max_tokens", 2048)
    timeout = cfg.get("timeout_seconds", 300)
    cache_enabled = cfg.get("cache_enabled", True) and not args.no_cache
    cache_ttl = cfg.get("cache_ttl_hours", 24)
    base_url = cfg["base_url"]
    api_key = cfg.get("api_key", "lm-studio")
    enable_thinking = cfg.get("enable_thinking", True)

    # ── Cache lookup ───────────────────────────────────────────────────────
    key = _cache_key(model, system, args.prompt, max_tokens)
    if cache_enabled:
        cached = _cache_get(key, cache_ttl)
        if cached is not None:
            print(cached)
            print(
                f"[local-llm] status=ok model={model} cached=true",
                file=sys.stderr,
            )
            sys.exit(0)

    # ── Call LM Studio ─────────────────────────────────────────────────────
    t0 = time.monotonic()
    response = call_streaming(
        base_url, api_key, model, system, args.prompt, max_tokens, temperature, timeout,
        enable_thinking=enable_thinking,
    )
    latency = time.monotonic() - t0
    token_estimate = len(response.split())

    # ── Print clean result to stdout (this is what callers capture) ────────
    print(response)

    # ── Cache result ───────────────────────────────────────────────────────
    if cache_enabled and response:
        _cache_set(key, response, cache_ttl)

    print(
        f"[local-llm] status=ok model={model} tokens~{token_estimate} "
        f"latency={latency:.1f}s cached=false",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
