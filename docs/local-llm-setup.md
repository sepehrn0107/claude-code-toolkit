# Local LLM Setup (Ollama)

## 1. Download & Install

Download: https://ollama.com/download

Install to the default location for your OS:
- **macOS**: open the `.dmg`, drag Ollama to Applications — installs to `/usr/local/bin/ollama`
- **Linux**: `curl -fsSL https://ollama.com/install.sh | sh` — installs to `/usr/local/bin/ollama`
- **Windows**: run the `.exe` installer — installs to `%LOCALAPPDATA%\Programs\Ollama`

## 2. Start the Server

    ollama serve

Runs in the foreground on `http://localhost:11434`.
To run in the background (macOS/Linux): `ollama serve &`
On macOS the menu-bar app also starts it automatically.

## 3. Pull a Model

Recommended lightweight models (fast on CPU):

    ollama pull phi3:mini        # ~2 GB, fast, good for text tasks
    ollama pull llama3.2:3b      # ~2 GB, good general purpose
    ollama pull mistral:7b       # ~4 GB, stronger reasoning

List installed models:

    ollama list

## 4. Verify

    curl http://localhost:11434/api/tags

Expected: JSON with `{"models": [...]}`. If you get connection refused, the server is not running.

## 5. Test a Prompt

    curl -s -X POST http://localhost:11434/api/generate \
      -H "Content-Type: application/json" \
      -d '{"model": "phi3:mini", "prompt": "Say hello", "stream": false}' \
      | python3 -c "import json,sys; print(json.load(sys.stdin)['response'])"

## 6. Configure the Toolbox (optional)

To pin a specific model and skip auto-detection, add to
`{{TOOLBOX_PATH}}/memory/model-config.md`:

    ---
    default_model: local
    local_model: phi3:mini
    local_endpoint: http://localhost:11434
    saved_by_user: true
    ---

If you skip this, `select-model` will auto-detect your fastest available model.
