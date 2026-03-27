# /local-llm

Called by `select-model` when the local tier is selected. Executes a prompt against
the local Ollama instance via curl and returns the result inline (no Agent tool).

## When to Use

Do not invoke this directly. It is called from `select-model.md` when model tier is `local`.

## Steps

### 1. Check Ollama Availability

Run this health check:

    curl -s --max-time 3 http://localhost:11434/api/tags

- If the command succeeds (exit 0) and returns JSON → Ollama is running. Continue to Step 2.
- If it fails (exit non-zero, timeout, or connection refused) → Ollama is unavailable.
  Fall back: invoke the Agent tool with `model: haiku` instead, and note in the response:
  > "[local unavailable — fell back to haiku]"

### 2. Determine Which Local Model to Use

Read `{{TOOLBOX_PATH}}/memory/model-config.md`.

- If `local_model` is present in frontmatter → use that value as MODEL.
- If `local_model` is absent → run:

      curl -s http://localhost:11434/api/tags | python3 -c "
      import json,sys
      models = json.load(sys.stdin).get('models', [])
      names = [m['name'] for m in models]
      priority = ['phi3:mini', 'phi3', 'llama3.2:1b', 'llama3.2:3b', 'mistral:7b', 'llama3.1:8b']
      for p in priority:
          if p in names:
              print(p)
              break
      else:
          print(names[0] if names else '')
      "

  If no models are found, fall back to haiku (same as Step 1 failure).
  Auto-selected model is used for this call only — it is NOT persisted unless the user says "save this config".

### 3. Determine the Endpoint

Read `{{TOOLBOX_PATH}}/memory/model-config.md`.

- If `local_endpoint` is present in frontmatter → use that value as ENDPOINT.
- Otherwise → use `http://localhost:11434`.

### 4. Call Ollama API

Construct and run this curl command, substituting PROMPT, MODEL, and ENDPOINT:

    curl -s --max-time 60 \
      -X POST "${ENDPOINT}/api/generate" \
      -H "Content-Type: application/json" \
      -d "{
        \"model\": \"${MODEL}\",
        \"prompt\": \"${PROMPT}\",
        \"stream\": false
      }" | python3 -c "import json,sys; print(json.load(sys.stdin).get('response',''))"

Where:
- `PROMPT` is the task prompt string (escape double quotes with `\"`)
- `MODEL` is from Step 2
- `ENDPOINT` is from Step 3

If curl times out or the response JSON is malformed → fall back to haiku. Note in response:
> "[local call failed — fell back to haiku]"

### 5. Return Result

Print the response text directly to the conversation. Do not wrap it in an Agent result.
Prefix it with: `[local: ${MODEL}]` on its own line, then the response.

Example output:

    [local: phi3:mini]
    fix(auth): validate JWT expiry before returning user session
